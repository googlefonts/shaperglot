# Overview

Test font files for OpenType language support

[![PyPI Version](https://img.shields.io/pypi/v/shaperglot.svg)](https://pypi.org/project/shaperglot)
[![PyPI License](https://img.shields.io/pypi/l/shaperglot.svg)](https://pypi.org/project/shaperglot)

Development has barely started, so don't try using this yet.

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
