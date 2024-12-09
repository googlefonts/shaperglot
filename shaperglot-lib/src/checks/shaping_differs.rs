use std::collections::HashSet;

use super::CheckImplementation;
use crate::{
    checker::Checker,
    reporter::{Fix, Problem},
    shaping::ShapingInput,
};
use itertools::Itertools;
use rustybuzz::SerializeFlags;
use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
/// Whether the features are optional
pub struct FeaturesOptional(pub bool);

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
/// Whether to ignore any notdefs generated while shaping
pub struct IgnoreNotdefs(pub bool);

#[derive(Serialize, Deserialize, Debug, Clone)]
/// A check implementation which ensures that two shaping inputs produce different outputs
pub struct ShapingDiffers {
    /// The pairs of strings to shape and compare
    pairs: Vec<(ShapingInput, ShapingInput)>,
    /// Whether the features are optional
    ///
    /// If this is true, the check will only run if the font contains the requested feature;
    /// otherwise it will be skiped. If it is false, the check will always run.
    features_optional: FeaturesOptional,
    /// Whether to ignore any notdefs generated while shaping
    ignore_notdefs: IgnoreNotdefs,
}

impl CheckImplementation for ShapingDiffers {
    fn name(&self) -> String {
        "Shaping Differs".to_string()
    }

    fn should_skip(&self, checker: &Checker) -> Option<String> {
        if !self.features_optional.0 {
            return None;
        }
        let needed_features: HashSet<String> = self
            .pairs
            .iter()
            .flat_map(|(a, b)| a.features.iter().chain(b.features.iter()))
            .cloned()
            .collect();
        let missing_features: Vec<String> = needed_features
            .difference(&checker.features)
            .cloned()
            .collect();
        if missing_features.is_empty() {
            return None;
        }
        Some(format!(
            "The following features are needed for this check, but are missing: {}",
            missing_features.join(", ")
        ))
    }

    fn execute(&self, checker: &Checker) -> (Vec<Problem>, usize) {
        let mut problems = vec![];
        for (before, after) in self.pairs.iter() {
            let glyph_buffer_before = before
                .shape(checker)
                .expect("Failed to shape before string for ShapingDiffers");
            let glyph_buffer_after = after
                .shape(checker)
                .expect("Failed to shape after string for ShapingDiffers");
            let serialized_before =
                glyph_buffer_before.serialize(&checker.face, SerializeFlags::default());
            let serialized_after =
                glyph_buffer_after.serialize(&checker.face, SerializeFlags::default());
            if serialized_before != serialized_after {
                continue;
            }
            if self.ignore_notdefs.0
                && glyph_buffer_before
                    .glyph_infos()
                    .iter()
                    .any(|glyph| glyph.glyph_id == 0)
            {
                continue;
            }
            let mut fail = Problem::new(
                &self.name(),
                "shaping-same",
                format!(
                    "When {} and {}, the output is expected to be different, but was the same",
                    before.describe(),
                    after.describe()
                ),
            );
            fail.fixes.push(Fix {
                fix_type: "add_feature".to_string(),
                fix_thing: format!(
                    "A rule such that {} and {} give different results",
                    before.describe(),
                    after.describe()
                ),
            });
            problems.push(fail);
        }
        (problems, self.pairs.len())
    }

    fn describe(&self) -> String {
        format!(
            "in the following situations, different results are produced: {}",
            self.pairs
                .iter()
                .map(|(a, b)| format!("{} versus {}", a.describe(), b.describe()))
                .join(", ")
        )
    }
}

impl ShapingDiffers {
    /// Create a new `ShapingDiffers` check implementation
    pub fn new(
        pairs: Vec<(ShapingInput, ShapingInput)>,
        features_optional: FeaturesOptional,
        ignore_notdefs: IgnoreNotdefs,
    ) -> Self {
        Self {
            pairs,
            features_optional,
            ignore_notdefs,
        }
    }
}
