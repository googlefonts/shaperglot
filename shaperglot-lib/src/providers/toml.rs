use std::collections::HashMap;

use crate::{checks::Check, language::Language, Provider};

const TOML_PROFILE: &str = include_str!("../../manual_checks.toml");

use std::sync::LazyLock;

static MANUAL_CHECKS: LazyLock<HashMap<String, Vec<Check>>> =
    LazyLock::new(|| toml::from_str(TOML_PROFILE).expect("Could not parse manual checks file: "));

pub struct TomlProvider;

impl Provider for TomlProvider {
    fn checks_for(&self, language: &Language) -> Vec<Check> {
        MANUAL_CHECKS
            .get(language.id())
            .cloned()
            .unwrap_or_default()
    }
}
