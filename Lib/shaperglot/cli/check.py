from shaperglot.checker import Checker
from shaperglot.languages import Languages


def check(options):
    """Check a particular language or languages are supported"""
    checker = Checker(options.font)
    langs = Languages()
    for lang in options.lang:
        if lang not in langs:
            print(f"Language '{options.lang}' not known")
            continue

        results = checker.check(langs[lang])

        if results.is_unknown:
            print(f"Cannot determine whether font supports language '{lang}'")
        elif results.is_success:
            print(f"Font supports language '{lang}'")
        else:
            print(f"Font does not fully support language '{lang}'")

        if options.verbose and options.verbose > 1:
            for message in results:
                print(f" * {message}")
        elif options.verbose or not results.is_success:
            for message in results.fails:
                print(f" * {message}")
