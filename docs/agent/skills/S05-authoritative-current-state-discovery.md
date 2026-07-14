# S05 — Authoritative Current-State Discovery

## Invoke when

- inventorying database schema, routes, contracts, roles, permissions, workflows, or operational controls;
- creating a baseline or current-to-target map;
- a review identifies missing current fields, routes, writers, or readers;
- generated documentation may be stale.

## Required inputs

- accepted migrations and migration runner;
- application source and generated contracts;
- current environment templates and scripts;
- work-order scope;
- disposable PostgreSQL/PostGIS environment;
- current OpenAPI generation path.

## Procedure

### 1. Discover database state from a real database

- create a disposable PostgreSQL/PostGIS database;
- apply accepted migrations through the controlled runner;
- verify ledger filenames and checksums;
- query `pg_catalog`, `information_schema`, PostGIS metadata, indexes, constraints, triggers, functions, extensions, and comments;
- include migration-ledger and operational-control tables;
- record the exact migration head used.

Do not treat migration-text parsing as the authoritative catalog.

### 2. Discover API contracts from the running application

- generate the actual OpenAPI document;
- inventory method, path, operation ID, parameters, request bodies, response schemas, status/error responses, and deprecation metadata;
- capture dynamic response shapes through explicit models, source analysis, or executable contract tests when OpenAPI is incomplete.

### 3. Discover authorization precisely

For every operation identify:

- exact handler;
- auth mode;
- all allowed roles;
- institution/territorial scope where implemented;
- optional authentication;
- session-required behavior;
- delegated policy helpers;
- sensitive-field projection.

Key policy by **HTTP method + path + operation ID/handler**. Do not key only by path.

### 4. Discover writers and readers

Search and verify:

- API writes and queries;
- scripts and maintenance tools;
- imports, exports, reports, workers, and jobs;
- frontend consumers;
- generated clients/types;
- backup/restore and audit scripts.

### 5. Discover actual value domains

For each status, type, source, or code field:

- inspect validation models and UI values;
- inspect database distinct values in approved non-production data where permitted;
- inspect fixtures/imports;
- identify undocumented or conflicting values.

### 6. Produce source-backed inventory

Each field or operation should record:

- physical type and constraints;
- semantic meaning;
- writers/readers;
- authority/source;
- classification;
- lifecycle meaning;
- public/protected projections;
- retention/archival behavior;
- target disposition if part of convergence.

## Outputs

- catalog-derived database inventory;
- OpenAPI operation and field inventory;
- independently reviewed expected authorization registry;
- writer-reader-source register;
- current controlled-value register;
- unknowns/RFIs.

## Stop or RFI conditions

Stop when:

- the disposable schema cannot be created through accepted migrations;
- runtime schema differs from accepted migration authority;
- OpenAPI omits a dynamic successful response needed for compatibility analysis;
- route policy cannot be derived unambiguously;
- current values conflict with target vocabulary;
- sensitive current data would be required without approved access.

## Evidence gate

Discovery is complete only when:

- database catalog comes from executed migrations;
- all relevant OpenAPI operations are inventoried;
- expected policy is maintained independently from observed policy;
- all roles are captured, not only the first argument;
- dynamic response gaps are explicitly resolved or marked blocking;
- inventory generation is reproducible and deterministic.

## Anti-patterns

- Regex-parsing migrations and calling the result the current schema.
- Classifying routes from path keywords.
- Scanning a fixed number of lines after a handler.
- Generating the expected policy registry from observed output.
- Assigning classifications solely from field-name substrings.
- Omitting operational scripts and migration-ledger fields.
