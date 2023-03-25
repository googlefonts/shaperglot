import os
import yaml
import sys
import unicodedata
from gflanguages import LoadLanguages, LoadScripts
from google.protobuf.json_format import MessageToDict

gflangs = LoadLanguages()
gfscripts = LoadScripts()

isoconv = {"aar": "aa", "afr": "af", "aka": "ak", "amh": "am", "bam": "bm", "ewe": "ee", "ful": "ff", "hau": "ha", "her": "hz", "ibo": "ig", "kik": "ki", "kin": "rw", "kon": "kg", "kua": "kj", "lin": "ln", "lub": "lu", "lug": "lg", "mlg": "mg", "nbl": "nr", "nde": "nd", "ndo": "ng", "nya": "ny", "orm": "om", "run": "rn", "sag": "sg", "sna": "sn", "som": "so", "sot": "st", "ssw": "ss", "swa": "sw", "tir": "ti", "tsn": "tn", "tso": "ts", "twi": "tw", "ven": "ve", "wol": "wo", "xho": "xh", "yor": "yo"}

with open('./language_tag_data/ot-lang-tags.yaml', 'r') as f:
    ot_tags = yaml.safe_load(f)

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

def build_orthographies(bases, auxiliary):
    ortho_string = ""
    orth_smcp_test = []

    if bases:
        ortho_string = "".join(bases)
    if auxiliary:
        ortho_string = ortho_string.join(auxiliary)

    if ortho_string:
        orth_smcp_test = {"check": "orthographies", "input": {"text": ortho_string, "features": {"smcp": True}}, "conditions": {"features": ['smcp']}}
    return(orth_smcp_test)


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
    basemark_string = "".join(basemarks)
    if basemark_string:
        nom_test = {"check": "no_orphaned_marks", "input": {"text": basemark_string}}
        nom_smcp_test = {"check": "no_orphaned_marks", "input": {"text": basemark_string, "features": {"smcp": True}}, "conditions": {"features": ['smcp']}}
    return(nom_test, nom_smcp_test)

def check_ot_tags(tag): #to be used for unencoded glyph variant check may not be needed

    for ot_tag in ot_tags:
        if tag in ot_tag['codes']:
            return(True)
        else:
            return(False)

def build_unencoded_variants(record, bases, auxiliary): #to be used for unencoded glyph variant check
    uv_test = []
    if record.get("exemplarChars"):
        if "Ŋ" in bases or 'Ŋ' in auxiliary:
            uv_test = {"check": "unencoded_variants", "input": {"text": 'Ŋ'}}
    if record.get("language") == "tod":
        uv_test = {"check": "unencoded_variants", "input": {"text": 'ʋ'}}
        uv_test = {"check": "unencoded_variants", "input": {"text": 'Ʋ'}}
    if record.get("language") == "xpe" or record.get("language") == "lom" or record.get("language") == "dnj":
        uv_test = {"check": "unencoded_variants", "input": {"text": 'Ɓ'}}
    if record.get("language") == "gaa":
        uv_test = {"check": "unencoded_variants", "input": {"text": 'Ʃ'}}
        uv_test = {"check": "unencoded_variants", "input": {"text": 'Ʒ'}}

    return(uv_test)


def build_sd_smcp(bases, auxiliary):
    sd_smcp_collection = []
    for base in bases:
        sd_smcp_test = []
        if len(base) == 1 and unicodedata.category(base) == 'Ll' :
            sd_smcp_test = {'check': 'shaping_differs', 'inputs': [{'text': base}, {'text': base, 'features': {'smcp': True}}], 'conditions': {'features': ['smcp']}, 'rationale': "Requires Small-cap: " + base}
            sd_smcp_collection.append(sd_smcp_test)
    for aux in auxiliary:
        sd_smcp_test = []
        if len(aux) == 1 and unicodedata.category(aux) == 'Ll' :
            sd_smcp_test = {'check': 'shaping_differs', 'inputs': [{'text': aux}, {'text': aux, 'features': {'smcp': True}}], 'conditions': {'features': ['smcp']}, 'rationale': "Requires Small-cap: " + aux}
            sd_smcp_collection.append(sd_smcp_test)
    return(sd_smcp_collection)

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

            sd_smcp_test = build_sd_smcp(bases, auxiliary)
            nom_test, nom_smcp_test = build_no_orphaned_marks(bases, auxiliary)
            uv_test = build_unencoded_variants(record, bases, auxiliary)
        

            if nom_smcp_test:
                new_profile.append(nom_test)
                new_profile.append(nom_smcp_test)
            if uv_test:
                new_profile.append(uv_test)
            if sd_smcp_test:
                for test in sd_smcp_test:
                    new_profile.append(test)
            if new_profile:
                build_results(item, new_profile)



    f.close
    f2.close
                                                
    print("African ISO-639 tags:\t" + str(all_tags) + "\nAvailable GF Lang Record:\t" + str(with_record) + "\nGF Lang Contains Exemplar Characters:\t" + str(with_exemplars) + "\nCorresponding OT Lang Tag Exists:\t" + str(with_ot_tags) + "\nNeeds Glyphs Variant:\t" + str(needs_variant))

if __name__ == '__main__':
    main()