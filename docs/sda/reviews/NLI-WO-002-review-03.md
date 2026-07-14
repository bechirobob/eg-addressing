# SDA Review — NLI-WO-002 — Review 03

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed implementation/design commit:** `c1643738a2ad17d56ff021b4c3e13b783c590709`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-14  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the exact draft-PR head, all 44 changed files, the Review 02 resolution log, typed target model, target registry and dictionary, current-state inventory, JSON and Markdown current-to-target maps, generator, semantic checker/report, conceptual model, ERD, vocabularies, lifecycle tables, API projection inventory, convergence plan, draft physical schema, representative records, ADRs 005–009, RFIs 001–006, reserved-question matrix, PR evidence, and CI integration.

Independent verification at the reviewed head:

- PR #7 is open, draft, and unmerged.
- Runtime/application source and executable migrations remain unchanged.
- The only non-`docs/sda/**` change is `.github/workflows/api-ci.yml`, adding design regeneration/checking.
- API CI run `29311278606`: **success**.
  - `sda-design-model`: success.
  - `api-tests`: success.
  - `migration-lifecycle`: success.
  - `api-image-runtime`: success.
- Frontend CI run `29311278596`: **success**.

The remediation resolves the portability, self-modification, and CI-absence defects in the prior toolchain. It also introduces useful typed metadata, a single recorded-interval current-version rule, immutable release payloads, source/geometry entities, and more explicit migration batches. It remains unsuitable for acceptance because current-state discovery, field mapping, model semantics, physical constraints, API projection analysis, examples, and validation are still materially inaccurate or incomplete.

This review does not authorize NLI-WO-002B, executable schema work, production deployment, official publication, public-code issuance, or real-data migration.

## 2. Review 02 finding disposition

| Finding | Review 03 disposition | Assessment |
|---|---|---|
| F01 | OPEN | README evidence is improved, but the PR evidence still omits the exact SHA/workflow IDs and repeats generic evidence for all criteria. |
| F02 | PARTIALLY RESOLVED — OPEN | Mapping target existence is checked, but the current inventory omits real fields and many mappings are semantically invalid or lossy. |
| F03 | PARTIALLY RESOLVED — OPEN | Target fields are typed explicitly, but several types, vocabularies, authorities and constraints are semantically wrong or not rendered into SQL. |
| F04 | PARTIALLY RESOLVED — OPEN | Identity/version, naming and creation-safe object structures improved; ID migration, code history, polymorphic integrity and cardinality enforcement remain incomplete. |
| F05 | PARTIALLY RESOLVED — OPEN | One stored current-version mechanism and complete release payloads are improvements; effective-interval, chain and historical consistency constraints remain absent. |
| F06 | PARTIALLY RESOLVED — OPEN | Observation/version/licence/transformation entities exist, but role/subject/type integrity is deferred rather than specified as an enforceable physical design. |
| F07 | OPEN | Vocabulary coverage increased, but vocabularies are misapplied and required transitions remain incomplete. |
| F08 | OPEN | Dictionary metadata improved, but the API map is not OpenAPI/field-derived and contains incorrect audience classifications. |
| F09 | PARTIALLY RESOLVED — OPEN | Batches and planning volumes were added, but the plan is built on invalid mappings and lacks field-level migration authority. |
| F10 | OPEN | Scenarios are distinct in title and a few rows, but remain abbreviated narratives rather than complete valid record sets. |
| F11 | PARTIALLY RESOLVED — OPEN | RFIs and the twelve-question matrix improved; ADR trade-off analysis remains generic and technically unconvincing. |
| F12 | PARTIALLY RESOLVED — OPEN | Generation is portable/deterministic and runs in CI; the checker still reports semantic and SQL assurances it does not test. |

## 3. Acceptance-criterion decision

| Criterion | Decision | Evidence assessed | Finding/reference |
|---|---|---|---|
| AC-01 — Complete current-state inventory | FAIL | generated inventory | F02/F12: migration-text parsing is not a real database catalog and the migration ledger is already incomplete. |
| AC-02 — One canonical registry authority | CONDITION | target model/ADR-007 | `location_record` is explicitly sole anchor; surrounding identity, mapping and integrity issues remain. F03–F05. |
| AC-03 — Administrative geography explicit | FAIL | identity/version model, ADR-006, schema | Code history, level/parent rules, naming and effective constraints are incomplete. F03–F05. |
| AC-04 — Operational areas separate | CONDITION | operational area/coverage model | Separation is sound conceptually, but spatial/coverage integrity and migration semantics remain incomplete. F04/F06/F09. |
| AC-05 — Addressable-object coverage | FAIL | object entities/cardinality metadata/examples | Entity coverage exists, but vocabularies, polymorphic integrity, cardinality enforcement and scenario proof are incomplete. F03/F04/F07/F10. |
| AC-06 — Identifier separation | FAIL | ADR-005/public alias/model/map | Public/internal separation is stated, but ULID rules and current-ID convergence conflict. F02/F04/F11. |
| AC-07 — Lifecycle separation | FAIL | vocabularies/state machines | One canonical lifecycle is reused across unrelated entities and required transitions are absent. F07. |
| AC-08 — Temporal reconstruction | FAIL | version and publication model | Current marker and release snapshot improved; effective-overlap, reciprocal chain and full entity history constraints remain absent. F05. |
| AC-09 — Geometry provenance and quality | FAIL | geometry entities/ADR/schema | Lineage is broader, but subject/type/role, validity, interval and promotion integrity remain deferred or unrendered. F06/F12. |
| AC-10 — Multilingual and naming integrity | CONDITION | reusable `name_record` model | Reusable naming exists, but subject integrity, official-name cardinality and name history constraints are not physically specified. F04/F08. |
| AC-11 — Source and authority lineage | FAIL | source/evidence/assertion model and field map | Hash-only archive mappings and invalid field targets cannot preserve or reconstruct source facts. F02/F08. |
| AC-12 — Data classification | FAIL | target metadata/current inventory | Target classifications are explicit; current classifications remain substring-derived and several field assignments are semantically wrong. F02/F03. |
| AC-13 — Controlled vocabularies | FAIL | vocabulary registry/state machines | Many fields use inappropriate vocabularies and transition coverage is incomplete. F07. |
| AC-14 — Integrity constraints | FAIL | typed metadata and draft SQL | Metadata constraints are not consistently emitted; FK order, polymorphic integrity, interval and cardinality checks are incomplete. F03–F06/F12. |
| AC-15 — API projection compatibility | FAIL | route projection inventory | It scans decorators rather than OpenAPI schemas, defers fields, and misclassifies protected routes. F08. |
| AC-16 — Current-to-target no-loss mapping | FAIL | JSON/Markdown field map | All targets exist syntactically, but multiple mappings are invalid, ambiguous or lossy. F02. |
| AC-17 — Expand–migrate–contract plan | FAIL | B0–B9 plan | Useful structure exists, but it is not grounded in valid field transformations and complete compatibility/recovery rules. F09. |
| AC-18 — Representative records | FAIL | seven scenario files | Scenario-specific facts remain incomplete and are not validated as actual target records. F10/F12. |
| AC-19 — Scale and index rationale | CONDITION | planning volumes and index list | Initial quantities exist, but assumptions, workload model and threshold rationale remain unsupported. F09. |
| AC-20 — Draft physical schema coherent | FAIL | generated SQL | The SQL has invalid creation ordering and omits declared target constraints and polymorphic checks. F03–F06/F12. |
| AC-21 — ADR decision pack | FAIL | ADRs/RFIs/question matrix | Coverage exists, but ADR alternatives and consequences remain generic and do not justify several implementation-shaping choices. F11. |
| AC-22 — No runtime behavior change | PASS WITH DOCUMENTED EXCEPTION | changed-file list and CI | No runtime/schema/API/data change; CI configuration changed only to validate this design pack. |

## 4. Open findings

### NLI-WO-002-F01 — Exact-head evidence remains indirect and repetitive

**Class:** REQUIRED  
**Affected criteria:** all; documentation/evidence standard  
**Observation:** The PR body identifies `c1643738...`, but `NLI-WO-002-pull-request-evidence.md` says the final head is recorded elsewhere and supplies the same “See README” evidence for every AC. It does not record workflow IDs or criterion-specific assertions/results. Review 02 resolution rows all cite one fixing commit and one generic report.  
**Risk/consequence:** The controlled evidence file is not self-contained or reproducible and can survive later PR-body edits without detecting staleness.  
**Required resolution:** Put the exact final SHA, workflow/run/job IDs, changed-path proof and criterion-specific file sections/check assertions directly in the evidence record. Each finding-resolution row must cite the actual correcting commit and finding-specific evidence.  
**Disposition:** OPEN

### NLI-WO-002-F02 — Current-state inventory and field map are still incomplete, heuristic and lossy

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-11, AC-12, AC-16, AC-17  
**Observation:** Current schema discovery still parses migration text with regular expressions rather than applying migrations and querying `pg_catalog`. The hand-created `schema_migrations` inventory has four fields, but the accepted runtime ledger has five: `version`, `filename`, `checksum`, `applied_at`, and `execution_context`. Source references use line-name matching and current classifications use substring rules. Mapping logic is table-level dictionaries plus defaults, not a field-authority registry. Concrete invalid examples include:

- `address_corrections.reviewer_note` falls through to `correction_case.correction_case_id`;
- `address_corrections.updated_at` maps unconditionally to `correction_case.resolved_at`;
- `citizen_geotag_submissions.field_note` maps to `field_observation.notes_classification`, losing the note;
- citizen/reporter identity and contact values map only to `source_record.raw_payload_hash`, which cannot reconstruct the original value;
- `address_records.id` is reused directly as `location_record.location_record_id`, conflicting with the selected ULID-compatible ID policy;
- `address_records.is_archived` maps to `location_record.retired_at` without a retirement timestamp/decision transformation;
- publication-looking fields map directly to release state despite RFI-006 requiring authority review/exception handling.

The checker verifies only that target names exist, not that mappings preserve meaning, type, relationships, authority or reconstructability.  
**Risk/consequence:** WO-002B could create valid-looking but wrong canonical data, lose sensitive evidence, fabricate resolution/publication state and violate accepted identifier policy.  
**Required resolution:** Build the current inventory from a disposable migrated PostGIS database and authoritative API/OpenAPI/code metadata. Create a hand-reviewed mapping registry with one explicit typed transformation per field or grouped multi-field transform, source and target keys, target-ID generation/crosswalk, value-preservation/archive location, controlled value map, authority decision, validation SQL, exception behavior and loss decision. Hash-only storage is not a no-loss archive; add a governed raw-payload object/reference model or retain an explicitly controlled archive.  
**Disposition:** OPEN

### NLI-WO-002-F03 — Typed metadata still contains semantically incorrect vocabulary and field assignments

**Class:** BLOCKER  
**Affected criteria:** AC-03–AC-07, AC-10, AC-12–AC-14, AC-20  
**Observation:** Explicit typing replaced suffix inference, but several field definitions remain semantically invalid:

- `unit.unit_type`, `landmark.landmark_type`, and `non_building_object.object_type` use the `record_type` vocabulary rather than dedicated object-type vocabularies;
- `entrance.entrance_role` uses record object-link roles such as `context-road`, `nearby-landmark` and `external-parcel-reference` rather than entrance roles;
- `geometry_quality_assessment.check_result` uses geometry lifecycle/quality state instead of a check outcome vocabulary;
- canonical `lifecycle_state` is reused for country, source authority, operational area, road, building, unit and location versions even though their valid states/transitions differ;
- `administrative_unit.stable_code` is stored on immutable identity with no effective-dated code/alias history despite the requirement to reconstruct official codes over time.

**Risk/consequence:** Database checks can pass while domain meaning is wrong, producing incompatible workflows, analytics and migrations.  
**Required resolution:** Define entity-appropriate vocabularies and field semantics. Introduce effective-dated administrative code/name history where codes may change. Separate canonical-record, reference-object, operational-area, source-authority, name, case and geometry lifecycles. Update typed metadata, dictionary, SQL, mapping, state machines and examples consistently.  
**Disposition:** OPEN

### NLI-WO-002-F04 — Polymorphic names, object links, disputes and cardinality are not an enforceable design

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-02–AC-06, AC-10, AC-14, AC-20, AC-21  
**Observation:** `name_record`, `location_record_object_link`, `dispute_case`, and geometry subjects use entity-name plus opaque-ID polymorphism. Allowed subject registries, referential validation, deletion/supersession behavior and insertion/update algorithms are not specified in the physical proposal. The record-type/object-role cardinality matrix exists only in JSON/Markdown and is not represented by constraints or a fully specified trigger design. Name cardinality—one current official Spanish name, optional English name, alternatives/history—is also not enforced.  
**Risk/consequence:** Orphaned links, invalid object roles, multiple primary objects/names and untraceable disputes can satisfy the proposed schema.  
**Required resolution:** Choose a concrete strategy for each polymorphic relationship: typed link tables, shared supertype registry, or fully specified trigger/constraint functions. Provide allowed subject/entity lists, referential checks, update/delete policy, cardinality checks, current-name rules and pseudocode/non-executable SQL sufficient for WO-002B to implement without inventing architecture.  
**Disposition:** OPEN

### NLI-WO-002-F05 — Temporal and publication design lacks enforceable interval and chain consistency

**Class:** BLOCKER  
**Affected criteria:** AC-07, AC-08, AC-14, AC-20  
**Observation:** `recorded_to IS NULL` is now the only stored current marker and release items now store exact version/alias and full payload, both positive improvements. However, effective and recorded intervals have no `from < to` or overlap/exclusion design, and the SQL merely comments that future constraints are required. Predecessor/successor alias and version links can disagree or create cycles; reciprocal and same-record rules are absent. Object links and addressable objects have independent effective periods with no containment/consistency rule against their owning record version. Administrative, road, building, unit, locality and operational-area changes are not uniformly versioned for recorded-time reconstruction.  
**Risk/consequence:** Multiple overlapping “official” states and inconsistent historical chains could pass all documented checks.  
**Required resolution:** Specify interval ranges/exclusion constraints, backdated correction handling, reciprocal/cycle rules, version/object-link interval consistency and temporal strategy for every mutable authoritative entity. Render these constraints or complete trigger designs in the draft schema and validate worked timelines.  
**Disposition:** OPEN

### NLI-WO-002-F06 — Geometry role, subject, type and quality integrity remains deferred

**Class:** BLOCKER  
**Affected criteria:** AC-09, AC-11, AC-14, AC-20  
**Observation:** Geometry observation/version, licence and transformation entities are useful. Yet the SQL stores `geometry(Geometry,4326)` and does not render the metadata’s `ST_IsValid` or role-to-geometry-type checks. `subject_entity/subject_id` integrity and role-to-subject enforcement are deferred to a comment for WO-002B. The checker verifies that a JSON rule exists, not that the physical design enforces it. Quality assessment `check_result` conflates check outcome and geometry lifecycle.  
**Risk/consequence:** Orphaned or wrong-type geometry can be marked canonical while the design report remains green.  
**Required resolution:** Provide a typed association or complete trigger/check design for subject existence and allowed role/type; render SRID, validity, dimensionality, role/type, one-current and interval constraints; separate assessment outcome from geometry lifecycle; and validate administrative/operational boundary, road, building, entrance and location examples against those rules.  
**Disposition:** OPEN

### NLI-WO-002-F07 — Controlled vocabularies and lifecycle transition coverage remain incomplete

**Class:** BLOCKER  
**Affected criteria:** AC-07, AC-10, AC-13, AC-14  
**Observation:** Vocabulary count increased, but field-to-vocabulary semantics remain wrong as noted in F03. Transition tables cover only seven vocabularies and omit material paths: duplicate review resolution, evidence rejection/cancellation/recapture, canonical correction/revocation/dispute resolution, valid-with-warning/rejection, suspended release reactivation, and disputed/retired names. The document says values not shown as `From` are terminal/derived, which is false for several values. Effective/recorded time and audit-event requirements are stated globally rather than represented per transition.  
**Risk/consequence:** Implementers would still invent valid transitions, permissions and public behavior.  
**Required resolution:** Build a field-to-vocabulary registry and complete entity-specific transition matrices for every stateful entity. Include every non-terminal state and path, actor/permission/scope, authority, evidence, effective time, recorded time, audit event, visibility, reversal/appeal and invalid-transition result. Validate transition graph reachability and terminality in CI.  
**Disposition:** OPEN

### NLI-WO-002-F08 — API projection analysis is not OpenAPI- or field-complete and misclassifies protected routes

**Class:** BLOCKER  
**Affected criteria:** AC-10–AC-12, AC-15  
**Observation:** `api-projection-map.md` is generated from source decorator text, not OpenAPI request/response schemas. It explicitly defers request/response fields to WO-002B. Audience classification is based on path substrings: protected routes such as `/api/v1/field/geotag-tasks` and its status/evidence actions are marked `public` because they contain `geotag`, and are mapped to public release projections. Other public/protected routes are labelled `mixed/protected` without authorization analysis.  
**Risk/consequence:** The design can expose protected field operations or miss breaking/sensitive response changes while claiming full operation coverage.  
**Required resolution:** Generate the current OpenAPI document and produce operation-, request-field-, response-field- and status/error-level mappings. Derive audience from actual authentication/authorization dependencies and route policy, not path names. For every field, identify target projection, classification, release prerequisite, compatibility/breaking effect, adapter, deprecation and test.  
**Disposition:** OPEN

### NLI-WO-002-F09 — Convergence plan and scale model are not grounded in valid transformations

**Class:** BLOCKER  
**Affected criteria:** AC-17, AC-19  
**Observation:** B0–B9, owners, recovery notes and planning quantities are useful. The plan still references a “validated” map that contains the invalid/lossy transformations in F02. It does not enumerate per-batch field groups/crosswalk tables, dual-write ownership by field, release-authority exception rules, exact validation tolerances, application-version compatibility, exception SLA/capacity, or reversible boundary for each migration unit. Planning numbers are asserted without source, growth horizon, concurrency/QPS, evidence size/retention, query selectivity or storage estimates.  
**Risk/consequence:** WO-002B cannot be safely decomposed, estimated, performance-tested or cut over.  
**Required resolution:** Rebuild the plan after the field map is corrected. Add a batch-to-field/migration matrix, crosswalk and exception schemas, compatible application versions, idempotency/conflict rules, validation queries/tolerances, backup/forward-recovery point, cutover/abort thresholds, monitoring window and accountable owner. Document scale assumptions with basis, horizon, workloads, data sizes, retention and index/partition thresholds.  
**Disposition:** OPEN

### NLI-WO-002-F10 — Representative records remain abbreviated narratives, not valid target datasets

**Class:** REQUIRED  
**Affected criteria:** AC-05, AC-08–AC-11, AC-18, AC-20  
**Observation:** The files are now scenario-specific, but they contain only a few prose/table rows and generic bullets. The multi-unit case includes only one unit and omits complete location version, object-link, geometry, alias and release rows. The administrative-boundary case invokes a generic public release pattern even though the release-item model targets location records, not administrative boundary versions. Examples do not instantiate all non-null target fields or prove FK, vocabulary, interval and cardinality validity. The checker checks selected words rather than parsing records.  
**Risk/consequence:** Defining urban, rural, no-road, multi-unit, correction, dispute and boundary cases remain untested, hiding contradictions.  
**Required resolution:** Provide distinct machine-readable fixtures (JSON/YAML/CSV or SQL inserts) for each scenario that instantiate every required field and relationship. Validate them against the typed model and disposable draft schema, and render exact public/operator projections from the stored release/case data.  
**Disposition:** OPEN

### NLI-WO-002-F11 — ADR analysis remains generated and generic

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-06, AC-08, AC-09, AC-21  
**Observation:** RFIs now follow the controlled structure and the twelve-question matrix exists. ADRs still generate identical drivers, generic benefits, generic “fails one or more requirements” risks, repeated rejection reasons and the same acceptance checks. For example, UUID-only identifiers are rejected without assessing UUIDv7/ULID interoperability, database generation, offline generation, collision, ordering, leakage or library support. Object/cardinality and polymorphic-integrity trade-offs are similarly not analyzed.  
**Risk/consequence:** The selected architecture has no defensible rationale or bounded consequences and can be reinterpreted during WO-002B.  
**Required resolution:** Hand-author each ADR using the controlled template. Evaluate real alternatives with domain-specific benefits/costs, security/privacy, performance, operational support, migration impact, failure modes and acceptance tests. Separate SDA technical decisions from institutional RFIs and identify the exact authority for each.  
**Disposition:** OPEN

### NLI-WO-002-F12 — CI validates the checker, not the claimed model semantics

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-03–AC-21  
**Observation:** Portability, determinism and CI execution are resolved. The semantic checker still does not:

- build the current schema and query the actual PostgreSQL/PostGIS catalog;
- parse/apply `draft-physical-schema.sql`;
- compare every target metadata type/nullability/default/constraint/index to generated SQL;
- detect forward-reference creation failures (e.g. `proposed_country` references `proposed_source_authority` before that table exists, and several cyclic FKs are emitted inline);
- render or verify metadata constraints such as country-code uniqueness/uppercase, version-number uniqueness, object cardinality, `ST_IsValid`, role/type checks and interval exclusions;
- validate mapping semantics beyond target-name existence;
- derive field-level OpenAPI coverage;
- parse representative records as data.

`render_sql()` emits PK, FK and vocabulary checks but ignores most `constraints` metadata. The checker then uses string presence, minimum counts and keyword checks while the report claims SQL parsing, structural validation and semantic completeness.  
**Risk/consequence:** An invalid, non-insertable and lossy design receives a green CI result and creates false programme assurance.  
**Required resolution:** In CI, build the accepted current schema in PostGIS and query `pg_catalog`; generate the target proposal into a dependency-safe disposable schema and execute it (or use a real PostgreSQL parser plus topological FK phase); compare metadata to physical columns/defaults/nullability/FKs/checks/indexes; validate mappings and fixtures structurally; generate OpenAPI field coverage; and fail on unexplained regeneration diff. Report only checks actually performed.  
**Disposition:** OPEN

## 5. Positive controls to preserve

- Draft/design-only delivery boundary.
- Real CI execution and deterministic regeneration.
- Machine-readable typed target model.
- `location_record` as intended sole canonical registry anchor.
- Separate administrative identity/version and operational-area concepts.
- Separate source evidence, geometry observation and approved geometry version.
- `recorded_to IS NULL` as the intended single current-version mechanism.
- Immutable publication release payload, hash, manifest URI, exact version and alias.
- Structured migration exception concept.
- Improved RFIs and twelve-question coverage matrix.
- NLI-WO-002B remains explicitly unauthorized.

## 6. Evidence quality

Exact-head CI establishes that the generator is deterministic relative to its own rules and that current application checks remain green. It does not establish that the rules accurately represent current data or that the target design can be created, populated, migrated and queried consistently. The generated PASS report overstates its assertions and is not accepted as model-completeness evidence.

## 7. Decision

`REWORK REQUIRED`

The submission is progressing from outline toward a controlled model, but accepting it would still authorize a lossy current-to-target map, invalid physical proposal, incomplete lifecycle/projection rules and untested architecture. NLI-WO-002B remains unauthorized.

Keep PR #7 in draft.

## 8. Required follow-up sequence

1. Replace migration-text and substring discovery with actual current PostGIS catalog/OpenAPI inventory.
2. Replace table-dictionary/default mappings with an explicit reviewed transformation registry and governed raw archive.
3. Correct typed field semantics, vocabularies, identity/code history and lifecycle models.
4. Specify and physically express polymorphic, cardinality, temporal and geometry integrity.
5. Generate/apply the target proposal in a disposable database and validate machine-readable scenario fixtures.
6. Produce field-complete OpenAPI projection mapping and rebuild convergence/scale plans from valid transformations.
7. Hand-author ADRs and exact-head evidence.
8. Obtain green semantic-design CI and request SDA Review 04.

## 9. Review 03 resolution log

| Finding | Agent response | Commit/evidence | SDA disposition | Date |
|---|---|---|---|---|
| F01 | Pending | — | OPEN | 2026-07-14 |
| F02 | Pending | — | OPEN | 2026-07-14 |
| F03 | Pending | — | OPEN | 2026-07-14 |
| F04 | Pending | — | OPEN | 2026-07-14 |
| F05 | Pending | — | OPEN | 2026-07-14 |
| F06 | Pending | — | OPEN | 2026-07-14 |
| F07 | Pending | — | OPEN | 2026-07-14 |
| F08 | Pending | — | OPEN | 2026-07-14 |
| F09 | Pending | — | OPEN | 2026-07-14 |
| F10 | Pending | — | OPEN | 2026-07-14 |
| F11 | Pending | — | OPEN | 2026-07-14 |
| F12 | Pending | — | OPEN | 2026-07-14 |
