use pyo3::prelude::*;
use shaperglot::{Language as RustLanguage, Languages as RustLanguages};

use crate::check::Check;

#[pyclass(module = "shaperglot", mapping)]
/// A language in the database
///
/// For backwards compatibility, this can be used as a dictionary in a very limited way;
/// the following keys are supported:
///
/// - `name`: The name of the language
/// - `language`: The language code
/// - `autonym`: The autonym of the language (name of the language in the language itself)
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

    /// Base characters needed for support
    ///
    /// Returns:
    ///    List[str]: A list of base characters needed for support
    #[getter]
    fn bases(&self) -> Vec<String> {
        self.0.bases.iter().map(|s| s.to_string()).collect()
    }

    /// Marks needed for support
    ///
    /// Returns:
    ///   List[str]: A list of marks needed for support
    #[getter]
    fn marks(&self) -> Vec<String> {
        self.0.marks.iter().map(|s| s.to_string()).collect()
    }

    /// Auxiliary characters
    ///
    /// Auxiliary characters are not required but are recommended for support.
    /// The most common case for these is for borrowed words which are occasionally
    /// used within the language.
    /// For example, the letter é is not a required character to support the English
    /// language, but the word "café" is used in English and includes the letter é,
    /// so is an auxiliary character.
    ///
    /// Returns:
    ///   List[str]: A list of auxiliary characters
    #[getter]
    fn auxiliaries(&self) -> Vec<String> {
        self.0.auxiliaries.iter().map(|s| s.to_string()).collect()
    }

    /// Checks for the language
    ///
    /// Returns:
    ///  List[Check]: A list of checks for the language
    #[getter]
    fn checks(&self) -> Vec<Check> {
        self.0.checks.iter().map(|c| Check(c.clone())).collect()
    }
}
/// The language database
///
/// Instantiating `Languages` object loads the database and fills it with checks.
/// The database can be used like a Python dictionary, with the language ID as the key.
/// Language IDs are made up of an ISO639-3 language code, an underscore, and a ISO 15927
/// script code. (e.g. `en_Latn` for English in the Latin script.)

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

    /// Get a list of all language IDs in the database
    ///
    /// Returns:
    ///    List[str]: A list of all language IDs in the database
    pub(crate) fn keys(&self) -> Vec<String> {
        self.0.iter().map(|l| l.id().to_string()).collect()
    }

    /// Get a list of all languages in the database
    ///
    /// Returns:
    ///   List[Language]: A list of all languages in the database
    pub(crate) fn values(&self) -> Vec<Language> {
        self.0.iter().cloned().map(Language).collect()
    }

    /// Try to find a matching language ID given an ID or name
    ///
    /// This will try to find a language ID that matches the given string; it will return
    /// a list of candidate language IDs. For example, if you provide "en", it will return
    /// "en_Latn" and "en_Cyrl" if those are in the database. Otherwise, it will look for
    /// a matching name - if you provide "english", it will return "en_Latn".
    ///
    /// Args:
    ///     lang (str): The language ID or name to search for
    ///
    /// Returns:
    ///    List[str]: A list of candidate language IDs
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
