from datetime import datetime
from unittest.mock import MagicMock

import pytest

from oaipmh.solr import solr_date_range, Index, DEFAULT_SOLR_CONFIG


@pytest.mark.parametrize(
    ('timestamp_from', 'timestamp_until'),
    [
        ('not a date', 'also not'),
        (datetime.fromisoformat('2023-06-16'), 'not a date'),
        ('not a date', datetime.fromisoformat('2023-06-16')),
        ('not a date', None),
        (None, 'not a date'),
    ]
)
def test_solr_date_range_invalid(timestamp_from, timestamp_until):
    with pytest.raises(TypeError):
        solr_date_range(timestamp_from, timestamp_until)


@pytest.mark.parametrize(
    ('timestamp_from', 'timestamp_until', 'expected'),
    [
        (None, None, '[* TO *]'),
        (datetime.fromisoformat('2023-06-15'), None, '[2023-06-15T00:00:00Z TO *]'),
        (None, datetime.fromisoformat('2023-06-15'), '[* TO 2023-06-15T00:00:00Z]'),
        (
            datetime.fromisoformat('2023-01-31'),
            datetime.fromisoformat('2023-06-15'),
            '[2023-01-31T00:00:00Z TO 2023-06-15T00:00:00Z]',
        ),
    ]
)
def test_solr_date_range(timestamp_from, timestamp_until, expected):
    date_range = solr_date_range(timestamp_from, timestamp_until)
    assert date_range == expected


def test_index_with_solr_client(mock_solr_client):
    index = Index(config=DEFAULT_SOLR_CONFIG, solr_client=mock_solr_client)
    assert index.solr is mock_solr_client


def test_index_accessors(mock_solr_client):
    index = Index(config=DEFAULT_SOLR_CONFIG, solr_client=mock_solr_client)
    assert index.base_query == DEFAULT_SOLR_CONFIG['base_query']
    assert index.uri_field == DEFAULT_SOLR_CONFIG['uri_field']
    assert index.handle_field == DEFAULT_SOLR_CONFIG['handle_field']
    assert index.last_modified_field == DEFAULT_SOLR_CONFIG['last_modified_field']
    assert index.auto_set_config is None
    assert len(index.get_sets()) == 0


def test_auto_create_sets(mock_solr_client):
    mock_solr_client.search = MagicMock(
        return_value=[{'display_title': 'Foo Collection'}, {'display_title': 'Bar Stuff'}],
    )
    index = Index(
        config={
            **DEFAULT_SOLR_CONFIG,
            'auto_create_sets': True,
            'auto_set': {
                'query': 'component:Collection',
                'name_field': 'display_title',
                'name_query_field': 'collection_title_facet',
            }
        },
        solr_client=mock_solr_client,
    )
    sets = index.get_sets()
    assert len(sets) == 2
    assert sets.keys() == {'foo_collection', 'bar_stuff'}


def test_get_set(mock_solr_client):
    index = Index(
        config={**DEFAULT_SOLR_CONFIG, 'sets': [{'spec': 'foo', 'name': 'Foo!', 'filter': 'title:Foo'}]},
        solr_client=mock_solr_client,
    )
    set_conf = index.get_set('foo')
    assert set_conf['spec'] == 'foo'
    assert set_conf['name'] == 'Foo!'
    assert set_conf['filter'] == 'title:Foo'
