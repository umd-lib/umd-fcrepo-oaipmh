# umd-fcrepo-oaipmh

OAI-PMH Server for Fedora

## Purpose

## Development Environment

Python version: 3.11

### Installation

```bash
git clone git@github.com:umd-lib/umd-fcrepo-oaipmh.git
cd umd-fcrepo-oaipmh
pyenv install --skip-existing $(cat .python-version)
python -m venv .venv --prompt umd-fcrepo-oaipmh-py$(cat .python-version)
pip install -r requirements.txt -e .
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
flask --app oaipmh.web:app run -p 8000
```
