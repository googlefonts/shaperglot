use std::collections::{BTreeMap, HashSet};

use crate::{
    font::{feature_tags, glyph_names},
    language::Language,
    reporter::Reporter,
    ResultCode,
};
use rustybuzz::Face;
use skrifa::{raw::ReadError, FontRef, GlyphId, MetadataProvider};

/// The context for running font language support checks
pub struct Checker<'a> {
    /// The font to check, as a [read_fonts::FontRef]
    pub font: FontRef<'a>,
    /// The face to use for shaping
    pub face: Face<'a>,
    /// The glyph names in the font
    pub glyph_names: Vec<String>,
    /// The OpenType features present in the font
    pub features: HashSet<String>,
    /// The character map of the font
    pub cmap: BTreeMap<u32, GlyphId>,
    /// The reversed character map of the font
    reversed_cmap: BTreeMap<GlyphId, u32>,
    // full_reversed_cmap: Arc<Mutex<Option<BTreeMap<GlyphId, u32>>>>,
}

impl<'a> Checker<'a> {
    /// Create a new font checker
    pub fn new(font_binary: &'a [u8]) -> Result<Self, ReadError> {
        let face = Face::from_slice(font_binary, 0).expect("Couldn't load font");
        let font = FontRef::new(font_binary)?;
        let glyph_names = glyph_names(&font)?;
        let cmap: BTreeMap<u32, GlyphId> = font.charmap().mappings().collect();
        let reversed_cmap = cmap.iter().map(|(k, v)| (*v, *k)).collect();
        let features = feature_tags(&font)?;
        Ok(Self {
            font,
            glyph_names,
            cmap,
            face,
            features,
            reversed_cmap,
            // full_reversed_cmap: Arc::new(Mutex::new(None)),
        })
    }

    /// Get the codepoint for a given glyph ID
    pub fn codepoint_for(&self, gid: GlyphId) -> Option<u32> {
        // self.reversed_cmap.get(&gid).copied().or_else(||
        // if !self.full_reversed_cmap.is_some() {
        //     self.full_reversed_cmap = Some(self.font.charmap().mappings().collect());
        // }
        // None)
        self.reversed_cmap.get(&gid).copied()
    }

    /// Check a font for language support
    pub fn check(&self, language: &Language) -> Reporter {
        let mut results = Reporter::default();
        for check_object in language.checks.iter() {
            // let toml = toml::to_string(&check_object).unwrap();
            // println!("Running check:\n{}", toml);
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
