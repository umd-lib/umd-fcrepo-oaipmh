import os
from http import HTTPStatus

import pysolr
from flask import Flask, request, abort
from oai_repo import OAIRepository, OAIRepoInternalException, OAIRepoExternalException
from oai_repo.response import OAIResponse

from oaipmh.dataprovider import DataProvider

app = Flask(__name__)

SOLR_URL = os.environ.get('SOLR_URL')


def status(response: OAIResponse) -> int:
    """Get the HTTP status code to return with the given OAI response."""

    # the OAIResponse casts to boolean "False" on error
    if response:
        return HTTPStatus.OK
    else:
        error = response.xpath('/OAI-PMH/error')[0]
        if error.get('code') in {'noRecordsMatch', 'idDoesNotExist'}:
            return HTTPStatus.NOT_FOUND
        else:
            return HTTPStatus.BAD_REQUEST


@app.route('/oai')
def endpoint():
    try:
        repo = OAIRepository(DataProvider(solr_client=pysolr.Solr(SOLR_URL)))
        response = repo.process(request.args.copy())
    except OAIRepoExternalException as e:
        # An API call timed out or returned a non-200 HTTP code.
        # Log the failure and abort with server HTTP 503.
        app.logger.error(f'Upstream error: {e}')
        abort(HTTPStatus.SERVICE_UNAVAILABLE)
    except OAIRepoInternalException as e:
        # There is a fault in how the DataInterface was implemented.
        # Log the failure and abort with server HTTP 500.
        app.logger.error(f'Internal error: {e}')
        abort(HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        return bytes(response).decode(), status(response), {'Content-Type': 'application/xml'}
