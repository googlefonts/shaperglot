import os
import yaml
import sys
import unicodedata
from gflanguages import LoadLanguages, LoadScripts
from google.protobuf.json_format import MessageToDict

gflangs = LoadLanguages()
gfscripts = LoadScripts()

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

with open('./data/ArabicShaping.txt', 'r') as f:
    arabic_shaping = [
        line
        for line in f.read().splitlines()
        if not line.startswith('#') and line.strip()
    ]


def create_file(profile_name):
    path = "./shaperglot/languages/"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    profile = open(path + profile_name, "w")
    return profile


def build_results(item, new_profile):
    profile_name = '%s.yaml' % item
    profile = create_file(profile_name)
    profile.write("#auto-generated using sg-bulk-builder-arabic.py\n")
    yaml.safe_dump(new_profile, profile, allow_unicode=True, sort_keys=False)
    print("Building " + item + ".yaml")


def get_joining_type(char):
    hex_code = str(hex(ord(char))).split("x")[1].zfill(4).upper()
    for line in arabic_shaping:
        if line.startswith(f"{hex_code};"):
            return line.split(';')[2].strip()


def mark_checks(pre_context, character, post_context, check_these_marks, position):
    for marks, rationale in check_these_marks:
        shaping_test = {
            'check': 'no_orphaned_marks',
            'input': {"text": pre_context + character + marks + post_context},
            'rationale': f"{rationale} on top of {unicodedata.name(character)} (.{position})",
        }
        yield shaping_test


def shaping_checks(pre_context, character, post_context, position):
    shaping_test = {
        'check': 'shaping_differs',
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
    yield shaping_test


def main():
    for language in gflangs:
        tests = []
        if gflangs[language].script == "Arab" and gflangs[language].exemplar_chars.base:
            # Assemble list of marks
            check_these_marks = []
            for character in gflangs[language].exemplar_chars.marks:
                if unicodedata.category(character) == "Mn":
                    check_these_marks.append([character, unicodedata.name(character)])
            if language in MANUALLY_DEFINED_MARKS:
                check_these_marks.extend(MANUALLY_DEFINED_MARKS[language])

            for character in gflangs[language].exemplar_chars.base:
                if unicodedata.category(character).startswith("L"):
                    joining_type = get_joining_type(character)
                    if joining_type in ("R", "D"):
                        # .fina
                        tests.extend(shaping_checks(ZWJ, character, '', 'fina'))
                        tests.extend(
                            mark_checks(ZWJ, character, '', check_these_marks, 'fina')
                        )
                    if joining_type == "D":
                        # .medi
                        tests.extend(shaping_checks(ZWJ, character, ZWJ, 'medi'))
                        tests.extend(
                            mark_checks(ZWJ, character, ZWJ, check_these_marks, 'medi')
                        )
                        # .init
                        tests.extend(shaping_checks('', character, ZWJ, 'init'))
                        tests.extend(
                            mark_checks('', character, ZWJ, check_these_marks, 'init')
                        )
                    # .isol
                    tests.extend(
                        mark_checks('', character, '', check_these_marks, 'isol')
                    )

        if tests:
            build_results(language, tests)


if __name__ == '__main__':
    main()
