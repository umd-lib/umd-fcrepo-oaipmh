from unittest.mock import MagicMock

import pysolr
import pytest
from lxml import etree
from oai_repo.exceptions import OAIErrorCannotDisseminateFormat

from oaipmh.dataprovider import DataProvider, OAIIdentifier


@pytest.fixture
def mock_solr_client():
    mock_solr = MagicMock(spec=pysolr.Solr)
    mock_solr.url = 'http://localhost:8983/solr/fcrepo'
    return mock_solr


@pytest.fixture
def provider(mock_solr_client):
    return DataProvider(solr_client=mock_solr_client)


@pytest.fixture
def xml():
    return etree.XML('<rdf:Description xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"/>')


@pytest.fixture
def prange_rdf(datadir):
    return etree.parse(datadir / 'prange_poster.xml')


def test_dataprovider(monkeypatch, provider):
    monkeypatch.setenv('OAI_NAMESPACE_IDENTIFIER', 'fcrepo')
    assert provider.is_valid_identifier('oai:fcrepo:foo')
    assert not provider.is_valid_identifier('oai:other:thing')


def test_transform_unsupported_format(provider, xml):
    with pytest.raises(OAIErrorCannotDisseminateFormat):
        provider.transform('fake', xml)


@pytest.mark.parametrize(
    ('transformer', 'result_tag'),
    [
        ('oai_dc', '{http://www.openarchives.org/OAI/2.0/oai_dc/}dc'),
        ('rdf', '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF'),
    ]
)
def test_transform(provider, prange_rdf, transformer, result_tag):
    result = provider.transform(transformer, prange_rdf)
    assert result.tag == result_tag


def test_get_metadata_formats(provider):
    formats = provider.get_metadata_formats()
    assert len(formats) == 2
    assert {f.metadata_prefix for f in formats} == {'oai_dc', 'rdf'}


@pytest.mark.parametrize(
    ('local_identifier', 'expected'),
    [
        ('foo', 'oai:fcrepo:foo'),
        ('http://fcrepo-local:8080/fcrepo/rest/bar', 'oai:fcrepo:http%3A//fcrepo-local%3A8080/fcrepo/rest/bar'),
    ]
)
def test_get_oai_identifier(monkeypatch, provider, local_identifier, expected):
    monkeypatch.setenv('OAI_NAMESPACE_IDENTIFIER', 'fcrepo')
    identifier = provider.get_oai_identifier(local_identifier)
    assert isinstance(identifier, OAIIdentifier)
    assert str(identifier) == expected


def test_get_record_header_from_solr_results(provider):
    provider.solr_results = {
        'oai:fcrepo:foo': {
            'last_modified': '2023-06-16T08:37:29Z'
        }
    }
    header = provider.get_record_header('oai:fcrepo:foo')
    assert header.identifier == 'oai:fcrepo:foo'
    assert header.datestamp == '2023-06-16T08:37:29Z'
