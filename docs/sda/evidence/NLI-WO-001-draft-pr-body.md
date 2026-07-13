# Work-order implementation

**Work order:** `docs/sda/work-orders/NLI-WO-001-controlled-database-lifecycle.md`  
**Implementation plan:** `docs/sda/implementation-plans/NLI-WO-001-controlled-database-lifecycle.md`  
**Head commit reviewed for this evidence:** `edd2ce4`

> For SDA-governed work, the complete evidence structure from `docs/sda/templates/pull-request-evidence.md` is included in `docs/sda/evidence/NLI-WO-001-pull-request-evidence.md`. This PR does not claim SDA acceptance or national production approval.

## Outcome

Implements controlled database/reference-data lifecycle for NLI-WO-001:

- API startup no longer creates/changes schema or seeds data.
- Ordered migrations now create an empty PostGIS database through a checksum ledger.
- Existing migrations `001–006` remain byte-for-byte checksum-preserved.
- Existing pilot DB transition is explicit and data-preserving.
- Governed reference data and non-production fixtures are loaded by separate commands.
- API CI now runs a real PostGIS lifecycle rehearsal.
- Restore drill validates migration ledger and PostGIS after restore.

## Acceptance criteria

| Criterion | Status | Implementation | Evidence/test | Residual condition |
|---|---|---|---|---|
| AC-01 | PASS | Empty DB creation via `000` + ordered runner | Empty PostGIS proof: ledger `7`, PostGIS `1` | SDA review of generated schema bridge |
| AC-02 | PASS | Ledger includes version/filename/checksum/context | `migrate.py apply/status` | None known |
| AC-03 | PASS | Checksum mismatch fails closed | Source/status controls | Add deeper negative DB test if requested |
| AC-04 | PASS | Transactions + advisory lock | Source and empty DB proof | Optional future concurrency stress |
| AC-05 | PASS | `transition-pilot` for existing DB | Before/after counts identical; live pilot transitioned | Drift outside checked tables fails closed |
| AC-06 | PASS | API lifespan no longer calls `init_db()` | Startup invariance test | None |
| AC-07 | PASS | Startup does not auto-apply pending migrations | Read-only status path | Expand pending DB integration if requested |
| AC-08 | PASS | Explicit idempotent reference loader | First load `74`, second `0` | Source authority signoff still institutional |
| AC-09 | PASS | Fixtures explicit and production-refusing | Prod refusal + allowed load/cleanup | Fixture package can expand later |
| AC-10 | PASS | Credential preservation/default protection | Backend tests + loader SQL | None known |
| AC-11 | PASS | Local bootstrap script added | Shell syntax + lifecycle proof | Depends on private env values |
| AC-12 | PASS | CI PostGIS service and rehearsal | Workflow YAML ok; local equivalent passed | Remote CI awaits PR run |
| AC-13 | PASS | Restore drill validates ledger/PostGIS | Restore drill passed | Backup artifact local/ignored |
| AC-14 | PASS | README/env/plan/evidence updated | Docs included | Runbook polish after SDA review |
| AC-15 | PASS | Existing gates preserved | Backend `175 passed`; frontend `test:ci` passed | Existing httpx warnings remain |

## Required declarations

- [x] I read the repository `AGENTS.md`, active work order, referenced ADRs, and standards.
- [x] Every acceptance criterion is represented truthfully.
- [x] Database, API, identity/security, GIS, audit/evidence, workflow, operations, and documentation effects are covered or marked not applicable with a reason.
- [x] Required tests and generated contracts are current.
- [x] No control was disabled merely to pass CI.
- [x] No secrets or production personal/evidence data were committed.
- [x] RFIs, deviations, limitations, and residual risks are linked.
- [x] This pull request does not claim SDA acceptance, official publication authority, or national-production approval.

## Evidence

See full evidence file:

`docs/sda/evidence/NLI-WO-001-pull-request-evidence.md`
