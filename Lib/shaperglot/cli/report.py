from collections import defaultdict
import os
import re
from textwrap import fill
from typing import Iterable

from shaperglot.checker import Checker
from shaperglot.languages import Languages
from shaperglot.reporter import Result


def report(options) -> None:
    """Report which languages are supported by the given font"""
    checker = Checker(options.font)
    langs = Languages()
    nearly = []
    supported = []
    unsupported = []
    fixes_needed = defaultdict(set)

    if options.csv:
        print(
            "Language,Name,Supported,Bases Missing,Marks Missing,Orphaned Marks,Other"
        )

    for lang in sorted(langs.keys()):
        if options.filter and not re.search(options.filter, lang):
            continue
        results = checker.check(langs[lang])

        if results.is_unknown:
            continue

        if options.csv:
            report_csv(lang, langs[lang], results)
            continue

        if results.is_success:
            supported.append(lang)
            msg = "supports"
        elif results.is_nearly_success(options.nearly):
            nearly.append(lang)
            msg = "nearly supports"
        else:
            unsupported.append(lang)
            msg = "does not fully support"

        for fixtype, things in results.unique_fixes().items():
            fixes_needed[fixtype].update(things)
        if options.group:
            continue
        print(f"Font {msg} language '{lang}' ({langs[lang]['name']})")

        if options.verbose and options.verbose > 1:
            for status, message in results:
                print(f" * {status.value}: {message}")

    if options.csv:
        return

    if options.group:
        if supported:
            print("Supported languages")
            print("===================\n")
        for lang in supported:
            print(f"Font supports language '{lang}' ({langs[lang]['name']})")

        if nearly:
            print("\nNearly supported languages")
            print("===================\n")
        for lang in nearly:
            print(f"Font nearly supports language '{lang}' ({langs[lang]['name']})")

        if unsupported:
            print("\nUnsupported languages")
            print("====================\n")
        for lang in unsupported:
            print(
                f"Font does not fully support language '{lang}' ({langs[lang]['name']})"
            )
    # Collate a useful fixing guide
    short_summary(supported, nearly, unsupported)
    if options.verbose:
        long_summary(fixes_needed, unsupported)


def short_summary(supported, nearly, unsupported) -> None:
    print("\n== Summary ==\n")
    print(f"* {len(supported)+len(nearly)+len(unsupported)} languages checked")
    if supported:
        print(f"* {len(supported)} languages supported")
    if nearly:
        print(f"* {len(supported)} languages nearly supported")


def long_summary(fixes_needed, unsupported) -> None:
    if unsupported:
        print(
            fill(
                "* Unsupported languages: " + ", ".join(unsupported),
                subsequent_indent=" " * 25,
                width=os.get_terminal_size()[0] - 2,
            )
        )
        print("\nTo add support:")
    for category, fixes in fixes_needed.items():
        plural = "s" if len(fixes) > 1 else ""
        print(f" * {category.replace('_', ' ').capitalize()}{plural}: ")
        for fix in sorted(fixes):
            print("    - " + fix)


def report_csv(langcode, lang, results: Iterable[Result]) -> None:
    print(f"{langcode},\"{lang['name']}\",{results.is_success},", end="")
    missing_bases = set()
    missing_marks = set()
    missing_anchors = set()
    other_errors = set()
    for msg in results:
        if msg.result_code == "bases-missing":
            missing_bases |= set(msg.context["glyphs"])
        elif msg.result_code == "marks-missing":
            missing_marks |= set(msg.context["glyphs"])
        elif msg.result_code == "orphaned-mark":
            missing_anchors.add(msg.context["base"] + "/" + msg.context["mark"])
        else:
            other_errors.add(msg.result_code)
    print(" ".join(sorted(missing_bases)), end=",")
    print(" ".join(sorted(missing_marks)), end=",")
    print(" ".join(sorted(missing_anchors)), end=",")
    print(" ".join(sorted(other_errors)), end="\n")
