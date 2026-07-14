# NLI-WO-002 Pull Request Evidence — Review 07

Exact final head, workflow IDs, job IDs, and changed-path proof are recorded in this evidence file after the final green CI head.

## Criterion-specific evidence matrix

| Criterion | Status | Assertion | Evidence | Remaining condition |
|---|---|---|---|---|
| AC-01 | READY FOR SDA REVIEW | pg_catalog inventory generated from disposable migrated PostGIS DB: 25 tables, 237 fields, ledger included. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-02 | READY FOR SDA REVIEW | location_record remains sole canonical anchor; subject registry/crosswalks prevent second address authority. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-03 | READY FOR SDA REVIEW | administrative_code_history and name history added for mutable official codes/names. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-04 | READY FOR SDA REVIEW | operational_area lifecycle separated from administrative units. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-05 | READY FOR SDA REVIEW | object vocabularies/cardinality and fixture validation included. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-06 | READY FOR SDA REVIEW | ULID-compatible canonical ids plus legacy_crosswalk; public aliases release-gated. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-07 | READY FOR SDA REVIEW | separate lifecycle vocabularies and transition matrices generated. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-08 | READY FOR SDA REVIEW | effective/recorded intervals and current/exclusion/chain rules in target SQL/design. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-09 | READY FOR SDA REVIEW | geometry observation/version model physically validates SRID/type/current role and lineage. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-10 | READY FOR SDA REVIEW | name_record plus current official Spanish unique rule and history model. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-11 | READY FOR SDA REVIEW | source_payload_archive preserves restricted raw values beyond hashes. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-12 | READY FOR SDA REVIEW | current and target classifications included in catalog/mapping/OpenAPI fields. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-13 | READY FOR SDA REVIEW | field-to-vocabulary registry and transition graph validated. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-14 | READY FOR SDA REVIEW | target schema executed; 263 constraints and 111 indexes cataloged. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-15 | READY FOR SDA REVIEW | OpenAPI inventory generated for 105 operations with auth, request, response and status fields. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-16 | READY FOR SDA REVIEW | transformation registry covers 237 current fields with preservation/exception/validation. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-17 | READY FOR SDA REVIEW | convergence plan rebuilt by target owner/field groups with crosswalk/exception/idempotency/cutover gates. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-18 | READY FOR SDA REVIEW | machine-readable fixtures inserted: 324 rows into target schema. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-19 | READY FOR SDA REVIEW | scale plan includes workload, storage, retention, concurrency and query assumptions. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-20 | READY FOR SDA REVIEW | dependency-safe target SQL executed in disposable PostGIS schema and catalog compared to typed model. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-21 | READY FOR SDA REVIEW | ADRs 005-009 hand-authored with alternatives, security/privacy, operations, migration, failures and tests. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |
| AC-22 | READY FOR SDA REVIEW | changed-path proof excludes runtime code, executable migrations, app code and production data; PR remains draft. | Review 07 semantic-design CI exact-head run; final IDs stamped after green CI | SDA acceptance pending |

## Changed-path proof

Generated at final closeout after push; scope guard requires no `services/api/**`, `infra/migrations/**`, `apps/**`, `infra/docker/**`, `data/**`, or `.env*` changes. The only permitted non-docs change is `.github/workflows/api-ci.yml` for SDA design CI.
