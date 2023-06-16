import pytest
from oai_repo import OAIRepoInternalException

from oaipmh.transformers import Transformer


def test_bad_transformer(datadir):
    with pytest.raises(OAIRepoInternalException):
        Transformer(datadir / 'no_xsi-schemaLocation.xsl')
