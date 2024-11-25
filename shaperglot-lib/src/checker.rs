use std::{
    collections::BTreeMap,
    sync::{Arc, Mutex},
};

use crate::{font::glyph_names, language::Language, reporter::Reporter};
use rustybuzz::Face;
use skrifa::{raw::ReadError, FontRef, GlyphId, MetadataProvider};

pub struct Checker<'a> {
    pub font: FontRef<'a>,
    pub face: Face<'a>,
    pub glyph_names: Vec<String>,
    pub cmap: BTreeMap<u32, GlyphId>,
    reversed_cmap: BTreeMap<GlyphId, u32>,
    full_reversed_cmap: Arc<Mutex<Option<BTreeMap<GlyphId, u32>>>>,
}

impl<'a> Checker<'a> {
    pub fn new(font_binary: &'a [u8]) -> Result<Self, ReadError> {
        let face = Face::from_slice(font_binary, 0).expect("Couldn't load font");
        let font = FontRef::new(font_binary)?;
        let glyph_names = glyph_names(&font)?;
        let cmap: BTreeMap<u32, GlyphId> = font.charmap().mappings().collect();
        let reversed_cmap = cmap.iter().map(|(k, v)| (*v, *k)).collect();
        Ok(Self {
            font,
            glyph_names,
            cmap,
            face,
            reversed_cmap,
            full_reversed_cmap: Arc::new(Mutex::new(None)),
        })
    }

    pub fn codepoint_for(&self, gid: GlyphId) -> Option<u32> {
        self.reversed_cmap.get(&gid).copied().or_else(||
            // if !self.full_reversed_cmap.is_some() {
            //     self.full_reversed_cmap = Some(self.font.charmap().mappings().collect());
            // }
            None)
    }

    pub fn check(&self, language: &Language, fail_fast: bool) -> Reporter {
        let mut results = Reporter::default();
        for check_object in language.checks.iter() {
            // let toml = toml::to_string(&check_object).unwrap();
            // println!("Running check:\n{}", toml);
            let checkresult = check_object.execute(self);
            results.add(checkresult);
        }
        results
    }
}
