use std::{
    fmt::{Display, Formatter},
    str::FromStr,
};

use rustybuzz::GlyphBuffer;
use serde::{Deserialize, Serialize};

use crate::Checker;

#[derive(Serialize, Deserialize, Debug)]
pub struct ShapingInput {
    pub text: String,
    pub features: Vec<String>,
    pub language: Option<String>,
}

impl ShapingInput {
    pub fn new_simple(text: String) -> Self {
        Self {
            text,
            features: Vec::new(),
            language: None,
        }
    }

    pub fn new_with_feature(text: String, feature: impl AsRef<str>) -> Self {
        Self {
            text,
            features: vec![feature.as_ref().to_string()],
            language: None,
        }
    }
    pub fn shape(&self, checker: &Checker) -> Result<GlyphBuffer, String> {
        let mut buffer = rustybuzz::UnicodeBuffer::new();
        buffer.push_str(&self.text);
        if let Some(language) = &self.language {
            buffer.set_language(rustybuzz::Language::from_str(language)?);
        }
        let mut features = Vec::new();
        for f in &self.features {
            features.push(rustybuzz::Feature::from_str(f)?);
        }
        let glyph_buffer = rustybuzz::shape(&checker.face, &features, buffer);
        Ok(glyph_buffer)
    }

    pub fn describe(&self) -> String {
        let mut description = format!("shaping the text '{}'", self.text);
        if let Some(language) = &self.language {
            description.push_str(&format!(" in language '{}'", language));
        }
        if !self.features.is_empty() {
            description.push_str(" with features: ");
            description.push_str(&self.features.join(", "));
        }
        description
    }

    pub fn char_at(&self, pos: usize) -> Option<char> {
        self.text.chars().nth(pos)
    }
}

impl Display for ShapingInput {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.describe())
    }
}
