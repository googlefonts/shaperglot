use crate::{
    checks::{Check, CheckType, CodepointCoverage, NoOrphanedMarks, ScoringStrategy},
    language::Language,
    shaping::ShapingInput,
    Provider, ResultCode,
};
use itertools::Itertools;
use unicode_properties::{GeneralCategoryGroup, UnicodeGeneralCategory};

/// Check if a base character (in NFC) contains a mark
fn has_complex_decomposed_base(base: &str) -> bool {
    base.chars()
        .any(|c| c.general_category_group() == GeneralCategoryGroup::Mark)
}

/// Check that the font covers the basic codepoints for the language's orthography
///
/// This check is mandatory for all languages. Base and mark codepoints are required,
/// and auxiliary codepoints are optional.
pub struct OrthographiesProvider;

impl Provider for OrthographiesProvider {
    fn checks_for(&self, language: &Language) -> Vec<Check> {
        let mut checks: Vec<Check> = vec![];

        if !language.bases.is_empty() {
            checks.push(mandatory_orthography(language));
        }

        if let Some(check) = auxiliaries_check(language) {
            checks.push(check);
        }
        checks
    }
}

/// Orthography check. We MUST have all bases and marks.
fn mandatory_orthography(language: &Language) -> Check {
    let mut mandatory_orthography = Check {
        name: "Mandatory orthography codepoints".to_string(),
        description: format!(
            "The font MUST support the following {} bases{}: {}",
            language.name(),
            if !language.marks.is_empty() {
                " and marks"
            } else {
                ""
            },
            language
                .bases
                .iter()
                .map(|x| format!("'{}'", x))
                .chain(language.marks.iter().map(|x| format!("'{}'", x)))
                .join(", ")
        ),
        severity: ResultCode::Fail,
        weight: 80,
        scoring_strategy: ScoringStrategy::AllOrNothing,
        implementations: vec![CheckType::CodepointCoverage(CodepointCoverage::new(
            language.bases.clone(),
            "base".to_string(),
            true,
        ))],
    };
    let marks: Vec<String> = language.marks.iter().map(|s| s.replace("◌", "")).collect();
    if !marks.is_empty() {
        mandatory_orthography
            .implementations
            .push(CheckType::CodepointCoverage(CodepointCoverage::new(
                marks,
                "mark".to_string(),
                false,
            )));
    }
    let complex_bases: Vec<ShapingInput> = language
        .bases
        .iter()
        .filter(|s| has_complex_decomposed_base(s))
        .map(|x| ShapingInput::new_simple(x.to_string()))
        .collect();
    if !complex_bases.is_empty() {
        // If base exemplars contain marks, they MUST NOT be orphaned.
        mandatory_orthography
            .implementations
            .push(CheckType::NoOrphanedMarks(NoOrphanedMarks::new(
                complex_bases,
                true,
            )));
    }
    mandatory_orthography
}

/// We SHOULD have auxiliaries
fn auxiliaries_check(language: &Language) -> Option<Check> {
    if language.auxiliaries.is_empty() {
        return None;
    }
    let complex_auxs: Vec<String> = language
        .auxiliaries
        .iter()
        .filter(|s| has_complex_decomposed_base(s))
        .map(|s| {
            if s.chars().count() == 1 {
                format!("◌{}", s)
            } else {
                s.to_string()
            }
        })
        .collect();

    let mut auxiliaries_check = Check {
        name: "Auxiliary orthography codepoints".to_string(),
        description: format!(
            "The font SHOULD support the following auxiliary orthography codepoints: {}",
            language
                .auxiliaries
                .iter()
                .map(|x| format!("'{}'", x))
                .join(", ")
        ),
        weight: 20,
        scoring_strategy: ScoringStrategy::Continuous,
        implementations: vec![],
        severity: ResultCode::Warn,
    };
    // Since this is a continuous score, we add a check for each codepoint:
    for codepoint in &language.auxiliaries {
        auxiliaries_check
            .implementations
            .push(CheckType::CodepointCoverage(CodepointCoverage::new(
                vec![codepoint.clone()],
                "auxiliary".to_string(),
                false,
            )));
    }
    // If auxiliary exemplars contain marks, they SHOULD NOT be orphaned.
    auxiliaries_check
        .implementations
        .push(CheckType::NoOrphanedMarks(NoOrphanedMarks::new(
            complex_auxs
                .iter()
                .map(|x| ShapingInput::new_simple(x.to_string()))
                .collect(),
            true,
        )));
    Some(auxiliaries_check)
}
