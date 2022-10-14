from vharfbuzz import Vharfbuzz
from fontFeatures.ttLib import unparse, unparseLanguageSystems
from hyperglot.parse import parse_chars, parse_marks
import fontFeatures
from shaperglot.reporter import Reporter


def flatten(lst):
    return [item for sublist in lst for item in sublist]


def _get_cluster(buffers, index):
    input_id = index[0]
    cluster_id = index[1]
    glyphs = buffers[input_id].glyph_infos
    cluster = [x.codepoint for x in glyphs if x.cluster == cluster_id]
    if len(index) == 3:
        return [cluster[index[2]]]
    return cluster


class Checker:
    def __init__(self, fontfile):
        self.vharfbuzz = Vharfbuzz(fontfile)
        self.ttfont = self.vharfbuzz.ttfont
        # pylint: disable=C0103
        self.ff = unparse(self.ttfont, do_gdef=True)
        self.cmap = self.ttfont["cmap"].getBestCmap()
        self.results = None
        self.lang = None

    def check(self, lang):
        self.results = Reporter()
        self.lang = lang
        # Run all methods that start with check_
        checks = [x for x in dir(self) if x.startswith("check_")]
        for check in checks:
            getattr(self, check)()
        return self.results

    def check_orthographies(self):
        for ortho in self.lang["orthographies"]:
            marks = set(parse_marks(ortho.get("marks", "")))
            bases = set(parse_chars(ortho.get("base", ""))) - marks
            missing = [x for x in bases if ord(x) not in self.cmap]
            if missing:
                missing = ", ".join(missing)
                self.results.fail(f"Some base glyphs were missing: {missing}")
            else:
                self.results.okay("All base glyphs were present in the font")
            if not marks:
                continue
            missing = [x for x in marks if ord(x) not in self.cmap]
            if missing:
                missing = ", ".join(missing)
                self.results.fail(f"Some mark glyphs were missing: {missing}")
            else:
                self.results.okay("All mark glyphs were present in the font")

    def check_shaping(self):
        for shaping_check in self.lang.get("shaping", []):
            self._check_shaping(shaping_check)

    def _check_shaping(self, check):
        buffers = []
        if "if" in check:
            condition = check["if"]
            if "feature" in condition and condition["feature"] not in self.ff.features:
                self.results.skip(
                    f'{check["rationale"]}: ({condition["feature"]} not present)'
                )
                return

        for shaping_input in check["inputs"]:
            if isinstance(shaping_input, str):
                buffers.append(self.vharfbuzz.shape(shaping_input))
            else:
                text = shaping_input.get("text")
                buffers.append(self.vharfbuzz.shape(text, shaping_input))

        #Created a test to validate if a mark is being attached to a specific base.
        #Compares the GPOS history of a standalone mark against the mark following a specific base.
        if "mark2base" in check:
            params = check["mark2base"]
            params = [[0, x, 0] if isinstance(x, int) else x for x in params]
            clusters = [_get_cluster(buffers, param) for param in params]
            cluster_pos = []
            mark_pos1 = ""
            mark_pos2 = ""
            if len(clusters) != 2:
                self.results.fail("Cluster check did not identify two clusters!")
                return
            else:
                cluster_pos = self.vharfbuzz.serialize_buf(buffers[1]).split('|')
            if len(cluster_pos) != 2:   
                self.results.okay(check["rationale"] + " **Is Precomposed**")
                return
            else:
                mark_pos1 = self.vharfbuzz.serialize_buf(buffers[0])
                mark_pos2 = cluster_pos[1]
            if mark_pos2 == mark_pos1:
                self.results.fail(check["rationale"])
            else:
                self.results.okay(check["rationale"])
            #print(mark_pos1, cluster_pos, mark_pos2)


        if "differs" in check:
            params = check["differs"]
            params = [[0, x, 0] if isinstance(x, int) else x for x in params]
            clusters = [_get_cluster(buffers, param) for param in params]
            if len(clusters) != 2:
                self.results.fail("Cluster check did not identify two clusters!")
                return
            if clusters[0] == clusters[1]:
                self.results.fail(check["rationale"])
            else:
                self.results.okay(check["rationale"])

    def check_features(self):
        features = self.lang.get("features")
        if not features:
            return
        for feat in features.keys():
            if feat not in self.ff.features:
                self.results.fail(f"Required feature '{feat}' not present")
            else:
                self.results.okay(f"Required feature '{feat}' was present")
                for test in features[feat]:
                    if feat == "mark" and test["involves"] == "hyperglot":
                        self._check_mark_attachment()
                    elif "involves" in test:
                        self._feature_involves(feat, test["involves"])

    def _check_mark_attachment(self):
        rules = flatten([x.routine.rules for x in self.ff.features["mark"]])
        used_marks = flatten(
            [
                rule.marks.keys()
                for rule in rules
                if isinstance(rule, fontFeatures.Attachment)
            ]
        )

        for ortho in self.lang["orthographies"]:
            marks = parse_marks(ortho.get("marks", ""))
            for mark in marks:
                glyph = self.cmap.get(ord(mark))
                if not glyph:
                    continue  # Should be picked up by the orthographies tester
                if glyph in used_marks:
                    self.results.okay(
                        f"Mark glyph ◌{mark}  ({glyph}) took part in a mark positioning rule"
                    )
                else:
                    self.results.fail(
                        f"Mark glyph ◌{mark}  ({glyph}) did not "
                        "take part in any mark positioning rule"
                    )

    def _feature_involves(self, feat, involves):
        rules = flatten([x.routine.rules for x in self.ff.features[feat]])
        involved = flatten([x.involved_glyphs for x in rules])
        glyph = self.cmap.get(involves)
        if not glyph:
            return
        if glyph in involved:
            self.results.okay(
                f"Glyph {chr(involves)} ({glyph}) took part in a {feat} rule"
            )
        else:
            self.results.fail(
                f"Glyph {chr(involves)} ({glyph}) did not take part in any {feat} rule"
            )

    def check_languagesystems(self):
        if "languagesystems" not in self.lang:
            return
        gsub_gpos = [
            self.ttfont[tableTag]
            for tableTag in ("GSUB", "GPOS")
            if tableTag in self.ttfont
        ]
        language_systems = unparseLanguageSystems(gsub_gpos)
        script, lang = self.lang["languagesystems"]
        if script in language_systems and lang in language_systems[script]:
            self.results.okay(f"Language system '{script}/{lang}' found in font")
        else:
            self.results.fail(f"Language system '{script}/{lang}' not found in font")
