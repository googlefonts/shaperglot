import os
from textwrap import fill

from shaperglot import Languages


def describe(options) -> None:
    """Describe the checks shaperglot will perform to determine support for a given language"""
    langs = Languages()
    if options.lang not in langs:
        maybe = langs.disambiguate(options.lang)
        if len(maybe) == 1:
            lang = langs[maybe[0]]
            print(f"Assuming you meant {maybe[0]} ({lang['full_name']}).")
        elif len(maybe) > 1:
            print(f"Language '{options.lang}' not known", end="")
            print("; try one of: " + ", ".join(maybe))
            return
        else:
            print(f"Language '{options.lang}' not known", end="")
            print("")
            return
    else:
        lang = langs[options.lang]
    print(f"To test for {lang['name']} support:")
    try:
        width = os.get_terminal_size()[0]
    except OSError:
        width = 80
    for shaperglot_check in lang.checks:
        print(
            fill(
                shaperglot_check.description,
                initial_indent=" * ",
                subsequent_indent="   ",
                width=width - 2,
            )
        )
        if options.verbose:
            for implementation in shaperglot_check.implementations:
                print(
                    fill(
                        "check " + implementation,
                        initial_indent="   - ",
                        subsequent_indent="     ",
                        width=width - 4,
                    )
                )
