import os
from http import HTTPStatus
from typing import Any, Optional, TextIO

import pysolr
import yaml
from flask import Flask, request, abort, redirect, url_for
from oai_repo import OAIRepository, OAIRepoInternalException, OAIRepoExternalException
from oai_repo.response import OAIResponse

from oaipmh import __version__
from oaipmh.dataprovider import DataProvider
from oaipmh.solr import Index, DEFAULT_SOLR_CONFIG


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


def get_config(config_source: Optional[str | TextIO] = None) -> dict[str, Any]:
    if config_source is None:
        return DEFAULT_SOLR_CONFIG
    if isinstance(config_source, str):
        with open(config_source) as fh:
            return yaml.safe_load(fh)
    if config_source:
        return yaml.safe_load(config_source)


def create_app(solr_config_file) -> Flask:
    app = Flask(__name__)
    app.logger.info(f'Starting umd-fcrepo-oaipmh/{__version__}')
    index = Index(
        config=get_config(solr_config_file),
        solr_client=pysolr.Solr(os.environ['SOLR_URL']),
    )
    data_provider = DataProvider(index=index)
    app.logger.debug(f'Initialized the data provider: {data_provider.get_identify()}')

    @app.route('/')
    def root():
        return redirect(url_for('home'))

    @app.route('/oai')
    def home():
        identify_url = data_provider.base_url + '?verb=Identify'
        return f"""
        <h1>OAI-PMH Service for Fedora: {data_provider.oai_repository_name}</h1>
        <ul>
          <li>Version: umd-fcrepo-oaipmh/{__version__}</li>
          <li>Endpoint: {data_provider.base_url}</li>
          <li>Identify: <a href="{identify_url}">{identify_url}</a></li>
        </ul>
        <p>See the <a href="http://www.openarchives.org/OAI/openarchivesprotocol.html" target="_blank">OAI-PMH
        Protocol 2.0 Specification</a> for information about how to use this service.</p>
        """

    @app.route('/oai/api')
    def endpoint():
        try:
            repo = OAIRepository(data_provider)
            response = repo.process(request.args.copy())
        except OAIRepoExternalException as e:
            # An API call timed out or returned a non-200 HTTP code.
            # Log the failure and abort with server HTTP 503.
            app.logger.error(f'Upstream error: {e}')
            abort(HTTPStatus.SERVICE_UNAVAILABLE, str(e))
        except OAIRepoInternalException as e:
            # There is a fault in how the DataInterface was implemented.
            # Log the failure and abort with server HTTP 500.
            app.logger.error(f'Internal error: {e}')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            return bytes(response).decode(), status(response), {'Content-Type': 'application/xml'}

    return app
