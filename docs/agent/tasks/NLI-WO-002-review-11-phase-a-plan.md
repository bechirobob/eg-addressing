# NLI-WO-002 Review 11 Phase A Plan

## Authority header

| Item | Value |
|---|---|
| Work order | `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md` |
| Active PR | `#7 — nli/wo-002-canonical-location-model` |
| Required starting head | `e577cb99eae67ab6705abbce53fe636b592ebada` |
| Reviewed checkpoint | `4c755589441c9253563510060e931e2b2492d07c` |
| Reviewer-owned checkpoint/current PR head | `e577cb99eae67ab6705abbce53fe636b592ebada` |
| Latest authorization | `APPROVED WITH CONDITIONS — BOUNDED HARNESS PHASE A IMPLEMENTATION AUTHORIZED` |
| NLI-WO-002 status | `REWORK REQUIRED` |
| NLI-WO-002B status | `UNAUTHORIZED` |

## Scope

Implement **Phase A only**:

1. Harness topology foundation.
2. Stable independent fixture authority directories.
3. Authoritative F02 complete-record transforms against `canonical_target`.
4. Evidence and S16 self-audit for Phase A.
5. Review 11 resolution-log agent-response updates for F02 and F14 only.

## Finding mapping

| Finding | Phase A action | Status target |
|---|---|---|
| F02 | Implement complete-record transform fixtures, actual `canonical_target` inserts, crosswalk/archive/exception/relationship evidence, idempotency and strict semantic negative probes. | `READY FOR SDA CHECKPOINT ASSESSMENT` in agent-response cell only |
| F14 | Implement approved topology: `current_source`, `canonical_target`, `test_control`, controlled current migrations, target schema application, schema-leakage checks, no new review-numbered shadow model. | `READY FOR SDA CHECKPOINT ASSESSMENT` in agent-response cell only |

## Explicitly out of scope

F04, F05, F06, F07, F08, F09, F10, F11 and F12 remain outside this implementation scope. Legacy guardrails stay running and labelled as legacy. They must not be marked resolved or reworked into target-domain suites in Phase A.

## Expected files touched

Allowed Phase A paths:

- `docs/agent/tasks/NLI-WO-002-review-11-phase-a-plan.md`
- `docs/agent/tasks/NLI-WO-002-review-11-phase-a-s16-self-audit.md`
- `docs/sda/data-model/scripts/authoritative_harness.py`
- `docs/sda/data-model/fixtures/current-source/**`
- `docs/sda/data-model/fixtures/expected-target/**`
- `docs/sda/data-model/fixtures/transform-specs/**`
- `docs/sda/data-model/fixtures/api-contracts/**`
- `docs/sda/data-model/fixtures/scenarios/**`
- `docs/sda/data-model/fixtures/mutations/**`
- `docs/sda/data-model/phase-a-*.json`
- `docs/sda/data-model/phase-a-*.md`
- `docs/sda/reviews/NLI-WO-002-review-11.md`
- `.github/workflows/api-ci.yml` only if adding a non-authoritative Phase A harness step/job while preserving all existing jobs.

Prohibited:

- `services/api/**`
- `apps/**`
- `frontend/**`
- executable migrations under `infra/migrations/**`
- `infra/scripts/migrate.py`
- Docker runtime configuration under `infra/docker/**`
- production/pilot data under `data/**`
- `.env*`
- secrets
- PR #8 runtime fix paths

## Implementation sequence

### A1 — Topology skeleton

- Add `docs/sda/data-model/scripts/authoritative_harness.py` with commands:
  - `discover-current`
  - `apply-target`
  - `check-topology`
- Create schemas explicitly: `current_source`, `canonical_target`, `test_control`.
- Apply accepted current migrations using the controlled command path with `search_path=current_source,public`; do not reimplement or modify the migration runner.
- Apply `docs/sda/data-model/draft-physical-schema.sql` with `search_path=canonical_target,public` while preventing the draft file's internal `nli_wo002_target` schema name from becoming the authoritative evidence schema.
- Schema-qualify all later harness checks.
- Prove allowed public objects are extensions only.
- Prove `test_control` has only harness metadata/control tables and no business-domain policies.

### A2 — Stable fixture authority

Create fixture directories:

- `fixtures/current-source/`
- `fixtures/expected-target/`
- `fixtures/transform-specs/`
- `fixtures/api-contracts/`
- `fixtures/scenarios/`
- `fixtures/mutations/`

For F02 fixtures:

- Complete source records are grouped operational rows keyed by actual current primary/natural keys.
- Structured coordinates and related facts stay as one coherent record.
- Expected target records are hand-maintained and include target entities, child rows, relationships, archives, exceptions, and real FK/crosswalk expectations.
- Transform specifications are separate from expected target output.
- No validation-time bootstrap, repair or expected-output generation is allowed.

### A3 — Authoritative F02 execution

Add commands:

- `run-transforms`
- `check-f02`

Requirements:

- Read complete current records from `current_source`.
- Insert coherent rows into actual `canonical_target` tables using actual PostgreSQL types.
- Create one target identity per intended entity, not one per field.
- Insert child/relationship rows using real target FKs.
- Create source-to-target crosswalks.
- Create archive and exception rows where required.
- Preserve source package and source-record lineage.
- Compare actual target state against independent expected target records.
- Reconcile separately: source records, fields covered, target entities, target child rows, relationships, crosswalks, archives, exceptions and assertions.
- Compare stable typed value hashes.
- Run complete transforms twice and prove:
  - first run inserts expected rows;
  - second run inserts zero rows;
  - second run updates zero rows;
  - duplicates zero;
  - existing correct rows unchanged.

Strict negative probes must fail for expected semantic reason:

- Wrong transform operation
- Wrong independent expected value
- Invalid controlled translation
- Missing real target identity
- Unresolved real target FK
- Missing archive
- Missing exception
- Duplicate target output
- Lost relationship
- Mismatched typed hash

Unrelated database/setup errors do not count.

### A4 — CI and evidence

- Keep legacy Review 04–10 guardrails running as explicitly labelled legacy guardrails.
- Add a non-authoritative Phase A harness CI step/job if needed.
- Produce Phase A reports:
  - current-source migration/catalog report;
  - canonical-target catalog report;
  - topology/schema-leakage report;
  - complete-source-record fixture inventory;
  - target-entity transform inventory;
  - target FK/crosswalk evidence;
  - archive/exception evidence;
  - first-run/second-run idempotency evidence;
  - strict negative-probe report;
  - legacy-versus-authoritative distinction;
  - S16 self-audit.

### A5 — closeout

- Run local legacy guardrails and new Phase A harness.
- Validate skill pack.
- Commit bounded changes.
- Push branch.
- Verify local/remote equality and PR #7 draft/unmerged state.
- Verify exact-head CI green for agent-skills, api-tests, migration-lifecycle, api-image-runtime, frontend and Phase A harness.
- Update only Review 11 F02/F14 agent-response cells with `READY FOR SDA CHECKPOINT ASSESSMENT`.
- Do not request SDA Review 12.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Migration runner may hard-code `public.schema_migrations` lookups. | Use DSN/PGOPTIONS `search_path=current_source,public`; verify ledger location. If unsafe, stop and raise RFI rather than moving objects. |
| Draft schema file creates `nli_wo002_target` internally. | Apply safely into a temporary execution context only if it can be made to produce `canonical_target` without editing the source artifact; otherwise stop/RFI. |
| F02 fixture scope could expand into F04–F12. | Limit Phase A to complete-record transformation and topology; leave domain suites/scenarios/API/runtime observation as legacy/out-of-scope. |
| Expected truth could become self-generated. | Keep source records, expected target records and transform specs as separate fixture files; harness may validate but not author/repair them. |
| CI could treat new harness as final SDA gate. | Label Phase A job/step non-authoritative and preserve existing required jobs. |

## Verification commands planned

Local:

```bash
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/authoritative_harness.py discover-current
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/authoritative_harness.py apply-target
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/authoritative_harness.py check-topology
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/authoritative_harness.py run-transforms
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/authoritative_harness.py check-f02
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/review04_design_pipeline.py
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/review09_f02_independent_transform.py
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/review09_f04_f07_executed_tests.py
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/review09_api_contract_comparison.py
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/review09_scenario_comparison.py
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/review09_semantic_mutation_tests.py
PYTHONPATH=services/api DATABASE_URL=$DATABASE_URL python docs/sda/data-model/scripts/review09_f09_f11_reconciliation.py
PYTHONPATH=services/api python docs/sda/data-model/scripts/design_consistency_check.py
python docs/agent/scripts/validate_skill_pack.py
```

CI:

- exact-head `agent-skills-ci`
- exact-head `api-ci` jobs including legacy and Phase A harness evidence
- exact-head `frontend-ci`

## Readiness boundary

Phase A will be ready for SDA checkpoint assessment only. NLI-WO-002 remains `REWORK REQUIRED`; NLI-WO-002B remains unauthorized; Phase B cannot start until SDA assesses Phase A.
