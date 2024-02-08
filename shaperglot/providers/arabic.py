import unicodedata
from youseedee import ucd_data

from shaperglot.checks import NoOrphanedMarksCheck, ShapingDiffersCheck

ZWJ = "\u200D"
MANUALLY_DEFINED_MARKS = {
    'ar_Arab': [
        ["\u064E\u0651", 'FATHA+SHADDA'],
        ["\u064B\u0651", 'FATHATAN+SHADDA'],
        ["\u0650\u0651", 'KASRA+SHADDA'],
        ["\u064D\u0651", 'KASRATAN+SHADDA'],
        ["\u064F\u0651", 'DAMMA+SHADDA'],
        ["\u064C\u0651", 'DAMMATAN+SHADDA'],
    ]
}


def get_joining_type(char):
    return ucd_data(ord(char)).get("Joining_Type", "U")


class ArabicProvider:
    @classmethod
    def fill(cls, language):
        if language["script"] != "Arab":
            return
        if "exemplarChars" not in language or "base" not in language["exemplarChars"]:
            return
        # Assemble list of marks
        check_these_marks = []
        for character in language["exemplarChars"].get("marks", []):
            if unicodedata.category(character) == "Mn":
                check_these_marks.append([character, unicodedata.name(character)])
        if language["id"] in MANUALLY_DEFINED_MARKS:
            check_these_marks.extend(MANUALLY_DEFINED_MARKS[language["id"]])
        for character in language["exemplarChars"]["base"]:
            if unicodedata.category(character).startswith("L"):
                joining_type = get_joining_type(character)
                if joining_type in ("R", "D"):
                    language["shaperglot_checks"].extend(
                        cls.shaping_checks(ZWJ, character, '', 'fina')
                    )
                    language["shaperglot_checks"].extend(
                        cls.mark_checks(ZWJ, character, '', check_these_marks, 'fina')
                    )
                if joining_type == "D":
                    language["shaperglot_checks"].extend(
                        cls.shaping_checks(ZWJ, character, ZWJ, 'medi')
                    )
                    language["shaperglot_checks"].extend(
                        cls.mark_checks(ZWJ, character, ZWJ, check_these_marks, 'medi')
                    )
                    language["shaperglot_checks"].extend(
                        cls.shaping_checks('', character, ZWJ, 'init')
                    )
                    language["shaperglot_checks"].extend(
                        cls.mark_checks('', character, ZWJ, check_these_marks, 'init')
                    )
                language["shaperglot_checks"].extend(
                    cls.mark_checks('', character, '', check_these_marks, 'isol')
                )

    @classmethod
    def mark_checks(  # pylint: disable=too-many-arguments
        cls, pre_context, character, post_context, check_these_marks, position
    ):
        for marks, rationale in check_these_marks:
            yield NoOrphanedMarksCheck(
                {
                    'input': {"text": pre_context + character + marks + post_context},
                    'rationale': f"{rationale} on top of {unicodedata.name(character)} (.{position})",
                }
            )

    @classmethod
    def shaping_checks(cls, pre_context, character, post_context, position):
        yield ShapingDiffersCheck(
            {
                'inputs': [
                    {
                        'text': pre_context + character + post_context,
                        'features': {
                            "init": False,
                            "medi": False,
                            "fina": False,
                        },
                    },
                    {'text': pre_context + character + post_context},
                ],
                'rationale': f".{position} version of {unicodedata.name(character)}",
            }
        )
