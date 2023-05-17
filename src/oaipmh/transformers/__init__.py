from os.path import dirname
from pathlib import Path
from typing import Mapping

from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import _Element
from oai_repo import OAIRepoInternalException, MetadataFormat


def load_transformers() -> Mapping[str, 'Transformer']:
    xsl_dir = Path(dirname(__file__))
    return {
        'rdf': Transformer(xsl_dir / 'rdf.xsl'),
        'oai_dc': Transformer(xsl_dir / 'oai_dc.xsl'),
    }


class Transformer:
    def __init__(self, xsl_filepath: Path, prefix: str = None):
        self.prefix = xsl_filepath.stem if prefix is None else prefix

        with xsl_filepath.open() as fh:
            xslt_doc = etree.parse(fh)
        schema_location = xslt_doc.xpath(
            '@xsi:schemaLocation', namespaces={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
        )
        if not schema_location:
            raise OAIRepoInternalException(f'No @xsi:schemaLocation in {xsl_filepath}')
        self.namespace, self.schema = schema_location[0].split(maxsplit=1)
        self.xslt = etree.XSLT(xslt_doc)

    def __call__(self, *args, **kwargs) -> _Element:
        return self.xslt(*args, **kwargs).getroot()

    @property
    def metadata_format(self) -> MetadataFormat:
        return MetadataFormat(
            metadata_prefix=self.prefix,
            metadata_namespace=self.namespace,
            schema=self.schema,
        )
