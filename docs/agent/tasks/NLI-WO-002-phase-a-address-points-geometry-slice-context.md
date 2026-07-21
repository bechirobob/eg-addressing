# NLI-WO-002 Phase A Address Points Geometry Slice Context Pack

**Repository:** `bechirobob/eg-addressing`  
**Base branch/SHA:** `main` / not changed by this task  
**Task branch/SHA:** `nli/wo-002-canonical-location-model` / `5bd923875aa654d2831dd55c1f7164481d515d04`  
**PR/issue:** PR #7, draft/open/unmerged  
**Working tree:** clean at task start  
**Prepared at:** 2026-07-15

## 1. Authority

- Programme: Equatorial Guinea National Location Infrastructure.
- Active work order: `NLI-WO-002 — Canonical National Location Data Model`.
- Current SDA outcome/review: broad Phase A reassessment paused; `NLI-WO-002-PA-GEO-01` authorizes one address-points geometry vertical slice only.
- Change class: Class B controlled data-model/semantic evidence harness; no runtime migration or production schema change.
- Applicable ADRs: ADR-001, ADR-002, ADR-003, ADR-004 remain binding.
- Mandatory standards: data/migrations, GIS/location data, audit/evidence, security, documentation/records.
- Readiness boundary: one implementation pattern checkpoint only; does not accept Phase A, F02, F14, NLI-WO-002, NLI-WO-002B, publication, production, or Phase B.

## 2. Whole-project impact map

- Repository areas: `docs/sda/data-model/scripts/authoritative_harness.py`; evidence under `docs/sda/data-model/`; task context under `docs/agent/tasks/`.
- NLI bounded domains: Location Registry; Evidence and Verification; Administrative/GIS provenance only as test fixture context.
- Product modules/applications: no runtime app/frontend/backend module changes.
- User roles/institutions: SDA reviewer and implementation agent only.
- Territorial/data scopes: controlled Phase A fixture rows only; no pilot/production data.
- Trust zones: disposable local/CI PostgreSQL/PostGIS schemas `current_source`, `canonical_target`, `test_control` only.
- Environments: local test DB and GitHub CI.
- Lifecycle stages: design-authority validation / checkpoint evidence.
- Partner/external dependencies: none.
- Operational/support/rollout impact: none; no deployment or migration.

## 3. Selected skills

### Cross-cutting S01–S16

| Skill | Trigger | Required output |
|---|---|---|
| S01 | every task, explicit scope/prohibitions | authority/scope matrix |
| S03 | acceptance checkpoint | criterion-mapped plan |
| S05 | current-source row and target identity discovery | source/target query proof |
| S06 | current-to-target transform pattern | explicit registry binding and convergence proof |
| S07 | fixture loading into disposable schema | fixture/FK-safe execution evidence |
| S09 | geometry/evidence/provenance | WKT/SRID, accuracy, evidence, exception proof |
| S11 | positive/negative semantic evidence | eight normal-path tests |
| S12 | PR/exact-head CI | SHA/workflow/job proof |
| S13 | SDA checkpoint remediation | preserve reviewer-owned oracle; bounded correction |
| S16 | self-audit/handoff | final boundary and exact next step |

### Whole-project S17–S31

| Skill | Trigger | Required output |
|---|---|---|
| S17 | domain boundary: observed geometry not canonical promotion | readiness boundary |
| S19 | PostgreSQL/PostGIS harness logic | typed DB execution proof |
| S21 | location registry identity resolution | address crosswalk to target subject |
| S23 | evidence/quality checkpoint | negative tests and unchanged-state proof |
| S31 | programme sequencing | stop after one slice |

### Considered but not applicable

| Skill | Why not applicable |
|---|---|
| S08 | no API/identity/security/runtime contract changed |
| S10/S18/S20/S22/S24-S30 | no UI, field app, publication, integration, analytics, infra, performance, training, or release change |
| S14/S15 | no unrelated maintenance fix or operational change planned |

## 4. Scope matrix

### In scope

- Implement `transform_address_points_geometry()`.
- Add explicit binding `impl_wo002_r06_geometry_observation_address_points -> transform_address_points_geometry`.
- Add a one-slice harness command/test path for `WO002-R06-geometry-observation-address_points`.
- Query complete `current_source.address_points` row from PostgreSQL.
- Resolve `address_id` through reviewed `proposed_legacy_crosswalk` precondition.
- Create exactly one `proposed_geometry_observation` and one conditional `proposed_migration_exception` per reviewer oracle.
- Compare against reviewer-owned oracle only after observed rows exist.
- Run the eight required tests through normal path.

### Supporting evidence

- `docs/sda/data-model/phase-a-address-points-geometry-slice-report.json`.
- Updated harness evidence command included in local/CI SDA design model job.
- This task context pack.

### Separate maintenance

- Existing aggregate 90-group generic transform quality remains outside this checkpoint.
- Existing migration concurrency flake remains outside this checkpoint unless CI blocks and SDA authorizes maintenance.

### Prohibited

- Modify reviewer-owned oracle JSON.
- Modify other 89 groups.
- Request broad Phase A reassessment or SDA Review 12.
- Modify F04-F12.
- Modify runtime app/frontend/API code, executable migrations, `infra/scripts/migrate.py`, Docker runtime config, production/pilot data, secrets, `.env*`, or PR #8.

## 5. Current-state evidence inspected

| Domain/object/workflow | Source path, runtime, or command | What it establishes |
|---|---|---|
| Checkpoint authority | `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-checkpoint.md` | one-slice authorization and final return contract |
| Reviewer oracle | `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-expected.json` | independent expected rows/tests/preconditions |
| Current harness | `docs/sda/data-model/scripts/authoritative_harness.py` | generic all-groups path must not be reused for slice |
| Oracle hash | `sha256sum` | byte-for-byte guard baseline `cf699de04e0ca500c3a7826f257e190d24835356ef96db1650160d7d438edaea` |

## 6. Acceptance-criterion plan

| AC | Observable product/operational result | Affected modules/roles/environments | Change/model | Positive test | Negative test | Authority check | Operational/recovery check | Evidence | Risk/RFI |
|---|---|---|---|---|---|---|---|---|---|
| Explicit binding | Binding maps exactly `impl_wo002_r06_geometry_observation_address_points` to `transform_address_points_geometry` | Harness only | Add specific registry | report names function and binding | no generic function flag is false | reviewer checkpoint | no runtime effect | slice report | none |
| Complete source query | SQL queries full address_points row by ID | disposable current_source | add one-slice source query | returned row matches oracle | missing-source mutation | oracle source record | rollback/reset DB | slice report | none |
| Identity resolution | address_id resolves via reviewed crosswalk to target subject | disposable canonical_target | add precondition/crosswalk resolver | target subject query succeeds | missing-crosswalk mutation | oracle precondition | state unchanged after failure | slice report | none |
| Geometry observation | exact WKT/SRID/accuracy/capture/source/evidence inserted | disposable canonical_target | add transform function | positive and idempotency | wrong-longitude, invalid-coordinate, missing-evidence | GIS/evidence standards | idempotent second run | slice report | none |
| Conditional exception | exact owned authority exception inserted | disposable canonical_target | add transform function | exact row comparison | expected comparison catches wrong oracle | unresolved authority preserved | state unchanged after failure | slice report | none |
| Absent rows | no geometry version/quality/transformation/per-field assertions | disposable canonical_target | no row creation for prohibited tables | absent queries zero | wrong expected geometry normal path | checkpoint prohibited rows | no runtime effect | slice report | none |

## 7. Expected changed paths

### Add

- `docs/agent/tasks/NLI-WO-002-phase-a-address-points-geometry-slice-context.md`
- `docs/sda/data-model/phase-a-address-points-geometry-slice-report.json`

### Modify

- `docs/sda/data-model/scripts/authoritative_harness.py`
- CI workflow only if needed to run the specific checkpoint command in exact-head CI.

### Remove/deprecate

- none

## 8. Effect assessment

- System architecture/domain boundaries: reinforces observation-only geometry; no canonical promotion.
- Database/migrations/reference data/fixtures: disposable fixture execution only; no migrations.
- API/contracts/identity/authorization: none.
- Security/privacy/audit/evidence: evidence lineage checked inside disposable target rows.
- GIS/geometry/provenance: direct effect; exact WKT/SRID, accuracy, capture method, lineage, and authority exception.
- Frontend/design system/accessibility/localization: none.
- Backend/domain logic/transactions: no runtime backend code.
- Citizen/public services: none.
- Registry/operator case management: design-harness identity resolution only.
- Field/mobile/offline synchronization: none.
- Verification/quality/recapture: semantic evidence only; no quality approval row.
- Publication/corrections/certificates/signage: none.
- Agency integrations/notifications/interoperability: none.
- Imports/exports/workers/batch jobs: none.
- Reporting/analytics/data products: none.
- Infrastructure/environments/platform: CI evidence only.
- Performance/scalability/resilience: not claimed.
- Operations/backup/restore/DR: no operational change.
- Support/training/change adoption: no change.
- Programme roadmap/release/rollout: stop after checkpoint.

## 9. Decisions and RFIs

| Decision | Classification | Owner | ADR/RFI | Blocking? |
|---|---|---|---|---|
| Geometry remains observation, not canonical promotion | already decided by checkpoint | SDA | checkpoint/oracle | no |
| Additional transform groups | SDA decision needed | SDA | next instruction required | yes after this slice |

## 10. Execution sequence

1. Add slice-specific source/precondition/transform/comparator/test functions.
2. Run RED/GREEN local one-slice command with eight tests.
3. Verify reviewer oracle hash unchanged.
4. Run relevant local gate and changed-path guard.
5. Commit, push, verify exact-head CI, and stop.

## 11. Recovery and compatibility

- Rollback safe: yes; docs/harness-only branch change.
- Forward recovery: revert commit or patch harness command.
- Idempotency: required second run zero inserts/updates.
- Breaking/compatibility effect: none on runtime systems.
- External effects: GitHub PR/CI only.
- Monitoring/alert changes: none.
- Support/training/communication: none.
- Rollout/cutover gate: not applicable.

## 12. Submission plan

- Draft PR target: PR #7 remains draft/open/unmerged.
- Required workflows/jobs: exact-head `sda-design-model` at minimum plus existing required CI observed for PR head.
- Expected exact-head evidence: workflow/job IDs, local/remote equality, PR state, prohibited-path guard.
- Required browser/device/runtime/recovery artifacts: not applicable.
- Review request format: no broad reassessment; final report only one-slice checkpoint and next SDA instruction required.

## 13. Agent declaration

- [x] Authority and scope are explicit.
- [x] Whole-project impact is mapped using `PROJECT-COVERAGE-MATRIX.md`.
- [x] Applicable S01–S16 and S17–S31 skills are selected.
- [x] Skills considered but not applicable have rationale.
- [x] Every criterion has specific positive and negative evidence.
- [x] Expected evidence is independent from observed generation.
- [x] Reserved decisions are not silently embedded.
- [x] Out-of-scope defects will use S14.
- [x] Operational, support, training, rollout, and recovery effects are addressed where applicable.
- [x] No prohibited path or behavior is planned.
