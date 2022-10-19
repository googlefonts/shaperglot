from vharfbuzz import Vharfbuzz
from fontFeatures.ttLib import unparse, unparseLanguageSystems
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
        self.glyphorder = self.ttfont.getGlyphOrder()
        # pylint: disable=C0103
        self.ff = unparse(self.ttfont, do_gdef=True)
        self.cmap = self.ttfont["cmap"].getBestCmap()
        self.results = None
        self.lang = None

    def check(self, lang):
        self.results = Reporter()
        self.lang = lang
        for check_object in self.lang.get("shaperglot_checks", []):
            check_object.execute(self)
        return self.results

