use pyo3::prelude::*;
use shaperglot::checks::CheckImplementation;
use shaperglot::Check as RustCheck;

/// A check to be executed
///
/// This is a high-level check which is looking for a particular piece of behaviour in
/// a font. It may be made up of multiple "implementations" which are the actual code
/// that is run to check for the behaviour. For example, an orthography check will
/// first check bases, then marks, then auxiliary codepoints. The implementations for
/// this check would be "given this list of bases, ensure the font has coverage for
/// all of them", and so on.
#[pyclass(module = "shaperglot")]
pub(crate) struct Check(pub(crate) RustCheck);

#[pymethods]
impl Check {
    /// A human-readable description of the check
    ///
    /// Returns:
    ///     A string describing the check
    #[getter]
    fn description(&self) -> String {
        self.0.description.to_string()
    }

    /// An array of human-readable descriptions for what the check does.
    ///
    /// Returns:
    ///     An array of strings describing the check
    #[getter]
    fn implementations(&self) -> Vec<String> {
        self.0
            .implementations
            .iter()
            .map(|s| s.describe())
            .collect()
    }
}
