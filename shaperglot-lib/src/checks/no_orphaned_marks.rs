use super::CheckImplementation;
use crate::{
    checker::Checker,
    reporter::{Fix, Problem},
    shaping::ShapingInput,
};
use itertools::Itertools;
use serde::{Deserialize, Serialize};
use unicode_properties::{GeneralCategory, UnicodeGeneralCategory};

#[derive(Serialize, Deserialize)]
pub struct NoOrphanedMarks {
    test_strings: Vec<ShapingInput>,
    has_orthography: bool,
}

impl CheckImplementation for NoOrphanedMarks {
    fn name(&self) -> String {
        "No Orphaned Marks".to_string()
    }

    fn should_skip(&self, _checker: &Checker) -> Option<String> {
        None
    }

    fn execute(&self, checker: &Checker) -> (Vec<Problem>, usize) {
        let tests_run = self.test_strings.len();
        let dotted_circle = checker.cmap.get(&0x25CC).map(|g| g.to_u32());
        let mut problems = vec![];

        for string in self.test_strings.iter() {
            let mut previous = None;
            let glyph_buffer = string
                .shape(checker)
                .expect("Failed to shape string for NoOrphanedMarks");
            for (codepoint, position) in glyph_buffer
                .glyph_infos()
                .iter()
                .zip(glyph_buffer.glyph_positions().iter())
            {
                // We got a notdef. The orthographies check would tell us about missing
                // glyphs, so if we are running one (we have exemplars) we ignore it; if not,
                // we report it.
                if codepoint.glyph_id == 0 && !self.has_orthography {
                    let mut fail = Problem::new(
                        &self.name(),
                        "notdef-produced",
                        format!("Shaper produced a .notdef while {}", string),
                    );
                    if let Some(input_codepoint) = string.char_at(codepoint.cluster as usize) {
                        fail.fixes = vec![Fix {
                            fix_type: "add_codepoint".to_string(),
                            fix_thing: input_codepoint.to_string(),
                        }];
                    }
                    problems.push(fail);
                }
                if checker
                    .codepoint_for(codepoint.glyph_id.into())
                    .map(simple_mark_check)
                    .unwrap_or(false)
                {
                    if previous.is_some() && previous == dotted_circle {
                        let fail = Problem {
                            check_name: self.name(),
                            message: format!("Shaper produced a dotted circle when {}", string),
                            code: "dotted-circle-produced".to_string(),
                            context: serde_json::json!({
                                "text": previous,
                                "mark": codepoint.glyph_id,
                            }),
                            fixes: vec![Fix {
                                fix_type: "add_feature".to_string(),
                                fix_thing: format!("to avoid a dotted circle while {}", string),
                            }],
                        };
                        problems.push(fail);
                    } else if position.x_offset == 0 && position.y_offset == 0 {
                        // Suspicious
                        let previous_name = previous.map_or_else(
                            || format!("The base glyph when {}", string),
                            |gid| {
                                checker
                                    .glyph_names
                                    .get(gid as usize)
                                    .cloned()
                                    .unwrap_or_else(|| format!("Glyph #{}", gid))
                            },
                        );
                        let this_name = checker
                            .glyph_names
                            .get(codepoint.glyph_id as usize)
                            .cloned()
                            .unwrap_or_else(|| format!("Glyph #{}", codepoint.glyph_id));
                        let fail = Problem {
                            check_name: self.name(),
                            message: format!(
                                "Shaper didn't attach {} to {} when {}",
                                this_name, previous_name, string
                            ),
                            code: "orphaned-mark".to_string(),
                            context: serde_json::json!({
                                "text": string,
                                "mark": this_name,
                                "base": previous_name,
                            }),
                            fixes: vec![Fix {
                                fix_type: "add_anchor".to_string(),
                                fix_thing: format!("{}/{}", previous_name, this_name),
                            }],
                        };
                        problems.push(fail);
                    }
                }
                previous = Some(codepoint.glyph_id);
            }
        }
        (problems, tests_run)
    }

    fn describe(&self) -> String {
        format!(
            "Checks that, when {}, no marks are left unattached",
            self.test_strings.iter().map(|x| x.describe()).join(" and ")
        )
    }
}

fn simple_mark_check(c: u32) -> bool {
    char::from_u32(c)
        .map(|c| matches!(c.general_category(), GeneralCategory::NonspacingMark))
        .unwrap_or(false)
}

impl NoOrphanedMarks {
    pub fn new(test_strings: Vec<ShapingInput>, has_orthography: bool) -> Self {
        Self {
            test_strings,
            has_orthography,
        }
    }
}