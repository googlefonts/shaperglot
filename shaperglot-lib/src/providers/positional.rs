use unicode_joining_type::{get_joining_type, JoiningType};
use unicode_properties::{GeneralCategoryGroup, UnicodeGeneralCategory};

use crate::{
    checks::{Check, CheckType, ScoringStrategy, ShapingDiffers},
    language::Language,
    shaping::ShapingInput,
    Provider, ResultCode,
};

const ZWJ: &str = "\u{200D}";

// const MARKS_FOR_LANG: [(&str, &str); 1] = [(
//     "ar_Arab",
//         "\u{064E}\u{0651} \u{064B}\u{0651} \u{0650}\u{0651} \u{064D}\u{0651} \u{064F}\u{0651} \u{064C}\u{0651}",
// )];

pub struct PositionalProvider;

impl Provider for PositionalProvider {
    fn checks_for(&self, language: &Language) -> Vec<Check> {
        if language.script() != "Arab" {
            return vec![];
        }
        // let marks = language
        //     .marks
        //     .iter()
        //     .map(|s| s.replace("\u{25CC}", ""))
        //     .filter(|s| {
        //         s.chars()
        //             .all(|c| c.general_category() == GeneralCategory::NonspacingMark)
        //     });
        let letters = language.bases.iter().filter(|s| {
            s.chars().count() == 1
                && s.chars()
                    .all(|c| c.general_category_group() == GeneralCategoryGroup::Letter)
        });
        let mut fina_pairs = vec![];
        let mut medi_pairs = vec![];
        let mut init_pairs = vec![];
        for base in letters {
            match get_joining_type(base.chars().next().unwrap()) {
                JoiningType::DualJoining => {
                    init_pairs.push(positional_check("", base, ZWJ, "init"));
                    medi_pairs.push(positional_check(ZWJ, base, ZWJ, "medi"));
                    fina_pairs.push(positional_check(ZWJ, base, "", "fina"));
                }
                JoiningType::RightJoining => {
                    fina_pairs.push(positional_check(ZWJ, base, "", "fina"));
                }
                _ => {}
            }
        }
        let implementations = vec![
            CheckType::ShapingDiffers(ShapingDiffers::new(init_pairs, false)),
            CheckType::ShapingDiffers(ShapingDiffers::new(medi_pairs, false)),
            CheckType::ShapingDiffers(ShapingDiffers::new(fina_pairs, false)),
        ];
        vec![Check {
            name: "Positional forms for Arabic letters".to_string(),
            severity: ResultCode::Fail,
            description: "Arabic letters should form positional forms when the init, medi, and fina features are enabled"
                .to_string(),
            scoring_strategy: ScoringStrategy::Continuous,
            weight: 20,
            implementations,
        }]
    }
}

fn positional_check(
    pre: &str,
    character: &str,
    post: &str,
    feature: &str,
) -> (ShapingInput, ShapingInput) {
    let input = pre.to_string() + character + post;
    let before = ShapingInput::new_with_feature(input.clone(), "-".to_string() + feature);
    let after = ShapingInput::new_simple(input);
    (before, after)
}