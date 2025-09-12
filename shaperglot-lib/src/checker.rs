use std::collections::{BTreeMap, HashSet};

use crate::{language::Language, reporter::Reporter, GlyphId, ResultCode};
use harfrust::{Shaper, ShaperData};

/// The context for running font language support checks
pub struct Checker<'a> {
    /// The font reference
    pub fontref: harfrust::FontRef<'a>,
    /// The shaper data
    pub shaper_data: ShaperData,
    /// The glyph names in the font
    pub glyph_names: Vec<String>,
    /// The OpenType features present in the font
    pub features: HashSet<String>,
    /// The character map of the font
    pub cmap: BTreeMap<u32, GlyphId>,
    /// The reversed character map of the font
    reversed_cmap: BTreeMap<GlyphId, u32>,
}

impl<'a> Checker<'a> {
    /// Create an instance given the binary data of a font.
    #[cfg(feature = "skrifa")]
    pub fn new(data: &'a [u8]) -> Result<Self, Box<dyn std::error::Error>> {
        use skrifa::MetadataProvider;
        let font_for_charmap = skrifa::FontRef::from_index(data, 0)?; // XXX allow selection of face indices
        let font_for_shaping = harfrust::FontRef::from_index(data, 0)?;
        // XXX allow variations
        // let instance = ShaperInstance::from_variations(&font, &args.variations);

        Ok(Self::from_parts(
            font_for_shaping,
            crate::font::glyph_names(&font_for_charmap)?,
            crate::font::feature_tags(&font_for_charmap)?,
            font_for_charmap
                .charmap()
                .mappings()
                .map(|(character, glyph)| (character, glyph.to_u32()))
                .collect(),
        ))
    }

    /// Create an instance given the parts of a font.
    pub fn from_parts(
        fontref: harfrust::FontRef<'a>,
        glyph_names: Vec<String>,
        features: HashSet<String>,
        cmap: BTreeMap<u32, GlyphId>,
    ) -> Self {
        let reversed_cmap = cmap.iter().map(|(k, v)| (*v, *k)).collect();
        let shaper_data = harfrust::ShaperData::new(&fontref);

        Self {
            fontref,
            glyph_names,
            features,
            cmap,
            reversed_cmap,
            shaper_data,
        }
    }

    /// Get the shaper for the font.
    pub fn shaper(&'a self) -> Shaper<'a> {
        self.shaper_data.shaper(&self.fontref).build()
    }

    /// Get the codepoint for a given glyph ID.
    pub fn codepoint_for(&self, gid: GlyphId) -> Option<u32> {
        self.reversed_cmap.get(&gid).copied()
    }

    /// Check if the font supports a given language.
    pub fn check(&self, language: &Language) -> Reporter {
        let mut results = Reporter::default();
        for check_object in language.checks.iter() {
            let checkresult = check_object.execute(self);
            let status = checkresult.status;
            results.add(checkresult);
            if status == ResultCode::StopNow {
                break;
            }
        }
        results
    }
}
