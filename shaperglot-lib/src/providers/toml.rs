use std::collections::HashMap;

use crate::{checks::Check, language::Language, Provider};

/// The manual checks profile, a TOML file
const TOML_PROFILE: &str = include_str!("../../manual_checks.toml");

use std::sync::LazyLock;

/// The manual checks, loaded from the TOML profile
static MANUAL_CHECKS: LazyLock<HashMap<String, Vec<Check>>> =
    LazyLock::new(|| toml::from_str(TOML_PROFILE).expect("Could not parse manual checks file: "));

/// Provide additional language-specific checks via a static TOML file
pub struct TomlProvider;

impl Provider for TomlProvider {
    fn checks_for(&self, language: &Language) -> Vec<Check> {
        MANUAL_CHECKS
            .get(language.id())
            .cloned()
            .unwrap_or_default()
    }
}
