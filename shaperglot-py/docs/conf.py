import shaperglot

project = 'shaperglot'
copyright = '2025, Simon Cozens'
author = 'Simon Cozens'
release = shaperglot.__version__
version = release
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.napoleon',
    'myst_parser',
]

autosummary_generate = True
autosummary_imported_members = True

templates_path = ['_templates']

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'
html_static_path = ['_static']

html_theme_options = {
    'nosidebar': True,
}
