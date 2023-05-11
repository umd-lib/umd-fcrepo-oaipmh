import logging
import os
from datetime import datetime

# noinspection PyProtectedMember
from lxml.etree import _Element
from oai_repo import MetadataFormat, DataInterface, Identify, RecordHeader, Set

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000/')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
DATESTAMP_GRANULARITY = os.environ.get('DATESTAMP_GRANULARITY', 'YYYY-MM-DDThh:mm:ssZ')
EARLIEST_DATESTAMP = os.environ.get('EARLIEST_DATESTAMP')
OAI_REPOSITORY_NAME = os.environ.get('OAI_REPOSITORY_NAME')
REPORT_DELETED_RECORDS = os.environ.get('REPORT_DELETED_RECORDS', 'no')


class DataProvider(DataInterface):
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
        pass

    def get_metadata_formats(self, identifier: str | None = None) -> list[MetadataFormat]:
        pass

    def get_record_header(self, identifier: str) -> RecordHeader:
        pass

    def get_record_metadata(self, identifier: str, metadataprefix: str) -> _Element | None:
        pass

    def get_record_abouts(self, identifier: str) -> list[_Element]:
        pass

    def list_set_specs(self, identifier: str = None, cursor: int = 0) -> tuple:
        pass

    def get_set(self, setspec: str) -> Set:
        pass

    def list_identifiers(self, metadataprefix: str, filter_from: datetime = None, filter_until: datetime = None,
                         filter_set: str = None, cursor: int = 0) -> tuple:
        pass
