from strictyaml import FixedSeq, Str, Map, Int, Optional, MapPattern, Bool

shaping_input_schema = Map(
    {
        "text": Str(),
        Optional("language"): Str(),
        Optional("features"): MapPattern(Str(), Bool()),
    }
)

def and_join(lst):
    lst = list(lst)
    if len(lst) == 0:
        return "(nothing here)"
    if len(lst) > 1:
        return ', '.join(lst[:-1]) + ' and ' + lst[-1]
    elif len(lst) == 1:
        return lst[0]

class ShapeInput:
    def __init__(self, check_yaml):
        self.text = str(check_yaml["text"])
        self.language = str(check_yaml.get("language", ""))
        if "features" in check_yaml:
            self.features = check_yaml["features"].data
        else:
            self.features = {}

    def describe(self):
        r = f"shaping the text '{self.text}' "
        if self.language or self.features:
            r += "while "
        if self.language:
            r += f"setting the language to '{self.language}' "
            if self.features:
                r += "and "
        if self.features:
            r += "turning " + and_join([
                f"the '{feat}' feature " + (state and "on" or "off")
                for feat, state in self.features.items()
            ])
        return r.strip()

    def shape(self, checker):
        parameters = {}
        if self.language:
            parameters["language"] = self.language
        if self.features:
            parameters["features"] = self.features
        return checker.vharfbuzz.shape(self.text, parameters)


class ShaperglotCheck:
    def __init__(self, check_yaml):
        self.definition = check_yaml
        if "inputs" in check_yaml:
            self.inputs = [ShapeInput(x) for x in check_yaml["inputs"]]
        if "input" in check_yaml:
            self.input = ShapeInput(check_yaml["input"])
