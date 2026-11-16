use crate::{
    checks::{
        shaping_differs::{FeaturesOptional, IgnoreNotdefs},
        Check, CheckType, ScoringStrategy, ShapingDiffers,
    },
    language::Language,
    shaping::ShapingInput,
    Provider, ResultCode,
};

/// KANNADA SIGN VIRAMA
const VIRAMA: char = '\u{0CCD}';
/// KANNADA LETTER RA
const RA: char = '\u{0CB0}';
/// KANNADA LETTER RRA, an archaic letter that fonts are not expected to draw below another
const RRA: char = '\u{0CB1}';
/// ಕ್ಷ and ಜ್ಞ: fonts draw these as ligatures, sometimes in features that cannot be turned off
const LIGATURES: [(char, char); 2] = [('\u{0C95}', '\u{0CB7}'), ('\u{0C9C}', '\u{0C9E}')];
/// The Indic shaping features that form conjuncts, subscripts and the reph
const CONJUNCT_FEATURES: [&str; 7] = [
    "-akhn", "-rphf", "-blwf", "-half", "-pstf", "-cjct", "-pres",
];

/// A provider that checks that Kannada consonant clusters form conjuncts
///
/// A font can cover every Kannada codepoint and still show a visible virama in
/// every cluster, if its conjunct rules are missing or are not registered for the
/// script tag the shaper uses. This provider checks that consonant + virama +
/// consonant shapes differently when the conjunct features are turned off, and
/// that ra + virama + consonant forms the reph (arkavattu).
pub struct KannadaConjunctsProvider;

impl Provider for KannadaConjunctsProvider {
    fn checks_for(&self, language: &Language) -> Vec<Check> {
        if language.script() != "Knda" {
            return vec![];
        }
        let consonants: Vec<char> = language
            .bases
            .iter()
            .filter(|s| s.chars().count() == 1)
            .filter_map(|s| s.chars().next())
            .filter(|c| ('\u{0C95}'..='\u{0CB9}').contains(c))
            .collect();
        if consonants.is_empty() {
            return vec![];
        }

        let mut cluster_pairs = vec![];
        for first in &consonants {
            for second in consonants.iter().filter(|c| **c != RRA) {
                if LIGATURES.contains(&(*first, *second)) {
                    continue;
                }
                let text = format!("{first}{VIRAMA}{second}");
                cluster_pairs.push((
                    ShapingInput::new_simple(text.clone()),
                    ShapingInput {
                        text,
                        features: CONJUNCT_FEATURES.iter().map(|f| f.to_string()).collect(),
                        language: None,
                    },
                ));
            }
        }

        // ರ್ರ is left out: many fonts draw it with a subscript ra, not the reph.
        let reph_pairs = consonants
            .iter()
            .filter(|c| **c != RA)
            .map(|c| {
                let text = format!("{RA}{VIRAMA}{c}");
                (
                    ShapingInput::new_simple(text.clone()),
                    ShapingInput::new_with_feature(text, "-rphf"),
                )
            })
            .collect();

        vec![
            Check {
                name: "Kannada consonant clusters form conjuncts".to_string(),
                severity: ResultCode::Fail,
                description: "Consonant + virama + consonant MUST shape differently when the conjunct features are turned off"
                    .to_string(),
                scoring_strategy: ScoringStrategy::Continuous,
                weight: 20,
                implementations: vec![CheckType::ShapingDiffers(ShapingDiffers::new(
                    cluster_pairs,
                    FeaturesOptional(false),
                    IgnoreNotdefs(true),
                ))],
            },
            Check {
                name: "Kannada ra before a consonant forms the arkavattu".to_string(),
                severity: ResultCode::Fail,
                description: "Ra + virama + consonant MUST shape differently when the rphf feature is turned off"
                    .to_string(),
                scoring_strategy: ScoringStrategy::Continuous,
                weight: 10,
                implementations: vec![CheckType::ShapingDiffers(ShapingDiffers::new(
                    reph_pairs,
                    FeaturesOptional(false),
                    IgnoreNotdefs(true),
                ))],
            },
        ]
    }
}
