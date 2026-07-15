# NLI-WO-002 Review 11 Phase A Execution Correction Plan

## Authority header

| Item | Value |
|---|---|
| Reviewer-owned start head | `62ba492f05adb233f57f52138c7ba7393c9bd445` |
| Reviewed corrected implementation head | `882a0f08758d8ec714c1d8b2c62628f986b8fd5d` |
| Reassessment record | `docs/sda/reviews/NLI-WO-002-review-11-phase-a-reassessment.md` |
| Decision | `PHASE A CORRECTION REQUIRED` |
| Allowed correction | Replace direct expected-row insertion with real `current_source -> transform implementation -> canonical_target` execution for A2/A3 only |
| Explicitly prohibited | F04-F12, Phase B, Review 12, runtime API/frontend changes, executable migrations, `infra/scripts/migrate.py`, Docker runtime config, production/pilot data, secrets, `.env*`, PR #8 paths |

## Selected repo-native skills

- Mandatory: S01, S03, S11, S12, S16
- Review/remediation: S13
- Current-state/data model/GIS/database evidence: S05, S06, S07, S09
- Affected whole-project surfaces: S17, S19, S21, S23, S24, S26, S28, S31
- Not applicable: S10/S18 public UI, because no frontend/user-facing route is changed; S08 API/security runtime, because no API/auth/privacy implementation is changed.

## Scope classification

| Path | Classification | Reason |
|---|---|---|
| `docs/sda/data-model/scripts/authoritative_harness.py` | In scope | Phase A harness execution architecture |
| `docs/sda/data-model/fixtures/current-source/phase-a-complete-source-records.json` | In scope | Source fixture loaded into actual current tables |
| `docs/sda/data-model/fixtures/transform-specs/phase-a-transform-specs.json` | In scope | Reviewed group dispatch inputs |
| `docs/sda/data-model/fixtures/expected-target/phase-a-expected-target-records.json` | In scope | Comparator-only expected rows, re-authored semantics |
| `docs/sda/data-model/fixtures/mutations/phase-a-negative-probes.json` | In scope | Normal-path source/spec/implementation mutations |
| `docs/sda/data-model/phase-a-*.json` | Supporting evidence | Runtime telemetry and reports |
| `docs/sda/reviews/NLI-WO-002-review-11.md` | In scope, limited | Update only F02/F14 agent-response cells |
| `docs/agent/tasks/*phase-a*` | Supporting evidence | plan/S16 handoff |
| `.github/workflows/**` | Preserve unless needed | Existing non-authoritative Phase A CI step remains |
| `services/api/**`, `apps/**`, `frontend/**`, `infra/migrations/**`, `infra/scripts/migrate.py`, `infra/docker/**`, `data/**`, `.env*`, secrets | Prohibited | Explicit reassessment boundary |

## Implementation plan

1. Preserve A1 topology.
   - Keep disposable schemas: `current_source`, `canonical_target`, `test_control`.
   - Keep current migrations applied via `infra/scripts/migrate.py` with `search_path=current_source,public`.
   - Keep target draft applied to `canonical_target` only.

2. Load complete source fixtures into real current tables.
   - Insert all 25 fixture records into `current_source.<actual_current_table>`.
   - Use table metadata from live PostgreSQL for types/defaults.
   - Query inserted rows by real primary key or fixture natural key.
   - Emit source population evidence: tables, keys, fields queried, FK relationship query summary.

3. Replace expected-row insertion with transform dispatch.
   - Add `TRANSFORM_IMPLEMENTATIONS = {group_id: callable}`.
   - Every reviewed group must resolve and be invoked exactly once.
   - Shared generic functions are allowed only through group-specific dispatch and telemetry.
   - Each implementation reads only declared source fields and source keys from `current_source`.
   - Expected target rows are not read until after observed rows exist.

4. Re-author transform semantics at group level.
   - Produce typed target entities for grouped typed transforms.
   - Create geometry observations for geometry groups with lat/lon/accuracy/source/provenance and conditional authority exception where required.
   - Create one correction-case identity/crosswalk/decision lineage for correction source records.
   - Create archives only for archive dispositions, exceptions only for unresolved/conditional groups, crosswalks only for source identity to actual target identity.
   - Avoid universal per-field assertion/archive/crosswalk rows.

5. Generate execution coverage from telemetry.
   - Runtime telemetry records source table/key, fields consumed, implementation invoked, target rows, FKs, child rows, relationships, crosswalks, archives, exceptions, and comparison result.
   - Gate remains: 237 reviewed fields, 237 executed field dispositions, 0 missing, 0 duplicate/conflicting, 90 reviewed groups, 90 invoked, 0 unexecuted.

6. Rebuild comparator-only expected target fixture.
   - Controlled authoring pass may pin DB-normalized expected rows outside validation.
   - Harness validation must never modify or repair the expected fixture.
   - Comparator reads expected only after transform execution.

7. Replace negative probes.
   - Mutate actual source fixture/spec/implementation/id/crosswalk/archive/exception/relationship/expected input.
   - Run normal load + transform + compare path.
   - Require strict semantic reason and unchanged authoritative state after rollback.

8. Verify lifecycle.
   - Execute full transform twice: first inserts expected rows, second inserts 0/updates 0.
   - Query duplicates from PostgreSQL.
   - Prove cleanup after success and failure, recreation from empty, same current/target catalogs, same observed target hash.

9. Close out only authorized records.
   - Update S16 self-audit.
   - Update only F02/F14 agent-response cells to `READY FOR SDA PHASE A REASSESSMENT`.
   - Keep SDA dispositions unchanged.
   - Push exact head, keep PR draft/unmerged, obtain green CI, request Phase A reassessment only.

## Verification commands

- `PYTHONPATH=services/api .venv-api-test/bin/python docs/sda/data-model/scripts/authoritative_harness.py phase-a-all`
- Existing legacy guardrail command chain remains green and labelled legacy.
- `python3 docs/agent/scripts/validate_skill_pack.py`
- `git diff --check`
- prohibited-path guard from reviewer head.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Current fixture values violate live current schema | Use live column metadata, dependency-safe ordering, JSON/geometry adaptation, and fail closed on insert/query mismatch |
| Shared transform function hides unexecuted groups | Dispatch by transform group ID and require telemetry per group |
| Expected fixture becomes circular again | Validation path hard-fails if expected file is read before observed target rows exist |
| Crosswalks remain generic | Validate target entity to actual target table/PK existence |
| Negative probes are manual | Use source/spec/implementation mutations and the normal path; no direct expected-error raise |
| Boundary drift | Prohibited-path guard before commit and final report |
