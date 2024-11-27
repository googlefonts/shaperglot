use crate::{checks::Check, language::Language};

/// Orthographic checks provider
mod orthographies;
/// Arabic positional forms checks provider
mod positional;
/// Latin small caps checks provider
mod small_caps;
/// Manually-coded checks provider
mod toml;

use orthographies::OrthographiesProvider;
use positional::PositionalProvider;
use small_caps::SmallCapsProvider;
use toml::TomlProvider;

/// A provider of checks for a language
pub trait Provider {
    /// Given a language, return a list of checks that apply to it
    fn checks_for(&self, language: &Language) -> Vec<Check>;
}

/// The base check provider provides all checks for a language
///
/// It calls all other known providers to get their checks.
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
