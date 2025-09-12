#![deny(missing_docs)]
#![deny(clippy::missing_docs_in_private_items)]
//! Shaperglot is a library for checking a font's language support.
//!
//! Unlike other language coverage tools, shaperglot is based on the idea
//! that the font must not simply cover Unicode codepoints to support a
//! language but must also behave in certain ways. Shaperglot does not
//! dictate particular implementations of language support, in terms of
//! what glyphs or rules are present in the font or how glyphs should be named,
//! but tests a font for its behaviour.
//!
//! # Example
//!
//! ```
//! use shaperglot::{Checker, Languages, Provider};
//!
//! fn test_font(font_binary: &[u8]) {
//!   let font = Checker::new(font_binary).expect("Failed to load font");
//!   let languages = Languages::new();
//!   for language in languages.iter() {
//!      let results = font.check(language);
//!      println!("{}", results.to_summary_string(language));
//!   }
//! }
//! ```

/// The checker object, representing the context of a check
mod checker;
/// Low-level checks and their implementations
pub mod checks;
/// Utility functions to extract information from a font
#[cfg(feature = "skrifa")]
mod font;
/// Structures and routines relating to the language database
mod language;
/// Providers turn a language definition into a set of checks
mod providers;
/// The reporter object, representing the results of a language test
mod reporter;
/// Utility functions for text shaping
mod shaping;

pub use crate::{
    checker::Checker,
    checks::Check,
    language::{Language, Languages},
    providers::Provider,
    reporter::{CheckResult, Problem, Reporter, ResultCode, SupportLevel},
};

/// A glyph ID.
pub type GlyphId = u32;
