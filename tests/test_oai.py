import pytest

from oaipmh.oai import OAIIdentifier, get_set_spec


def test_oai_identifier_parse_invalid():
    with pytest.raises(ValueError):
        OAIIdentifier.parse('invalid:ident')


@pytest.mark.parametrize(
    ('identifier_string', 'namespace_identifier', 'local_identifier'),
    [
        ('oai:fcrepo:foo', 'fcrepo', 'foo'),
        ('oai:fcrepo:http%3A//fcrepo-local%3A8080/rest/foo', 'fcrepo', 'http://fcrepo-local:8080/rest/foo'),
    ]
)
def test_oai_identifier_parse(identifier_string, namespace_identifier, local_identifier):
    identifier = OAIIdentifier.parse(identifier_string)
    assert isinstance(identifier, OAIIdentifier)
    assert identifier.namespace_identifier == namespace_identifier
    assert identifier.local_identifier == local_identifier
    assert str(identifier) == identifier_string


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('', ''),
        ('Simple', 'simple'),
        ('SOME Collection [#1]', 'some_collection_1_'),
    ]
)
def test_get_set_spec(title, expected):
    assert get_set_spec(title) == expected
