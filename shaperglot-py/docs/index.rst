.. include:: ../../README.md
   :parser: myst_parser.sphinx_

Library usage
-------------

Reading the code of the CLI tool is a good way to understand how to use the library.
However, the most common use case - checking a font for language support - looks like
this::

   from shaperglot import Checker, Languages

   langs = Languages() # Load a language database
   checker = Checker(filename) # Create a checker context for the font
   supported = []
   for lang_id, language in langs.values():
      if checker.check(language).score > 80:
         supported.append(lang_id)

Running checks and getting results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: shaperglot.Checker
   :members:
   :undoc-members:

.. autoclass:: shaperglot.Reporter
   :members:
   :undoc-members:

.. autoclass:: shaperglot.CheckResult
   :members:
   :undoc-members:

.. autoclass:: shaperglot.Problem
   :members:
   :undoc-members:

Handling languages
^^^^^^^^^^^^^^^^^^

.. autoclass:: shaperglot.Languages
   :members:
   :undoc-members:

.. autoclass:: shaperglot.Language
   :members:
   :undoc-members:

Low level check information
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: shaperglot.Check
   :members:
   :undoc-members:

