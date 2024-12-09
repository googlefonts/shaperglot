use ::shaperglot::Check as RustCheck;
use pyo3::prelude::*;
use shaperglot::checks::CheckImplementation;

#[pyclass(module = "shaperglot")]
pub(crate) struct Check(pub(crate) RustCheck);

#[pymethods]
impl Check {
    #[getter]
    fn description(&self) -> String {
        self.0.description.to_string()
    }

    #[getter]
    fn implementations(&self) -> Vec<String> {
        self.0
            .implementations
            .iter()
            .map(|s| s.describe())
            .collect()
    }
}
