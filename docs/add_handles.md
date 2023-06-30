# add-handles

Handles script for oaipmh

## Purpose

This script is supposed to add the handles field to items in Fedora
that don't have it. Specifically it takes in the results from the plastron
export command, and creates a new csv file with the handles column so the items
can be updated.

## Development Environment

Same as in [README.md]

## Installation

Same as in [README.md]

### Configuration

Create a `handle_conf.yml` file with the following contents:

```yaml
# Endpoint for the handles server
# (e.g., http://localhost:3000/api/v1)
HANDLE_URL:
# The base URL for the items
# (e.g., http://fcrepo-local:8080/fcrepo/rest/)
BASE_URL:
# The public URL for where the items are in the frontend
# (e.g., https://digital.lib.umd.edu/result/id/)
PUBLIC_BASE_URL:
# The JWT authentication token generated from fcrepo
AUTH:

```

### Running

```zsh
$ add-handles -h
Usage: add-handles [OPTIONS]

Options:
  -i, --input-file FILENAME   The CSV export file to take in and add handles
                              to. Defaults to STDIN.
  -o, --output-file FILENAME  Output file for CSV file with handles. Defaults
                              to STDOUT.
  -c, --config-file FILENAME  Config file to use for interacting with UMD-
                              Handle and Fcrepo  [required]
  -V, --version               Show the version and exit.
  -h, --help                  Show this message and exit.
```

### Testing

Same as in [README.md]

[README.md]: ../README.md
