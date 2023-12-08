import argparse
import os
import subprocess
import glob
import yaml
import json
from multiprocessing import Pool
from pathlib import Path
from itertools import repeat
import datetime

from shaperglot.languages import Languages
from shaperglot.checker import Checker
from shaperglot.reporter import Result

gflangs = Languages()


with open("./data/iso639-3-afr-all.txt", "r") as f2:
    afr_tags = f2.read().splitlines()

results = open("results.json", "w", encoding="utf8")
overview = open("afr_tag_overview.json", "w", encoding='utf8')

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


def split_dict(input_dict: dict, num_parts: int) -> list:
    list_len: int = len(input_dict)
    return [
        dict(
            list(input_dict.items())[
                i * list_len // num_parts : (i + 1) * list_len // num_parts
            ]
        )
        for i in range(num_parts)
    ]


def summarize(failing_fonts, passing_fonts):
    pass_fails = []
    failkeys = set([key for l in failing_fonts for key in l.keys()])
    failfonts = [[d[x] for d in failing_fonts if x in d] for x in failkeys]

    passkeys = set([key for l in passing_fonts for key in l.keys()])
    passfonts = [[d[x] for d in passing_fonts if x in d] for x in passkeys]

    for idk, key in enumerate(passkeys):
        this_passfonts = passfonts[idk]
        if this_passfonts:
            pass_fails.append(
                {
                    'tag': key,
                    'pass': {'count': len(this_passfonts), 'fonts': this_passfonts},
                }
            )

    for idk, key in enumerate(failkeys):
        this_failfonts = failfonts[idk]
        id_in_passfails = next(
            (index for index, d in enumerate(pass_fails) if key in d['tag']), None
        )
        if this_failfonts and id_in_passfails != None:
            pass_fails[id_in_passfails]['fail'] = {
                'count': len(this_failfonts),
                'fonts': this_failfonts,
            }
        elif not this_failfonts and id_in_passfails != None:
            pass_fails[id_in_passfails]['fail'] = {'count': 0, 'fonts': []}
        elif this_failfonts and id_in_passfails == None:
            pass_fails.append(
                {
                    'tag': key,
                    'pass': {'count': 0, 'fonts': []},
                    'fail': {'count': len(this_failfonts), 'fonts': this_failfonts},
                }
            )
    return pass_fails


def check_one(font, available_tags):
    checker = Checker(font)
    print(f"analyzing {font}")
    results_for_font = {}
    for tag, item in available_tags.items():
        try:
            results_for_font[tag] = checker.check(gflangs[item])
        except:
            print(f"Something went wrong with {font}")
    return results_for_font


def run_checker(fonts, tag_results, args, failing_fonts, passing_fonts):
    with Pool() as p:
        all_font_results = p.starmap(check_one, args)
    for font, font_results in zip(fonts, all_font_results):
        fontname = Path(font).stem
        for tag, this_tag_results in font_results.items():
            fails = [
                message.message
                for message in this_tag_results
                if message.result != Result.PASS
            ]
            if fails:
                tag_results.setdefault(tag, {})[fontname] = fails
                failing_fonts.append({tag: fontname})
            else:
                passing_fonts.append({tag: fontname})


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Check a library for African language support"
    )
    parser.add_argument('directory', help='directory to check')

    args = parser.parse_args()
    fonts = [str(f) for f in Path(args.directory).glob("**/*.ttf")]

    tag_results = {}
    missing_tags = []
    available_tags = {}
    passing_fonts = []
    failing_fonts = []

    for tag in afr_tags:
        if isoconv.get(tag) is not None:
            item = isoconv.get(tag) + "_Latn"
        else:
            item = tag + "_Latn"
        if item not in gflangs:
            missing_tags.append(item)
            continue

        available_tags[tag] = item

    split_avail_tags = split_dict(available_tags, 50)

    for idx, x in enumerate(split_avail_tags):
        args = zip(fonts, repeat(split_avail_tags[idx]))
        run_checker(fonts, tag_results, args, failing_fonts, passing_fonts)

    pf = summarize(failing_fonts, passing_fonts)
    pf.append({"Missing GFLang Data": missing_tags})
    current_time = datetime.datetime.now()
    pf.append({"Timestamp": f"{current_time}"})
    json.dump(tag_results, results, indent=1)
    json.dump(pf, overview, indent=1)


if __name__ == "__main__":
    main()
