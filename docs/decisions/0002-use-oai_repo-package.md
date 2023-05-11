---
ID: umd-iiif-0002
Status: Accepted
Date: 2023-05-11
Author: Peter Eichman <peichman@umd.edu>

---
# Use the `oai_repo` package for building our OAI-PMH server

## Context

We need to build a new [OAI-PMH] endpoint for sharing metadata stored in our
Fedora repository (fcrepo) with other institutions. Rather than focussing on
implementing the OAI-PMH server protocol ourselves, we would like to start 
from an existing code base. Thus, we can focus on implementing the unique 
metadata mappings for our collections. 

## Decision Drivers

* Use a language we already have experience with: Python (preferred) or Java
* Be easy to integrate into our current webapp microservice pattern of a
  small application that focuses on doing one thing well
* Be straightforward to develop and maintain

## Considered Options

1. [oai_repo](#oai_repo)
2. [pyoai](#pyoai)
3. [OAICat](#oaicat)

## Decision

Chosen option: [oai_repo](#oai_repo), because it is a modern Python solution 
with good documentation and extensibility.

## Pros and Cons of the Options

### oai_repo

[oai_repo] is a Python package developed by the Michigan State University 
Libraries, which "provides a configurable implementation of an OAI-PMH
compatible repository."

* Good, because it is focused on server implementation
* Good, because it is a modern codebase (Python 3.10+, type annotations)
* Good, because it has the most recent release date (December 2022)
* Good, because is allows simple customization of the metadata source via 
  the DataInterface class
* Good, because there is thorough documentation
* Bad, because it is technically still a "Beta" release (0.3.4)

### pyoai

[pyoai] is "a Python implementation of an “Open Archives Initiative Protocol
for Metadata Harvesting” (version 2) client and server."

* Good, because it has a relatively recent release date (March 2022)
* Bad, because its focus is on the OAI-PMH client
* Bad, because it is unclear how to use it to implement a server without 
  using the companion [MOAI] application, which has not been updated in 
  around ten years
* Bad, because it is written in a non-Pythonic style that is dissonant 
  with modern Python coding practices 

### OAICat

[OAICat] is "a Java Servlet web application [originally developed by OCLC]
providing a repository framework that conforms to the Open Archives
Initiative Protocol for Metadata Harvesting (OAI-PMH) v2.0."

* Good, because it is focused on server implementation
* Good, because we are already using it with Fedora 2
* Bad, because it is an old codebase that is no longer actively maintained
* Bad, because off the shelf it is written in Java 1.6, which current 
  build tools no longer support

[OAI-PMH]: http://www.openarchives.org/OAI/openarchivesprotocol.html
[oai_repo]: https://pypi.org/project/oai-repo/
[pyoai]: https://pypi.org/project/pyoai/
[OAICat]: https://github.com/openpreserve/oaicat
