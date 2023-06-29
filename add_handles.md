# add_handles

Handles script for oaipmh

## Purpose

This script is supposed to add the handles field to items in Fedora
that don't have it. Specifically it takes in the results from the plastron
export command, and creates a new csv file with the handles column so the items
can be updated.

## Developtment Environment

Same as in [README.md]

## Installation

Same as in [README.md]

### Configuration

Create a `handle_conf.yml` file with the following contents:

```yml
# Domain for the handles server
HANDLE_URL:
# The base URL for the items
# (ex: http://fcrepo-local:8080/fcrepo/rest/)
BASE_URL:
# The public URL for where the items are in the frontend
# (ex: https://digital.lib.umd.edu/result/id/)
PUBLIC_BASE_URL:
# The JWT authenatication token generated from fcrepo
AUTH:

```

### Running

```zsh
❯ add_handles -h
Usage: add_handles [OPTIONS]

Options:
  -f, --file FILENAME         The export file to take in and add handles to.
                              [required]
  -o, --output FILENAME       Output for the handles, will default to stdout.
  -c, --config-file FILENAME  Config file to use for interacting with UMD-
                              Handle and Fcrepo  [required]
  -V, --version               Show the version and exit.
  -h, --help                  Show this message and exit.
```

### Testing

Same as in [README.md]

[README.md]: README.md
