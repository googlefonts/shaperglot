from shaperglot.checker import Checker
from shaperglot.languages import Languages
import argparse
import sys


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Check a font file's language coverage")
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('font', metavar='FONT', help='the font file')
    parser.add_argument('lang', metavar='LANG', help='an ISO639-3 language code')
    options = parser.parse_args(args)
    checker = Checker(options.font)
    langs = Languages()
    if options.lang not in langs:
        print(f"Language '{options.lang}' not known")
        sys.exit(1)

    results = checker.check(langs[options.lang])

    if results.is_success:
        print(f"Font supports language '{options.lang}'")
    else:
        print(f"Font does not fully support language '{options.lang}'")

    if options.verbose and options.verbose > 1:
        for status, message in results:
            print(f" * {status.value}: {message}")
    elif options.verbose or not results.is_success:
        for message in results.fails:
            print(f" * {message}")

if __name__ == '__main__':  # pragma: no cover
    main()
