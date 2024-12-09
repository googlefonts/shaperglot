use ::shaperglot::{Check as RustCheck, Language as RustLanguage, Languages as RustLanguages};
use pyo3::prelude::*;

use crate::check::Check;

#[pyclass(module = "shaperglot", mapping)]
pub(crate) struct Language(pub(crate) RustLanguage);

#[pymethods]
impl Language {
    fn __getitem__(&self, key: &str) -> Option<String> {
        match key {
            "name" => Some(self.0.name().to_string()),
            "language" => Some(self.0.proto.language().to_string()),
            "autonym" => Some(self.0.proto.autonym().to_string()),
            _ => None,
        }
    }

    #[getter]
    fn bases(&self) -> Vec<String> {
        self.0.bases.iter().map(|s| s.to_string()).collect()
    }

    #[getter]
    fn marks(&self) -> Vec<String> {
        self.0.marks.iter().map(|s| s.to_string()).collect()
    }
    #[getter]
    fn auxiliaries(&self) -> Vec<String> {
        self.0.auxiliaries.iter().map(|s| s.to_string()).collect()
    }

    #[getter]
    fn checks(&self) -> Vec<Check> {
        self.0.checks.iter().map(|c| Check(c.clone())).collect()
    }
}

#[pyclass(module = "shaperglot", mapping)]
pub(crate) struct Languages(RustLanguages);

#[pymethods]
impl Languages {
    #[new]
    pub(crate) fn new() -> Self {
        Self(RustLanguages::new())
    }

    pub(crate) fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<LanguageIterator>> {
        let iter = LanguageIterator {
            // Make a new one, they're all the same
            inner: RustLanguages::new().into_iter(),
        };
        Py::new(slf.py(), iter)
    }

    pub(crate) fn __getitem__(&self, lang: &str) -> Option<Language> {
        self.0.get_language(lang).cloned().map(Language)
    }

    pub(crate) fn __contains__(&self, lang: &str) -> bool {
        self.0.get_language(lang).is_some()
    }

    pub(crate) fn keys(&self) -> Vec<String> {
        self.0.iter().map(|l| l.id().to_string()).collect()
    }
    pub(crate) fn values(&self) -> Vec<Language> {
        self.0.iter().cloned().map(Language).collect()
    }

    pub(crate) fn disambiguate(&self, lang: &str) -> Vec<String> {
        let maybe_keys: Vec<String> = self
            .0
            .iter()
            .map(|l| l.id())
            .filter(|k| k.to_lowercase().starts_with(&(lang.to_lowercase() + "_")))
            .map(|k| k.to_string())
            .collect();
        if !maybe_keys.is_empty() {
            return maybe_keys;
        }
        self.0
            .iter()
            .filter(|l| l.name().to_lowercase().starts_with(&lang.to_lowercase()))
            .map(|l| l.id().to_string())
            .collect()
    }
}

#[pyclass(module = "shaperglot")]
pub(crate) struct LanguageIterator {
    inner: std::vec::IntoIter<RustLanguage>,
}

#[pymethods]
impl LanguageIterator {
    pub(crate) fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    pub(crate) fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<Language> {
        slf.inner.next().map(Language)
    }
}
