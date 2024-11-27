use crate::{checks::Check, language::Language};

mod orthographies;
mod positional;
mod small_caps;
mod toml;

use orthographies::OrthographiesProvider;
use positional::PositionalProvider;
use small_caps::SmallCapsProvider;
use toml::TomlProvider;

pub trait Provider {
    fn checks_for(&self, language: &Language) -> Vec<Check>;
}

/// The base check provider provides all checks for a language
pub struct BaseCheckProvider;

impl Provider for BaseCheckProvider {
    fn checks_for(&self, language: &Language) -> Vec<Check> {
        let mut checks: Vec<Check> = vec![];
        checks.extend(OrthographiesProvider.checks_for(language));
        checks.extend(SmallCapsProvider.checks_for(language));
        checks.extend(PositionalProvider.checks_for(language));
        checks.extend(TomlProvider.checks_for(language));
        checks
    }
}
