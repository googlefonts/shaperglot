from itertools import permutations
import os
from xxlimited import new
import yaml
import sys
import unicodedata
import itertools
from gflanguages import LoadLanguages, LoadScripts
from google.protobuf.json_format import MessageToDict

gflangs = LoadLanguages()
gfscripts = LoadScripts()

isoconv = {"aar": "aa", "afr": "af", "aka": "ak", "amh": "am", "bam": "bm", "ewe": "ee", "ful": "ff", "hau": "ha", "her": "hz", "ibo": "ig", "kik": "ki", "kin": "rw", "kon": "kg", "kua": "kj", "lin": "ln", "lub": "lu", "lug": "lg", "mlg": "mg", "nbl": "nr", "nde": "nd", "ndo": "ng", "nya": "ny", "orm": "om", "run": "rn", "sag": "sg", "sna": "sn", "som": "so", "sot": "st", "ssw": "ss", "swa": "sw", "tir": "ti", "tsn": "tn", "tso": "ts", "twi": "tw", "ven": "ve", "wol": "wo", "xho": "xh", "yor": "yo"}

with open('./language_tag_data/ot-lang-tags.yaml', 'r') as f:
    ot_tags = yaml.safe_load(f)
    #debug pprint(dataMap)

with open('./language_tag_data/iso639-3-afr-all.txt', 'r') as f2:
    afr_tags = f2.read().splitlines() 

def create_file(profile_name):
    path = "./shaperglot/languages/"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    profile = open(path + profile_name, "w")
    return profile

def collect(lang):
    exemplar_chars = lang.get("exemplarChars", {})
    marks = exemplar_chars.get("marks", "").replace("◌", "").split() or []
    bases = exemplar_chars.get("base", "").split() or []
    auxiliary = exemplar_chars.get("auxiliary", "").split() or []
    return(bases, auxiliary, marks)

def check_ot_tags (tag): #to be used for unencoded glyph variant check
    for ot_tag in ot_tags:
        if tag in ot_tag['codes']:
            return(True)
        else:
            return(False)

def build_unencoded_gv(record, bases, auxiliary): #to be used for unencoded glyph variant check
    if record.get("exemplarChars"):
        if "\u014A" in bases or '\u014A' in auxiliary:
            return(True)

def build_no_orphaned_marks(bases, auxiliary):
    basemarks = []
    nom_test = []
    nom_smcp_test = []
    new_basemarks = []

    for base in bases:
        if len(base) > 1 :
            unpack = base.replace("{", "").replace("}", "")
            for char in unpack:
                if unicodedata.combining(char):
                    basemarks.append(unpack)
    for aux in auxiliary:
        if len(aux) > 1:
            unpack = aux.replace("{", "").replace("}", "")
            for char in unpack:
                if unicodedata.combining(char):
                    basemarks.append(unpack)

    for basemark in basemarks:
        if len(basemark) > 2:
            base_only = basemark[0]
            marks_only = "basemark"[1:len(basemark)]
            for i in itertools.permutations(marks_only, len(marks_only)): #generate mark permutations
                new_basemark = base_only.join(i)
                new_basemarks.append(new_basemark)

    if new_basemarks:
        basemark_string = "".join(basemarks).join(new_basemarks)
    else:
        basemark_string = "".join(basemarks)
    
    if basemark_string:
        nom_test = {"check": "no_orphaned_marks", "input": {"text": basemark_string}}
        nom_smcp_test = {"check": "no_orphaned_marks", "input": {"text": basemark_string, "features": {"smcp": True}}}
    return(nom_test, nom_smcp_test)

def build_results(item, new_profile):
    profile = ""
    if(profile == ''):
        current_script = item
        profile_name = '%s.yaml' % item
        profile = create_file(profile_name)
        profile.write("#auto-generated using sg-bulk-builder.py\n")
        yaml.safe_dump(new_profile, profile, allow_unicode=True, sort_keys=False)
        print("Building " + item + ".yaml")
    elif(item != current_script):
        profile.close
        current_script = item
        profile_name = '%s.yaml' % item
        profile = create_file(profile_name)
        profile.write("#auto-generated using sg-bulk-builder.py\n")
        yaml.safe_dump(new_profile, profile, allow_unicode=True, sort_keys=False)
        print("Building " + item + ".yaml")



def main():
    new_profile = []
    record = {}
    all_tags = 0
    with_record = 0
    with_ot_tags = 0
    with_exemplars = 0
    needs_variant = 0


    for tag in afr_tags:
        new_profile = []

        all_tags = all_tags + 1
        item = ""
        if isoconv.get(tag) is not None:
            item =  isoconv.get(tag)+"_Latn"
        else:
            item = tag+"_Latn"
        if item in gflangs:
            record = MessageToDict(gflangs[item])
            bases, auxiliary, marks = collect(record)
            with_record = with_record + 1
            if bases:
                with_exemplars = with_exemplars + 1

            nom_test, nom_smcp_test = build_no_orphaned_marks(bases, auxiliary)
            if nom_test:
                new_profile.append(nom_test)
                new_profile.append(nom_smcp_test)
            
                build_results(item, new_profile)


    #profile.close
    f.close
    f2.close
                                                
    print("African ISO-639 tags:\t" + str(all_tags) + "\nAvailable GF Lang Record:\t" + str(with_record) + "\nGF Lang Contains Exemplar Characters:\t" + str(with_exemplars) + "\nCorresponding OT Lang Tag Exists:\t" + str(with_ot_tags) + "\nNeeds Glyphs Variant:\t" + str(needs_variant))

if __name__ == '__main__':
    main()
