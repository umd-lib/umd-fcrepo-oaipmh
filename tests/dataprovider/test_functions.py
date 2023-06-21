from datetime import datetime
from unittest.mock import MagicMock

import pysolr
import pytest
from oai_repo import Set

from oaipmh.dataprovider import get_solr_date_range, get_set_spec, get_sets, get_collection_titles


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
def test_get_solr_date_range(timestamp_from, timestamp_until, expected):
    date_range = get_solr_date_range(timestamp_from, timestamp_until)
    assert date_range == expected


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
def test_get_solr_date_range_invalid(timestamp_from, timestamp_until):
    with pytest.raises(TypeError):
        get_solr_date_range(timestamp_from, timestamp_until)


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


def test_get_sets():
    titles = ['Katherine Anne Porter Correspondence', 'Punk Fanzines']
    sets = get_sets(titles)
    assert len(sets) == 2
    assert isinstance(sets[0], Set)
    assert sets[0].name == 'Katherine Anne Porter Correspondence'
    assert sets[0].spec == 'katherine_anne_porter_correspondence'
    assert isinstance(sets[1], Set)
    assert sets[1].name == 'Punk Fanzines'
    assert sets[1].spec == 'punk_fanzines'


def test_get_collection_titles():
    mock_solr = MagicMock(spec=pysolr.Solr)
    mock_solr.search = MagicMock(return_value=[{'display_title': 'Foo'}, {'display_title': 'Bar'}])
    titles = get_collection_titles(mock_solr)
    assert len(titles) == 2
    assert titles[0] == 'Foo'
    assert titles[1] == 'Bar'
