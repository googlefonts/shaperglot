import os
from strictyaml import load, Seq
from pathlib import Path
from gflanguages import LoadLanguages, LoadScripts
from strictyaml import YAMLValidationError
from .checks import schemas, checks_map
from .checks.orthographies import OrthographiesCheck
from google.protobuf.json_format import MessageToDict
import sys

gflangs = LoadLanguages()
gfscripts = LoadScripts()

definitions_directory = Path(__file__).parent / "languages"


def load_shaperglot_definition(language, validate=False):
    definition_file = definitions_directory / (language + ".yaml")
    if not definition_file.is_file():
        return []
    data = load(open(definition_file).read())
    check_objects = []
    for ix, check in enumerate(data):
        if validate:
            if check["check"] not in schemas:
                raise ValueError(
                    f"Language definition file for {language} invalid; unknown check type {check['check']} in check {ix} - choose from { ', '.join(schemas.keys()) }"
                )
            try:
                check.revalidate(schemas[check["check"]])
            except YAMLValidationError as e:
                raise ValueError(
                    f"Language definition file for {language} invalid; parser error in check {ix}: {e}"
                )
        # This turns a { "check": "foobar" } into a FoobarCheck({"check": "foobar"})
        check_objects.append(checks_map[check["check"]](check))
    return check_objects


class Languages():
    loaded = {}

    def __contains__(self, item):
        return item in gflangs

    def keys(self):
        return gflangs.keys()

    def disambiguate(self, lang):
        maybe_keys = [
            k for k in gflangs.keys() if k.lower().startswith(lang.lower()+"_")
        ]
        if maybe_keys:
            return maybe_keys
        maybe_keys = [
            k for k,v in gflangs.items() if v.name.lower().startswith(lang.lower())
        ]
        return maybe_keys

    def __getitem__(self, item):
        if item in self.loaded:
            return self.loaded[item]
        if item not in gflangs:
            return
        orig = MessageToDict(gflangs[item])
        orig["full_name"] = orig["name"]+ " in the "+ gfscripts[orig["script"]].name+" script"
        orig["shaperglot_checks"] = [OrthographiesCheck(orig)]
        try:
            checks = load_shaperglot_definition(item, validate=True)
        except Exception as e:
            print(f"The shaperglot definition for {item} is not valid. Please report a bug.")
            print(e)
            sys.exit(1)
        orig["shaperglot_checks"].extend(checks)
        self.loaded[item] = orig
        return orig
