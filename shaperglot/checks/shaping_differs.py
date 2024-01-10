from itertools import permutations
from strictyaml import Seq, Map, Int, Optional
from num2words import num2words

from .common import shaping_input_schema, ShaperglotCheck, check_schema

cluster_schema = Map({Optional("cluster"): Int(), "glyph": Int()})


class ShapingDiffersCheck(ShaperglotCheck):
    name = "shaping_differs"
    schema = check_schema(
        {
            "inputs": Seq(shaping_input_schema),
            Optional("differs"): Seq(cluster_schema),
        }
    )

    def describe(self):
        cluster_desc = []
        if "differs" in self.definition:
            for differs in self.definition["differs"]:
                desc = f"the {num2words(1+int(differs['glyph']), to='ordinal')} glyph"
                if "cluster" in differs:
                    desc += f" of the {num2words(1+int(differs['cluster']), to='ordinal')} cluster"
                cluster_desc.append(desc)
            result = (
                " is different to ".join(
                    [
                        f"{cluster_desc[i]} of the {num2words(1+i, to='ordinal')} output"
                        for i in range(len(cluster_desc))
                    ]
                )
                + "."
            )
        else:
            result = "the outputs differ."
        full_result = f"that, when {self.inputs[0].describe()}, "
        for input_index in range(1, len(self.inputs)):
            full_result += f"and then {self.inputs[input_index].describe()}, "
        full_result += result
        if str(self.definition["rationale"]):
            full_result += f" This is because {self.definition['rationale']}."
        return full_result

    def execute(self, checker):
        # Additional validation to allow arbitrary number of inputs
        assert len(self.inputs) >= 2, "shaping_differs check needs at least two inputs"
        if "differs" in self.definition:
            assert (
                len(self.definition["differs"]) >= 2
            ), "shaping_differs check needs at least two 'differs' items"
            assert len(self.definition["differs"]) == len(
                self.inputs
            ), "'inputs' and 'differs' must have the same length"

        # Build permutations of inputs and differs
        input_permutations = list(permutations(self.inputs, 2))
        differs_permutations = []
        if "differs" in self.definition:
            differs_permutations = list(permutations(self.definition["differs"], 2))

        # Check each permutation
        for permutation, inputs in enumerate(input_permutations):
            buffers = [i.shape(checker) for i in inputs]
            if "differs" not in self.definition:
                # Any difference is OK
                serialized_buf1 = checker.vharfbuzz.serialize_buf(buffers[0])
                serialized_buf2 = checker.vharfbuzz.serialize_buf(buffers[1])
                if serialized_buf1 != serialized_buf2:
                    checker.results.okay(
                        check_name="shaping-differs",
                        message=f"{self.definition['rationale']}",
                    )
                else:
                    checker.results.fail(
                        check_name="shaping-differs",
                        result_code="shaping-did-not-differ",
                        message=f"{self.definition['rationale']}"
                        + "; both buffers returned "
                        + serialized_buf1,
                        context={
                            "input1": inputs[0].check_yaml,
                            "input2": inputs[1].check_yaml,
                        },
                    )
                return
            # We are looking for a specific difference
            glyphs = []
            for differs, buffer in zip(differs_permutations[permutation], buffers):
                buffer = list(zip(buffer.glyph_infos, buffer.glyph_positions))
                if "cluster" in differs:
                    buffer = [
                        x for x in buffer if x[0].cluster == int(differs["cluster"])
                    ]
                glyph_ix = int(differs["glyph"])
                if len(buffer) - 1 < glyph_ix:
                    checker.results.fail(
                        check_name="shaping-differs",
                        result_code="too-few-glyphs",
                        message=f"Test asked for glyph {glyph_ix} but shaper only returned {len(buffer)} glyphs",
                        context={
                            "input1": inputs[0].check_yaml,
                            "input2": inputs[1].check_yaml,
                        },
                    )
                    return
                glyphs.append((buffer[glyph_ix][0].codepoint, buffer[glyph_ix][1]))
            if glyphs[0] != glyphs[1]:
                checker.results.okay(
                    check_name="shaping-differs",
                    result_code="shaping-did-not-differ",
                    message=f"{self.definition['rationale']}",
                )
            else:
                checker.results.fail(
                    check_name="shaping-differs",
                    result_code="shaping-did-not-differ",
                    message=f"{self.definition['rationale']}"
                    + "; both buffers returned "
                    + serialized_buf1,
                    context={
                        "input1": inputs[0].check_yaml,
                        "input2": inputs[1].check_yaml,
                    },
                )
