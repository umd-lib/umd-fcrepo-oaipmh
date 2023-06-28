import click
import requests
import sys
import uuid
import yaml

from csv import DictReader, DictWriter
from oaipmh import __version__
from typing import TextIO


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
    config = yaml.safe_load(config_file)
    reader = DictReader(file, delimiter=',')
    exports = create_handles(reader, config)

    # Write out to file or stdout
    fieldnames = reader.fieldnames + ['Handle']
    writer = DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in exports:
        writer.writerow(row)


def create_handles(reader: DictReader, config: dict) -> list:
    exports = []
    for row in reader:
        if 'Handle' not in row or row['Handle'] is None:
            # extract relpath and uuid from fcrepo URI
            relpath, item_uuid = extract_from_url(row['URI'], config)

            # create url for http request
            public_url = config['PUBLIC_BASE_URL'] + item_uuid + f"?relpath={relpath}"

            # Send http Request to Umd-Handle-API to mint handle
            handle = mint_handle(public_url, config)

            # Store handle
            row['Handle'] = handle
            exports.append(row)


def extract_from_url(fcrepo_url: str, config: dict) -> tuple[str, str]:
    base_removed = fcrepo_url.replace(config['BASE_URL'], '')
    url_split = base_removed.split('/')

    # Remove base, then get relpath and uuid
    relpath = url_split[:3]
    item_uuid = url_split[-1]
    return relpath, item_uuid


def mint_handle(public_url: str, config: dict) -> str:
    endpoint = '/handle'

    results = requests.post(config['HANDLE_URL'] + endpoint)
    return public_url
