#[cfg(feature = "colored")]
use colored::Colorize;
use serde::{Deserialize, Serialize};
use std::{
    collections::{HashMap, HashSet},
    fmt::Display,
    hash::Hash,
};

use serde_json::Value;

use crate::language::Language;

/// A code representing the overall status of an individual check
#[derive(Debug, Default, Hash, Eq, PartialEq, Clone, Copy, Serialize, Deserialize)]
pub enum ResultCode {
    /// The check passed successfully
    #[default]
    Pass,
    /// There was a problem which does not prevent the font from being used
    Warn,
    /// There was a problem which does prevent the font from being used
    Fail,
    /// The check was skipped because some condition was not met
    Skip,
    /// The font doesn't support something fundamental, no need to test further
    StopNow,
}

impl Display for ResultCode {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        #[cfg(feature = "colored")]
        let to_string = match self {
            ResultCode::Pass => "PASS".green(),
            ResultCode::Warn => "WARN".yellow(),
            ResultCode::Fail => "FAIL".red(),
            ResultCode::Skip => "SKIP".blue(),
            ResultCode::StopNow => "STOP".red(),
        };
        #[cfg(not(feature = "colored"))]
        let to_string = match self {
            ResultCode::Pass => "PASS",
            ResultCode::Warn => "WARN",
            ResultCode::Fail => "FAIL",
            ResultCode::Skip => "SKIP",
            ResultCode::StopNow => "STOP",
        };
        write!(f, "{}", to_string)
    }
}

#[derive(Debug, Default, Serialize, Deserialize, Clone)]
/// Suggestions for how to fix the problem
pub struct Fix {
    /// The broad category of fix
    pub fix_type: String,
    /// What the designer needs to do
    pub fix_thing: String,
}

#[derive(Debug, Default, Serialize, Deserialize, Clone)]
/// A problem found during a sub-test of a check
pub struct Problem {
    /// The name of the check that found the problem
    pub check_name: String,
    /// The message describing the problem
    pub message: String,
    /// A unique code for the problem
    pub code: String,
    /// Whether the problem is terminal (i.e. the font is unusable)
    pub terminal: bool,
    /// Additional context for the problem
    #[serde(skip_serializing_if = "Value::is_null")]
    pub context: Value,
    /// Suggestions for how to fix the problem
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub fixes: Vec<Fix>,
}

impl Problem {
    /// Create a new problem
    pub fn new(check_name: &str, code: &str, message: String) -> Self {
        Self {
            check_name: check_name.to_string(),
            code: code.to_string(),
            message: message.to_string(),
            ..Default::default()
        }
    }
}

impl Hash for Problem {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.check_name.hash(state);
        self.message.hash(state);
    }
}

impl PartialEq for Problem {
    fn eq(&self, other: &Self) -> bool {
        self.check_name == other.check_name && self.message == other.message
    }
}

impl Display for Problem {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.message)
    }
}
impl Eq for Problem {}

#[derive(Debug, Default, Serialize, Deserialize, Clone)]
/// The result of an individual check
pub struct CheckResult {
    /// The name of the check
    pub check_name: String,
    /// A description of what the check does and why
    pub check_description: String,
    /// The score for the check from 0.0 to 1.0
    pub score: f32,
    /// The weight of the check in the overall score for language support
    pub weight: u8,
    /// The problems found during the check
    pub problems: Vec<Problem>,
    /// The total number of sub-tests run
    pub total_checks: usize,
    /// The overall status of the check
    pub status: ResultCode,
}

impl Display for CheckResult {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}:", self.check_name)?;
        for message in &self.problems {
            write!(f, "\n  {}", message)?;
        }
        Ok(())
    }
}
impl CheckResult {
    /// Describe the result in a sentence
    pub fn summary_result(&self) -> String {
        if self.problems.is_empty() {
            return format!("{}: no problems found", self.check_name);
        }
        format!("{} check failed", self.check_name)
    }
}

#[derive(Debug, Default, Serialize)]
/// A collection of check results
pub struct Reporter(Vec<CheckResult>);

impl Reporter {
    /// Create a new, empty reporter
    pub fn new() -> Self {
        Self(vec![])
    }

    /// Add a check result to the reporter
    pub fn add(&mut self, checkresult: CheckResult) {
        self.0.push(checkresult);
    }

    /// Iterate over check results
    pub fn iter(&self) -> impl Iterator<Item = &CheckResult> {
        self.0.iter()
    }

    /// Iterate over individual problems found while checking
    pub fn iter_problems(&self) -> impl Iterator<Item = &Problem> {
        self.0.iter().flat_map(|r| r.problems.iter())
    }

    /// A unique set of fixes required, organised by category
    ///
    /// Some checks may have multiple problems with the same fix,
    /// so this method gathers the problems by category and fix required.
    pub fn unique_fixes(&self) -> HashMap<String, HashSet<String>> {
        // Arrange by fix type
        let mut fixes: HashMap<String, HashSet<String>> = HashMap::new();
        for result in self.0.iter() {
            for message in &result.problems {
                for fix in &message.fixes {
                    let entry = fixes.entry(fix.fix_type.clone()).or_default();
                    entry.insert(fix.fix_thing.clone());
                }
            }
        }
        fixes
    }

    /// Language support as a numerical score
    ///
    /// This is a weighted sum of all scores of the checks run, out of 100%
    pub fn score(&self) -> f32 {
        let total_weight: u8 = self.0.iter().map(|r| r.weight).sum();
        let weighted_scores = self.0.iter().map(|r| r.score * f32::from(r.weight));
        let total_score: f32 = weighted_scores.sum();
        total_score / f32::from(total_weight) * 100.0
    }

    /// The overall level of support for a language
    pub fn support_level(&self) -> SupportLevel {
        if self.0.iter().any(|r| r.status == ResultCode::StopNow) {
            return SupportLevel::None;
        }
        if self.is_unknown() {
            return SupportLevel::Indeterminate;
        }
        if self.is_success() {
            return SupportLevel::Complete;
        }
        if self.0.iter().any(|r| r.status == ResultCode::Fail) {
            return SupportLevel::Unsupported;
        }
        if self.0.iter().any(|r| r.status == ResultCode::Warn) {
            return SupportLevel::Incomplete;
        }
        SupportLevel::Supported
    }

    /// Whether the font supports the language
    pub fn is_success(&self) -> bool {
        !self.is_unknown() && self.0.iter().all(|r| r.problems.is_empty())
    }

    /// Whether the support level is unknown
    ///
    /// This normally occurs when the language definition is not complete
    /// enough to run any checks.
    pub fn is_unknown(&self) -> bool {
        self.0.iter().map(|r| r.total_checks).sum::<usize>() == 0
    }

    /// The total number of unique fixes required to provide language support
    pub fn fixes_required(&self) -> usize {
        self.unique_fixes().values().map(|v| v.len()).sum::<usize>()
    }

    /// Whether the font is nearly successful in supporting the language
    ///
    /// This is a designer-focused measure in that it counts the number of
    /// fixes required and compares it to a threshold. The threshold is
    /// set by the caller.
    pub fn is_nearly_success(&self, nearly: usize) -> bool {
        self.fixes_required() <= nearly
    }

    /// A summary of the language support in one sentence
    pub fn to_summary_string(&self, language: &Language) -> String {
        match self.support_level() {
            SupportLevel::Complete => {
                format!(
                    "Font has complete support for {} ({}): 100%",
                    language.id(),
                    language.name()
                )
            }
            SupportLevel::Supported => format!(
                "Font fully supports {} ({}): {:.0}%",
                language.id(),
                language.name(),
                self.score()
            ),
            SupportLevel::Incomplete => format!(
                "Font partially supports {} ({}): {:.0}% ({} fixes required)",
                language.id(),
                language.name(),
                self.score(),
                self.fixes_required()
            ),
            SupportLevel::Unsupported => format!(
                "Font does not support {} ({}): {:.0}% ({} fixes required)",
                language.id(),
                language.name(),
                self.score(),
                self.fixes_required()
            ),
            SupportLevel::None => {
                format!(
                    "Font does not attempt to support {} ({})",
                    language.id(),
                    language.name()
                )
            }
            SupportLevel::Indeterminate => {
                format!(
                    "Cannot determine whether font supports {} ({})",
                    language.id(),
                    language.name()
                )
            }
        }
    }
}

#[derive(Debug, Serialize, PartialEq)]
/// Represents different levels of support for the language
pub enum SupportLevel {
    /// The support is complete; i.e. nothing can be improved
    Complete,
    /// There were no FAILs or WARNS, but some optional SKIPs which suggest possible improvements
    Supported,
    /// The support is incomplete, but usable; ie. there were WARNs, but no FAILs
    Incomplete,
    /// The language is not usable; ie. there were FAILs
    Unsupported,
    /// The font failed basic checks and is not usable at all for this language
    None,
    /// Language support could not be determined
    Indeterminate,
}
