use crate::{checks::Check, language::Language};

// use super::{african_latin_constants::AFRICAN_TAGS}
use super::Provider;
pub struct AfricanLatinProvider;

impl Provider for AfricanLatinProvider {
    fn checks_for(&self, _language: &Language) -> Vec<Check> {
        // let bases = &language.bases;
        // let auxiliaries = &language.auxiliaries;

        // The shaperglot-py African Latin provider looked over the
        // bases and auxiliaries to find any base+mark combinations inside
        // them, and then created a bunch of NoOrphanedMarks checks for
        // each of them. But now we do that anyway in NoOrphanMarksForOrthography,
        // so all that's left to do is small caps and eng.

        // And frankly the eng check was kind of broken, and the small caps
        // check is a pretty generic one. So nothing to do at this stage?

        vec![]
    }
}
