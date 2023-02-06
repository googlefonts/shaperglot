from ufo2ft.util import closeGlyphsOverGSUB
from vharfbuzz import Vharfbuzz
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


class Checker:  # pylint: disable=too-few-public-methods
    def __init__(self, fontfile):
        self.vharfbuzz = Vharfbuzz(fontfile)
        self.ttfont = self.vharfbuzz.ttfont
        self.glyphorder = self.ttfont.getGlyphOrder()
        self.cmap = self.ttfont["cmap"].getBestCmap()
        self.reversed_cmap = self.ttfont["cmap"].buildReversed()
        self.full_reversed_cmap = None
        self.results = None
        self.lang = None
        self.cache = {"can_shape": {}}

    def _build_full_reversed_cmap(self):
        gsub = self.ttfont.get("GSUB")
        self.full_reversed_cmap = {k: list(v)[0] for k,v in self.reversed_cmap.items()}
        if not gsub:
            return
        if len(self.full_reversed_cmap) > 5_000:
            # Some kind of CJK monstrosity, give up
            return
        for codepoint, glyph in self.cmap.items():
            glyphs = set([glyph])
            if gsub:
                closeGlyphsOverGSUB(gsub, glyphs)
            for new_glyph in glyphs:
                self.full_reversed_cmap[new_glyph] = codepoint

    def codepoint_for(self, glyphname):
        if glyphname in self.reversed_cmap:
            return list(self.reversed_cmap[glyphname])[0]
        if not self.full_reversed_cmap:
            self._build_full_reversed_cmap()
        return self.full_reversed_cmap.get(glyphname, 0)

    def check(self, lang):
        self.results = Reporter()
        self.lang = lang
        for check_object in self.lang.get("shaperglot_checks", []):
            skip_reason = check_object.should_skip(self)
            if skip_reason:
                self.results.skip(check_name=check_object.name, message=skip_reason)
                continue
            check_object.execute(self)
        return self.results
