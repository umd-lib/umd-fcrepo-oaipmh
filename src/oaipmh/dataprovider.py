import logging
import os
import urllib.parse
from collections.abc import Mapping
from datetime import datetime
from hashlib import md5
from typing import Optional

import pysolr
# noinspection PyProtectedMember
from lxml.etree import _Element
from oai_repo import MetadataFormat, DataInterface, Identify, RecordHeader, Set, OAIRepoExternalException
from oai_repo.helpers import datestamp_long, granularity_format

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000/')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
DATESTAMP_GRANULARITY = os.environ.get('DATESTAMP_GRANULARITY', 'YYYY-MM-DDThh:mm:ssZ')
EARLIEST_DATESTAMP = os.environ.get('EARLIEST_DATESTAMP')
PAGE_SIZE = os.environ.get('PAGE_SIZE', 25)
OAI_REPOSITORY_NAME = os.environ.get('OAI_REPOSITORY_NAME')
OAI_NAMESPACE_IDENTIFIER = os.environ.get('OAI_NAMESPACE_IDENTIFIER')
REPORT_DELETED_RECORDS = os.environ.get('REPORT_DELETED_RECORDS', 'no')

METADATA_FORMATS = {
    'oai_dc': MetadataFormat(
        metadata_prefix='oai_dc',
        schema='http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
        metadata_namespace='http://www.openarchives.org/OAI/2.0/oai_dc/',
    ),
    'rdf': MetadataFormat(
        metadata_prefix='rdf',
        schema='http://www.openarchives.org/OAI/2.0/rdf.xsd',
        metadata_namespace='http://www.openarchives.org/OAI/2.0/rdf/',
    ),
}


def oai_identifier(local_identifier):
    return f'oai:{OAI_NAMESPACE_IDENTIFIER}:{urllib.parse.quote(local_identifier)}'


class DataProvider(DataInterface):
    limit = PAGE_SIZE

    def __init__(self, solr_url: str):
        self.solr_url = solr_url
        self.solr = pysolr.Solr(self.solr_url)
        self.solr_results = None

    def get_identify(self) -> Identify:
        return Identify(
            base_url=BASE_URL,
            admin_email=[ADMIN_EMAIL],
            repository_name=OAI_REPOSITORY_NAME,
            earliest_datestamp=EARLIEST_DATESTAMP,
            deleted_record=REPORT_DELETED_RECORDS,
            granularity=DATESTAMP_GRANULARITY,
        )

    def is_valid_identifier(self, identifier: str) -> bool:
        return identifier.startswith(f'oai:{OAI_NAMESPACE_IDENTIFIER}:')

    def get_metadata_formats(self, identifier: str | None = None) -> list[MetadataFormat]:
        return list(METADATA_FORMATS.values())

    def get_record_header(self, identifier: str) -> RecordHeader:
        return RecordHeader(
            identifier=identifier,
            datestamp=granularity_format(
                DATESTAMP_GRANULARITY,
                datetime.fromisoformat(self.solr_results[identifier]['last_modified']),
            ),
            # TODO: include setSpec elements
        )

    def get_record_metadata(self, identifier: str, metadataprefix: str) -> _Element | None:
        pass

    def get_record_abouts(self, identifier: str) -> list[_Element]:
        pass

    def list_set_specs(self, identifier: str = None, cursor: int = 0) -> tuple:
        pass

    def get_set(self, setspec: str) -> Set:
        pass

    def list_identifiers(
            self,
            metadataprefix: str,
            filter_from: datetime = None,
            filter_until: datetime = None,
            filter_set: str = None,
            cursor: int = 0
    ) -> tuple:
        logger.debug(
            'list_identifiers('
            f'metadataprefix={metadataprefix}, '
            f'filter_from={filter_from}, '
            f'filter_until={filter_until}, '
            f'filter_set={filter_set}, '
            f'cursor={cursor})'
        )
        filter_query = 'component:*'
        if filter_from or filter_until:
            datetime_range = get_solr_date_range(filter_from, filter_until)
            filter_query += f' AND last_modified:{datetime_range}'
        logger.debug(f'Solr fq = "{filter_query}"')
        try:
            results = self.solr.search(q='*:*', fq=filter_query, start=cursor, rows=self.limit)
        except pysolr.SolrError as e:
            raise OAIRepoExternalException('Unable to connect to Solr') from e
        self.solr_results = {oai_identifier(get_local_identifier(doc)): doc for doc in results}
        identifiers = list(self.solr_results.keys())
        return identifiers, results.hits, None


# XXX: use the MD5 of the URI as a stopgap until handles are implemented for fcrepo
def get_local_identifier(doc: Mapping) -> str:
    return md5(doc['id'].encode()).hexdigest()


def get_solr_date_range(timestamp_from: Optional[datetime], timestamp_until: Optional[datetime]) -> str:
    datestamp_from = datestamp_long(timestamp_from) if timestamp_from else '*'
    datestamp_until = datestamp_long(timestamp_until) if timestamp_until else '*'
    return f'[{datestamp_from} TO {datestamp_until}]'
