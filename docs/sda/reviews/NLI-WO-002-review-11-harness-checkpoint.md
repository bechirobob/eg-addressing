# SDA Architecture Checkpoint — NLI-WO-002 Review 11 Authoritative Assurance Harness

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed checkpoint commit:** `4c755589441c9253563510060e931e2b2492d07c`  
**Reviewer:** System Design Authority  
**Checkpoint date:** 2026-07-15  
**Checkpoint decision:** `APPROVED WITH CONDITIONS — BOUNDED HARNESS PHASE A IMPLEMENTATION AUTHORIZED`  
**NLI-WO-002 status:** `REWORK REQUIRED`  
**NLI-WO-002B:** `UNAUTHORIZED`

## 1. Boundary and verification

Reviewed:

- `docs/agent/tasks/NLI-WO-002-review-11-task-context-pack.md`;
- `docs/agent/tasks/NLI-WO-002-review-11-finding-resolution-matrix.md`;
- `docs/sda/data-model/authoritative-assurance-harness.md`;
- PR #7 state, exact head, changed paths and exact-head workflows.

Independent verification:

- PR #7 is open, draft, mergeable and unmerged.
- Exact checkpoint head is `4c755589441c9253563510060e931e2b2492d07c`.
- The checkpoint is one commit after the reviewer-owned Review 11 record and changes only the two task records plus the harness architecture document.
- No runtime application, frontend, executable migration, migration runner, Docker runtime configuration, production/pilot data, `.env*`, secret or PR #8 path changed.
- Agent-skills CI run `29396570834`: success.
- API CI run `29396570852`: success.
  - `sda-design-model` job `87291306718`: success.
  - `api-tests` job `87291306716`: success.
  - `migration-lifecycle` job `87291306696`: success.
  - `api-image-runtime` job `87291306682`: success.
- Frontend CI run `29396570824`, job `87291306460`: success.
- No SDA Review 12 request was made.

## 2. Architecture assessment

The checkpoint correctly addresses F14 at the architecture level:

- one disposable PostgreSQL/PostGIS execution topology;
- accepted current migrations as source authority;
- `draft-physical-schema.sql` as target authority;
- `test_control` restricted to expected truth, run metadata and comparisons;
- no new review-numbered shadow schema;
- complete-record grouped transforms;
- target-schema domain suites and scenarios;
- runtime FastAPI observation rather than OpenAPI-only evidence;
- complete-repository/fresh-database mutation isolation;
- bounded replacement of legacy guardrails.

The design is approved as the implementation direction. This checkpoint does **not** resolve F02–F12 or F14 and does not accept NLI-WO-002.

## 3. Controlled architecture decisions

### R11-RFI-001 — Identity and institutional authority ownership

**Decision:** NLI-WO-002 does not own the authoritative human/service identity, institution-membership or credential lifecycle. Those capabilities belong to the future Identity and Trust bounded domain.

The canonical location design may and must contain typed external-reference contracts sufficient to prove authority-sensitive location decisions:

- `actor_ref` or `service_actor_ref`;
- `institution_ref`;
- `permission_ref`;
- `territorial_scope_ref`;
- `data_scope_ref`;
- immutable `authority_assertion` linking those references, source system, effective time and recorded time;
- decision/evidence/quality/observation records referencing that assertion.

These are typed authority references and decision evidence, not a second identity store. They must not contain passwords, sessions, authentication factors or an independent membership lifecycle.

### R11-RFI-002 — Lifecycle metadata authority

**Decision:** Add one independently reviewed lifecycle policy source:

```text
docs/sda/data-model/lifecycle-policy-reviewed.json
```

It must define, per vocabulary:

- initial states;
- terminal states;
- permitted re-entry;
- forbidden transitions;
- every allowed edge;
- permission key;
- institution/scope mode;
- evidence and reason prerequisites;
- audit event type;
- public effect;
- reversal/appeal behavior;
- accountable owner and review status.

The target schema must store/enforce the policy through target tables/functions. Expected lifecycle test cases remain independently authored and may not be generated from the policy executor.

### R11-RFI-003 — API observation method

**Decision:** FastAPI `TestClient` is the default observer for every current operation.

A deterministic handler/service fixture is permitted only where full HTTP execution requires an unrelated external dependency or asynchronous side effect. Each exception must be recorded in:

```text
docs/sda/data-model/api-runtime-observation-exceptions-reviewed.json
```

with operation ID, exact callable, reason, dependency avoided, owner, review status and proof that the fixture returns the same contract-producing object as the route.

Every operation must have an observed success or explicitly documented no-content result and applicable validation/authentication denial results. Dynamic success objects must be recursively field-complete. Unexpected observed fields fail unless separately reviewed and classified.

### R11-RFI-004 — Harness CLI and CI authority

**Decision:** `docs/sda/data-model/scripts/authoritative_harness.py` is authorized as the stable top-level design-assurance CLI.

`review04_design_pipeline.py` may be refactored into importable discovery/generation modules and remains a legacy guardrail during transition. It must not remain the final top-level acceptance authority.

During Phase A, old and new checks run in parallel. The `sda-design-model` workflow may switch its authoritative entrypoint only after parity is demonstrated and the SDA approves the cutover checkpoint.

### R11-RFI-005 — Expected-truth approval

**Decision:** Expected fixtures require explicit source ownership:

- SDA approval is sufficient for technical schema, compatibility and deterministic transformation expectations already within the work order.
- Programme Owner or responsible institutional authority remains required for final public-code grammar, official administrative/boundary authority, publication authority, cadastre/parcel authority and other reserved government-policy facts.
- Authority-sensitive fixtures without that decision must be marked `conditional` or `provisional`, must retain the RFI, and cannot be used to claim the institutional decision closed.

Validation may compare those conditional mechanics, but the evidence report must preserve the condition.

### R11-RFI-006 — Publication simulation

**Decision:** Controlled non-official simulation is authorized solely for design validation of release relationships and projections.

Simulation data and artifacts must:

- use synthetic fixture identities;
- carry `non_official=true` or an equivalent unmistakable marker;
- remain inside disposable harness schemas/artifacts;
- never issue final national codes;
- never generate externally distributable official certificates/signage;
- never imply publication authority or effective national release.

## 4. Approved database topology

Use one disposable PostgreSQL/PostGIS database per base harness run with:

```text
current_source
canonical_target
test_control
public  # extensions only
```

Rules:

1. Create all three schemas explicitly.
2. Apply accepted current migrations through the controlled migration command with session `search_path=current_source,public` or an equivalent DSN/PGOPTIONS mechanism. Do not reimplement the migration runner.
3. Prove the migration ledger and current operational objects are created in `current_source`; allowed PostGIS extension objects may remain in `public`.
4. Apply `draft-physical-schema.sql` with `search_path=canonical_target,public`.
5. All harness queries must be schema-qualified after creation.
6. `test_control` may contain only fixture manifests, expected rows/contracts, run metadata, comparison results and mutation control—not business-domain policy substitutes.
7. If accepted migrations or the draft schema cannot be applied safely under this topology, stop and raise an RFI. Do not move objects after creation or create a replacement shadow schema to make the test pass.

## 5. Authorized implementation scope — Phase A only

The agent is authorized to implement commit groups 1–3 from the checkpoint, limited to the harness foundation and F02.

### Phase A1 — Harness skeleton and topology

Add the stable CLI and supporting modules required to:

```text
authoritative_harness.py discover-current
authoritative_harness.py apply-target
authoritative_harness.py check-topology
```

Required evidence:

- empty disposable database;
- accepted migrations applied to `current_source` through the controlled migration path;
- migration-ledger and catalog inventory in `current_source`;
- target proposal applied from empty to `canonical_target`;
- expected target catalog parity;
- `test_control` contains no business tables;
- deterministic rerun and cleanup;
- no runtime/app/migration behavior changed.

### Phase A2 — Independent fixture authority

Create stable non-review-numbered fixture directories for:

```text
docs/sda/data-model/fixtures/current-source/
docs/sda/data-model/fixtures/expected-target/
docs/sda/data-model/fixtures/transform-specs/
docs/sda/data-model/fixtures/api-contracts/
docs/sda/data-model/fixtures/scenarios/
docs/sda/data-model/fixtures/mutations/
```

For F02, replace one-field-per-row inputs with complete current records keyed by actual current primary/natural keys. Expected target fixtures must describe complete typed target rows, child rows, relationships, archives, exceptions and real target FKs. Validator code must not author or repair these files.

### Phase A3 — Authoritative F02 execution

Implement grouped transforms that:

- read complete records from `current_source`;
- create coherent entities and child rows in `canonical_target`;
- use target PostgreSQL types rather than generic text value columns;
- create real target identities before reference resolution;
- create crosswalks referencing real target primary keys;
- create governed archive/exception rows where required;
- preserve source-record lineage;
- compare actual target rows with independently reviewed expected target rows;
- reconcile entity/relationship counts and stable value hashes;
- execute twice with zero second-run inserts/updates and zero duplicates;
- fail for the expected semantic reason on wrong transform, wrong expected value, unresolved FK, missing target identity, missing archive/exception, duplicate output, lost relationship and hash mismatch.

The F02 suite must cover every reviewed current field through complete-record groups. It must report source-record count separately from field count and target-entity/child-row counts separately from assertion count.

## 6. Phase A prohibitions

During this authorized phase, do not:

- implement F04–F12 target suites yet;
- mark F02 or F14 SDA-resolved;
- retire legacy guardrails;
- switch the CI authoritative entrypoint;
- request SDA Review 12;
- add `r11_*` or another shadow policy/schema;
- modify `services/api/**`, `apps/**`, executable migrations, `infra/scripts/migrate.py`, Docker runtime configuration, production/pilot data, `.env*`, secrets or PR #8;
- finalize identity, publication, public-code, boundary or parcel institutional authority beyond the decisions recorded above.

`.github/workflows/api-ci.yml` may change only as supporting evidence to add a non-authoritative Phase A harness job or step. Existing required jobs must remain intact.

## 7. Phase A exit gate

Before returning to the SDA:

1. Push the bounded Phase A commits.
2. Keep PR #7 draft and unmerged.
3. Provide exact local/remote head equality.
4. Run legacy guardrails and the new Phase A harness; label them separately.
5. Obtain green exact-head agent-skills, API tests, migration lifecycle, API image runtime, frontend and Phase A harness CI.
6. Provide target-schema catalog evidence, complete-record transform inventory and real FK/idempotency evidence.
7. Add a Phase A S16 self-audit.
8. Update only the Review 11 resolution-log agent-response cells for F02 and F14, using status `READY FOR SDA CHECKPOINT ASSESSMENT`; do not alter SDA disposition.
9. Do not update F04–F12 as resolved.
10. Do not request Review 12.

The next SDA action will assess Phase A and either authorize Phase B or require correction.

## 8. Non-claims

This checkpoint does not:

- accept NLI-WO-002;
- resolve F02–F12 or F14;
- authorize NLI-WO-002B;
- authorize executable production migrations;
- authorize official publication, public-code issuance, certificates/signage or partner release;
- authorize production deployment or national-production readiness.
