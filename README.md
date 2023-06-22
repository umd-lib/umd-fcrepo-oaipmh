# umd-fcrepo-oaipmh

OAI-PMH Server for Fedora

## Purpose

This is an [OAI-PMH] server for publishing metadata records from a Fedora 
repository. It uses a Solr index for general queries, and connects 
directly to Fedora to retrieve the full metadata record for an item.

## Development Environment

Python version: 3.11

### Installation

```bash
git clone git@github.com:umd-lib/umd-fcrepo-oaipmh.git
cd umd-fcrepo-oaipmh
pyenv install --skip-existing $(cat .python-version)
python -m venv .venv --prompt umd-fcrepo-oaipmh-py$(cat .python-version)
pip install -r test.requirements.txt -e .
```

### Configuration

Create a `.env` file with the following contents:

```bash
# OAI-PMH repository administrator email address
ADMIN_EMAIL=...
# domain name for the target Fedora repo
OAI_NAMESPACE_IDENTIFIER=...
# OAI-PMH repository name
OAI_REPOSITORY_NAME=...
# earliest datestamp of items in this repository
EARLIEST_DATESTAMP=2014-01-01T00:00:00Z
# JWT bearer token for accessing the Fedora repository
FCREPO_JWT_TOKEN=...
# enable debugging and hot reloading when run via "flask run"
FLASK_DEBUG=1
```

### Running

To run the application in debug mode, with hot code reloading:

```bash
flask --app oaipmh.web:app run
```

The application will be available at <http://localhost:5000/>

To change the port, add `-p {port number}` to the `flask` command:

```bash
# for example, to run on port 8000
flask --app oaipmh.web:create_app run -p 8000
```

### Testing

This project uses the [pytest] testing framework. To run the full
[test suite](tests):

```bash
pytest
```

To run the test suite with coverage information from [pytest-cov]:

```bash
pytest --cov src --cov-report term-missing
```

This project also uses [pycodestyle] as a style checker and linter:

```bash
pycodestyle src
```

Configuration of pycodestyle is found in the [tox.ini](tox.ini) file.

[OAI-PMH]: https://www.openarchives.org/pmh/
[pytest]: https://docs.pytest.org/en/7.3.x/
[pytest-cov]: https://pypi.org/project/pytest-cov/
[pycodestyle]: https://pycodestyle.pycqa.org/en/latest/
