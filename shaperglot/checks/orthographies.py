from strictyaml import Map

from .common import ShaperglotCheck, and_join


class OrthographiesCheck(ShaperglotCheck):
    name = "orthographies"
    schema = Map({})

    # pylint: disable=W0231
    def __init__(self, lang):
        exemplar_chars = lang.get("exemplarChars", {})
        marks = exemplar_chars.get("marks", "").replace("◌", "").split() or []
        bases = exemplar_chars.get("base", "").split() or []
        self.all_glyphs = marks + bases
        self.marks = set(marks)
        self.bases = set(bases) - self.marks

    def describe(self):
        return "that the following glyphs are in the font: " + and_join(
            f"'{g}'" for g in self.all_glyphs
        )

    def execute(self, checker):
        if not self.all_glyphs:
            checker.results.warn(
                f"No glyphs were defined for language {checker.lang['name']}"
            )
            return
        missing = [x for x in self.bases if ord(x) not in checker.cmap]
        if missing:
            missing = ", ".join(missing)
            checker.results.fail(f"Some base glyphs were missing: {missing}")
        else:
            checker.results.okay("All base glyphs were present in the font")
        if self.marks:
            missing = [x for x in self.marks if ord(x) not in checker.cmap]
            if missing:
                missing = ", ".join(missing)
                checker.results.fail(f"Some mark glyphs were missing: {missing}")
            else:
                checker.results.okay("All mark glyphs were present in the font")
