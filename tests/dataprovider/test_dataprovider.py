from typing import Optional
from unittest.mock import MagicMock

import pysolr
import pytest
import requests
from lxml import etree
from oai_repo import Set
from oai_repo.exceptions import OAIErrorCannotDisseminateFormat, OAIRepoExternalException

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
def prange_text(datadir):
    return (datadir / 'prange_poster.xml').read_text()


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


def test_identify(monkeypatch, provider):
    monkeypatch.setenv('ADMIN_EMAIL', 'jdoe@example.com')
    monkeypatch.setenv('BASE_URL', 'http://localhost:5555/')
    monkeypatch.setenv('DATESTAMP_GRANULARITY', 'YYYY-MM-DD')
    monkeypatch.setenv('EARLIEST_DATESTAMP', '2020-01-01')
    monkeypatch.setenv('OAI_REPOSITORY_NAME', 'foo records')
    monkeypatch.setenv('REPORT_DELETED_RECORDS', 'yes')

    identify = provider.get_identify()
    assert identify.admin_email == ['jdoe@example.com']
    assert identify.base_url == 'http://localhost:5555/'
    assert identify.granularity == 'YYYY-MM-DD'
    assert identify.earliest_datestamp == '2020-01-01'
    assert identify.repository_name == 'foo records'
    assert identify.deleted_record == 'yes'


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


def test_sets(provider):
    provider.solr.search = MagicMock(return_value=[{'display_title': 'Foo'}, {'display_title': 'Bar'}])
    sets = provider.sets
    assert len(sets) == 2
    assert sets.keys() == {'foo', 'bar'}
    assert all(isinstance(v, Set) for v in sets.values())


def test_handle_not_found(provider):
    provider.solr.search = MagicMock(return_value=[])
    with pytest.raises(OAIRepoExternalException):
        provider.get_record_header('oai:fcrepo:foo')


class OKResponse:
    ok = True

    def __init__(self, text):
        self.text = text

    def __call__(self, *args, **kwargs):
        return self


@pytest.mark.parametrize(
    ('solr_results', 'search_count'),
    [
        # already cached in solr_results, no request to Solr
        ({'oai:fcrepo:foo': {'id': 'http://example.com/foo'}}, 0),
        # missing id, should fall back to request to Solr
        ({'oai:fcrepo:foo': {}}, 1),
        # missing key, should fall back to request to Solr
        ({}, 1),
    ]
)
def test_get_record_metadata(provider, prange_text, solr_results, search_count):
    provider.session.get = MagicMock(return_value=OKResponse(prange_text))
    provider.solr_results = solr_results
    results = MagicMock()
    results.docs = [{'id': 'http://example.com/foo', 'handle': 'foo'}]
    provider.solr.search = MagicMock(return_value=results)

    assert provider.get_record_metadata('oai:fcrepo:foo', 'oai_dc') is not None
    assert provider.solr.search.call_count == search_count


class NotFoundResponse:
    ok = False
    status_code = 404
    reason = 'Not Found'


def test_get_record_metadata_not_found(provider):
    provider.session.get = MagicMock(return_value=NotFoundResponse())
    with pytest.raises(OAIRepoExternalException) as e:
        provider.get_record_metadata('oai:fcrepo:foo', 'oai_dc')

    assert str(e.value) == 'Unable to retrieve resource from fcrepo'
