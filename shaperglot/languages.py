from pathlib import Path
import sys
import yaml

from gflanguages import LoadLanguages, LoadScripts
from strictyaml import YAMLValidationError
from strictyaml import load as strictyaml_load
from google.protobuf.json_format import MessageToDict

from shaperglot.checks.no_orphaned_marks import NoOrphanedMarksInOrthographiesCheck

from .checks import schemas, checks_map
from .checks.orthographies import OrthographiesCheck

gflangs = LoadLanguages()
gfscripts = LoadScripts()

definitions_directory = Path(__file__).parent / "languages"

definition_cache = {}

def load_shaperglot_definition(language, validate=False):
    if language in definition_cache:
        return definition_cache[language]
    definition_file = definitions_directory / (language + ".yaml")
    if not definition_file.is_file():
        return []
    with open(definition_file, encoding="utf-8") as fh:
        print("Loading ", language)
        if validate:
            data = strictyaml_load(fh.read())
        else:
            data = yaml.safe_load(fh.read())
        print("Loaded ", language)
    check_objects = []
    for ix, check in enumerate(data):
        if validate:
            if check["check"] not in schemas:
                raise ValueError(
                    f"Language definition file for {language} invalid; "
                    f"unknown check type {check['check']} in check {ix} "
                    f"- choose from { ', '.join(schemas.keys()) }"
                )
            try:
                check.revalidate(schemas[check["check"]])
            except YAMLValidationError as e:
                raise ValueError(
                    f"Language definition file for {language} invalid; "
                    f"parser error in check {ix}: {e}"
                ) from e
            # This turns a { "check": "foobar" } into a FoobarCheck({"check": "foobar"})
            check = check.data
        check_objects.append(checks_map[check["check"]](check))
    definition_cache[language] = check_objects
    return check_objects


class Languages:
    loaded = {}

    def __contains__(self, item):
        return item in gflangs

    def keys(self):
        return gflangs.keys()

    def disambiguate(self, lang):
        maybe_keys = [k for k in gflangs if k.lower().startswith(lang.lower() + "_")]
        if maybe_keys:
            return maybe_keys
        maybe_keys = [
            k for k, v in gflangs.items() if v.name.lower().startswith(lang.lower())
        ]
        return maybe_keys

    def __getitem__(self, item):
        if item in self.loaded:
            return self.loaded[item]
        if item not in gflangs:
            return None
        orig = MessageToDict(gflangs[item])
        orig["full_name"] = (
            orig["name"] + " in the " + gfscripts[orig["script"]].name + " script"
        )
        orig["shaperglot_checks"] = [
            OrthographiesCheck(orig),
            NoOrphanedMarksInOrthographiesCheck(orig)
        ]
        checks = load_shaperglot_definition(item, validate=False)
        orig["shaperglot_checks"].extend(checks)
        self.loaded[item] = orig
        return orig
