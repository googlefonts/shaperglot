import os
import yaml
import sys
import unicodedata
from gflanguages import LoadLanguages, LoadScripts
from google.protobuf.json_format import MessageToDict

gflangs = LoadLanguages()
gfscripts = LoadScripts()
ZWJ = "\u200D"
MARKS = [
    "\u064E",  # FATHA
    "\u064E\u064E",  # 2xFATHA
    "\u064B",  # FATHATAN
    "\u064B\u0651",  # FATHATAN+SHADDA
    "\u0651\u064B",  # SHADDA+FATHATAN
    "\u064E\u064E\u0651",  # 2xFATHA+SHADDA
    "\u0651\u064E\u064E",  # SHADDA+2xFATHA
    "\u0650",  # KASRA
    "\u0650\u0650",  # 2xKASRA
    "\u064D",  # KASRATAN
    "\u064D\u0651",  # KASRATAN+SHADDA
    "\u0651\u064D",  # SHADDA+KASRATAN
    "\u0650\u0650\u0651",  # 2xKASRA+SHADDA
    "\u0651\u0650\u0650",  # SHADDA+2xKASRA
    "\u064F",  # DAMMA
    "\u064C",  # DAMMATAN
    "\u0651",  # SHADDA
    "\u0652",  # SUKUN
    "\u0652\u0651",  # SUKUN+SHADDA
    "\u0651\u0652",  # SHADDA+SUKUN
    "\u0653",  # MADDAH ABOVE
    "\u0654",  # HAMZA ABOVE
    "\u0655",  # HAMZA BELOW
]

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
    current_script = item
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


def main():
    for language in gflangs:
        tests = []
        if gflangs[language].script == "Arab" and gflangs[language].exemplar_chars.base:
            for character in gflangs[language].exemplar_chars.base:
                if unicodedata.category(character).startswith("L"):
                    # init/medi/fina
                    joining_type = get_joining_type(character)
                    if joining_type in ("R", "D"):
                        # .fina
                        shaping_test = {
                            'check': 'shaping_differs',
                            'inputs': [
                                {
                                    'text': ZWJ + character,
                                    'features': {
                                        "init": False,
                                        "medi": False,
                                        "fina": False,
                                    },
                                },
                                {'text': ZWJ + character},
                            ],
                            'rationale': f".fina version of {unicodedata.name(character)}",
                        }
                        tests.append(shaping_test)
                        # marks
                        for marks in MARKS:
                            shaping_test = {
                                'check': 'no_orphaned_marks',
                                'input': {"text": ZWJ + character + marks},
                                'rationale': f"{marks} on top of {unicodedata.name(character)} (.fina)",
                            }
                            tests.append(shaping_test)
                    if joining_type == "D":
                        # .medi
                        shaping_test = {
                            'check': 'shaping_differs',
                            'inputs': [
                                {
                                    'text': ZWJ + character + ZWJ,
                                    'features': {
                                        "init": False,
                                        "medi": False,
                                        "fina": False,
                                    },
                                },
                                {'text': ZWJ + character + ZWJ},
                            ],
                            'rationale': f".medi version of {unicodedata.name(character)}",
                        }
                        tests.append(shaping_test)
                        # marks
                        for marks in MARKS:
                            shaping_test = {
                                'check': 'no_orphaned_marks',
                                'input': {"text": ZWJ + character + marks + ZWJ},
                                'rationale': f"{marks} on top of {unicodedata.name(character)} (.medi)",
                            }
                            tests.append(shaping_test)
                        # .init
                        shaping_test = {
                            'check': 'shaping_differs',
                            'inputs': [
                                {
                                    'text': character + ZWJ,
                                    'features': {
                                        "init": False,
                                        "medi": False,
                                        "fina": False,
                                    },
                                },
                                {'text': character + ZWJ},
                            ],
                            'rationale': f".init version of {unicodedata.name(character)}",
                        }
                        tests.append(shaping_test)
                        # marks
                        for marks in MARKS:
                            shaping_test = {
                                'check': 'no_orphaned_marks',
                                'input': {"text": character + marks + ZWJ},
                                'rationale': f"{marks} on top of {unicodedata.name(character)} (.init)",
                            }
                            tests.append(shaping_test)
                    # .isol
                    # marks
                    for marks in MARKS:
                        shaping_test = {
                            'check': 'no_orphaned_marks',
                            'input': {"text": character + marks},
                            'rationale': f"{marks} on top of {unicodedata.name(character)} (.isol)",
                        }
                        tests.append(shaping_test)

        if tests:
            build_results(language, tests)


if __name__ == '__main__':
    main()
