# Contributing a Shaperglot Profile

Shaperglot relies on language-specific profile files which encode information about how languages should be correctly implemented. Additional language profiles from people with knowledge of a particular language's shaping requirements are very welcome.

## The structure of a profile

Language profiles are implemented as [YAML](https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started) files, placed in the `shaperglot/languages` directory. The language profile should be named after the [ISO639-3](https://iso639-3.sil.org/code_tables/639/data) tag for the language. For example, a language profile for Bemba should be found in the file `shaperglot/languages/bem.yaml`.

Shaperglot automatically tests that a font supports all base and mark characters identified by Hyperglot as being required for language support. Beyond that, Shaperglot language profiles define various tests for correct shaping. Writing these tests correctly is more of an art than a science. **Because font engineers may implement language-specific layout rules in arbitrary ways and because fonts may have an arbitrary set of glyphs, these tests must be written in a way that "probes" the font - without checking for specific rules or making assumptions about glyph names or the presence or absence of specific glyphs - but which collectively provide a picture of the font's likely shaping implementation.** In many cases, we will be testing that the font does *something* in particular situations - without necessarily testing for some specific result.

A language profile may have the following top-level elements:

### `features`

This is a list of OpenType feature tags, together with certain tests:

* `present` simply checks that the feature is present.

```yaml
features:
  locl:
    - present
```

* `involves` checks whether the given Unicode codepoint is involved in *any* rules defined by this feature. For example, this code:

```yaml
features:
  init:
    - involves: 0x0639
```

ensures that a rule in the `init` feature does *something* with U+0639 ARABIC LETTER AIN. In the particular case of the `mark` feature, the special check `involves: hyperglot` ensures that all codepoints designated as marks in the Hyperglot database are involved in rules in the `mark` feature.

### `languagesystems`

This checks that the given script and language tag is present in the font's language systems list:

```yaml
languagesystems: ["arab", "URD "]
```

### `shaping`

This is where the majority of the checks will find themselves. This will run the Harfbuzz shaper on one or more `inputs`, and allow you to check the results. Here is how inputs are specified:

### `inputs`

Each input is a dictionary with at least the `text` key, and optionally `language` and `features` keys:

```yaml
shaping:
    inputs:
        - text: "abc"
          language: "bem"
          features:
            smcp: true
```

The `features` dictionary is passed to `uharfbuzz`, and can specify either boolean values to turn on/off certain features, or a list of ranges of character positions and whether the feature should be on or off. Here is an example of the second form of the `features` dictionary:

```yaml
shaping:
    inputs:
        - text: "abcdef"
          features:
            smcp:
              - [0, 3, 0]
              - [3, 6, 1]
```

This turns off the `smcp` feature for the first three characters but turns it on for characters `def`.

Once the inputs have been shaped, the next stage is to compare the outputs. As the results will be glyph IDs, and we cannot assume anything about glyph coverage, tests will generally ensure that something *differs* between shaping runs.

### `differs`

This check compares the glyph IDs returned from the shaper at different cluster positions, and ensures that they differ. Returned glyph ID sequences to be compared are specified based on their *index*, which can take three forms:

* `[input ID, cluster ID, glyph within cluster]`
* `[input ID, cluster ID]`
* `cluster ID` (for comparisons of two clusters within the same, first input)

> You will need to ensure that you are familiar with the concept of a *cluster* in OpenType shaping. The Harfbuzz documentation defines a cluster as "a sequence of codepoints that must be treated as an indivisible unit. Clusters can include code-point sequences that form a ligature or base-and-mark sequences."

For example, the Burmese medial ra glyph needs to stretch across the width of the consonant that it surrounds. To test that this happens correctly, we shape two inputs, one with a medial ra surrounding a single bowl consonant and one with a double bowl consonant: 

```yaml
shaping:
    inputs:
        - text: "ပြ"
        - text: "ကြ"
```

This sets up our inputs. Now we check that the first glyph of the first cluster we got from shaping the first input is different to the first glyph of the first cluster we got from shaping the second input:

```yaml
    differs:
        - [0,0,0]
        - [1,0,0]
```

and we provide a reason for the test, which is displayed with the test report:

```yaml
    rationale: Medial ra should be selected based on width of base consonant
```

To test for correct `smcp` handling of the letter `i` in Turkish (which should uppercase to `İ`), we first shape small-cap `i` *without* Turkish language support, and then we shape it again with Turkish language turned on, and check we get different results:

```yaml
  - inputs:
    - text: "hi"
      features:
        smcp: true
    - text: "hi"
      language: "tr"
      features:
        smcp: true
    differs: 
      - [0,1]
      - [1,1]
    rationale: "Small-caps processing of Turkish should replace i with dotted I"
```

Notice that here we are using the second index format to compare whole clusters; it's just that in non-syllabic scripts, there's only one glyph in a cluster.

Of course, this check only applies to fonts which *have* a small caps feature, so we can make the execution of the check conditional on the `smcp` feature being present:

```yaml
    if:
      feature: smcp
```

And finally, an example of the shorthand index format for testing for differences within a single input:

```yaml
  - inputs:
      - "کک"
    differs: 
      - 0
      - 1
    rationale: Initial and final forms should differ
```

This shapes a single input of Arabic text, and checks that the glyphs returned at cluster zero differ from the glyphs at cluster one.

### `forms_cluster`

Another shaping test checks that certain character sequences end up in the same cluster after shaping. This is important in two ways: to ensure that syllables have been correctly formed, and to ensure that required ligatures have been applied.

For example, the lam-alif ligature is mandatory in Arabic, and we can test for its presence by shaping a lam-alif pair an ensuring that both characters end up in the same cluster:

```yaml
  - inputs:
      - "پلا"
    forms_cluster: [1, 2]
    rationale: Lam-alif should form ligature
```

The parameter for the `forms_cluster` check is a list of *character positions* in the input. Only one input string should be provided for `forms_cluster` checks.
