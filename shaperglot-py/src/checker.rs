use crate::{language::Language, reporter::Reporter};
use pyo3::{exceptions::PyValueError, prelude::*};
use shaperglot::Checker as RustChecker;

use std::sync::Arc;

#[pyclass(module = "shaperglot")]
/// The context for running font language support checks
///
/// This is the main entry point to shaperglot; it is used to load a font and run checks
/// against it.
pub(crate) struct Checker(Vec<u8>);

impl Checker {
    pub(crate) fn _checker(&self) -> Result<Arc<RustChecker>, PyErr> {
        Ok(Arc::new(RustChecker::new(&self.0).map_err(|e| {
            PyErr::new::<PyValueError, _>(e.to_string())
        })?))
    }
}

#[pymethods]
impl Checker {
    /// Create a new checker
    ///
    /// This will load a font from the given filename and prepare it for running checks.
    #[new]
    pub(crate) fn new(filename: &str) -> Result<Self, PyErr> {
        let font_binary = std::fs::read(filename)?;
        Ok(Self(font_binary))
    }

    /// Run a check against the font
    ///
    /// Args:
    ///     lang: A `Language` object obtained from the `Languages` directory.
    ///
    /// Returns:
    ///     A `Reporter` object with the results of checking the font for language coverage.
    pub(crate) fn check(&self, lang: &Language) -> PyResult<Reporter> {
        Ok(self._checker()?.check(&lang.0).into())
    }
}
