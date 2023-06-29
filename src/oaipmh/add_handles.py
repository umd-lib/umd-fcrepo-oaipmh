import click
import requests
import sys
import uuid
import yaml

from csv import DictReader, DictWriter
from oaipmh import __version__
from typing import TextIO


class RequestFailure(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


@click.command()
@click.option(
    '--file', '-f',
    help='The export file to take in and add handles to.',
    type=click.File(),
    required=True
)
@click.option(
    '--output', '-o',
    help='Output for the handles, will default to stdout.',
    default=sys.stdout,
    type=click.File(mode='w'),
)
@click.option(
    '--config-file', '-c',
    help='Config file to use for interacting with UMD-Handle and Fcrepo',
    type=click.File(mode='r'),
    required=True
)
@click.version_option(__version__, '--version', '-V')
@click.help_option('--help', '-h')
def main(file: TextIO, output: TextIO, config_file: TextIO):
    try:
        config = yaml.safe_load(config_file)
        reader = DictReader(file, delimiter=',')
        exports = create_handles(reader, config)

        # Write out to file or stdout
        fieldnames = reader.fieldnames + ['Handle']
        writer = DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in exports:
            writer.writerow(row)
    except Exception as e:
        print(f'{type(e).__name__}: {str(e)}', file=sys.stderr)


def create_handles(reader: DictReader, config: dict) -> list:
    exports = []
    for row in reader:
        if 'Handle' not in row or row['Handle'] is None:
            fcrepo_path = row['URI'].replace(config['BASE_URL'], '')

            # extract relpath and uuid from fcrepo path
            relpath, item_uuid = extract_from_url(fcrepo_path)

            # create url for http request
            public_url = config['PUBLIC_BASE_URL'] + item_uuid + f"?relpath={relpath}"

            # Send http Request to Umd-Handle-API to mint handle
            handle = mint_handle(config,
                                 prefix='1903.1',
                                 url=public_url,
                                 repo='fcrepo',
                                 repo_id=fcrepo_path
                                 )

            # Store handle
            row['Handle'] = handle
            exports.append(row)
        else:
            exports.append(row)

    return exports


def extract_from_url(fcrepo_path: str) -> tuple[str, str]:
    path_split = fcrepo_path.split('/')

    # Remove base, then get relpath and uuid
    relpath = '/'.join(path_split[:3])
    item_uuid = path_split[-1]
    return relpath, item_uuid


def mint_handle(config: dict, **json) -> str:
    endpoint = '/api/v1/handles'
    headers = {'Authorization': f'Bearer {config["AUTH"]}'}
    response = requests.post(config['HANDLE_URL'] + endpoint, json=json, headers=headers)

    if response.status_code != 200:
        raise RequestFailure(f"Got a {response.status_code} error code, check the configuration file.")

    handle = response.json().get('handle_url')

    return handle
