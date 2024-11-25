mod codepoint_coverage;
mod no_orphaned_marks;

use crate::{
    checker::Checker,
    reporter::{CheckResult, Problem},
    ResultCode,
};
use ambassador::{delegatable_trait, Delegate};
pub use codepoint_coverage::CodepointCoverage;
pub use no_orphaned_marks::NoOrphanedMarks;
use serde::{Deserialize, Serialize};

#[delegatable_trait]
pub trait CheckImplementation {
    fn name(&self) -> String;
    fn describe(&self) -> String;
    fn should_skip(&self, checker: &Checker) -> Option<String>;
    fn execute(&self, checker: &Checker) -> (Vec<Problem>, usize);
}

#[derive(Serialize, Deserialize)]
pub enum ScoringStrategy {
    Continuous,
    AllOrNothing,
}

#[derive(Delegate, Serialize, Deserialize)]
#[delegate(CheckImplementation)]
#[serde(tag = "type")]
pub enum CheckType {
    CodepointCoverage(CodepointCoverage),
    NoOrphanedMarks(NoOrphanedMarks),
}

#[derive(Serialize, Deserialize)]
pub struct Check {
    pub name: String,
    pub severity: ResultCode,
    pub description: String,
    pub scoring_strategy: ScoringStrategy,
    pub weight: u8,
    pub implementations: Vec<CheckType>,
}

impl Check {
    pub fn execute(&self, checker: &Checker) -> CheckResult {
        let mut problems = Vec::new();
        let mut total_checks = 0;
        for implementation in &self.implementations {
            // if let Some(skip_reason) = implementation.should_skip(checker) {
            //     messages.push(Problem::new_skip(&implementation.name(), skip_reason))
            // } else {
            let (local_problems, checks_run) = implementation.execute(checker);
            problems.extend(local_problems);
            total_checks += checks_run;
            // }
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
