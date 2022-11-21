from functools import cache

from strictyaml import Str, Map, Optional
from youseedee import ucd_data

from .common import shaping_input_schema, ShaperglotCheck


class UnencodedVariantsCheck(ShaperglotCheck):
    name = "unencoded_variants"
    schema = Map(
        {
            "check": Str(),
            "input": shaping_input_schema,
            Optional("rationale"): Str(),
        }
    )

    def describe(self):
        return f"that, when {self.input.describe()}, an unencoded variant glyph is substituted used the `locl` feature"

    def execute(self, checker):
        if len(self.input.text) > 1:
            raise ValueError(f"Please only pass one codepoint at a time to the unencoded variants check (not '{self.input.text}')")
        self.input.features["locl"] = False
        buffer = self.input.shape(checker)
        glyphname = checker.glyphorder[buffer.glyph_infos[0].codepoint]
        # Are there variant versions of this glyph?
        variants = [glyph for glyph in checker.glyphorder if glyph.startswith(glyphname+".")]
        if not variants:
            checker.results.warn(
                check_name="unencoded-variants",
                result_code="no-variant",
                message="No variant glyphs were found for "+glyphname,
                context = { "text": self.input.check_yaml, "glyph": glyphname }
            )
            return
        # Try it again with locl on, set the language to the one we're
        # looking for see if something happens.
        # self.input.language = ???
        self.input.features["locl"] = True
        buffer2 = self.input.shape(checker)
        glyphname2 = checker.glyphorder[buffer2.glyph_infos[0].codepoint]
        if glyphname2 == glyphname:
            checker.results.fail(
                check_name="unencoded-variants",
                result_code="unchanged-after-locl",
                message=f"The locl feature did not affect {glyphname}",
                context = { "text": self.input.check_yaml, "glyph": glyphname }
            )
        else:
            checker.results.okay(
                check_name="unencoded-variants",
                message=f"The locl feature changed {glyphname} to {glyphname2}",
                context= { "text": self.input.check_yaml, "glyph": glyphname }
            )
        

