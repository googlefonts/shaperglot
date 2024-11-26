use google_fonts_languages::{LanguageProto, LANGUAGES, SCRIPTS};
use unicode_normalization::UnicodeNormalization;

use crate::{
    checks::Check,
    providers::{BaseCheckProvider, Provider},
};
pub struct Language {
    pub proto: Box<LanguageProto>,
    pub checks: Vec<Check>,
    pub bases: Vec<String>,
    pub auxiliaries: Vec<String>,
    pub marks: Vec<String>,
}

impl Language {
    pub fn id(&self) -> &str {
        self.proto.id()
    }

    pub fn name(&self) -> &str {
        self.proto.name()
    }

    pub fn full_name(&self) -> String {
        format!(
            "{} in the {} script",
            self.proto.name(),
            SCRIPTS
                .get(self.proto.script())
                .map(|s| s.name())
                .unwrap_or("Unknown")
        )
    }

    pub fn script(&self) -> &str {
        self.proto.script()
    }
    pub fn language(&self) -> &str {
        self.proto.language()
    }
}

pub struct Languages(Vec<Language>);

impl Languages {
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

    pub fn iter(&self) -> std::slice::Iter<Language> {
        self.0.iter()
    }

    pub fn get_language(&self, id: &str) -> Option<&Language> {
        self.0
            .iter()
            .find(|l| l.id() == id)
            .or_else(|| self.0.iter().find(|l| l.name() == id))
    }
}

impl Default for Languages {
    fn default() -> Self {
        Self::new()
    }
}

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
