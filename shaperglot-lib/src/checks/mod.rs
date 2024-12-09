/// A check implementation which ensures codepoints are present in a font
mod codepoint_coverage;
/// A check implementation which ensures marks are anchors to their respective base characters
pub(crate) mod no_orphaned_marks;
/// A check implementation which ensures that two shaping inputs produce different outputs
pub(crate) mod shaping_differs;

use crate::{
    checker::Checker,
    reporter::{CheckResult, Problem},
    ResultCode,
};
use ambassador::{delegatable_trait, Delegate};
pub use codepoint_coverage::CodepointCoverage;
pub use no_orphaned_marks::NoOrphanedMarks;
use serde::{Deserialize, Serialize};
pub use shaping_differs::ShapingDiffers;

#[delegatable_trait]
/// A check implementation
///
/// This is a sub-unit of a [Check]; a Check is made up of multiple
/// `CheckImplementations`. For example, an orthography check will
/// first check bases, then marks, then auxiliary codepoints.
pub trait CheckImplementation {
    /// The name of the check implementation
    fn name(&self) -> String;
    /// A description of the check implementation
    fn describe(&self) -> String;
    /// Whether the subcheck should be skipped for this font
    fn should_skip(&self, checker: &Checker) -> Option<String>;
    /// Execute the check implementation and return problems found
    fn execute(&self, checker: &Checker) -> (Vec<Problem>, usize);
}

#[derive(Serialize, Deserialize, PartialEq, Debug, Clone)]
/// The scoring strategy for a check
pub enum ScoringStrategy {
    /// A continuous score; the score is the proportion of checks that pass
    Continuous,
    /// An all-or-nothing score; the score is 1 if all checks pass, 0 otherwise
    AllOrNothing,
}

#[derive(Delegate, Serialize, Deserialize, Debug, Clone)]
#[delegate(CheckImplementation)]
#[serde(tag = "type")]
/// Check implementations available to higher-level checks
pub enum CheckType {
    /// A check implementation which ensures codepoints are present in a font
    CodepointCoverage(CodepointCoverage),
    /// A check implementation which ensures marks are anchors to their respective base characters
    NoOrphanedMarks(NoOrphanedMarks),
    /// A check implementation which ensures that two shaping inputs produce different outputs
    ShapingDiffers(ShapingDiffers),
}

#[derive(Serialize, Deserialize, Debug, Clone)]
/// A check to be executed
pub struct Check {
    /// The name of the check
    pub name: String,
    /// The severity of the check in terms of how it affects language support
    pub severity: ResultCode,
    /// A description of the check
    pub description: String,
    /// The scoring strategy for the check
    pub scoring_strategy: ScoringStrategy,
    /// The weight of the check
    pub weight: u8,
    /// Individual implementations to be run
    pub implementations: Vec<CheckType>,
}

impl Check {
    /// Execute the check and return the results
    pub fn execute(&self, checker: &Checker) -> CheckResult {
        let mut problems = Vec::new();
        let mut total_checks = 0;
        for implementation in &self.implementations {
            if let Some(skip_reason) = implementation.should_skip(checker) {
                // If there's only one implementation and we skipped, return a skip
                // result. Otherwise, add a skip problem.
                let skip_problem = Problem::new(
                    &self.name,
                    "skip",
                    format!("Check skipped: {}", skip_reason),
                );
                if self.implementations.len() == 1 {
                    return CheckResult {
                        check_name: self.name.clone(),
                        check_description: self.description.clone(),
                        status: ResultCode::Skip,
                        score: 0.5,
                        weight: self.weight,
                        problems: vec![skip_problem],
                        total_checks: 1,
                    };
                } else {
                    problems.push(skip_problem);
                    total_checks += 1;
                }
            } else {
                let (local_problems, checks_run) = implementation.execute(checker);
                problems.extend(local_problems);
                total_checks += checks_run;
            }
        }

        let score = match self.scoring_strategy {
            ScoringStrategy::AllOrNothing => {
                if problems.is_empty() {
                    1.0
                } else {
                    0.0
                }
            }
            ScoringStrategy::Continuous => {
                if total_checks == 0 {
                    1.0
                } else {
                    1.0 - (problems.len() as f32 / total_checks as f32)
                }
            }
        };
        CheckResult {
            check_name: self.name.clone(),
            check_description: self.description.clone(),
            status: if total_checks == 0 {
                ResultCode::Skip
            } else if problems.is_empty() {
                ResultCode::Pass
            } else if self.scoring_strategy == ScoringStrategy::AllOrNothing
                && problems.iter().any(|p| p.terminal)
            {
                ResultCode::StopNow
            } else {
                self.severity
            },
            score,
            weight: self.weight,
            problems,
            total_checks,
        }
    }
}
