#![deny(clippy::unwrap_used, clippy::expect_used)]
use check::Check;
use checkresult::{CheckResult, Problem};
use language::{Language, Languages};
use pyo3::prelude::*;
use reporter::Reporter;

mod check;
mod checker;
mod checkresult;
mod language;
mod reporter;

use crate::checker::Checker;
#[pymodule(name = "_shaperglot")]
fn shaperglot(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Checker>()?;
    m.add_class::<Check>()?;
    m.add_class::<Language>()?;
    m.add_class::<Languages>()?;
    m.add_class::<CheckResult>()?;
    m.add_class::<Reporter>()?;
    m.add_class::<Problem>()
}
