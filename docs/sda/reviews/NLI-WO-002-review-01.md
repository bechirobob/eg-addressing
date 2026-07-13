# SDA Review — NLI-WO-002 — Review 01

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed implementation/design commit:** `75cb53c04d7dfb2ecc368c6f9e4a7b0771b016a1`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-13  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the exact draft-PR head, all 33 changed files, the complete submitted `docs/sda/data-model/` pack, proposed ADRs 005–009, RFIs 001–005, implementation/modelling plan, PR evidence record, current operational migrations and representative current table definitions, and exact-head workflow results.

Independent verification:

- PR #7 is open and draft.
- Changed paths are confined to `docs/sda/**`; no runtime code, executable migration, API contract, infrastructure, or data file changed.
- API CI run `29293901869`: **success**.
- Frontend CI run `29293901998`: **success**.

The submission correctly preserves the design-only boundary and identifies several important target domains. It is not yet an authoritative canonical data model. The principal problem is not document absence; it is that many documents are summaries or placeholders rather than complete, mutually consistent model specifications.

This review does not authorize executable schema work, NLI-WO-002B, production deployment, official publication, public-code issuance, or real-data migration.

## 2. Acceptance-criterion decision

| Criterion | Decision | Evidence assessed | Finding/reference |
|---|---|---|---|
| AC-01 — Complete current-state inventory | FAIL | `current-state-inventory.md` | Table-level summary only; fields, keys, constraints, indexes, writers/readers, classifications, JSON contents, and lifecycle behavior are not inventoried. F02. |
| AC-02 — One canonical registry authority | CONDITION | `canonical-conceptual-model.md`, ADR-007 | `location_record` is named as sole authority, but current/version/publication/object semantics remain internally ambiguous. F03/F04/F05. |
| AC-03 — Administrative geography explicit | FAIL | conceptual model, ERD, dictionary, draft SQL, ADR-006 | Boundary-version entity and authoritative hierarchy decisions are missing from the physical proposal; hierarchy choice is implicit, not decided. F03/F04/F12. |
| AC-04 — Operational areas separate | FAIL | conceptual model and draft SQL | Separation is stated, but coverage, geometry, effective period, purpose authority, and relationship to admin units are absent from the proposed physical model. F03/F04. |
| AC-05 — Addressable-object coverage | FAIL | conceptual model, ERD, draft SQL, examples | Object names exist, but cardinality and canonical identity semantics—especially units, entrances, road segments, landmarks, and multiple object relationships—are unresolved. F04/F10. |
| AC-06 — Identifier separation | FAIL | identifier document and ADR-005 | Classes are separated, but internal ID type/generation, offline allocation/reconciliation, alias versioning, and record-vs-object identifiers are not decided. F04/F12. |
| AC-07 — Lifecycle separation | FAIL | controlled vocabularies and state machines | Multiple vocabularies conflict; transitions do not fully state actor, evidence, visibility, effective/recorded time, reversal, and terminal behavior. F07. |
| AC-08 — Temporal reconstruction | FAIL | ADR-008 and draft SQL | `location_record_version` lacks effective dates and supersession links; release items target mutable records rather than exact versions/projections. F05. |
| AC-09 — Geometry provenance and quality | FAIL | geometry document, ADR-009, draft SQL | Observation versus approved version is not physically represented; `geom` is only a comment; polymorphic subjects have no integrity or one-current constraint. F06. |
| AC-10 — Multilingual and naming integrity | FAIL | dictionary, controlled vocabularies, draft SQL | Complete official/alternate/local/historical/normalized name modelling is absent for several entity classes and vocabularies conflict. F07/F08. |
| AC-11 — Source and authority lineage | FAIL | conceptual/source documents and draft SQL | A canonical version cannot be traced to all contributing source records/evidence/decisions at fact or assertion level; evidence and observation entities are absent from the draft schema. F03/F06/F08. |
| AC-12 — Data classification | FAIL | data dictionary and source/classification document | Only a small subset of target fields is classified; externally exposed and sensitive fields lack complete field-level treatment. F08. |
| AC-13 — Controlled vocabularies | FAIL | `controlled-vocabularies.md`, state machines, dictionary | Conflicting and missing values exist across documents; no complete owner/transition/current-value mapping is supplied. F07. |
| AC-14 — Integrity constraints | FAIL | draft SQL and ERD | FK-like columns have no `REFERENCES`; required check/exclusion/spatial/current-version/supersession constraints are largely absent. F03/F05/F06. |
| AC-15 — API projection compatibility | FAIL | `api-projection-map.md` | Only selected route groups and coarse allowed/forbidden field classes are mapped; current operations and response fields are not comprehensively traced. F08. |
| AC-16 — Current-to-target no-loss mapping | FAIL | `current-to-target-mapping.md` | Mapping is mainly table-level plus a small “critical fields” list; most current columns have no target, transform, classification, validation, or disposition. F02. |
| AC-17 — Expand–migrate–contract plan | FAIL | `schema-convergence-plan.md` | High-level phases exist, but migration units, precedence, dual-write/conflict behavior, per-field backfills, validation queries, cutover, and recovery are not implementation-authority ready. F09. |
| AC-18 — Representative records | FAIL | seven files under `representative-records/` | Files are one- or few-sentence narratives, not worked records demonstrating IDs, versions, relationships, state history, provenance, geometry, classification, and projections. F10. |
| AC-19 — Scale and index rationale | FAIL | convergence plan and draft SQL | No quantified assumptions, cardinalities, access-path analysis, query rationale, or partition thresholds; the draft contains almost no indexes. F09/F11. |
| AC-20 — Draft physical schema coherent | FAIL | ERD, dictionary, draft SQL | Numerous conceptual entities/relationships are missing; fields are undocumented; geometry and referential integrity are absent; temporal/publication semantics conflict. F03–F06. |
| AC-21 — ADR decision pack | FAIL | ADRs 005–009 and RFIs 001–005 | ADRs/RFIs are generic and do not resolve or meaningfully analyze several reserved questions. F12. |
| AC-22 — No runtime behavior change | PASS | changed-file list and workflows | All changes are under `docs/sda/**`; runtime and executable migrations are unchanged. |

## 3. Findings

### NLI-WO-002-F01 — Plan and evidence matrix are boilerplate and stale

**Class:** BLOCKER  
**Affected criteria:** all; documentation/evidence standard  
**Observation:** The plan maps every criterion to the same generic statement—“create or update the design authority artifact”—rather than a named section, model rule, and validation. The PR evidence repeats “See data-model pack sections” for AC-01 through AC-22. Its head remains `<filled after final commit>`, and its verification commands remain `pending final head`, although the PR body declares a final commit.  
**Risk/consequence:** The SDA cannot reproduce or audit criterion-by-criterion completion, and unsupported completeness claims can pass through document presence alone.  
**Required resolution:** Replace every generic row with exact artifact/section/decision/evidence links and truthful `PASS/PARTIAL/FAIL/N/A` implementation-agent status. Record the exact final head and completed no-runtime-diff/consistency checks. Add a deliverable-completeness and cross-document consistency report.  
**Disposition:** OPEN

### NLI-WO-002-F02 — Current-state inventory and no-loss mapping are not field-complete

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-16, AC-17  
**Observation:** `current-state-inventory.md` lists tables and short roles but not every column, type, nullability, default, PK/FK/unique/check constraint, index, geometry, JSON content, writer, reader, projection, classification, source, retention, or state meaning. It even omits migration-ledger treatment. `current-to-target-mapping.md` contains table mappings and roughly twenty “critical” fields while the current schema contains many more fields—for example routing readiness, archive flags, address issuance/source/verification/supersession fields, address-point accuracy/source, citizen identity and map-suggestion fields, field evidence fields, event actors, import fields, and publication fields. Several mappings remain alternatives such as “publication state or release item” rather than a decision.  
**Risk/consequence:** WO-002B could silently drop, misclassify, duplicate, or overwrite operational, identity, evidentiary, publication, and geometry data.  
**Required resolution:** Produce a reproducible catalog-derived inventory and one row for every current field. Each row must include current semantics/constraints/readers/writers plus target entity.field, transform, default/provisional rule, authority, classification, ambiguity/loss risk, validation query, compatibility period, and retirement condition. Unknowns must become explicit RFIs or accepted-loss requests.  
**Disposition:** OPEN

### NLI-WO-002-F03 — Logical model, dictionary, ERD, and draft physical schema do not describe the same system

**Class:** BLOCKER  
**Affected criteria:** AC-02–AC-05, AC-11, AC-12, AC-14, AC-20  
**Observation:** The conceptual model names entities including `administrative_boundary_version`, `operational_area_coverage`, `campaign_area`, `routing_assignment`, `geometry_observation`, `geometry_quality_assessment`, `intake_case`, `field_observation`, `evidence_object`, `location_record_relationship`, `correction_case`, `dispute_case`, `resolution_event`, and `partner_projection`. Many are absent from `draft-physical-schema.sql`. The data dictionary documents only a small subset of fields and does not cover all fields that do appear in the draft SQL. The SQL defines many FK-like text columns but no foreign-key constraints, and it has no complete evidence/observation/correction/dispute model.  
**Risk/consequence:** The “canonical” package contains competing implicit models; implementers would have to invent missing entities, fields, and authority rules during migration work.  
**Required resolution:** Establish one authoritative entity/field list. Make the conceptual model, ERD, data dictionary, controlled vocabularies, API projections, field mapping, representative records, ADRs, and draft SQL trace one-to-one. Every omitted conceptual entity must be modelled or explicitly removed with rationale. Add a generated consistency report proving entity/field/relationship coverage.  
**Disposition:** OPEN

### NLI-WO-002-F04 — Canonical identity, addressable-object cardinality, and geography decisions remain unresolved

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-02–AC-06, AC-21  
**Observation:** The conceptual model says a version references “zero or more” addressable objects, while the ERD/SQL provides at most one nullable column for each object type. The multi-unit example says units may use “separate location records or sub-address versions,” which leaves the canonical unit of identity undecided. `location_record_relationship` is named but not defined. Whole-road versus road-segment identity, entrance versus location-point authority, and locality/neighbourhood treatment remain unspecified. The draft uses a generic administrative-unit table, but ADR-006 does not actually decide generic hierarchy versus level-specific tables or model official hierarchy/effective changes in sufficient detail.  
**Risk/consequence:** Different implementers can create incompatible record identities, unit addressing, road references, and administrative scope behavior while each claiming compliance.  
**Required resolution:** Expand ADR-006 and ADR-007—or add ADRs—to decide: canonical record unit; object association roles/cardinalities; unit/sub-address behavior; road/segment semantics; entrance/access-point semantics; locality/settlement handling; generic versus level-specific administrative model; operational-area coverage and effective-period rules. Reflect decisions consistently in the ERD, dictionary, examples, and draft SQL.  
**Disposition:** OPEN

### NLI-WO-002-F05 — Temporal, supersession, and publication reconstruction cannot meet the stated requirement

**Class:** BLOCKER  
**Affected criteria:** AC-07, AC-08, AC-14, AC-20  
**Observation:** ADR-008 promises effective and recorded dates plus explicit supersession, but `proposed_location_record_version` contains only `recorded_at`; it has no effective interval, predecessor/successor, correction relationship, or transaction/effective semantics. `location_record.current_version_id` and `location_record_version.is_current` create two ungoverned current-state authorities. Publication release items target `location_record`, not the exact version/public code/projection artifact that was released, so later changes prevent reconstruction of what the public actually received.  
**Risk/consequence:** The platform could not reliably answer “what did the registry believe?”, “what was officially effective?”, and “what was published?” at a named time.  
**Required resolution:** Define the temporal model precisely, including recorded versus effective time, version intervals, correction/supersession links, one-current enforcement, backdated decisions, dispute behavior, and immutable release snapshots/manifests targeting exact versions and aliases. Update ADR-008, publication model, constraints, examples, and convergence plan.  
**Disposition:** OPEN

### NLI-WO-002-F06 — Geometry observation, approval, provenance, and integrity are incomplete

**Class:** BLOCKER  
**Affected criteria:** AC-09, AC-11, AC-14, AC-20  
**Observation:** ADR-009 and the conceptual model distinguish observations from approved geometry versions, but the draft schema has only `proposed_geometry_version`. Its `geom` column is commented out, its `subject_type/subject_id` association is polymorphic without referential integrity, and it lacks source-record/evidence links, validation actor/method, transformation history, licensing, quality assessment, dispute/supersession links, and a one-current-per-subject/role constraint. Administrative boundary versions are absent.  
**Risk/consequence:** Unverified geometry could be promoted without reconstructable evidence, or geometry could become orphaned, multiply current, incorrectly typed, or impossible to restore to its source decision.  
**Required resolution:** Model geometry observations separately from approved versions; choose and justify a referential association strategy; include actual non-executable PostGIS types/SRID constraints; model source/evidence, transformation, validation, quality, licensing, effective time, supersession/dispute, and current-version constraints; include administrative and operational boundary geometry.  
**Disposition:** OPEN

### NLI-WO-002-F07 — Controlled vocabularies and lifecycle state machines conflict

**Class:** BLOCKER  
**Affected criteria:** AC-07, AC-10, AC-13, AC-14  
**Observation:** Field-verification lifecycle uses `linked-to-canonical` and `needs-recapture`, but those values are absent from the field-verification vocabulary. The source-authority vocabulary includes `operator-confirmed`, while the source-authority model instead uses `registry-authority` and `gis-data-authority`. Road-name values in the dictionary (`candidate/under_review/official/...`) conflict with the controlled vocabulary (`under-review`, `official-current`, `official-historical`, etc.). `registry-review`, `partner-released`, and other declared states have no complete transition path. Most transitions omit required permission/authority, evidence, visibility, effective time, recorded time, reversal, and invalid-transition rules.  
**Risk/consequence:** Database constraints, APIs, workflow guards, analytics, and migration mappings would implement different meanings for the same state.  
**Required resolution:** Create one authoritative vocabulary registry with stable key, definition, owner, classification, current-value mappings, terminality, and allowed transitions. Make every state-machine row specify actor/permission/scope, evidence/reason, public/internal behavior, effective/recorded time, reversal/appeal, audit event, and invalid transitions. Add a machine-checkable cross-reference.  
**Disposition:** OPEN

### NLI-WO-002-F08 — Data dictionary, naming, classification, lineage, and API projections are incomplete

**Class:** BLOCKER  
**Affected criteria:** AC-10–AC-12, AC-15  
**Observation:** The dictionary contains only selected fields and uses ambiguous types such as `text/uuid`. It does not assign classification/source/projection to every target field or cover all draft-schema fields. Alternative, local, historical, normalized, and multilingual names are not consistently modelled for landmarks, buildings, non-building objects, localities, and other named entities. Canonical versions have a free-text `source_authority` but no complete relationship to all contributing source records, evidence objects, validation decisions, and field-level assertions. The API map covers selected route groups only and provides coarse field classes rather than current-response-field-to-target-projection mapping.  
**Risk/consequence:** Sensitive fields may be exposed or lost; public/operator/partner behavior cannot be implemented predictably; source lineage can be reduced to an unverifiable label.  
**Required resolution:** Complete the dictionary for every target field. Define reusable multilingual name/history structures or explicit entity-specific exceptions. Model source/evidence/decision lineage at the appropriate assertion/version level. Generate a current OpenAPI operation/response inventory and map each relevant field to public, operator, partner, publication, export, or prohibited projections with compatibility/breaking impact.  
**Disposition:** OPEN

### NLI-WO-002-F09 — Convergence plan and scale/index analysis are not implementation-authority ready

**Class:** BLOCKER  
**Affected criteria:** AC-17, AC-19  
**Observation:** The convergence document provides useful phase headings but no migration units/dependencies, deterministic authority precedence, dual-write or conflict behavior, idempotent per-field backfills, exception queues, validation SQL, cutover thresholds, rollback/forward-recovery strategy, deployment compatibility matrix, or retirement evidence. Scale analysis lists “high-growth tables” and index names without record-volume, growth, concurrency, query, storage, or partitioning assumptions.  
**Risk/consequence:** WO-002B cannot be safely scoped or sequenced, and an apparently compatible cutover could lose data or serve conflicting authorities.  
**Required resolution:** Derive a stepwise expand–migrate–contract plan from the complete field map. State migration batches, dependencies, source-of-truth precedence, dual-write/read rules, idempotency, validation queries and tolerances, exception handling, monitoring window, rollback/forward recovery, API compatibility, cutover/deprecation gates, and owner. Add explicit national-scale assumptions and query/index/partition rationale.  
**Disposition:** OPEN

### NLI-WO-002-F10 — Representative-record files are scenarios, not worked records

**Class:** REQUIRED  
**Affected criterion:** AC-18 and cross-document validation  
**Observation:** The seven required files are one- or few-sentence narratives. They do not instantiate internal/public/external identifiers, object relationships, version/effective history, state transitions, source/evidence lineage, classification, geometry/provenance, publication release, corrections, or public/operator projections. The multi-unit example explicitly leaves the core design alternative unresolved.  
**Risk/consequence:** The model has not been demonstrated against the cases it claims to support, and contradictions remain hidden.  
**Required resolution:** Replace each narrative with a worked, internally consistent example—tables or JSON are acceptable—showing all relevant entities/IDs, relationships, source/evidence, state/event timeline, effective/recorded times, geometry and quality, classification, aliases, release projection, and expected public/operator views. Validate every example against the dictionary/ERD/draft schema.  
**Disposition:** OPEN

### NLI-WO-002-F11 — ADRs and RFIs do not provide adequate decision analysis or coverage

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-06, AC-08, AC-09, AC-21  
**Observation:** ADRs 005–009 are extremely brief and repeat the same generic alternatives (“keep current,” “copy proposal,” “use proposed model”) instead of evaluating the real design alternatives. ADR-005 does not choose internal ID type/generation. ADR-006 does not decide generic versus level-specific hierarchy. ADR-007 does not decide record/unit/cardinality semantics. ADR-008 does not specify temporal mechanics. ADR-009 does not choose a referential geometry-subject model. The RFIs use “decide now” versus “reserve” rather than substantive options and recommendations. RFI-001 about issue #6 access is now obsolete and remains open. Required questions concerning localities, road/segment identity, evidence-to-decision lineage, and existing published-looking pilot records are not adequately covered.  
**Risk/consequence:** Consequential architecture would be invented during executable schema work, defeating the design-authority phase.  
**Required resolution:** Rewrite ADRs with actual alternatives, drivers, decision, consequences, implementation constraints, and migration effects. Create precise RFIs with concrete options where institutional authority is genuinely required. Close/withdraw RFI-001 and incorporate issue #6 context. Add a question-to-ADR/RFI matrix covering all twelve reserved questions in the work order.  
**Disposition:** OPEN

### NLI-WO-002-F12 — Draft schema lacks enforceable integrity and reproducible consistency validation

**Class:** BLOCKER  
**Affected criteria:** AC-14, AC-19, AC-20, AC-21  
**Observation:** The draft SQL has FK-named columns but no `REFERENCES`, almost no indexes, no controlled-value checks, no temporal exclusion/one-current/supersession constraints, no hierarchy-cycle protection, no publication prerequisites, and no actual spatial columns/indexes. The evidence test plan checks changed paths and headings only; it does not parse Mermaid, parse/lint the SQL, compare ERD/dictionary/schema entities and fields, validate vocabulary references, or confirm ADR/RFI coverage.  
**Risk/consequence:** A syntactically present design pack can be mutually contradictory and still report every criterion as represented.  
**Required resolution:** Make the non-executable schema structurally complete enough to express intended FKs, unique/check/exclusion/spatial/current-version constraints and indexes. Add a reproducible design-consistency checker/report covering entity/field parity, FK targets, vocabulary usage, state transitions, dictionary/classification completeness, representative-record validity, ADR/RFI coverage, Mermaid parse, and SQL parse/lint.  
**Disposition:** OPEN

## 4. Positive controls to preserve

- Strict documentation-only change boundary.
- PostgreSQL/PostGIS remains the intended system of record.
- One canonical registry principle centred on `location_record`.
- Candidate/evidence separation from canonical authority.
- Administrative geography separated conceptually from operational areas.
- Registry-ready remains separate from publication release.
- Public code separated conceptually from internal identity.
- Public projections are allowlisted rather than inferred from database presence.
- Proposal schema remains non-authoritative.
- The PR remains draft and explicitly denies schema-deployment authority.

## 5. Evidence quality

Exact-head CI and changed-path evidence are valid for AC-22 only. They do not validate data-model completeness or consistency. The current evidence record is stale and generic; it must be rebuilt after substantive model corrections and tied to the final review head.

## 6. Decision

`REWORK REQUIRED`

The submission has a useful outline and vocabulary for continued work, but accepting it would delegate core national data-model decisions to the later migration implementer. NLI-WO-002B is not authorized.

Keep PR #7 in draft. Resolve F01–F12, update the complete criterion matrix and exact-head evidence, obtain green workflows, and request SDA Review 02.

## 7. Required follow-up sequence

1. Generate the complete current catalog and field-level current-to-target map.
2. Decide the canonical identity/cardinality, geography, temporal, and geometry architecture through substantive ADRs/RFIs.
3. Reconcile conceptual model, ERD, dictionary, vocabularies, examples, projections, mapping, convergence plan, and draft SQL.
4. Add reproducible completeness/consistency validation.
5. Replace narrative examples with worked records.
6. Update PR evidence to the exact final head and request Review 02.

## 8. Review 01 resolution log

| Finding | Agent response | Commit/evidence | SDA disposition | Date |
|---|---|---|---|---|
| F01 | Pending | — | OPEN | 2026-07-13 |
| F02 | Pending | — | OPEN | 2026-07-13 |
| F03 | Pending | — | OPEN | 2026-07-13 |
| F04 | Pending | — | OPEN | 2026-07-13 |
| F05 | Pending | — | OPEN | 2026-07-13 |
| F06 | Pending | — | OPEN | 2026-07-13 |
| F07 | Pending | — | OPEN | 2026-07-13 |
| F08 | Pending | — | OPEN | 2026-07-13 |
| F09 | Pending | — | OPEN | 2026-07-13 |
| F10 | Pending | — | OPEN | 2026-07-13 |
| F11 | Pending | — | OPEN | 2026-07-13 |
| F12 | Pending | — | OPEN | 2026-07-13 |
