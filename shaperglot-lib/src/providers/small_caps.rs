use crate::{
    checks::{
        shaping_differs::{FeaturesOptional, IgnoreNotdefs},
        Check, CheckType, ScoringStrategy, ShapingDiffers,
    },
    language::Language,
    shaping::ShapingInput,
    Provider, ResultCode,
};
use unicode_properties::{GeneralCategory, UnicodeGeneralCategory};

/// A provider that checks for small caps support in Latin-based languages
///
/// This provider checks that Latin letters form small caps when the `smcp` feature is enabled.
/// If the `smcp` feature is not present in the font, the check will be skipped.
pub struct SmallCapsProvider;

impl Provider for SmallCapsProvider {
    fn checks_for(&self, language: &Language) -> Vec<Check> {
        if language.script() != "Latn" {
            return vec![];
        }

        let smcp_able = language
            .bases
            .iter()
            .chain(language.auxiliaries.iter())
            .filter(|s| {
                s.chars().count() == 1
                    && s.chars()
                        .all(|c| c.general_category() == GeneralCategory::LowercaseLetter)
            });
        let implementations = vec![CheckType::ShapingDiffers(ShapingDiffers::new(
            smcp_able
                .map(|s| {
                    (
                        ShapingInput::new_simple(s.to_string()),
                        ShapingInput::new_with_feature(s.to_string(), "smcp"),
                    )
                })
                .collect(),
            FeaturesOptional(true),
            IgnoreNotdefs(true),
        ))];
        vec![Check {
            name: "Small caps for Latin letters".to_string(),
            severity: ResultCode::Warn,
            description: "Latin letters should form small caps when the smcp feature is enabled"
                .to_string(),
            scoring_strategy: ScoringStrategy::Continuous,
            weight: 10,
            implementations,
        }]
    }
}
