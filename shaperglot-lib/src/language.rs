use google_fonts_languages::{LanguageProto, LANGUAGES};
use unicode_normalization::UnicodeNormalization;

use crate::{
    checks::Check,
    providers::{BaseCheckProvider, Provider},
};

/// A language definition, including checks and exemplar characters
#[derive(Clone, Debug)]
pub struct Language {
    /// The underlying language definition from the google-fonts-languages database
    pub proto: Box<LanguageProto>,
    /// The checks that apply to this language
    pub checks: Vec<Check>,
    /// Mandatory base characters for the language
    pub bases: Vec<String>,
    /// Optional auxiliary characters for the language
    pub auxiliaries: Vec<String>,
    /// Mandatory mark characters for the language
    pub marks: Vec<String>,
}

impl Language {
    /// The language's ISO 639-3 code
    pub fn id(&self) -> &str {
        self.proto.id()
    }

    /// The language's name
    pub fn name(&self) -> &str {
        self.proto.name()
    }

    /// The language's ISO15924 script code
    pub fn script(&self) -> &str {
        self.proto.script()
    }
}

/// The language database
pub struct Languages(Vec<Language>);

impl Languages {
    /// Instantiate a new language database
    ///
    /// This loads the database and fills it with checks.
    pub fn new() -> Self {
        let mut languages = Vec::new();
        for (_id, proto) in LANGUAGES.iter() {
            let bases = proto
                .exemplar_chars
                .as_ref()
                .map(|e| parse_chars(e.base()))
                .unwrap_or_else(Vec::new);
            let auxiliaries = proto
                .exemplar_chars
                .as_ref()
                .map(|e| parse_chars(e.auxiliary()))
                .unwrap_or_else(Vec::new);
            let marks = proto
                .exemplar_chars
                .as_ref()
                .map(|e| e.marks().split_whitespace().collect())
                .unwrap_or_else(Vec::new)
                .iter()
                .map(|x| {
                    if x.starts_with('\u{25cc}') {
                        x.to_string()
                    } else {
                        format!("\u{25cc}{}", x)
                    }
                })
                .collect();

            let mut lang = Language {
                proto: Box::new(*proto.clone()),
                checks: vec![],
                bases,
                auxiliaries,
                marks,
            };
            lang.checks = BaseCheckProvider.checks_for(&lang);
            languages.push(lang);
        }
        Languages(languages)
    }

    /// Get an iterator over the languages
    pub fn iter(&self) -> std::slice::Iter<Language> {
        self.0.iter()
    }
    /// Get a single language by ID or name
    pub fn get_language(&self, id: &str) -> Option<&Language> {
        self.0
            .iter()
            .find(|l| l.id() == id)
            .or_else(|| self.0.iter().find(|l| l.name() == id))
    }
}

impl IntoIterator for Languages {
    type Item = Language;
    type IntoIter = std::vec::IntoIter<Language>;

    fn into_iter(self) -> Self::IntoIter {
        self.0.into_iter()
    }
}
impl Default for Languages {
    fn default() -> Self {
        Self::new()
    }
}

/// Split up an exemplars string into individual characters
fn parse_chars(chars: &str) -> Vec<String> {
    chars
        .split_whitespace()
        .flat_map(|x| {
            let mut s = x.to_string();
            if s.len() > 1 {
                s = s.trim_start_matches("{").trim_end_matches("}").to_string()
            }
            let normalized = s.nfc().collect::<String>();
            if normalized != s {
                vec![s, normalized]
            } else {
                vec![s]
            }
        })
        .filter(|x| !x.is_empty())
        .collect()
}
