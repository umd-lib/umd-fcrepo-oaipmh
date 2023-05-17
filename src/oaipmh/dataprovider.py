import logging
import os
import urllib.parse
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional

import pysolr
from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import _Element
from oai_repo import MetadataFormat, DataInterface, Identify, RecordHeader, Set, OAIRepoExternalException
from oai_repo.exceptions import OAIErrorCannotDisseminateFormat
from oai_repo.helpers import datestamp_long, granularity_format
from requests import Session
from requests_jwtauth import HTTPBearerAuth

from oaipmh.transformers import load_transformers

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


class OAIIdentifier:
    @classmethod
    def parse(cls, identifier: str):
        if not identifier.startswith('oai:'):
            raise ValueError('OAI identifier must start with "oai:"')
        _, namespace_identifier, local_identifier = identifier.split(':', maxsplit=2)
        return cls(
            namespace_identifier=namespace_identifier,
            local_identifier=urllib.parse.unquote(local_identifier)
        )

    def __init__(self, namespace_identifier: str, local_identifier: str):
        self.namespace_identifier = namespace_identifier
        self.local_identifier = local_identifier

    def __str__(self):
        return f'oai:{self.namespace_identifier}:{urllib.parse.quote(self.local_identifier)}'


class DataProvider(DataInterface):
    limit = PAGE_SIZE

    def __init__(self, solr_url: str):
        self.solr_url = solr_url
        self.solr = pysolr.Solr(self.solr_url)
        self.solr_results = None
        self.session = Session()
        self.session.auth = HTTPBearerAuth(os.environ.get('FCREPO_JWT_TOKEN'))
        self._transformers = load_transformers()

    def transform(self, target_format: str, xml_root: _Element) -> _Element:
        try:
            transform = self._transformers[target_format]
        except KeyError:
            raise OAIErrorCannotDisseminateFormat
        return transform(xml_root)

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
        return [transformer.metadata_format for transformer in self._transformers.values()]

    def get_record_header(self, identifier: str) -> RecordHeader:
        if self.solr_results is not None:
            last_modified = datetime.fromisoformat(self.solr_results[identifier]['last_modified'])
        else:
            response = self.session.head(OAIIdentifier.parse(identifier).local_identifier)
            last_modified = parsedate_to_datetime(response.headers['Last-Modified'])
        return RecordHeader(
            identifier=identifier,
            datestamp=granularity_format(DATESTAMP_GRANULARITY, last_modified),
            # TODO: include setSpec elements
        )

    def get_record_metadata(self, identifier: str, metadataprefix: str) -> _Element | None:
        oai_id = OAIIdentifier.parse(identifier)
        uri = oai_id.local_identifier
        response = self.session.get(uri, headers={'Accept': 'application/rdf+xml'})
        rdf_xml = etree.fromstring(response.text)
        return self.transform(metadataprefix, rdf_xml)

    def get_record_abouts(self, identifier: str) -> list[_Element]:
        return []

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
        filter_query = 'component:* NOT component:Page NOT component:Article'
        if filter_from or filter_until:
            datetime_range = get_solr_date_range(filter_from, filter_until)
            filter_query += f' AND last_modified:{datetime_range}'
        logger.debug(f'Solr fq = "{filter_query}"')
        try:
            results = self.solr.search(q='*:*', fq=filter_query, start=cursor, rows=self.limit)
        except pysolr.SolrError as e:
            raise OAIRepoExternalException('Unable to connect to Solr') from e
        self.solr_results = {str(get_oai_identifier(doc['id'])): doc for doc in results}
        identifiers = list(self.solr_results.keys())
        return identifiers, results.hits, None


# XXX: use the URI as a stopgap until handles are implemented for fcrepo
def get_oai_identifier(local_identifier: str) -> OAIIdentifier:
    return OAIIdentifier(namespace_identifier=OAI_NAMESPACE_IDENTIFIER, local_identifier=local_identifier)


def get_solr_date_range(timestamp_from: Optional[datetime], timestamp_until: Optional[datetime]) -> str:
    datestamp_from = datestamp_long(timestamp_from) if timestamp_from else '*'
    datestamp_until = datestamp_long(timestamp_until) if timestamp_until else '*'
    return f'[{datestamp_from} TO {datestamp_until}]'
