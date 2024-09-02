from .common import ShaperglotCheck, check_schema, shaping_input_schema


class UnencodedVariantsCheck(ShaperglotCheck):
    name = "unencoded_variants"
    schema = check_schema(
        {
            "input": shaping_input_schema,
        }
    )

    def describe(self) -> str:
        return (
            f"that, when {self.input.describe()}, an unencoded variant glyph "
            "is substituted used the `locl` feature"
        )

    def execute(self, checker) -> None:
        if len(self.input.text) > 1:
            raise ValueError(
                "Please only pass one codepoint at a time to the unencoded "
                f"variants check (not '{self.input.text}')"
            )
        self.input.features["locl"] = False
        buffer = self.input.shape(checker)
        if buffer.glyph_infos[0].codepoint == 0:
            checker.results.fail(
                check_name="unencoded-variants",
                result_code="notdef-produced",
                message="Shaper produced a .notdef",
                context={"text": self.input.check_yaml},
                fixes=[
                    {
                        "type": "add_codepoint",
                        "thing": self.input.text[buffer.glyph_infos[0].cluster],
                    },
                ],
            )
            return
        glyphname = checker.glyphorder[buffer.glyph_infos[0].codepoint]
        # Are there variant versions of this glyph?
        variants = [
            glyph for glyph in checker.glyphorder if glyph.startswith(glyphname + ".")
        ]

        if not self.input.language:
            self.input.language = checker.lang["language"]

        if not variants:
            checker.results.warn(
                check_name="unencoded-variants",
                result_code="no-variant",
                message="No variant glyphs were found for " + glyphname,
                context={"text": self.input.check_yaml, "glyph": glyphname},
                fixes=[
                    {
                        "type": "add_glyph",
                        "thing": glyphname + ".locl" + self.input.language.upper(),
                    }
                ],
            )
            return
        # Try it again with locl on, set the language to the one we're
        # looking for see if something happens.
        self.input.features["locl"] = True
        buffer2 = self.input.shape(checker)
        glyphname2 = checker.glyphorder[buffer2.glyph_infos[0].codepoint]
        if glyphname2 == glyphname:
            checker.results.fail(
                check_name="unencoded-variants",
                result_code="unchanged-after-locl",
                message=f"The locl feature did not affect {glyphname}",
                context={"text": self.input.check_yaml, "glyph": glyphname},
                fixes=[
                    {
                        "type": "add_feature",
                        "thing": f"a locale rule to substitute {glyphname} with a variant glyph",
                    }
                ],
            )
        else:
            checker.results.okay(
                check_name="unencoded-variants",
                message=f"The locl feature changed {glyphname} to {glyphname2}",
                context={"text": self.input.check_yaml, "glyph": glyphname},
            )
