import re

from strictyaml import Map

from .common import ShaperglotCheck, and_join

def parse_bases(bases):
    return [x[0] or x[1] for x in re.findall(r"\{([^}]+)\}|(\S+)", bases)]


def can_shape(text, checker):
    buf = checker.vharfbuzz.shape(text)
    return all(gi.codepoint != 0 for gi in buf.glyph_infos)


class OrthographiesCheck(ShaperglotCheck):
    name = "orthographies"
    schema = Map({})

    # pylint: disable=W0231
    def __init__(self, lang):
        exemplar_chars = lang.get("exemplarChars", {})
        marks = exemplar_chars.get("marks", "").replace("◌", "").split() or []
        bases = parse_bases(exemplar_chars.get("base", ""))
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
        missing = [x for x in self.bases if not can_shape(x, checker)]
        if missing:
            missing = ", ".join(missing)
            checker.results.fail(f"Some base glyphs were missing: {missing}")
        else:
            checker.results.okay("All base glyphs were present in the font")
        if self.marks:
            missing = [x for x in self.marks if not can_shape(x, checker)]
            if missing:
                missing = ", ".join([chr(0x25cc)+x for x in missing])
                checker.results.fail(f"Some mark glyphs were missing: {missing}")
            else:
                checker.results.okay("All mark glyphs were present in the font")
