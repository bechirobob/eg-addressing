# Agent Task Context Pack — NLI-WO-002 Review 06 Remediation After Skill-Pack Merge

**Repository:** `bechirobob/eg-addressing`  
**Base branch/SHA:** `origin/main` @ `0a60bbdadd81afab818bfdff3d3962f6b50b47eb`  
**Task branch/SHA:** `nli/wo-002-canonical-location-model` local @ `257318899a191c0fbca6953f97b1a6762b3086c3` after merging `origin/main`  
**Remote PR branch/SHA before checkpoint push:** `origin/nli/wo-002-canonical-location-model` @ `2789194a1949ceccdd2c34210461f46ddf65dbb7`  
**PR/issue:** PR #7 — `https://github.com/bechirobob/eg-addressing/pull/7` — open, draft, unmerged  
**Working tree at preparation:** clean immediately after main merge; this file and the finding matrix are the first checkpoint artifacts  
**Prepared at:** `2026-07-14T15:19:30Z`

## 1. Authority

- **Programme:** Equatorial Guinea National Location Infrastructure (NLI), national addressing as first service.
- **Programme Owner instruction:** use the merged repository-native delivery-agent skill pack before continuing PR #7; do not modify design/implementation files until the task context pack and finding-resolution matrix exist.
- **Active work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`.
- **Current SDA outcome/review:** `docs/sda/reviews/NLI-WO-002-review-06.md`, outcome `REWORK REQUIRED`.
- **Change class:** Class B for canonical data-model/design-authority remediation; Class C / maintenance-controlled for the separated migration-ledger race fix under NLI-WO-001 controls.
- **Applicable ADRs:** accepted ADR-001, ADR-002, ADR-003, ADR-004; proposed Review 07 ADR-005 through ADR-009 must remain proposed until SDA acceptance.
- **Mandatory standards:** `data-and-migrations.md`, `gis-and-location-data.md`, `api-design.md`, `audit-and-evidence.md`, `security.md`, `documentation-and-records.md`.
- **Readiness boundary:** architecture/data-model authority only. No executable schema migration, runtime behavior change, production deployment, publication, public-code issuance, or NLI-WO-002B authorization.

## 2. Selected skills

| Skill | Trigger | Required output |
|---|---|---|
| S01 | Every task; branch and PR state changed by main merge | Authority header, scope matrix, PR/branch state, selected skills |
| S02 | Main merge introduces repo-native operating layer and review findings proved prior impact assessment gaps | Domain/component impact map and current implementation surfaces inspected |
| S03 | NLI-WO-002 AC-01 through AC-22 and Review 06 remediation planning | Criterion-specific plan, tests, evidence, RFIs |
| S05 | Review 06 findings depend on schema/catalog, route, role, policy, dynamic response and current-value discovery | Catalog/OpenAPI/source-backed inventory boundaries |
| S06 | Canonical model, transformation registry, target SQL, scenarios and convergence are the core work | Typed target model, reviewed mapping, executable disposable design validation |
| S08 | API projection, route policy, auth roles, classification and dynamic response contracts are finding F08 scope | Method/path/handler policy matrix and field-level projection contracts |
| S09 | Geometry promotion, provenance, publication lock and evidence chain are findings F05/F06/F10 scope | Geometry/evidence/publication authority checks |
| S11 | Every `READY FOR SDA REVIEW` claim must be backed by executable assertions | Claim-to-assertion matrix, positive/negative tests, limitations |
| S12 | Branch merge, PR body, exact-head CI, workflow/job IDs and Review 07 request | Exact-head proof and accurate GitHub submission status |
| S13 | Latest SDA review is `REWORK REQUIRED` with findings F02 and F04-F13 | Finding-specific root causes, corrections, tests, evidence, protected resolution-log update |
| S14 | Review 06 F13: runtime migration-ledger race fix appeared in design-only PR | Separate maintenance PR, restored PR #7 boundary, dependency note |
| S16 | Context shift after skill-pack merge and before any completion/review claim | Self-audit, stale metadata check, truthful handoff |

### Skills considered but not invoked for this checkpoint

| Skill | Reason not invoked now |
|---|---|
| S04 | No new RFI or ADR-authority change is being made in this checkpoint; if later work changes reserved decisions, invoke before editing. |
| S07 | PR #7 is design-only and must not add executable migrations; S07 applies only to the separate maintenance PR if migration lifecycle code changes continue. |
| S10 | No UI/workflow screen is planned for this checkpoint; invoke if public/operator workflow evidence changes. |
| S15 | No deployment, operations, backup, restore, or DR change is planned inside PR #7; invoke if maintenance/release operations change. |

## 3. Scope matrix

### In scope

- `docs/agent/tasks/NLI-WO-002-review-06-task-context-pack.md`
- `docs/agent/tasks/NLI-WO-002-review-06-finding-resolution-matrix.md`
- Repository-native skill-pack merge from `origin/main` into `nli/wo-002-canonical-location-model`
- Review 06 resolution-log section only, if later remediation evidence needs updates
- NLI-WO-002 design artifacts under `docs/sda/data-model/`, proposed ADRs 005–009, RFIs, and PR evidence only when specifically mapped to Review 06 findings

### Supporting evidence

- `.github/workflows/api-ci.yml` only where already used as SDA design CI evidence and explicitly in PR #7 changed-path proof
- `docs/agent/templates/*` as source templates, not as filled task records
- `docs/sda/evidence/NLI-WO-002-pull-request-evidence.md`
- Exact-head CI workflow and job IDs from GitHub
- Current OpenAPI/catalog/generated design reports produced by deterministic scripts

### Separate maintenance

- `infra/scripts/migrate.py` advisory-lock/migration-ledger race fix — already isolated to maintenance PR #8 and must not reappear in PR #7
- Any executable migration, runtime code, API behavior, deployment, backup/restore or operational fix found during PR #7 remediation

### Prohibited

- `services/api/**`
- `infra/scripts/migrate.py` inside PR #7
- `infra/migrations/**`
- `apps/**`
- `infra/docker/**`
- `data/**`
- `.env*`
- Editing Review 06 outcome, finding observations, required resolutions, acceptance-criterion decisions, or reviewer disposition tables
- Marking SDA findings resolved/accepted; agent status is only `READY FOR SDA REVIEW`
- Runtime schema changes, production DDL, public-code issuance, publication enablement, national-production claims, NLI-WO-002B implementation

## 4. Current-state evidence inspected

| Domain/object | Source path or command | What it establishes |
|---|---|---|
| Repository authority | `AGENTS.md`, `docs/sda/README.md`, `docs/agent/README.md`, `docs/agent/master-operating-protocol.md`, `docs/agent/skill-manifest.yaml` | SDA precedence, skill routing, exact-head and self-audit obligations |
| Active work order | `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md` | Design-only boundary, AC-01 through AC-22, no runtime code/migration authority |
| Latest review | `docs/sda/reviews/NLI-WO-002-review-06.md` | Outcome `REWORK REQUIRED`; open findings F02 and F04-F13; protected sections and resolution-log boundary |
| Accepted lifecycle authority | `docs/sda/work-orders/NLI-WO-001-closeout.md`, `docs/sda/reviews/NLI-WO-001-review-04.md`, ADR-003 | Maintenance PR #8 must preserve migration-only lifecycle controls |
| Architecture authority | ADR-001 through ADR-004, proposed ADR-005 through ADR-009 | Accepted platform constraints and proposed model decisions requiring Review 07 acceptance |
| Mandatory standards | SDA standards for data/migrations, GIS/location, API, audit/evidence, security, documentation | Domain-specific evidence gates and prohibited shortcuts |
| PR state | GitHub PR #7 API read | PR #7 open/draft/unmerged, remote head `2789194a1949ceccdd2c34210461f46ddf65dbb7` before checkpoint push |
| Branch state | `git fetch`, `git merge origin/main`, `git rev-parse`, `git diff --name-status origin/main...HEAD` | Local PR branch contains skill-pack merge at `257318899a191c0fbca6953f97b1a6762b3086c3`; PR design diff remains docs/SDA plus workflow evidence |
| Current remediation scripts | `docs/sda/data-model/scripts/review04_design_pipeline.py`, `design_consistency_check.py` | Current deterministic generator/checker surfaces and known Review 07 semantic-check claims |

## 5. Acceptance-criterion plan

| AC | Observable result | Change/model | Positive test | Negative test | Authority check | Evidence | Risk/RFI |
|---|---|---|---|---|---|---|---|
| AC-01 | Every current operational field has authority/source/classification/disposition | Preserve catalog-derived current inventory | Disposable PostGIS catalog generation succeeds | Unknown current field rejected by reviewed registry | S05; WO section 5.1 | current-state inventory, mapping registry, CI `sda-design-model` | Generated inference must not replace reviewed meaning |
| AC-02 | One canonical location authority remains explicit | `location_record` sole anchor and crosswalks | Target model and subject/crosswalk assertions | Competing canonical anchor detection | ADR-002, WO 5.5 | target model, design checker | None new unless dual authority found |
| AC-03 | Admin identity/code/name/history explicit | Admin unit identity separate from code/name history | Target schema/catalog validation | Overlap or stale-code authority check | ADR-006, GIS/data standards | target registry, ADR-006 | Official admin authority remains provisional |
| AC-04 | Operational areas not administrative authority | `operational_area` lifecycle and model remain separate | Lifecycle/catalog validation | Conflation guard in checker/model review | WO 5.3, target architecture | controlled vocabularies | None new |
| AC-05 | Actual record types have required/min/max role rules | Record-object matrix keyed by target `record_type` values | Positive fixtures for record/object roles | Missing/invalid/excess role negatives | S06, Review F04 | target SQL, semantic checker | Matrix must not use placeholder `standard-address` |
| AC-06 | Internal/public/legacy IDs separated | ADR-005 and crosswalk joins remain explicit | Crosswalk/alias assertions | Public code as PK/identity guard | ADR-005, data standard | transformation registry, ADR-005 | Public-code grammar remains RFI/future authority |
| AC-07 | Lifecycle graphs separated and executable | Transition policy metadata and bindings | Positive transition checks | Forbidden/orphan/terminality checks | S06, Review F07 | lifecycle registry, checker | Full implementation enforcement is future WO-002B |
| AC-08 | Temporal reconstruction supported | Version/alias/geometry chains and release snapshots | Scenario reconstruction assertions | Cycle/reciprocal/cross-owner negatives | ADR-008 | target SQL and scenario evidence | Avoid overclaiming production behavior |
| AC-09 | Geometry provenance/promotion authority explicit | Geometry observation/version, decision/evidence/scope | Valid promotion scenario | Missing/unauthorized/cross-subject/wrong type negatives | ADR-009, GIS standard | target SQL, geometry fixtures | Publication/official boundary authority remains pending |
| AC-10 | Multilingual/name integrity preserved | `name_record` subject and current-name rules | Name-record positive fixture | Missing subject/duplicate current name negative | WO 5.10 | target schema validation | Full localization UI is out of scope |
| AC-11 | Source/authority lineage traceable | Source archive, evidence, decision, crosswalk fields | Transformation value/relationship assertions | Hash-only/no-archive guard | audit/evidence standard | reviewed transformation registry | Institutional retention still future authority |
| AC-12 | Classification/projection explicit | Field/API projection contracts include classification | Contract completeness checks | Keyword-only/default classification rejected | security/API standards | API projection contracts | Privacy policy remains broader future work |
| AC-13 | Controlled vocabularies documented | Vocabulary registry and transition graphs | Vocabulary binding checks | Unknown status/type rejected | data standard | controlled vocabularies | None new |
| AC-14 | Integrity constraints identified and executable in disposable SQL | Draft SQL expresses FK/check/unique/exclusion/triggers | Disposable PostGIS execution and catalog parity | Semantic negative fixtures | data/GIS standards | target schema validation | Not production DDL |
| AC-15 | API projection compatibility mapped | Route policies and field contracts | Method/path/handler/role contract checks | Wrong handler/method/dynamic empty contract guard | S08/API standard | route/projection registries | No runtime API contract change in PR #7 |
| AC-16 | Current-to-target no-loss mapping complete | Reviewed transformation rows with executable assertions | Value/relationship transform checks | Pseudo-ASSERT/invalid controlled map rejected | S06/S11 | transformation registry and checker | Unknown current values must surface, not coerce |
| AC-17 | Expand–migrate–contract plan derived from accepted transforms | Convergence units use accepted transformation groups | Dependency/order validation | Generic unit/pseudo-validation guard | ADR-003/data standard | schema convergence plan | WO-002B still unauthorized |
| AC-18 | Seven national scenarios have scenario-specific proof | Scenario builders/fixtures and expected projections | Seven positives insert and validate | Seven negative semantic cases execute | S06/S11 | representative records, target report | Expected outcomes must stay independent from observed generation |
| AC-19 | Scale/index assumptions explicit and bounded | Scale notes remain assumptions, not approval | Index/catalog rationale checks | Production-readiness/SLA overclaim guard | risk register, standards | convergence plan | Owner approval remains future RFI/condition |
| AC-20 | Draft SQL coherent and traceable | Non-executable design SQL matches metadata | SQL executes in disposable PostGIS | Catalog parity/semantic guard failures | WO design boundary | draft SQL and validation report | Must not become migration |
| AC-21 | ADR/RFI pack decision-complete for design phase | Proposed ADRs 005–009 and RFIs remain current | ADR claim-to-assertion checks | Stale status/unsupported claim guard | documentation standard | ADRs and checker | ADRs not accepted until SDA Review 07 |
| AC-22 | No runtime behavior change in PR #7 | Runtime fix remains in PR #8 only | Changed-path guard | Any prohibited path change fails submission | WO out-of-scope; S14 | git diff, PR #8 link | PR #8 remains separate maintenance dependency |

## 6. Expected changed paths

### Add

- `docs/agent/tasks/NLI-WO-002-review-06-task-context-pack.md`
- `docs/agent/tasks/NLI-WO-002-review-06-finding-resolution-matrix.md`

### Modify

- Possible later, only if a checkpoint finds stale metadata after the main merge:
  - `docs/sda/evidence/NLI-WO-002-pull-request-evidence.md`
  - PR #7 body and immutable PR comment/metadata
  - Review 06 resolution-log section only

### Remove/deprecate

- None planned in this checkpoint.

## 7. Data/API/security/GIS/workflow/operations effects

- **Database/migrations:** PR #7 must remain design-only; no executable migrations or runtime schema changes. Disposable PostGIS validation is supporting evidence only.
- **Reference data/fixtures:** scenario fixtures are non-production design validation; no pilot/production fixture mutation.
- **API/contracts:** API projection and route-policy registries are design/evidence artifacts; no runtime API contract change authorized.
- **Identity/authorization:** role/policy analysis is design evidence only; no new runtime role/permission/scope.
- **Security/privacy/audit:** classifications and evidence/publication controls are modelled; no production secrets, data exports, or retention changes.
- **GIS/evidence/publication:** geometry authority and publication gating are modelled; no official publication, signage, certificates, or public-code issuance.
- **UI/accessibility/localization:** no UI files planned; public/operator workflow changes are out of scope.
- **Deployment/operations/DR:** no deployment or DR change in PR #7; maintenance PR #8 remains the only runtime lifecycle dependency.
- **Documentation:** controlled docs/evidence are affected; review-owned text remains protected.

## 8. Decisions and RFIs

| Decision | Classification | Owner | ADR/RFI | Blocking? |
|---|---|---|---|---|
| National public-code grammar and issuance | Programme/SDA/GIS authority | Programme Owner + SDA | Existing RFI | Blocks publication/issuance, not design remediation |
| Administrative hierarchy/boundary authority | GIS/data authority | Government data/GIS authority | Existing RFI | Blocks official authority claim |
| Publication authority/effective date | Programme/publication authority | Programme Owner | Existing RFI | Blocks publication readiness |
| Parcel reference authority | Institutional/cadastre authority | Future named authority | Existing RFI | Blocks land-title/cadastre claims |
| Existing published-looking pilot records | SDA/programme | SDA + Programme Owner | Existing RFI | Future convergence handling |
| Maintenance PR #8 acceptance/merge order | Class C maintenance / NLI-WO-001 controls | SDA/platform engineering | PR #8 | Separate dependency; not required to duplicate into PR #7 |

## 9. Execution sequence

1. Complete this task context pack and finding-resolution matrix before any design/implementation edits.
2. Run repository skill-pack validation after the merge from main.
3. Verify PR #7 diff still excludes prohibited runtime paths after main merge.
4. If stale metadata appears from the main merge, update only checkpoint/PR evidence surfaces; do not edit design artifacts without a finding-specific plan row.
5. If any Review 06 finding requires additional changes, handle one finding at a time with root cause, correction, assertion, commit and evidence.
6. Run self-audit before any renewed Review 07 request.
7. Push the merge/checkpoint branch only after local checks pass, then verify remote head and exact-head CI.

## 10. Recovery and compatibility

- **Rollback safe:** process docs and merge commit can be reverted before submission if needed; design/runtime behavior is not changed by this checkpoint.
- **Forward recovery:** if CI fails after merge, inspect exact failing job and fix only the governing generated/source artifact or isolate runtime defects via S14.
- **Idempotency:** context pack/matrix are deterministic documentation records; rerunning design generators must not alter their content.
- **Breaking/compatibility effect:** none for runtime/API/UI.
- **External effects:** GitHub PR metadata/CI only after push.

## 11. Submission plan

- **Draft PR target:** PR #7 against `main`; remains draft.
- **Required workflows/jobs:** `api-ci` including `sda-design-model`, `migration-lifecycle`, `api-image-runtime`, `api-tests`; `frontend-ci` including `frontend`; new `agent-skills-ci` if it runs for this branch after merge.
- **Expected exact-head evidence:** local and remote SHA, PR draft/open/unmerged state, changed-path guard, workflow run IDs, job IDs, conclusions, Review 07 request comment if a new request is needed.
- **Review request format:** use S12 exact-head sequence and S16 report; do not cite CI from an older commit.

## 12. Agent declaration

- [x] Authority and scope are explicit.
- [x] Every criterion has specific positive and negative evidence planned.
- [x] Expected evidence is independent from observed generation.
- [x] Reserved decisions are not silently embedded.
- [x] Out-of-scope defects will use S14.
- [x] No prohibited path is planned.
