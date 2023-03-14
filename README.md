# Shaperglot - Test font files for OpenType language support

[![PyPI Version](https://img.shields.io/pypi/v/shaperglot.svg)](https://pypi.org/project/shaperglot)
[![PyPI License](https://img.shields.io/pypi/l/shaperglot.svg)](https://pypi.org/project/shaperglot)

Shaperglot is a library and a utility for testing a font's language support.
You give it a font, and it tells you what languages are supported and to what
degree.

Most other libraries to check for language support (for example, Rosetta's
wonderful [hyperglot](https://hyperglot.rosettatype.com) library) do this by
looking at the Unicode codepoints that the font supports. Shaperglot takes
a different approach.

## What's wrong with the Unicode codepoint coverage approach?

For many common languages, it's possible to check that the language is
supported just by looking at the Unicode coverage. For example, to support
English, you need the 26 lowercase and uppercase letters of the Latin alphabet.

However, for the majority of scripts around the world, covering the codepoints
needed is not enough to say that a font really *supports* a particular language.
For correct language support, the font must also *behave* in a particular way.

Take the case of Arabic as an example. A font might contain glyphs which cover
all the codepoints in the Arabic block (0x600-0x6FF). But the font only *supports*
Arabic if it implements joining rules for the `init`, `medi` and `fina` features.
To say that a font supports Devanagari, it needs to implement conjuncts (which
set of conjuncts need to be included before we can say the font "supports"
Devanagari is debated...) and half forms, as well as contain a `languagesystem`
statement which triggers Indic reordering.

Even within the Latin script, a font only supports a language such as Turkish
if its casing behaving respects the dotless / dotted I distinction; a font
only supports Navajo if its ogonek anchoring is different to the anchoring used in
Polish; and so on.

But there's a further problem with testing language support by codepoint coverage:
it encourages designers to "fill in the blanks" to get to support, rather than
necessarily engage with the textual requirements of particular languages.

## Testing for behaviour, not coverage

Shaperglot therefore determines language support not just on codepoint coverage,
but also by examining how the font behaves when confronted with certain character
sequences.

The trick is to do this in a way which is not prescriptive. We know that there
are many different ways of implementing language support within a font, and that
design and other considerations will factor into precisely how a font is
constructed. Shaperglot presents the font with different strings, and makes sure
that "something interesting happened" - without necessarily specifying what.

In the case of Arabic, we need to know that the `init` feature is present, and that
when we shape some Arabic glyphs, the output with `init` turned on is different
to the output with `init` turned off. We don't care what's different; we only
care that something has happened. *(Yes, this still makes it possible to trick shaperglot into reporting support for a language which is not correctly implemented, but at that point, it's probably less effort to actually implement it...)*

Shaperglot includes (or will include) the following kinds of test:

* Certain codepoints were mapped to base or mark glyphs.
* A named feature was present.
* A named feature changed the output glyphs.
* A mark glyph was attached to a base glyph or composed into a precomposed glyph (but not left unattached).
* Certain glyphs in the output were different to one another.
* Languagesystems were defined in the font.
* ...

Using this library of tests, we then create language support definitions which
exercise the font's capabilities to obtain a fuller picture of its support for
a particular language. These language support definitions, expressed as YAML
files, are the core of Shaperglot; to extend and improve Shaperglot, we need as
many language support definition files as possible - so if you know a language
well and can express what it means to "support" that language properly, please
contribute a definition!

## Using Shaperglot

To report whether or not a given language is supported, pass a font and one or
more ISO639-3 language codes. 

```
$ shaperglot -v -v MyFont.ttf urd
Font does not fully support language 'urd'
 * PASS: All base glyphs were present in the font
 * FAIL: Some mark glyphs were missing: ْ
 * PASS: Required feature 'mark' was present
 * PASS: Mark glyph ◌َ  (FATHA) took part in a mark positioning rule
 * PASS: Mark glyph ◌ُ  (DAMMA) took part in a mark positioning rule
 * PASS: Mark glyph ◌ِ  (KASRA) took part in a mark positioning rule
 * PASS: Mark glyph ◌ٰ  (LONG_A) took part in a mark positioning rule
 * PASS: Required feature 'init' was present
 * PASS: Glyph ع (AINu1) took part in a init rule
 * PASS: Required feature 'medi' was present
 * PASS: Glyph ع (AINu1) took part in a medi rule
 * PASS: Required feature 'fina' was present
 * PASS: Glyph ع (AINu1) took part in a fina rule
 * PASS: Repeated beh forms should produce different shapes
 * PASS: Initial and final forms should differ
```

Shaperglot can also be run in bulk mode to check language support of entire font libraries. This is done by running `bulk-run-sg-.py` located in the scripts folder.

```
$ python bulk-run-sg.py ./<path-to-font-library>
```

This script will automatically drill down the direcory tree and identify all .ttf font files and check them against a subset of language tags. At this time `bulk-run-sg.py` only checks fonts for Pan-African language support. The list of relevant language tags are defined in `language_tag_data/iso639-3-afr-all.txt`. Shaperglot results procesed in bulk can be quite large and may require additional tools to analyze. See [font-lang-support-afr](https://github.com/JamraPatel/font-lang-support-afr) for an example of how bulk results can be reported. Results are saved into two `.json` files.

```
results.json
afr_tag_overview.json
```

`results.json` contains the checker results (`<failure type>: <failure details>`) for each language tag, broken down by font.
`afr_tag_overview.json` is a summary of which fonts in the library pass and fail for each language tag that was checked.


# Setup

## Requirements

* Python 3.9+

## Installation

Install it directly into an activated virtual environment:

```text
$ pip install shaperglot
```

or add it to your [Poetry](https://poetry.eustace.io/) project:

```text
$ poetry add shaperglot
```

# Usage

After installation, the package can imported:

```text
$ python
>>> import shaperglot
>>> shaperglot.__version__
```
