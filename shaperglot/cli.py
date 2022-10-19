import argparse
import sys
from textwrap import fill
import os

from shaperglot.checker import Checker
from shaperglot.languages import Languages


def describe(options):
    langs = Languages()
    if options.lang not in langs:
        maybe = langs.disambiguate(options.lang)
        if len(maybe) == 1:
            l = langs[maybe[0]]
            print(f"Assuming you meant {maybe[0]} ({l['full_name']}).")
        elif len(maybe) > 1:
            print(f"Language '{options.lang}' not known", end="")
            print("; try one of: " + ", ".join(maybe))
            return
        else:
            print(f"Language '{options.lang}' not known", end="")
            print("")
            return
    else:
        l = langs[options.lang]
    print(f"To test for {l['name']} support, shaperglot will:")
    for shaperglot_check in l.get("shaperglot_checks", []):
        print(
            fill(
                "ensure " + shaperglot_check.describe(),
                initial_indent=" * ",
                subsequent_indent="   ",
                width=os.get_terminal_size()[0] - 2,
            )
        )


def check(options):
    checker = Checker(options.font)
    langs = Languages()
    for lang in options.lang:
        if lang not in langs:
            print(f"Language '{options.lang}' not known")
            continue

        results = checker.check(langs[lang])

        if results.is_success:
            print(f"Font supports language '{lang}'")
        else:
            print(f"Font does not fully support language '{lang}'")

        if options.verbose and options.verbose > 1:
            for status, message in results:
                print(f" * {status.value}: {message}")
        elif options.verbose or not results.is_success:
            for message in results.fails:
                print(f" * {message}")


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Check a font file's language coverage"
    )
    subparsers = parser.add_subparsers(help='sub-commands')

    parser_describe = subparsers.add_parser(
        'describe', help='describe what is needed for language support'
    )
    parser_describe.add_argument(
        'lang', metavar='LANG', help='an ISO639-3 language code'
    )
    parser_describe.set_defaults(func=describe)

    parser_check = subparsers.add_parser(
        'check', help='check a particular language or languages are supported'
    )
    parser_check.add_argument('--verbose', '-v', action='count')
    parser_check.add_argument('font', metavar='FONT', help='the font file')
    parser_check.add_argument(
        'lang', metavar='LANG', help='one or more ISO639-3 language codes', nargs="+"
    )
    parser_check.set_defaults(func=check)

    parser_report = subparsers.add_parser(
        'report', help='report which languages are supported'
    )
    parser_report.add_argument('font', metavar='FONT', help='the font file')

    options = parser.parse_args(args)
    if not hasattr(options, "func"):
        parser.print_help()
        sys.exit(1)
    options.func(options)


if __name__ == '__main__':  # pragma: no cover
    main()
