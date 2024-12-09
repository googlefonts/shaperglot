import sys
from textwrap import wrap

from shaperglot import Languages


def whatuses(options) -> None:
    """Report which languages use a particular codepoint"""

    char = options.char
    if len(char) > 1:
        try:
            if (
                char.startswith("U+")
                or char.startswith("u+")
                or char.startswith("0x")
                or char.startswith("0X")
            ):
                char = chr(int(char[2:], 16))
            else:
                char = chr(int(char, 16))
        except ValueError:
            print("Could not understand codepoint " + char)
            sys.exit(1)
    langs = Languages()
    base_langs = []
    mark_langs = []
    aux_langs = []
    for lang in langs.values():
        bases = lang.bases
        marks = lang.marks
        aux = lang.auxiliaries
        lang_key = f"{lang['name']} [{lang['id']}]".replace(" ", "\u00A0")
        if char in bases:
            base_langs.append(lang_key)
        elif char in marks:
            mark_langs.append(lang_key)
        elif char in aux:
            aux_langs.append(lang_key)

    if base_langs:
        print(f"{char} is used as a base character in the following languages:")
        for line in wrap(", ".join(sorted(base_langs)), width=75):
            print("  " + line)
        print()
    if mark_langs:
        print(f"◌{char} is used as a mark character in the following languages:")
        for line in wrap(", ".join(sorted(mark_langs)), width=75):
            print("  " + line)
        print()
    if aux_langs:
        print(f"{char} is used as an auxiliary character in the following languages:")
        for line in wrap(", ".join(sorted(aux_langs)), width=75):
            print("  " + line)
