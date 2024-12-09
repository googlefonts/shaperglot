#![deny(clippy::unwrap_used, clippy::expect_used)]
use std::collections::{HashMap, HashSet};

use ::shaperglot::{
    CheckResult as RustCheckResult, Reporter as RustReporter, ResultCode, SupportLevel,
};
use pyo3::prelude::*;

use crate::{checkresult::CheckResult, language::Language};

#[pyclass(module = "shaperglot")]
pub(crate) struct Reporter(pub(crate) RustReporter);

#[pymethods]
impl Reporter {
    #[getter]
    fn is_unknown(&self) -> bool {
        self.0.is_unknown()
    }

    fn is_nearly_success(&self, fixes: usize) -> bool {
        self.0.is_nearly_success(fixes)
    }

    #[getter]
    fn is_success(&self) -> bool {
        self.0.is_success()
    }

    fn unique_fixes(&self) -> HashMap<String, HashSet<String>> {
        self.0.unique_fixes().into_iter().collect()
    }

    #[getter]
    fn fixes_required(&self) -> usize {
        self.0.fixes_required()
    }

    #[getter]
    fn fails(&self) -> Vec<CheckResult> {
        self.0
            .iter()
            .filter(|r| r.status == ResultCode::Fail)
            .map(|r| CheckResult(r.clone()))
            .collect()
    }

    #[getter]
    fn warns(&self) -> Vec<CheckResult> {
        self.0
            .iter()
            .filter(|r| r.status == ResultCode::Warn)
            .map(|r| CheckResult(r.clone()))
            .collect()
    }

    #[getter]
    fn score(&self) -> f32 {
        self.0.score()
    }

    #[getter]
    fn support_level(&self) -> &str {
        match self.0.support_level() {
            SupportLevel::None => "none",
            SupportLevel::Complete => "complete",
            SupportLevel::Supported => "supported",
            SupportLevel::Incomplete => "incomplete",
            SupportLevel::Unsupported => "unsupported",
            SupportLevel::Indeterminate => "indeterminate",
        }
    }

    fn to_summary_string(&self, language: &Language) -> String {
        self.0.to_summary_string(&language.0)
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<CheckResultIterator>> {
        let iter = CheckResultIterator {
            inner: slf.0.iter().cloned().collect::<Vec<_>>().into_iter(),
        };
        Py::new(slf.py(), iter)
    }
}

#[pyclass(module = "shaperglot")]
pub(crate) struct CheckResultIterator {
    inner: std::vec::IntoIter<RustCheckResult>,
}

#[pymethods]
impl CheckResultIterator {
    pub(crate) fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    pub(crate) fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<CheckResult> {
        slf.inner.next().map(CheckResult)
    }
}

impl From<RustReporter> for Reporter {
    fn from(reporter: RustReporter) -> Self {
        Self(reporter)
    }
}
