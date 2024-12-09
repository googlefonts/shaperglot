use crate::{language::Language, reporter::Reporter};
use ::shaperglot::Checker as RustChecker;
use pyo3::{exceptions::PyValueError, prelude::*};

use std::sync::Arc;

#[pyclass(module = "shaperglot")]
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
    #[new]
    pub(crate) fn new(filename: &str) -> Result<Self, PyErr> {
        let font_binary = std::fs::read(filename)?;
        Ok(Self(font_binary))
    }

    pub(crate) fn check(&self, lang: &Language) -> PyResult<Reporter> {
        Ok(self._checker()?.check(&lang.0).into())
    }
}
