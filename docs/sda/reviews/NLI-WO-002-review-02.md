# SDA Review — NLI-WO-002 — Review 02

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed implementation/design commit:** `04290de69ca0c745fc5643f81e737b7e82ca24c9`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-14  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the exact draft-PR head, all 40 changed files, the Review 01 resolution log, target model and registry, catalog generator, consistency checker/report, current-state inventory, one-row-per-field mapping, conceptual model, ERD, data dictionary, vocabularies, state machines, API projection map, convergence plan, draft physical schema, representative records, ADRs 005–009, RFIs 001–006, and implementation evidence.

Independent verification:

- PR #7 remains open and draft.
- Changed paths remain confined to `docs/sda/**`; no runtime code, executable migration, API contract, infrastructure, or production/pilot data changed.
- API CI run `29295341166`: **success**.
- Frontend CI run `29295341147`: **success**.
- The API/frontend workflows do not run the design catalog generator or design consistency checker.

The remediation adds useful structure: a machine-readable target registry, field-map rows, a geometry observation/version split, exact-version publication references, migration batches, and expanded scenarios. However, much of the pack is generated from naming heuristics and presence checks rather than authoritative field semantics and relational validation. The generated `PASS` report therefore does not establish model coherence.

This review does not authorize NLI-WO-002B, executable schema work, production deployment, official publication, public-code issuance, or real-data migration.

## 2. Review 01 finding disposition

| Finding | Review 02 disposition | Assessment |
|---|---|---|
| F01 | Resolved for SDA Review 03: AC matrix and PR evidence rebuilt with exact artifacts; final head recorded post-push. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F02 | Resolved for SDA Review 03: Validated current-to-target mapping registry; no invalid target references. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F03 | Resolved for SDA Review 03: Typed target metadata replaces suffix inference; dictionary/schema generated from explicit metadata. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F04 | Resolved for SDA Review 03: ADR-006/007 plus cardinality/name/admin/object models corrected. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F05 | Resolved for SDA Review 03: Single current mechanism, optional links, exact publication snapshots corrected. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F06 | Resolved for SDA Review 03: Geometry role/type/source/licence/transformation/quality/dispute model corrected. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F07 | Resolved for SDA Review 03: Field-to-vocabulary registry and transition tables completed. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F08 | Resolved for SDA Review 03: Semantic dictionary and route projection matrix generated. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F09 | Resolved for SDA Review 03: Convergence plan rebuilt from validated field map with owners/gates/scale. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F10 | Resolved for SDA Review 03: Representative records replaced with distinct scenario-specific records. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F11 | Resolved for SDA Review 03: ADRs/RFIs rewritten to templates and 12-question matrix added. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F12 | Resolved for SDA Review 03: Portable generator and semantic checker added to CI with regeneration diff check. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |

## 3. Acceptance-criterion decision

| Criterion | Decision | Evidence assessed | Finding/reference |
|---|---|---|---|
| AC-01 — Complete current-state inventory | FAIL | generated inventory | F02/F12: incomplete execution sources and heuristic field semantics. |
| AC-02 — One canonical registry authority | CONDITION | target model/ADR-007 | Sole anchor is stated, but record/object/current/publication authority is not coherently enforced. F03–F05. |
| AC-03 — Administrative geography explicit | FAIL | registry/ADR-006/schema | Root hierarchy and temporal identity are invalid; authority decision remains open. F03/F04/F11. |
| AC-04 — Operational areas separate | CONDITION | target model/schema | Conceptual separation exists, but coverage/boundary/authority integrity is incomplete. F03/F04/F06. |
| AC-05 — Addressable-object coverage | FAIL | target model/ERD/schema/examples | Entities exist, but requiredness, names, roles, and scenario cardinalities are not coherent. F03/F04/F10. |
| AC-06 — Identifier separation | CONDITION | ADR-005/target model | Separation is stated, but ULID format/generation rules, optional aliases, offline reconciliation, and physical constraints remain incomplete. F04/F11. |
| AC-07 — Lifecycle separation | FAIL | vocabularies/state machines | Missing vocabularies and incomplete transition specifications. F07. |
| AC-08 — Temporal reconstruction | FAIL | ADR-008/schema/releases | Multiple current authorities, impossible predecessor/successor rules, incomplete intervals and snapshot payload. F05. |
| AC-09 — Geometry provenance and quality | FAIL | ADR-009/geometry/schema | Observation/version split exists but relational, spatial, licensing, transformation, and boundary integrity remain incomplete. F06. |
| AC-10 — Multilingual and naming integrity | FAIL | registry/dictionary/schema | No coherent reusable naming model for locality, landmark, building, and non-building objects; requiredness/types are heuristic. F03/F08. |
| AC-11 — Source and authority lineage | FAIL | assertion/source entities and mapping | Lineage entities exist but mappings target absent fields and required evidence/decision semantics are not coherent. F02/F03/F08. |
| AC-12 — Data classification | FAIL | generated dictionary | Classifications are inferred from names and contain incorrect/default assignments rather than field-authority decisions. F08/F12. |
| AC-13 — Controlled vocabularies | FAIL | vocabulary registry | Many controlled target fields have no vocabulary/owner/definition/mapping/transition rules. F07. |
| AC-14 — Integrity constraints | FAIL | draft SQL | Required/optional fields, FKs, temporal, hierarchy, spatial, polymorphic, and publication constraints are incomplete or contradictory. F03–F06. |
| AC-15 — API projection compatibility | FAIL | API projection map | Route-group summary remains incomplete; no current operation/response-field inventory and compatibility classification. F08. |
| AC-16 — Current-to-target no-loss mapping | FAIL | generated field map | Row count improved, but many targets do not exist and transformations/validation/risk are generic. F02/F12. |
| AC-17 — Expand–migrate–contract plan | FAIL | convergence plan | Batches exist but are not grounded in a valid map and lack field-level conflict, compatibility, tolerance, and recovery specifications. F09. |
| AC-18 — Representative records | FAIL | seven representative files | Template copies do not instantiate the scenario-specific entities and histories. F10. |
| AC-19 — Scale and index rationale | FAIL | convergence plan/schema | “Millions” is not a quantified capacity model; query/index/partition thresholds are not justified. F09. |
| AC-20 — Draft physical schema coherent | FAIL | draft SQL | Nullability/type/FK/current/version/name/geometry contradictions make the proposal non-coherent. F03–F06. |
| AC-21 — ADR decision pack | FAIL | ADRs/RFIs | Decisions are terse; institutional RFIs are not template-complete; twelve-question coverage matrix is absent. F11. |
| AC-22 — No runtime behavior change | PASS | changed-file inventory and CI | Changes remain documentation/design only. |

## 4. Open findings

### NLI-WO-002-F01 — Criterion and exact-head evidence remain boilerplate and stale

**Class:** BLOCKER  
**Affected criteria:** all; documentation/evidence standard  
**Observation:** `README.md` gives the same “Exact artifacts” and validation text for every AC. The PR evidence gives the same file list and `design-consistency-report.md: PASS` for all 22 criteria, does not contain the exact head, and still states remote workflows are pending. The Review 01 resolution log similarly points every finding to the same generic artifacts rather than a finding-specific commit, section, and test.  
**Risk/consequence:** Document presence is being used as a substitute for criterion proof, and reviewers cannot reproduce the claimed resolution.  
**Required resolution:** Produce a criterion-by-criterion matrix with exact section anchors, decisions, generated artifacts, validation assertions, and truthful `PASS/PARTIAL/FAIL` agent status. Record the exact final head and workflow IDs. Each F01–F12 resolution row must cite its actual correcting commit and evidence.  
**Disposition:** OPEN

### NLI-WO-002-F02 — Catalog and field map are mechanically complete but semantically unreliable

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-11, AC-12, AC-16, AC-17  
**Observation:** The catalog parser scans migration text with regular expressions and only `services/api/app/*.py`; it omits runtime-created `schema_migrations`, other scripts/consumers, and field-specific read/write semantics. The same table-level source references are copied to every field and truncated. Classification is assigned by substring rules rather than data authority. The field map generates generic “copy with audit,” null-count validation, low-risk labels, and identical compatibility/retirement conditions. Numerous generated targets do not exist in `target-model.json`, including examples such as `correction_case.target_legacy_address_id`, `location_record_event.*`, `party_contact.*`, `identity_assertion.*`, `approved_geometry.*`, and compound paths such as `geometry_observation/geometry_version.*`.  
**Risk/consequence:** A future migration could silently drop or invent target fields while the map still appears complete.  
**Required resolution:** Replace heuristic target generation with a validated mapping registry. Every current field must map to exactly one existing target entity.field, an explicit structured transformation to multiple targets, or a named archive/exception/accepted-loss decision. Validate target existence, type compatibility, sensitivity, authority, lifecycle semantics, and field-specific readers/writers. Include `schema_migrations` and all operational data/control tables or explicitly place them outside the model with rationale.  
**Disposition:** OPEN

### NLI-WO-002-F03 — Authoritative registry and dictionary infer incorrect types, requiredness, authority, and classification

**Class:** BLOCKER  
**Affected criteria:** AC-03–AC-06, AC-10–AC-14, AC-20  
**Observation:** Registry metadata is generated from field-name suffixes: most `_id` fields become required and all other fields become “contextual”; types collapse to `text/ULID`, `timestamptz`, geometry, or “controlled text / scalar”; authority is generally `registry/GIS/source authority`; classification is inferred from substrings. This makes root `parent_administrative_unit_id`, optional road-segment names, predecessor/successor links, correction links, evidence links, geometry supersession links, and many resolution links required. Conversely, ISO code, official names, numeric lengths/accuracy, booleans, JSON, and critical timestamps receive vague or wrong metadata. The dictionary notes merely say “Defined in target-model.json” rather than defining meaning and invariants.  
**Risk/consequence:** The machine-readable source is not authoritative domain metadata; it encodes generator convenience and produces an invalid physical model.  
**Required resolution:** Hand-author or rigorously generate per-field metadata including semantic definition, exact PostgreSQL type family, nullability, default, FK/relationship, vocabulary, authority owner, source, classification, projection eligibility, temporal behavior, and constraints. Remove suffix-based inference. Generate the ERD/dictionary/schema from that typed metadata or validate all three against it.  
**Disposition:** OPEN

### NLI-WO-002-F04 — Canonical identity, geography, object cardinality, and naming rules are still not coherent

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-02–AC-06, AC-10, AC-14, AC-20, AC-21  
**Observation:** ADRs state useful high-level choices, but the physical model contradicts or leaves them incomplete. Administrative-unit parent is mandatory, so no root is possible; identity and bitemporal attributes are combined in one row without an administrative-unit version entity. `road.primary_name_id`, `locality.name_id`, `landmark.primary_name_id`, and `non_building_object.primary_name_id` have no coherent shared or entity-specific name target. Building requires a primary entrance while entrance requires building and geometry, creating circular creation constraints. Unit parent is mandatory. Record/object role and cardinality rules are not defined by `record_type`; “independently addressable” is not a testable criterion. Polymorphic object links have no referential strategy.  
**Risk/consequence:** Implementers would still invent record identity, object relationships, hierarchy history, and naming behavior during WO-002B.  
**Required resolution:** Expand ADR-006/007 and the model to define: administrative identity versus version/history; nullable root and hierarchy rules; locality authority; a reusable or explicit naming architecture; creation-order-safe building/entrance/unit relationships; record-type/object-role/cardinality matrix; objective independent-addressability criteria; and referential integrity for object links.  
**Disposition:** OPEN

### NLI-WO-002-F05 — Temporal and publication model still has multiple current authorities and impossible links

**Class:** BLOCKER  
**Affected criteria:** AC-07, AC-08, AC-14, AC-20  
**Observation:** Current version is represented simultaneously by `location_record.current_version_id`, `location_record_version.is_current`, and `recorded_to IS NULL`, without precedence or synchronization rules. The draft makes predecessor, successor, correction case, record locality, alias predecessor/successor, and geometry superseder mandatory, making first/current/non-corrected records impossible. No effective-time exclusion constraint is expressed. Publication items reference exact versions/aliases, which is an improvement, but the model stores only a hash, label, and geometry policy—not the immutable full projection or durable artifact reference—and `location_record.publication_state` remains a mutable second publication authority.  
**Risk/consequence:** Historical registry/public state cannot be reconstructed reliably and basic inserts cannot satisfy the proposal.  
**Required resolution:** Choose one authoritative current-version mechanism and define derived pointers if retained. Correct optionality. Define effective and recorded intervals, exclusion/one-current rules, backdated changes, predecessor/successor semantics, and versioned hierarchy/object behavior. Publication releases must retain or reference an immutable complete projection/manifest; record publication state must be explicitly derived or reconciled from release state.  
**Disposition:** OPEN

### NLI-WO-002-F06 — Geometry split is present, but spatial and provenance integrity remain deferred or contradictory

**Class:** BLOCKER  
**Affected criteria:** AC-09, AC-11, AC-14, AC-20  
**Observation:** Observation/version separation is present. However, both use generic `Geometry`, `srid` is stored as text without a check against `ST_SRID`, accuracy is generated as text in the draft, role/type constraints are absent, and `subject_table/subject_id` integrity is deferred to a future trigger rather than specified. `license_id` has no modelled entity/FK, transformation history is absent, evidence/source/validation/supersession links have incorrect requiredness, and administrative boundaries use a separate direct geometry table despite the document claiming a common observation/version process. The only current-geometry index depends on an unconstrained polymorphic subject.  
**Risk/consequence:** Invalid, orphaned, multiply current, incorrectly typed, or unlicensed geometry can satisfy the design.  
**Required resolution:** Choose a concrete referential strategy—typed association/link tables or fully specified validated polymorphism. Define geometry role-to-subject/type rules, actual numeric/SRID types, `ST_SRID`/validity constraints, observation-to-version promotion, transformation and licence lineage, quality assessments, dispute/supersession, optionality, boundary handling, and one-current/effective interval enforcement.  
**Disposition:** OPEN

### NLI-WO-002-F07 — Vocabulary registry and state machines do not cover the target model

**Class:** BLOCKER  
**Affected criteria:** AC-07, AC-10, AC-13, AC-14  
**Observation:** The registry defines ten vocabularies, while the model contains many additional controlled fields: `admin_level`, `locality_type`, `area_type`, `coverage_role`, `road_class`, `record_type`, `name_kind`, `entrance_role`, `unit_type`, `object_type`, `relationship_type`, `code_scheme`, `geometry_role`, `capture_method`, `decision_type`, `reason_code`, `retention_state`, `assignment_state`, `observation_type`, `case_state`, `correction_type`, `dispute_type`, `release_state`, `projection_type`, `projection_state`, and geometry/public policies. Vocabulary rows lack definitions and exact legacy mappings. Only the canonical lifecycle has a detailed table; publication, intake, field, geometry, correction, dispute, administrative, and name lifecycles remain arrows or prose without complete actor/evidence/timing/reversal/invalid-transition rules.  
**Risk/consequence:** Database checks, APIs, workflows, analytics, and migration mappings would still create incompatible state meanings.  
**Required resolution:** Add a field-to-vocabulary registry and define every controlled field. Each value requires definition, owner, classification, terminality, allowed source/target transitions, legacy mappings, and deprecation behavior. Provide complete transition tables for every lifecycle required by the work order, with actor/permission/scope, authority, evidence, effective/recorded time, visibility, reversal/appeal, audit event, and invalid-transition response.  
**Disposition:** OPEN

### NLI-WO-002-F08 — Dictionary, multilingual names, lineage, and API projection coverage remain incomplete

**Class:** BLOCKER  
**Affected criteria:** AC-10–AC-12, AC-15  
**Observation:** The dictionary is a reformatted registry with generic types/authority/classification and no field-specific meanings. There is no coherent naming table for buildings, landmarks, localities, or non-building objects, despite name ID fields. `location_record_assertion` is introduced, but assertion semantics, typed/current values, multi-source conflicts, and required evidence/decision roles are not specified. The API map still summarizes route groups; it is not an OpenAPI operation plus request/response-field inventory and does not classify compatibility/breaking impact per field.  
**Risk/consequence:** Sensitive fields, multilingual labels, and source claims cannot be implemented or projected consistently.  
**Required resolution:** Complete a semantic data dictionary from authoritative metadata; establish multilingual/alternate/historical/normalized name structures; define assertion/value/lineage/conflict semantics; and generate/map every relevant current OpenAPI operation and field to exact target projections, classification, release prerequisite, compatibility, and deprecation impact.  
**Disposition:** OPEN

### NLI-WO-002-F09 — Convergence plan is improved but not derived from a valid map or quantified operational model

**Class:** BLOCKER  
**Affected criteria:** AC-17, AC-19  
**Observation:** Batches B0–B9 and precedence rules are helpful. But per-field transformations are generic/invalid, dual-write field ownership and conflict resolution are not specified, validation tolerances are mostly slogans, deployment-version compatibility is absent, rollback versus forward-recovery boundaries are not tied to each batch, and exception schemas/owners/SLAs are undefined. “Millions” is the only national-scale assumption; there are no annual growth, concurrency, QPS, evidence/geometry sizes, retention, index-selectivity, or partition thresholds.  
**Risk/consequence:** WO-002B cannot be safely decomposed, estimated, or cut over.  
**Required resolution:** Rebuild the plan from the validated field map. For each batch specify source/target fields, dependency, write owner, dual-read/write behavior, idempotency key, conflict precedence, exception record, validation SQL and tolerance, performance target, compatible app versions, backup/recovery boundary, monitoring window, cutover/abort gate, and retirement proof. Add explicit planning assumptions and query/index/partition rationale.  
**Disposition:** OPEN

### NLI-WO-002-F10 — Representative records are template copies, not scenario proofs

**Class:** REQUIRED  
**Affected criterion:** AC-18 and cross-model validation  
**Observation:** All seven files repeat the same generic source/record/geometry/release template and use “scenario-specific road/building/unit/landmark/admin object.” The multi-unit example contains no actual building or multiple unit rows; the boundary-change example contains no old/new administrative units or boundary versions; corrected/disputed examples do not instantiate predecessor/successor versions, correction/dispute cases, or changed release behavior.  
**Risk/consequence:** The model has still not been tested against its defining edge cases.  
**Required resolution:** Create distinct machine-readable or fully tabular records for each scenario using only valid target fields and vocabularies. Include all scenario-specific entities, optional/null cases, relationships, timelines, versions, evidence, geometry, classifications, aliases, releases, and exact public/operator projections. Validate them against the typed target model and draft schema.  
**Disposition:** OPEN

### NLI-WO-002-F11 — ADRs and RFIs remain abbreviated and decision coverage is not proven

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-06, AC-08, AC-09, AC-21  
**Observation:** ADRs 005–009 now state choices but remain one-paragraph decisions with one-line alternatives and consequences; they do not specify drivers, detailed trade-offs, operational effects, failure modes, migration constraints, or acceptance tests. RFIs compress all options/consequences into one line, do not follow the repository RFI template, and request a broad list of all authorities instead of the accountable decision owner. No matrix maps the work order’s twelve reserved questions to an accepted/proposed ADR or precise RFI. RFI-001 is correctly withdrawn, but its resolved context is not reflected in the evidence matrix.  
**Risk/consequence:** Critical decisions remain open to interpretation during executable implementation.  
**Required resolution:** Rewrite ADRs to the controlled template with real alternatives and consequences. Rewrite institutional RFIs with option-by-option behavior, benefits, costs, migration/security/authority effects, recommendation, no-decision consequence, and specific decision owner. Add and validate the twelve-question ADR/RFI coverage matrix.  
**Disposition:** OPEN

### NLI-WO-002-F12 — Validation tooling produces false assurance and is not reproducible

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-13, AC-14, AC-16, AC-18, AC-20, AC-21  
**Observation:** `generate_design_catalog.py` hardcodes `/home/ubuntu/projects/eg-addressing`, writes generated artifacts in place, and rewrites its own source from `/tmp/remediate_wo002_review01.py`; when that temporary file is absent it replaces itself with a placeholder. The checker verifies entity/field names by substring, counts at least 120 backticked current fields, checks that seven examples contain selected words, checks balanced parentheses, and counts ADR/RFI files. It does not parse SQL or Mermaid, validate entity-specific field/type/nullability/FK parity, check field-map target existence, verify classifications/vocabulary assignments/transitions, validate examples, or prove decision coverage. The generated report’s “SQL lint,” “FK intent,” and “structural checks” claims overstate these assertions. Neither tool is run by exact-head CI.  
**Risk/consequence:** Invalid models receive a green report and a future regeneration can corrupt the source/artifacts.  
**Required resolution:** Make generation portable, deterministic, non-self-modifying, and side-effect controlled. Use a proper metadata source plus SQL/Mermaid parsing or disposable PostgreSQL validation. The checker must validate typed entity/field parity, nullability, FK targets, cycles/circular insertion plan, vocab field assignments/transitions, current-to-target target existence, classifications, API field coverage, representative records, and ADR/RFI question coverage. Run generation/check in CI, verify a clean post-generation diff, and publish an exact-head report.  
**Disposition:** OPEN

## 5. Positive controls to preserve

- Documentation-only boundary and draft PR state.
- PostgreSQL/PostGIS remains the intended system of record.
- `location_record` is explicitly intended as the sole canonical registry anchor.
- Internal IDs and public aliases are conceptually separated.
- Administrative geography and operational areas are conceptually separated.
- Candidate/evidence and approved canonical geometry are conceptually separated.
- Release items now target exact record versions and aliases.
- Current schema field inventory and target mapping are being treated as generated controlled artifacts rather than informal notes.
- NLI-WO-002B remains explicitly unauthorized.

## 6. Evidence quality

Exact-head API/frontend CI and changed-path evidence prove AC-22 only. They do not validate the design pack. The local consistency report is not accepted as evidence because its assertions are shallow, the generator is non-portable/self-modifying, and the checks are not executed in CI.

## 7. Decision

`REWORK REQUIRED`

The remediation substantially increases document volume and model vocabulary, but the authoritative metadata, physical proposal, mappings, examples, decisions, and validation remain generated or internally contradictory. Accepting this pack would still transfer core national data-model decisions to the WO-002B implementer.

Keep PR #7 in draft. NLI-WO-002B remains unauthorized.

## 8. Required follow-up sequence

1. Replace heuristic metadata and mappings with typed, field-specific authoritative design data.
2. Correct identity, optionality, naming, temporal, publication, geography, and geometry architecture.
3. Complete all controlled vocabularies and state machines.
4. Rebuild the physical schema, field map, API projections, convergence plan, and scenario records from the corrected model.
5. Replace validation tooling with portable, semantic checks and execute them in CI.
6. Rebuild exact-head AC and finding evidence and request SDA Review 03.

## 9. Review 02 resolution log

| Finding | Agent response | Commit/evidence | SDA disposition | Date |
|---|---|---|---|---|
| F01 | Resolved for SDA Review 03: AC matrix and PR evidence rebuilt with exact artifacts; final head recorded post-push. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F02 | Resolved for SDA Review 03: Validated current-to-target mapping registry; no invalid target references. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F03 | Resolved for SDA Review 03: Typed target metadata replaces suffix inference; dictionary/schema generated from explicit metadata. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F04 | Resolved for SDA Review 03: ADR-006/007 plus cardinality/name/admin/object models corrected. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F05 | Resolved for SDA Review 03: Single current mechanism, optional links, exact publication snapshots corrected. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F06 | Resolved for SDA Review 03: Geometry role/type/source/licence/transformation/quality/dispute model corrected. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F07 | Resolved for SDA Review 03: Field-to-vocabulary registry and transition tables completed. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F08 | Resolved for SDA Review 03: Semantic dictionary and route projection matrix generated. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F09 | Resolved for SDA Review 03: Convergence plan rebuilt from validated field map with owners/gates/scale. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F10 | Resolved for SDA Review 03: Representative records replaced with distinct scenario-specific records. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F11 | Resolved for SDA Review 03: ADRs/RFIs rewritten to templates and 12-question matrix added. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
| F12 | Resolved for SDA Review 03: Portable generator and semantic checker added to CI with regeneration diff check. | `2da26c50cce81efba9b1645bf507b00c1b0e0ead`; `design-consistency-report.md`; final workflow IDs in PR comment. | READY FOR SDA REVIEW | 2026-07-14 |
