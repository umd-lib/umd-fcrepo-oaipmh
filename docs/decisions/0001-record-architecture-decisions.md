---
ID: umd-fcrepo-oaipmh-0001
Status: Accepted
Date: 2023-05-11

---
# Record architecture decisions

## Context

Maintaining a record of key decisions made in the project seems worthwhile.

The general idea is to record important decisions that affect the application
as a whole, for the use of future developers and maintainers.

## Decision

See <http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions>
for general motivation and format for architecture decision records (ADRs).

- Use Markdown
- Include metadata in a YAML prologue to the ADR document:

  ```yaml
  ---
  ID: {project name}-{nnnn}
  Status: {Proposed|Accepted|Rejected|Superseded}
  Date: {last modified}
  
  ---
  ```
- Include a blank line at the end of the YAML prologue so non-YAML-aware
  Markdown processors will simply render the metadata block on a single
  line between two horizontal rules.

Use the [adr-template.md](adr-template.md) as a template for new ADR
documents.

## Consequences

Recording architecture decisions should reduce the learning curve for new
developers and maintainers coming on the project.

There is a maintenance burden in creating ADRs, but it is expected that this
will be outweighed by the benefits.
