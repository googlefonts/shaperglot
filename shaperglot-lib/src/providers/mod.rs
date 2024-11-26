use crate::{checks::Check, language::Language};

// mod african_latin;
mod orthographies;
mod small_caps;
use orthographies::OrthographiesProvider;
use small_caps::SmallCapsProvider;

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

        // And any manually coded checks

        checks
    }
}
