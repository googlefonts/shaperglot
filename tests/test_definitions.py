import pytest
from shaperglot.languages import definitions_directory, load_shaperglot_definition

tests = [ l.stem for l in definitions_directory.glob("*.yaml") ]

@pytest.mark.parametrize("language", tests)
def test_valid(language):
    load_shaperglot_definition(language, validate=True)

