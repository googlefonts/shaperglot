# A "provider" is a Python class which provides a profile for a given
# language. Instead of supplying the language's checks as a YAML file,
# the developer can supply a provider which knows how to generate
# the checks at runtime. They have a single method, `.fill`, which
# takes a language definition and adds any relevant checks to its
# "shaperglot_checks" list.
from .arabic import ArabicProvider
from .african_latin import AfricanLatinProvider

PROVIDERS = [
    ArabicProvider,
    AfricanLatinProvider,
]
