use std::collections::{BTreeMap, HashSet};

use crate::{language::Language, reporter::Reporter, GlyphId, ResultCode};
use rustybuzz::Face;

/// The context for running font language support checks
pub struct Checker<'a> {
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
}

impl<'a> Checker<'a> {
    /// Create an instance given the binary data of a font.
    #[cfg(feature = "skrifa")]
    pub fn new(data: &'a [u8]) -> Result<Self, skrifa::raw::ReadError> {
        use skrifa::{FontRef, MetadataProvider};

        let font = FontRef::new(data)?;
        Ok(Self::from_parts(
            Face::from_slice(data, 0).expect("could not parse the font"),
            crate::font::glyph_names(&font)?,
            crate::font::feature_tags(&font)?,
            font.charmap()
                .mappings()
                .map(|(character, glyph)| (character, glyph.to_u32()))
                .collect(),
        ))
    }

    /// Create an instance given the parts of a font.
    pub fn from_parts(
        face: Face<'a>,
        glyph_names: Vec<String>,
        features: HashSet<String>,
        cmap: BTreeMap<u32, GlyphId>,
    ) -> Self {
        let reversed_cmap = cmap.iter().map(|(k, v)| (*v, *k)).collect();
        Self {
            face,
            glyph_names,
            features,
            cmap,
            reversed_cmap,
        }
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
