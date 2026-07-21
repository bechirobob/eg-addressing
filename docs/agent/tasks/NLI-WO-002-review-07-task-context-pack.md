# Agent Task Context Pack — NLI-WO-002 Review 07 Remediation

**Repository:** `bechirobob/eg-addressing`  
**Base branch/SHA:** `origin/main` @ `f10016ed4cea8582ac48de41aa4f80b30c999ba1`  
**Task branch/SHA:** `nli/wo-002-canonical-location-model` @ `c34b924017ce7571ba8e58b33062336dbc0c9fe4` after synchronizing reviewer-owned remote head with latest `origin/main`  
**Reviewer-owned remote head before local checkpoint:** `origin/nli/wo-002-canonical-location-model` @ `ec3e88906cee173bac0f57c710398fe866e1e094`  
**PR/issue:** PR #7, draft/open/unmerged  
**Working tree at preparation:** clean before this checkpoint artifact  
**Prepared at:** `2026-07-14T17:21:07Z`

## 1. Authority

- **Programme:** National Location Intelligence / Digital Addressing pilot.
- **Active work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`.
- **Current SDA outcome/review:** `docs/sda/reviews/NLI-WO-002-review-07.md` — `REWORK REQUIRED`.
- **Change class:** Class B design/model/evidence remediation only; no runtime implementation authority.
- **Applicable ADRs:** ADR-001 through ADR-009, with ADR-005 through ADR-009 remaining proposed until defining evidence closes.
- **Mandatory standards:** all SDA standards under `docs/sda/standards/`, especially data/migrations, GIS/location, API design, identity/access, security, audit/evidence, testing/release, documentation/records, operations/DR, and UI/workflow where projection evidence is involved.
- **RFIs:** RFI-002 through RFI-006 remain open; RFI-001 is withdrawn. Open RFIs block public-code, administrative authority, publication authority, parcel/cadastre authority, and published-looking pilot-record production/publication decisions.
- **Readiness boundary:** design evidence only. PR #7 must remain draft/unmerged. NLI-WO-002B is unauthorized. No production/publication/signage/certificate/partner-release claim is allowed.

## 2. Whole-project impact map

- **Repository areas:** `docs/sda/data-model/**`, `docs/sda/adrs/**`, `docs/sda/rfis/**`, `docs/sda/reviews/NLI-WO-002-review-07.md` resolution-log section only, `docs/sda/evidence/**`, `docs/agent/tasks/**`, and supporting CI/workflow evidence already in PR scope.
- **NLI bounded domains:** Identity and Trust, Administrative Geography, Location Registry, Field Operations, Evidence and Verification, Publication and Corrections, Agency Integration, Audit/Reporting/Analytics, Platform Operations.
- **Product modules/applications:** no app runtime modification in PR #7; design artifacts affect future citizen, registry, field, publication, agency, analytics, support, and platform modules.
- **User roles/institutions:** citizen, registry operator, field enumerator, supervisor, publication authority, partner/machine client, platform admin, SDA/programme owner. Roles remain design concepts unless already implemented elsewhere.
- **Territorial/data scopes:** national/province/district/municipality/locality and operational areas remain modeled; official authority remains conditional on open RFIs.
- **Trust zones:** public, operator, administrative, partner/machine, operational, evidence/object storage, analytics/reporting, lower environments.
- **Environments:** disposable PostgreSQL/PostGIS design validation only; no runtime migration or production environment change.
- **Lifecycle stages:** candidate/evidence, reviewed, registry-ready, publication proposed/approved/published, corrected/superseded/withdrawn/retired; no public release authority.
- **Partner/external dependencies:** external maps/geocoders, cadastre/parcel authorities, partner agencies, GitHub CI; no direct partner integration is implemented.
- **Operational/support/rollout impact:** future migration, support, training, rollout, DR, and partner onboarding depend on closed findings and later work orders.

## 3. Selected skills

### Cross-cutting S01–S16

| Skill | Trigger | Required output |
|---|---|---|
| S01 | Every task | Authority header, scope/readiness boundary, PR state |
| S02 | Review shows incomplete impact analysis | Whole-project domain/surface map |
| S03 | Work-order remediation | AC-to-evidence plan and execution sequence |
| S04 | RFIs/ADRs remain open | Keep reserved decisions visible, no silent approval |
| S05 | Review disputes current/API/classification discovery | Source-backed inventory constraints |
| S06 | Core data-model remediation | Typed target model, relationships, lifecycle, transforms, fixtures |
| S07 | Disposable SQL/migration-unit evidence | No runtime migrations; design SQL and future migration units only |
| S08 | API policy/projection findings | Independent policy registry and field-level projection contracts |
| S09 | Geometry/evidence/publication findings | Promotion authority, provenance, publication gates |
| S10 | Projection/workflow vocabulary affects users | Bilingual/accessibility projection implications only |
| S11 | Evidence false-positive findings | Named executable positive/negative assertions |
| S12 | PR head/CI/review request | Exact-head proof and stale metadata prevention |
| S13 | Review 07 REWORK REQUIRED | Finding-specific matrix and protected resolution-log updates |
| S14 | PR #8 maintenance dependency | Keep runtime/migration-ledger fix separate |
| S15 | Readiness/DR language risk | No production/pilot/publication readiness overclaim |
| S16 | Before reporting/review request | Self-audit and handoff |

### Whole-project S17–S31

| Skill | Trigger | Required output |
|---|---|---|
| S17 | Domain ownership and authority boundaries | Singular canonical authority and trust-zone map |
| S18 | Future frontend projections/contracts | No client/public exposure assumptions |
| S19 | Backend/domain logic implications | Future use-case and invariant boundaries, no runtime code |
| S20 | Citizen portal/public services | Public-safe projection and tracking/proof boundaries |
| S21 | Registry operations/case management | Operator/case authority and scope model |
| S22 | Field/offline sync | Candidate/evidence/offline state separation |
| S23 | Verification/quality/evidence review | Signal versus authorized decision separation |
| S24 | Publication/corrections/certificates/signage | Immutable release, authority, revocation boundaries |
| S25 | Partner integrations | Purpose-limited partner projection and machine identity boundaries |
| S26 | Imports/exports/workers/batch | Future migration/import/export/job safety boundaries |
| S27 | Reporting/analytics/data products | Metrics/data-product authority and privacy boundaries |
| S28 | Infrastructure/environments | No environment/platform changes in PR #7 |
| S29 | Performance/scalability/resilience | Scale figures remain unapproved assumptions |
| S30 | Support/training/adoption | No rollout/training readiness claim from design evidence |
| S31 | Programme planning/roadmap | NLI-WO-002B remains blocked until SDA acceptance |

### Considered but not applicable

| Skill | Why not applicable |
|---|---|
| None in S01–S31 | Review 07 explicitly spans whole-project proof layers; all cards were read and mapped. |

## 4. Scope matrix

### In scope

- Correct Review 07 findings F02 and F04–F12 in PR #7 design/evidence artifacts.
- Correct the negative-test harness first and prove a false-pass invalid action fails the suite.
- Add named executable assertions and reports tied to exact remediation evidence.
- Update only the Review 07 resolution-log section after remediation evidence exists.
- Update PR #7 body/evidence with current exact-head status after push/CI.

### Supporting evidence

- Disposable PostgreSQL/PostGIS execution through design scripts.
- Deterministic regeneration of data-model outputs.
- Exact-head GitHub workflow/job evidence for PR #7.
- Changed-path guard proving no prohibited runtime paths in PR #7.
- Separate PR #8 reference for migration-ledger maintenance dependency.

### Separate maintenance

- PR #8 migration-ledger advisory-lock/ledger race fix: `5650cd219156d23f10836ab7041b34693e9250b0` remains external and must not be duplicated in PR #7.
- The Markdown typo in `docs/agent/templates/task-context-pack.md` is outside Review 07 remediation unless separately authorized.

### Prohibited

- Runtime/app/API/backend/frontend/container/migration changes in PR #7 unless a later explicit authority changes scope.
- Editing reviewer-owned Review 07 outcome, review boundary, AC decisions, finding observations, required resolutions, or SDA dispositions.
- Marking findings SDA-resolved; only `READY FOR SDA REVIEW` is permitted for agent status.
- Public-code grammar, publication, signage, certificates, partner release, production readiness, or NLI-WO-002B authorization.
- Production data, secrets, or official publication claims.

## 5. Current-state evidence inspected

| Domain/object/workflow | Source path, runtime, or command | What it establishes |
|---|---|---|
| Root authority | `AGENTS.md` | Repo-native SDA/agent protocol and branch/review discipline |
| Agent protocol | `docs/agent/README.md`, `master-operating-protocol.md`, `skill-manifest.yaml`, `PROJECT-COVERAGE-MATRIX.md` | S01–S31 invocation and whole-project coverage |
| Active work order | `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md` | Design-only authority and AC scope |
| Latest SDA decision | `docs/sda/reviews/NLI-WO-002-review-07.md` | Review 07 `REWORK REQUIRED`, open findings, required sequence |
| ADR/RFI layer | ADR-001–ADR-009, RFI-001–RFI-006 | Accepted baseline/proposed design decisions and open authority blockers |
| Standards | `docs/sda/standards/*.md` | Required controls for data, GIS, API, identity, audit, security, testing, operations, UI |
| Current branch state | `git fetch`, `git reset --hard` after approval, merge `origin/main` | Local PR branch now includes latest main and Review 07 head |
| Review 07 diff scope | `git diff --name-status origin/main...HEAD` | No prohibited runtime paths in branch diff after sync |
| Current negative harness | `docs/sda/data-model/scripts/review04_design_pipeline.py` | `expect_sql_failure` catches its own `AssertionError`, causing false-pass risk |
| Current semantic checker | `docs/sda/data-model/scripts/design_consistency_check.py` | Checker reports aggregate `Generated checks: 41` / `Errors: 0` despite open findings |

## 6. Acceptance-criterion plan

| AC | Observable product/operational result | Affected modules/roles/environments | Change/model | Positive test | Negative test | Authority check | Operational/recovery check | Evidence | Risk/RFI |
|---|---|---|---|---|---|---|---|---|---|
| AC-01 | Current-state inventory classifications/projections are field-specific and reviewed | Data/API/security | Replace generic inference with reviewed owner/status where required | Inventory rows with reviewed source/classification pass | Missing/default/keyword-only classification fails | S05/S08 | Disposable deterministic check | Design report named assertions | None, design-only |
| AC-02 | One canonical registry authority remains singular | Registry | Reference mappings prove final canonical FK/crosswalk outputs | Transform fixture resolves target FK | Unresolved reference fails | ADR-007/S06 | No runtime schema change | Transform fixture report | F02 dependency |
| AC-03 | Admin geography explicit but not officialized | Admin geography/GIS | Preserve open authority RFIs and temporal model | Admin version/codes reconstruct | Overlap/cross-owner invalid cases fail | RFI-003 | No publication claim | Temporal/register tests | RFI-003 open |
| AC-04 | Operational areas separate | Field/operations | Keep operational areas separate from official admin geography | Valid operational scope fixture passes | Official boundary substitution fails | ADR-006/S09 | No runtime ops change | Named assertion | RFI-003 open |
| AC-05 | Every record type has cardinality proof | Registry/citizen/operator | Complete record-type positive/negative datasets | Required/optional/min/max scenarios pass | Missing role, excess count, bad pairing fail | ADR-007/S06 | No implementation claim | Scenario/cardinality report | F04 |
| AC-06 | Identifier separation proves crosswalk/alias outputs | Identity/public codes | Executable transforms for internal/public/legacy aliases | Valid crosswalk joins pass | Public code grammar/publication without authority fails | ADR-005/RFI-002 | No public issuance | Transform and publication-gate tests | RFI-002 open |
| AC-07 | Lifecycle policy is populated and positively executed | All lifecycle families | Populate disposable policy from reviewed source | All allowed transitions pass | Invalid/orphan/duplicate/conflicting transitions fail | S06/S11 | No runtime policy change | Lifecycle graph report | F07 |
| AC-08 | Temporal reconstruction covers mutable authoritative entities | Registry/admin/geometry/publication | Complete temporal-strategy register and relationship chain rules | Historical reconstruction passes | cycles, overlap, cross-owner, mismatch fail | ADR-008 | No production migration | Temporal report | F05 |
| AC-09 | Geometry promotion requires institutional authority chain | GIS/evidence/verification | Actor/institution/permission/scope/decision/evidence/quality relations | Authorized promotion passes | wrong actor/scope/decision/evidence/assessment/cycle fails | ADR-009/S09 | No official promotion | Geometry promotion report | F06/RFIs |
| AC-10 | Naming history and multilingual official names tested | Registry/UI | Scenario-specific name history | Valid multilingual/current official name passes | duplicate/current/retired owner invalid cases fail | S06/S10 | No UI code change | Scenario/name report | F04/F10 |
| AC-11 | Source lineage reconciles source to target/archive/evidence | Evidence/audit/data | Executable transform fixtures | Source row to target/archive/evidence passes | Missing archive/evidence/final FK fails | S06/S11 | No data migration | Transform report | F02 |
| AC-12 | Data classification is reviewed, not keyword-only | Security/API/data | Reviewed classifications and owner/status | Reviewed field classes pass | default/inferred-only class fails | S08/S11 | No production data | Classification report | F08/F12 |
| AC-13 | Controlled vocab/lifecycle binding is executable | Data/API | Graph and field binding checks | Every lifecycle family bound and reachable | orphan/re-entry/terminal violations fail | S06/S11 | No runtime code | Lifecycle report | F07 |
| AC-14 | Integrity constraints are semantically proven | SQL/GIS/data | Named physical/semantic assertions | Constraints/triggers execute as intended | invalid action succeeds => test suite fails | S11 | Disposable DB only | Corrected negative harness report | F10/F12 |
| AC-15 | API projection compatibility is independent and field-complete | API/security/frontend/partners | Human-reviewed expected policy/projection registry | Observed implementation matches reviewed registry | AST-derived/unreviewed/dynamic-empty fields fail | S08 | No API runtime change | API projection report | F08 |
| AC-16 | No-loss mapping is executable | Data/migration | Source-to-target transform fixtures | Values/relationships/counts reconcile | pseudo assertion or relationship loss fails | S06/S11 | Future migration only | Transform report | F02/F12 |
| AC-17 | Convergence units are implementation-authority ready after F02 | Migration/planning | Hand-reviewed named units after executable transforms | Unit validation SQL/cutover gates pass | generic inherited controls fail | S07/S31 | No migration execution | Convergence report | F09 depends on F02 |
| AC-18 | Seven representative scenarios are independent and specific | Registry/GIS/publication/API | Scenario-specific builders/assertions | Each scenario expected outcome passes | irrelevant shells/missing projections fail | S06/S11 | Disposable DB only | Scenario report | F10 |
| AC-19 | Scale/index rationale remains bounded | Performance/planning | Keep unapproved scale explicit and owner-gated | Assumptions labelled with source/confidence | national-scale claim without owner fails | S29/S31 | No rollout claim | Plan/report text | RFI/owner pending |
| AC-20 | Draft physical schema coherent with metadata | SQL/model | Metadata-to-catalog parity named assertions | Type/nullability/default/FK/check/index/trigger parity passes | missing parity for any field fails | S06/S11 | Disposable DB only | Catalog parity report | F12 |
| AC-21 | ADRs stay proposed until evidence passes | Architecture | Reconcile claims to named assertions after F02/F04–F10/F12 | ADR evidence matrix complete | ADR accepted or aggregate PASS-only evidence fails | S04/S13 | No authority overclaim | ADR matrix | F11 |
| AC-22 | No runtime behavior change in PR #7 | GitHub/scope | Scope guard remains clean | Changed-path guard passes | prohibited path changed fails submission | S12/S14 | PR #8 external dependency stated | Git diff/CI evidence | F13 external condition |

## 7. Expected changed paths

### Add

- `docs/agent/tasks/NLI-WO-002-review-07-task-context-pack.md`
- `docs/agent/tasks/NLI-WO-002-review-07-finding-resolution-matrix.md`
- Additional design evidence reports under `docs/sda/data-model/**` if required by remediation.

### Modify

- `docs/sda/data-model/scripts/review04_design_pipeline.py`
- `docs/sda/data-model/scripts/design_consistency_check.py`
- Generated/regenerated model reports under `docs/sda/data-model/**`
- `docs/sda/reviews/NLI-WO-002-review-07.md` resolution-log section only, after evidence exists
- `docs/sda/evidence/NLI-WO-002-pull-request-evidence.md` / PR body evidence after exact-head CI

### Remove/deprecate

- None planned. Any deprecation must be explicit and evidence-backed.

## 8. Effect assessment

- **System architecture/domain boundaries:** design-only; singular canonical registry authority must remain explicit.
- **Database/migrations/reference data/fixtures:** disposable design SQL/fixtures only; no executable runtime migrations.
- **API/contracts/identity/authorization:** current API inventory/projection evidence only; no API runtime changes.
- **Security/privacy/audit/evidence:** classification/projection/evidence semantics strengthened; no secrets or production data.
- **GIS/geometry/provenance:** promotion authority/evidence/scope model strengthened; no official boundary/publication authority.
- **Frontend/design system/accessibility/localization:** future projection semantics only; no UI code.
- **Backend/domain logic/transactions:** no runtime domain service changes.
- **Citizen/public services:** public-safe projection rules only; no public release.
- **Registry/operator case management:** canonical case/registry model evidence only.
- **Field/mobile/offline synchronization:** candidate/evidence/offline semantics only.
- **Verification/quality/recapture:** signal versus authorized decision separation strengthened.
- **Publication/corrections/certificates/signage:** release manifest/gates only; no signage/certificate generation.
- **Agency integrations/notifications/interoperability:** partner projection boundaries only.
- **Imports/exports/workers/batch jobs:** future migration/import/export unit planning only.
- **Reporting/analytics/data products:** no official metric/public data-product claim.
- **Infrastructure/environments/platform:** no platform change.
- **Performance/scalability/resilience:** assumptions stay unapproved; no capacity claim.
- **Operations/backup/restore/DR:** future gates only.
- **Support/training/change adoption:** no rollout/training readiness claim.
- **Programme roadmap/release/rollout:** NLI-WO-002B remains blocked.

## 9. Decisions and RFIs

| Decision | Classification | Owner | ADR/RFI | Blocking? |
|---|---|---|---|---|
| Public-code grammar/issuance | Institutional | Programme Owner / Registry Authority | RFI-002 | Blocks public issuance and executable implementation in affected area |
| Official admin hierarchy/boundaries | Institutional/GIS | GIS/Data Authority | RFI-003 | Blocks officialization/publication |
| Publication authority/effective date | Institutional/publication | Publication Authority / Programme Owner | RFI-004 | Blocks public/signage/certificate release |
| Parcel/cadastre authority | Legal/GIS/privacy | Legal/Privacy Authority / GIS Authority | RFI-005 | Blocks authoritative parcel/cadastre treatment |
| Published-looking pilot records | SDA/publication | SDA / Publication Authority | RFI-006 | Blocks production treatment of existing publication-like data |
| ADR acceptance for 005–009 | SDA architecture | SDA | ADR-005–009/F11 | Blocked until named assertions close F02/F04–F10/F12 |

## 10. Execution sequence

1. Correct the negative-test harness first; add a regression demonstrating that a successful invalid action fails the suite.
2. Run the harness regression locally and regenerate target schema/fixture reports.
3. Resolve F02 executable transformation/no-loss/reference/archive/classification defects.
4. Resolve F04/F05 cardinality, relationship, temporal, name, merge/retirement defects.
5. Resolve F06/F07 geometry promotion and lifecycle graph execution defects.
6. Resolve F08 API policy/projection independence and field completeness.
7. Resolve F09 convergence units only after F02 executable transforms are credible.
8. Resolve F10 scenario-specific datasets/assertions and corrected negative evidence.
9. Resolve F11 ADR evidence matrix and proposed/conditional status truthfulness.
10. Resolve F12 named assertion/reporting limitations and CI fail-closed behavior.
11. Regenerate artifacts, update Review 07 resolution log only, update evidence/PR metadata, push, wait for exact-head CI, and request Review 08.

## 11. Recovery and compatibility

- **Rollback safe:** documentation/design scripts only; revert commits if remediation is wrong.
- **Forward recovery:** add follow-up design correction commits; no production data effects.
- **Idempotency:** regeneration must be deterministic and clean after repeated runs.
- **Breaking/compatibility effect:** no runtime/API/schema break in PR #7; future work-order compatibility decisions remain separate.
- **External effects:** GitHub branch/PR/CI only.
- **Monitoring/alert changes:** none.
- **Support/training/communication:** none beyond PR evidence/handoff.
- **Rollout/cutover gate:** not applicable; NLI-WO-002B unauthorized.

## 12. Submission plan

- **Draft PR target:** PR #7 remains draft/open/unmerged.
- **Required workflows/jobs:** `agent-skills-ci`, `api-ci`, `frontend-ci`, and SDA data-model/design CI jobs present for exact head.
- **Expected exact-head evidence:** implementation SHA, workflow run IDs, job IDs/conclusions, changed-path proof, deterministic regeneration output.
- **Required runtime/recovery artifacts:** disposable PostGIS design validation only; no browser/runtime production artifacts.
- **Review request format:** request SDA Review 08 against the exact implementation/model SHA after green CI and current PR metadata.

## 13. Agent declaration

- [x] Authority and scope are explicit.
- [x] Whole-project impact is mapped using `PROJECT-COVERAGE-MATRIX.md`.
- [x] Applicable S01–S16 and S17–S31 skills are selected.
- [x] Skills considered but not applicable have rationale.
- [x] Every criterion has specific positive and negative evidence planned.
- [x] Expected evidence must be independent from observed generation.
- [x] Reserved decisions are not silently embedded.
- [x] Out-of-scope defects will use S14.
- [x] Operational, support, training, rollout, and recovery effects are addressed where applicable.
- [x] No prohibited path or behavior is planned.
