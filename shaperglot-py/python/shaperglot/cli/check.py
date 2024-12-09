from collections import defaultdict
from typing import Optional

from shaperglot import Checker, Languages, Reporter

try:
    import glyphsets
except ImportError:
    glyphsets = None


def find_lang(lang: str, langs: Languages) -> Optional[str]:
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
    return None


def check(options) -> None:
    """Check a particular language or languages are supported"""
    checker = Checker(options.font)
    langs = Languages()
    fixes_needed = defaultdict(set)
    lang_arg = []
    for lang in options.lang:
        if glyphsets and lang in glyphsets.defined_glyphsets():
            lang_arg.extend(glyphsets.languages_per_glyphset(lang))
        else:
            lang_arg.append(lang)

    for orig_lang in lang_arg:
        lang = find_lang(orig_lang, langs)
        if not lang:
            print(f"Language '{orig_lang}' not known")
            continue

        reporter = checker.check(langs[lang])

        if reporter.is_unknown:
            print(f"Cannot determine whether font supports language '{lang}'")
        elif reporter.is_nearly_success(options.nearly):
            print(f"Font nearly supports language '{lang}' {reporter.score:.1f}%")
            for fixtype, things in reporter.unique_fixes().items():
                fixes_needed[fixtype].update(things)
        elif reporter.is_success:
            print(f"Font supports language '{lang}'")
        else:
            print(
                f"Font does not fully support language '{lang}' {reporter.score:.1f}%"
            )

        if options.verbose and options.verbose > 1:
            for result in reporter:
                print(f" * {result.message} {result.status_code}")
        elif options.verbose or not reporter.is_success:
            for result in reporter:
                if not result.is_success:
                    print(f" * {result}")

    if fixes_needed:
        show_how_to_fix(fixes_needed)


def show_how_to_fix(reporter: Reporter):
    print("\nTo add full support to nearly-supported languages:")
    for category, fixes in reporter.items():
        plural = "s" if len(fixes) > 1 else ""
        print(f" * {category.replace('_', ' ').capitalize()}{plural}: ", end="")
        print("; ".join(sorted(fixes)))
