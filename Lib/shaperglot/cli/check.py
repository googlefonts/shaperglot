from shaperglot.checker import Checker
from shaperglot.languages import Languages


def find_lang(lang, langs):
    # Find the language in the languages list; could be by ID, by name, etc.
    if lang in langs:
        return lang
    for lang_id in langs.keys():
        lang_info = langs[lang_id]
        if (
            lang_info['name'].lower() == lang.lower()
            or lang_id.lower() == lang.lower()
            or lang_info["language"].lower() == lang.lower()
            or lang_info.get("autonym", "").lower() == lang.lower()
        ):
            return lang_id


def check(options):
    """Check a particular language or languages are supported"""
    checker = Checker(options.font)
    langs = Languages()
    for orig_lang in options.lang:
        lang = find_lang(orig_lang, langs)
        if not lang:
            print(f"Language '{orig_lang}' not known")
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
