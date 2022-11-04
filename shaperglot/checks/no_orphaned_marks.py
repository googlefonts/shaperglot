from functools import cache

from strictyaml import Str, Map, Optional
from youseedee import ucd_data

from .common import shaping_input_schema, ShaperglotCheck


@cache
def _simple_mark_check(codepoint):
    return ucd_data(codepoint).get("General_Category") == "Mn"


class NoOrphanedMarksCheck(ShaperglotCheck):
    name = "no_orphaned_marks"
    schema = Map(
        {
            "check": Str(),
            "input": shaping_input_schema,
            Optional("rationale"): Str(),
        }
    )

    def describe(self):
        return f"that, when {self.input.describe()}, no marks are left unattached"

    def execute(self, checker):
        buffer = self.input.shape(checker)
        dotted_circle_glyph = checker.cmap.get(0x25CC)

        # GDEF may be wrong, don't trust it.
        passed = True
        previous = None
        # pylint: disable=C0103
        for ix, (info, pos) in enumerate(
            zip(buffer.glyph_infos, buffer.glyph_positions)
        ):
            glyphname = checker.glyphorder[buffer.glyph_infos[ix].codepoint]
            # Is this a mark glyph?
            if info.codepoint == 0:
                passed = False
                checker.results.fail("Shaper produced a .notdef")
                break
            if _simple_mark_check(checker.codepoint_for(glyphname)):
                # Was the previous glyph dotted circle?
                if previous and previous == dotted_circle_glyph:
                    passed = False
                    checker.results.fail("Shaper produced a dotted circle")
                elif pos.x_offset == 0 and pos.y_offset == 0:  # Suspicious
                    passed = False
                    checker.results.fail(
                        f"Shaper didn't attach {glyphname} to {previous}"
                    )
            previous = glyphname
        if passed:
            checker.results.okay(
                "No unattached mark glyphs were produced " + self.input.describe()
            )
