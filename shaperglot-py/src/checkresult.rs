use pyo3::prelude::*;
use pythonize::pythonize;
use shaperglot::{CheckResult as RustCheckResult, Problem as RustProblem, ResultCode};

/// The result of running a check
///
/// Remembering that determining language support is made up of _multiple_ checks
/// which are added together, the result of an individual check could tell us, for
/// example, that all base characters are present, or that some are missing; that
/// some auxiliary characters are missing; that shaping expectations were not met for
/// a particular combination, and so on.
///
/// Looking in CheckResults can give us a lower-level indication of what is needed for
/// support to be added for a particular language; for a higher-level overview ("is
/// this language supported or not?"), look at the `Reporter` object.
#[pyclass(module = "shaperglot")]
pub(crate) struct CheckResult(pub(crate) RustCheckResult);

#[pymethods]
impl CheckResult {
    /// The message of the check result
    #[getter]
    pub(crate) fn message(&self) -> String {
        self.0.to_string()
    }

    pub(crate) fn __str__(&self) -> String {
        self.0.to_string()
    }

    /// Whether the check was successful
    #[getter]
    pub(crate) fn is_success(&self) -> bool {
        self.0.status == ResultCode::Pass
    }

    /// The result of the check
    ///
    /// Returns:
    ///     str: The result of the check - one of "PASS", "WARN", "FAIL", "SKIP" or "STOP"
    #[getter]
    pub(crate) fn status_code(&self) -> String {
        self.0.status.to_string()
    }

    /// The problems found during the check
    ///
    /// These "problems" are aimed towards font designers, to guide them towards
    /// adding support for a particular language.
    ///
    /// Returns:
    ///    List[Problem]: A list of problems found during the check
    #[getter]
    pub(crate) fn problems(&self) -> Vec<Problem> {
        self.0.problems.iter().map(|p| Problem(p.clone())).collect()
    }
}

/// A problem found during a check
#[pyclass(module = "shaperglot")]
pub(crate) struct Problem(pub(crate) RustProblem);
#[pymethods]
impl Problem {
    /// The name of the check that found the problem
    #[getter]
    fn check_name(&self) -> String {
        self.0.check_name.to_string()
    }

    /// A textual description of the problem
    #[getter]
    fn message(&self) -> String {
        self.0.message.to_string()
    }

    /// A status code (e.g. ``bases-missing``)
    #[getter]
    fn code(&self) -> String {
        self.0.code.to_string()
    }

    /// Whether the problem is terminal
    ///
    /// Some problems are so bad that there's no point testing for any more
    /// language coverage. (Imagine checking a font for Arabic support which is
    /// missing the letter BEH. Once you've determined that, there's not much
    /// point checking if it supports correct shaping behaviour.)
    #[getter]
    fn terminal(&self) -> bool {
        self.0.terminal
    }

    /// The context of the problem
    ///
    /// Returns:
    ///    dict: A dictionary of additional information about the problem
    #[getter]
    fn context<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, PyErr> {
        pythonize(py, &self.0.context)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyTypeError, _>(e.to_string()))
    }
}
