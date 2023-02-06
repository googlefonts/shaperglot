import re

from strictyaml import Map

from .common import ShaperglotCheck, and_join


def parse_bases(bases):
    return [x[0] or x[1] for x in re.findall(r"\{([^}]+)\}|(\S+)", bases)]


def can_shape(text, checker):
    if text not in checker.cache["can_shape"]:
        buf = checker.vharfbuzz.shape(text)
        checker.cache["can_shape"][text] = all(
            gi.codepoint != 0 for gi in buf.glyph_infos
        )
    return checker.cache["can_shape"][text]


class OrthographiesCheck(ShaperglotCheck):
    name = "orthographies"
    schema = Map({})

    # pylint: disable=W0231
    def __init__(self, lang):
        exemplar_chars = lang.get("exemplarChars", {})
        marks = exemplar_chars.get("marks", "").replace("◌", "").split() or []
        bases = parse_bases(exemplar_chars.get("base", ""))
        aux = parse_bases(exemplar_chars.get("auxiliary", ""))
        bases = bases + aux
        self.all_glyphs = marks + bases
        self.marks = set(marks)
        self.bases = set(bases) - self.marks

    def should_skip(self, checker):
        return False

    def describe(self):
        return "that the following glyphs are in the font: " + and_join(
            f"'{g}'" for g in self.all_glyphs
        )

    def execute(self, checker):
        if not self.all_glyphs:
            checker.results.warn(
                check_name="orthographies",
                result_code="no-exemplars",
                message=f"No exemplar glyphs were defined for language {checker.lang['name']}",
            )
            return
        missing = sorted([x for x in self.bases if not can_shape(x, checker)])
        if missing:
            checker.results.fail(
                check_name="orthographies",
                result_code="bases-missing",
                message=f"Some base glyphs were missing: {', '.join(missing)}",
                context={"glyphs": missing},
            )
        else:
            checker.results.okay(
                check_name="orthographies",
                message="All base glyphs were present in the font",
            )

        if not self.marks:
            return

        missing = sorted([x for x in self.marks if not can_shape(x, checker)])
        if missing:
            missing_str = ", ".join([chr(0x25CC) + x for x in missing])
            checker.results.fail(
                check_name="orthographies",
                result_code="marks-missing",
                message=f"Some mark glyphs were missing: {missing_str}",
                context={"glyphs": missing},
            )
        else:
            checker.results.okay(
                check_name="orthographies",
                message="All mark glyphs were present in the font",
            )
