#[cfg(feature = "colored")]
use colored::Colorize;
use serde::{Deserialize, Serialize};
use std::{
    collections::{HashMap, HashSet},
    fmt::Display,
    hash::Hash,
};

use serde_json::Value;

#[derive(Debug, Default, Hash, Eq, PartialEq, Clone, Copy, Serialize, Deserialize)]
pub enum ResultCode {
    #[default]
    Pass,
    Warn,
    Fail,
    Skip,
}

impl Display for ResultCode {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        #[cfg(feature = "colored")]
        let to_string = match self {
            ResultCode::Pass => "PASS".green(),
            ResultCode::Warn => "WARN".yellow(),
            ResultCode::Fail => "FAIL".red(),
            ResultCode::Skip => "SKIP".blue(),
        };
        #[cfg(not(feature = "colored"))]
        let to_string = match self {
            ResultCode::Pass => "PASS",
            ResultCode::Warn => "WARN",
            ResultCode::Fail => "FAIL",
            ResultCode::Skip => "SKIP",
        };
        write!(f, "{}", to_string)
    }
}

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct Fix {
    pub fix_type: String,
    pub fix_thing: String,
}

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct Problem {
    pub check_name: String,
    pub message: String,
    pub code: String,
    #[serde(skip_serializing_if = "Value::is_null")]
    pub context: Value,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub fixes: Vec<Fix>,
}

impl Problem {
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

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct CheckResult {
    pub check_name: String,
    pub check_description: String,
    pub score: f32,
    pub weight: u8,
    pub problems: Vec<Problem>,
    pub total_checks: usize,
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
    pub fn summary_result(&self) -> String {
        if self.problems.is_empty() {
            return format!("{}: no problems found", self.check_name);
        }
        format!("{} check failed", self.check_name)
    }
}

#[derive(Debug, Default, Serialize)]
pub struct Reporter(Vec<CheckResult>);

impl Reporter {
    pub fn new() -> Self {
        Self(vec![])
    }

    pub fn add(&mut self, checkresult: CheckResult) {
        self.0.push(checkresult);
    }

    pub fn iter(&self) -> impl Iterator<Item = &CheckResult> {
        self.0.iter()
    }

    pub fn iter_problems(&self) -> impl Iterator<Item = &Problem> {
        self.0.iter().flat_map(|r| r.problems.iter())
    }

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

    pub fn count_fixes(&self) -> usize {
        let unique_fixes = self.unique_fixes();
        unique_fixes.values().map(|v| v.len()).sum()
    }

    pub fn score(&self) -> f32 {
        // Weighted sum of all scores, out of 100%
        let total_weight: u8 = self.0.iter().map(|r| r.weight).sum();
        let weighted_scores = self.0.iter().map(|r| r.score * f32::from(r.weight));
        let total_score: f32 = weighted_scores.sum();
        total_score / f32::from(total_weight) * 100.0
    }

    pub fn is_success(&self) -> bool {
        self.0.iter().all(|r| r.problems.is_empty())
    }
    pub fn is_unknown(&self) -> bool {
        self.0.iter().map(|r| r.total_checks).sum::<usize>() == 0
    }

    pub fn is_nearly_success(&self, nearly: usize) -> bool {
        self.unique_fixes().values().map(|v| v.len()).sum::<usize>() <= nearly
    }
}
