# Work-order implementation — Review 01 remediation

**Work order:** `docs/sda/work-orders/NLI-WO-001-controlled-database-lifecycle.md`  
**Implementation plan:** `docs/sda/implementation-plans/NLI-WO-001-controlled-database-lifecycle.md`  
**Review addressed:** `docs/sda/reviews/NLI-WO-001-review-01.md`  
**Remediation code commit:** `c2322a0`  
**Final implementation head verified remotely:** `555514347b9a243c5a1691a9a38ac1695edd9fff`  

> PR #4 remains draft. This does not claim SDA acceptance, official publication authority, or national-production approval.

## Outcome

Resolved Review 01 findings F01–F09 for controlled database lifecycle:

- Removed executable runtime schema creation/seed path.
- Added real PostgreSQL/PostGIS integration tests for checksum/filename drift, failed migrations, concurrent execution, startup invariance, pending migration readiness, credential/session preservation, existing-pilot transition, reference-data drift, and fixture ownership/cleanup.
- Reference-data and fixture commands now fail clearly when migrations are missing and do not create tables.
- Fixture cleanup is ownership-safe and collision-safe.
- Existing-pilot transition validates structure and holds one advisory lock through validation/application.
- `000` is schema-only; auth-token backfill is isolated in `007_lifecycle_metadata_hardening.sql`.
- Local bootstrap was fixed and proven from an isolated clean Compose project through API health.
- API CI is split into API tests plus dedicated migration lifecycle/dump-restore proof.

## Acceptance criteria

Criteria are marked `READY FOR SDA REVIEW`, not SDA-accepted `PASS`.

| Criterion | Status | Evidence |
|---|---|---|
| AC-01 | READY FOR SDA REVIEW | Empty PostGIS DB integration test; ledger `000–007`; PostGIS asserted. |
| AC-02 | READY FOR SDA REVIEW | Ledger field assertions and filename drift detection. |
| AC-03 | READY FOR SDA REVIEW | DB-backed checksum drift test. |
| AC-04 | READY FOR SDA REVIEW | Failed migration rollback test; concurrent runner test; transition lock fix. |
| AC-05 | READY FOR SDA REVIEW | Existing-pilot transition before/after invariant and drift rejection test. |
| AC-06 | READY FOR SDA REVIEW | Real API startup schema/row fingerprint invariance test. |
| AC-07 | READY FOR SDA REVIEW | Pending migration readiness/no-auto-apply test. |
| AC-08 | READY FOR SDA REVIEW | Missing-migration, idempotency, status, history, and drift tests. |
| AC-09 | READY FOR SDA REVIEW | Fixture collision/ownership/cleanup tests. |
| AC-10 | READY FOR SDA REVIEW | Credential/session preservation test. |
| AC-11 | READY FOR SDA REVIEW | Isolated clean bootstrap proof and API health check. |
| AC-12 | READY FOR SDA REVIEW | API CI PostGIS env + dedicated lifecycle job; remote result linked below. |
| AC-13 | READY FOR SDA REVIEW | Lifecycle CI includes dump/restore ledger/PostGIS proof; remote result linked below. |
| AC-14 | READY FOR SDA REVIEW | Bootstrap/docs/evidence updated. |
| AC-15 | READY FOR SDA REVIEW | Local backend/frontend gates green; remote result linked below. |

## Local verification

| Check | Result |
|---|---|
| Backend full suite with PostGIS env | `187 passed, 5 warnings` |
| Lifecycle integration suite | `11 passed` |
| Frontend API type generation | 105 operations; no diff |
| Frontend `test:ci` | passed |
| YAML / Python / shell syntax | passed |
| Isolated clean bootstrap | `bootstrap_local: ok`; `/api/v1/health` returned `status: ok` |

## Remote verification

Updated after push:

| Workflow/check | Final result | URL |
|---|---|---|
| API CI | `success` | https://github.com/bechirobob/eg-addressing/actions/runs/29278041290 |
| Frontend CI | `success` | https://github.com/bechirobob/eg-addressing/actions/runs/29278041293 |

## Review resolution log

See `docs/sda/reviews/NLI-WO-001-review-01.md` section 9 and full evidence at:

`docs/sda/evidence/NLI-WO-001-pull-request-evidence.md`

## Required declarations

- [x] I read the repository `AGENTS.md`, active work order, referenced ADRs, standards, and Review 01.
- [x] Every Review 01 finding F01–F09 has a response and evidence.
- [x] Database, API, identity/security, GIS, audit/evidence, workflow, operations, and documentation effects are covered or marked with a remaining condition.
- [x] Required local tests and generated contracts are current.
- [x] No control was disabled merely to pass CI.
- [x] No secrets or production personal/evidence data were committed.
- [x] This pull request remains draft and does not claim SDA acceptance, official publication authority, or national-production approval.
