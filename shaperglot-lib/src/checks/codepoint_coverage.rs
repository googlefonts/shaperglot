use super::CheckImplementation;
use crate::{
    checker::Checker,
    reporter::{Fix, Problem},
};
use itertools::Itertools;
use rustybuzz::Face;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::collections::HashSet;

#[derive(Serialize, Deserialize, Debug, Clone)]
/// A check implementation which ensures codepoints are present in a font
pub struct CodepointCoverage {
    /// The codepoints to check for
    strings: HashSet<String>,
    /// The unique code to return on failure (e.g. "marks-missing")
    code: String,
    /// Whether to mark the problem as terminal if no codepoints are found
    terminal_if_empty: bool,
}

fn can_shape(text: &str, face: &Face) -> bool {
    let mut buffer = rustybuzz::UnicodeBuffer::new();
    buffer.push_str(text);
    let glyph_buffer = rustybuzz::shape(face, &[], buffer);
    glyph_buffer.glyph_infos().iter().all(|x| x.glyph_id != 0)
}

impl CheckImplementation for CodepointCoverage {
    fn name(&self) -> String {
        "CodepointCoverage".to_string()
    }

    fn should_skip(&self, _checker: &Checker) -> Option<String> {
        None
    }

    fn execute(&self, checker: &Checker) -> (Vec<Problem>, usize) {
        let checks_run = self.strings.len();
        let missing_things: Vec<_> = self
            .strings
            .iter()
            .filter(|x| !can_shape(x, &checker.face))
            .cloned()
            .collect();
        let mut problems = vec![];
        if !missing_things.is_empty() {
            let mut fail = Problem::new(
                &self.name(),
                &format!("{}s-missing", self.code),
                format!(
                    "The following {} characters are missing from the font: {}",
                    self.code,
                    missing_things.join(", ")
                ),
            );
            if missing_things.len() == self.strings.len() && self.terminal_if_empty {
                fail.terminal = true;
            }
            fail.context = json!({"glyphs": missing_things});
            fail.fixes.extend(missing_things.iter().map(|x| Fix {
                fix_type: "add_codepoint".to_string(),
                fix_thing: x.to_string(),
            }));
            problems.push(fail);
        }
        (problems, checks_run)
    }

    fn describe(&self) -> String {
        format!(
            "Checks that all the following codepoints are covered in the font: {}",
            self.strings.iter().join(", ")
        )
    }
}

impl CodepointCoverage {
    /// Create a new `CodepointCoverage` check implementation
    pub fn new(test_strings: Vec<String>, code: String, terminal_if_empty: bool) -> Self {
        Self {
            strings: test_strings.into_iter().collect(),
            code,
            terminal_if_empty,
        }
    }
}
