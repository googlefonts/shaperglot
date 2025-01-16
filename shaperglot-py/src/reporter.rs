#![deny(clippy::unwrap_used, clippy::expect_used)]
use std::collections::{HashMap, HashSet};

use pyo3::prelude::*;
use shaperglot::{
    CheckResult as RustCheckResult, Reporter as RustReporter, ResultCode, SupportLevel,
};

use crate::{checkresult::CheckResult, language::Language};

/// The result of testing a font for support of a particular language
///
/// The Reporter object can be iterated on to return a list of `CheckResult` objects.
#[pyclass(module = "shaperglot")]
pub(crate) struct Reporter(pub(crate) RustReporter);

#[pymethods]
impl Reporter {
    /// Whether the language supported could not be determined
    ///
    /// If the languages database does not contain enough information about a
    /// language to determine whether or not a font supports it - for example,
    /// if there are no base characters defined - then the support level will
    /// be "indeterminate", and this method will return ``True``.
    #[getter]
    fn is_unknown(&self) -> bool {
        self.0.is_unknown()
    }

    /// Whether the font can be easily fixed to support the language.
    ///
    /// The audience of this method is the designer of the font, not the user of
    /// the font. It returns True if a font requires fewer than ``fixes`` fixes
    /// to support the language.
    fn is_nearly_success(&self, fixes: usize) -> bool {
        self.0.is_nearly_success(fixes)
    }

    /// Whether the font fully supports the language
    ///
    /// This method returns ``True`` if the font fully supports the language. Note
    /// that *fully* is a relatively high standard. For practical usage, a `score`
    /// of more than 80% is good enough.
    #[getter]
    fn is_success(&self) -> bool {
        self.0.is_success()
    }

    /// The set of unique fixes which need to be made to add support.
    ///
    /// The audience of this method is the designer of the font, not the user of
    /// the font. This returns a dictionary of fixes required, where the key is
    /// the area of support and the value is the set of fixes required.
    fn unique_fixes(&self) -> HashMap<String, HashSet<String>> {
        self.0.unique_fixes().into_iter().collect()
    }

    /// Number of fixes required to add support.
    #[getter]
    fn fixes_required(&self) -> usize {
        self.0.fixes_required()
    }

    /// Failing checks
    ///
    /// This returns `CheckResult` objects for all checks which failed.
    #[getter]
    fn fails(&self) -> Vec<CheckResult> {
        self.0
            .iter()
            .filter(|r| r.status == ResultCode::Fail)
            .map(|r| CheckResult(r.clone()))
            .collect()
    }

    /// Warnings
    ///
    /// This returns `CheckResult` objects for all checks which returned
    /// a warning status.
    #[getter]
    fn warns(&self) -> Vec<CheckResult> {
        self.0
            .iter()
            .filter(|r| r.status == ResultCode::Warn)
            .map(|r| CheckResult(r.clone()))
            .collect()
    }

    /// The score of the font for the language
    ///
    /// Returns how supported the language is, as a percentage. Shaperglot is
    /// calibrated so that a score of 80% is adequate for everyday use. However,
    /// language support can often be improved - for example, by supporting
    /// optional auxiliary glyphs, adding small caps support, and so on.
    #[getter]
    fn score(&self) -> f32 {
        self.0.score()
    }

    /// The support level of the font for the language
    ///
    /// Returns a string describing the support level; one of:
    ///   - "none": No support at all; the checker hit a "stop now" condition,
    ///     usually caused by a missing mandatory base
    ///   - "complete": Nothing can be done to improve this font's language support.
    ///   - "supported": There were no FAILs or WARNS, but some optional SKIPs which suggest possible improvements
    ///   - "incomplete": The support is incomplete, but usable; ie. there were WARNs, but no FAILs
    ///   - "unsupported": The language is not usable; ie. there were FAILs
    ///   - "indeterminate": The language support could not be determined, usually due to an incomplete language definition.
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

    /// The summary of the font's support for the language
    ///
    /// Returns a summary of the font's support for the language, in the form of a string
    /// suitable for display to the user. e.g.::
    ///
    ///     "Font fully supports en_Latn (English): 95%"
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
