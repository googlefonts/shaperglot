from strictyaml import Str, Map, Optional, MapPattern, Bool, Seq

shaping_input_schema = Map(
    {
        "text": Str(),
        Optional("language"): Str(),
        Optional("features"): MapPattern(Str(), Bool()),
    }
)

conditions_schema = Map({Optional("features"): Seq(Str())})


def check_schema(schema):
    base_schema = {
        "check": Str(),
        Optional("rationale"): Str(),
        Optional("conditions"): conditions_schema,
    }
    schema.update(base_schema)
    return Map(schema)


def and_join(lst):
    lst = list(lst)
    if len(lst) == 0:
        return "(nothing here)"
    if len(lst) > 1:
        return ', '.join(lst[:-1]) + ' and ' + lst[-1]
    return lst[0]


class ShapeInput:
    def __init__(self, check_yaml):
        self.text = str(check_yaml["text"])
        self.language = str(check_yaml.get("language", ""))
        if "features" in check_yaml:
            self.features = check_yaml["features"].data
        else:
            self.features = {}
        self.check_yaml = check_yaml

    def describe(self):
        result = f"shaping the text '{self.text}' "
        if self.language or self.features:
            result += "while "
        if self.language:
            result += f"setting the language to '{self.language}' "
            if self.features:
                result += "and "
        if self.features:
            result += "turning " + and_join(
                [
                    f"the '{feat}' feature " + (state and "on" or "off")
                    for feat, state in self.features.items()
                ]
            )
        return result.strip()

    def shape(self, checker):
        parameters = {}
        if self.language:
            parameters["language"] = self.language
        if self.features:
            parameters["features"] = self.features
        return checker.vharfbuzz.shape(self.text, parameters)


# pylint: disable=R0903
class ShaperglotCheck:
    def __init__(self, check_yaml):
        self.definition = check_yaml
        if "inputs" in check_yaml:
            self.inputs = [ShapeInput(x) for x in check_yaml["inputs"]]
        if "input" in check_yaml:
            self.input = ShapeInput(check_yaml["input"])

    def should_skip(self, checker):
        conditions = self.definition.get("conditions")
        if conditions is None:
            return False
        if "features" in conditions:
            font_features = set()
            for table in ["GSUB", "GPOS"]:
                if (
                    checker.ttfont.get(table)
                    and checker.ttfont[table].table.FeatureList
                ):
                    for feature_record in checker.ttfont[
                        table
                    ].table.FeatureList.FeatureRecord:
                        font_features.add(feature_record.FeatureTag)
            required = set(str(f) for f in conditions["features"])
            if required - font_features:
                return f"Missing features: {', '.join(required-font_features)}"
        return False
