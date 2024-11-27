use std::{
    fmt::{Display, Formatter},
    str::FromStr,
};

use rustybuzz::GlyphBuffer;
use serde::{Deserialize, Serialize};

use crate::Checker;

#[derive(Serialize, Deserialize, Debug, Clone)]
/// A struct representing the input to the shaping process.
pub struct ShapingInput {
    /// The text to shape.
    pub text: String,
    /// The OpenType features to apply.
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub features: Vec<String>,
    /// The language to shape the text in.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub language: Option<String>,
}

impl ShapingInput {
    /// Create a new `ShapingInput` with the given text, no features and language supplied
    pub fn new_simple(text: String) -> Self {
        Self {
            text,
            features: Vec::new(),
            language: None,
        }
    }

    /// Create a new `ShapingInput` with the given text and a single OpenType feature
    pub fn new_with_feature(text: String, feature: impl AsRef<str>) -> Self {
        Self {
            text,
            features: vec![feature.as_ref().to_string()],
            language: None,
        }
    }

    /// Shape the text using the given checker context
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

    /// Describe the shaping input
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

    /// Get the character at the given position in the text
    pub fn char_at(&self, pos: usize) -> Option<char> {
        self.text.chars().nth(pos)
    }
}

impl Display for ShapingInput {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.describe())
    }
}
