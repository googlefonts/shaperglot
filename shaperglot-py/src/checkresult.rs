use ::shaperglot::{CheckResult as RustCheckResult, Problem as RustProblem, ResultCode};
use pyo3::prelude::*;
use pythonize::pythonize;

#[pyclass(module = "shaperglot")]
pub(crate) struct CheckResult(pub(crate) RustCheckResult);

#[pymethods]
impl CheckResult {
    #[getter]
    pub(crate) fn message(&self) -> String {
        self.0.to_string()
    }

    pub(crate) fn __str__(&self) -> String {
        self.0.to_string()
    }

    #[getter]
    pub(crate) fn is_success(&self) -> bool {
        self.0.status == ResultCode::Pass
    }

    #[getter]
    pub(crate) fn status_code(&self) -> String {
        self.0.status.to_string()
    }

    #[getter]
    pub(crate) fn problems(&self) -> Vec<Problem> {
        self.0.problems.iter().map(|p| Problem(p.clone())).collect()
    }
}

#[pyclass(module = "shaperglot")]
pub(crate) struct Problem(pub(crate) RustProblem);
#[pymethods]
impl Problem {
    #[getter]
    fn check_name(&self) -> String {
        self.0.check_name.to_string()
    }

    #[getter]
    fn message(&self) -> String {
        self.0.message.to_string()
    }

    #[getter]
    fn code(&self) -> String {
        self.0.code.to_string()
    }

    #[getter]
    fn terminal(&self) -> bool {
        self.0.terminal
    }

    #[getter]
    fn context<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, PyErr> {
        pythonize(py, &self.0.context)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyTypeError, _>(e.to_string()))
    }
}
