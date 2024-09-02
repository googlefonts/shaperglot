import argparse
import sys

from shaperglot.cli.check import check
from shaperglot.cli.describe import describe
from shaperglot.cli.report import report


def main(args=None) -> None:
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Check a font file's language coverage"
    )
    subparsers = parser.add_subparsers(help='sub-commands')

    parser_describe = subparsers.add_parser('describe', help=describe.__doc__)
    parser_describe.add_argument(
        'lang', metavar='LANG', help='an ISO639-3 language code'
    )
    parser_describe.set_defaults(func=describe)

    parser_check = subparsers.add_parser('check', help=check.__doc__)
    parser_check.add_argument('--verbose', '-v', action='count')
    parser_check.add_argument(
        '--nearly',
        type=int,
        help="Number of fixes left to be considered nearly supported",
        default=5,
    )
    parser_check.add_argument('font', metavar='FONT', help='the font file')
    parser_check.add_argument(
        'lang', metavar='LANG', help='one or more ISO639-3 language codes', nargs="+"
    )
    parser_check.set_defaults(func=check)

    parser_report = subparsers.add_parser('report', help=report.__doc__)
    parser_report.add_argument('font', metavar='FONT', help='the font file')
    parser_report.add_argument('--verbose', '-v', action='count')
    parser_report.add_argument(
        '--nearly',
        type=int,
        help="Number of fixes left to be considered nearly supported",
        default=5,
    )
    parser_report.add_argument('--csv', action='store_true', help="Output as CSV")
    parser_report.add_argument(
        '--group', action='store_true', help="Group by success/failure"
    )
    parser_report.add_argument(
        '--filter', type=str, help="Regular expression to filter languages"
    )
    parser_report.set_defaults(func=report)

    options = parser.parse_args(args)
    if not hasattr(options, "func"):
        parser.print_help()
        sys.exit(1)
    options.func(options)


if __name__ == '__main__':  # pragma: no cover
    main()
