import os
import subprocess
import glob
import yaml
from multiprocessing import Pool
from pathlib import Path
from itertools import repeat

from shaperglot.languages import Languages
from shaperglot.checker import Checker
from shaperglot.reporter import Result

gflangs = Languages()


with open("./language_tag_data/iso639-3-afr-all.txt", "r") as f2:
    afr_tags = f2.read().splitlines()

output = open("results.txt", "w", encoding="utf8")
results = open("results.yaml", "w", encoding="utf8")
summary = open("summary.csv", "w", encoding="utf8")

isoconv = {
    "aar": "aa",
    "afr": "af",
    "aka": "ak",
    "amh": "am",
    "bam": "bm",
    "ewe": "ee",
    "ful": "ff",
    "hau": "ha",
    "her": "hz",
    "ibo": "ig",
    "kik": "ki",
    "kin": "rw",
    "kon": "kg",
    "kua": "kj",
    "lin": "ln",
    "lub": "lu",
    "lug": "lg",
    "mlg": "mg",
    "nbl": "nr",
    "nde": "nd",
    "ndo": "ng",
    "nya": "ny",
    "orm": "om",
    "run": "rn",
    "sag": "sg",
    "sna": "sn",
    "som": "so",
    "sot": "st",
    "ssw": "ss",
    "swa": "sw",
    "tir": "ti",
    "tsn": "tn",
    "tso": "ts",
    "twi": "tw",
    "ven": "ve",
    "wol": "wo",
    "xho": "xh",
    "yor": "yo",
}


#afr_tags = ["dje", "agq", "ro", "bjp", "bas"]


def summarize(tag, fontname, results):
    for code, failure in results:
        
        if code == Result.PASS:
            continue
        if "Some base glyphs were missing" in failure:
            details = failure.split(":")
            glyphs = details[1].split(",")
            errcount = str(len(glyphs))
            summary.write(fontname + "," + tag + ",missing base," + errcount + "\n")
        if "Some mark glyphs were missing" in failure:
            details = failure.split(":")
            glyphs = details[1].split(",")
            errcount = str(len(glyphs))
            summary.write(fontname + "," + tag + ",missing mark," + errcount + "\n")
        if (
            "Shaper produced a .notdef" in failure
        ):  # Needs implementation for when shaping succeeds
            summary.write(fontname + "," + tag + ",orphaned marks,1\n")
        if "not known" in failure:
            summary.write(fontname + "," + tag + ",profile missing,1\n")


def check_one(font, available_tags):
    checker = Checker(font)
    print(f"analyzing {font}")
    results_for_font = {}
    for tag, item in available_tags.items():
        results_for_font[tag] = checker.check(gflangs[item])
    return results_for_font


def main():
    fonts = glob.glob("./fonts/*.ttf")

    tag_results = {}
    missing_tags = []
    available_tags = {}

    for tag in afr_tags:
        if isoconv.get(tag) is not None:
            item = isoconv.get(tag) + "_Latn"
        else:
            item = tag + "_Latn"
        if item not in gflangs:
            missing_tags.append(item)
            continue
        available_tags[tag] = item

    args = zip(fonts, repeat(available_tags))
    with Pool() as p:
        all_font_results = p.starmap(check_one, args)
    for font, font_results in zip(fonts, all_font_results):
        fontname = Path(font).stem
        for tag, this_tag_results in font_results.items():
            summarize(tag, fontname, this_tag_results)
            tag_results.setdefault(tag, {})[fontname] = [
                message for code, message in this_tag_results if code != Result.PASS
            ]

    tag_results["Missing GFLang Data"] = missing_tags
    yaml.safe_dump(tag_results, results, allow_unicode=True, sort_keys=False)


if __name__ == "__main__":
    main()