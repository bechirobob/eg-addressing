# NLI-WO-002 Phase A accepted-family convergence mapping

**Checkpoint type:** mapping-only design pack
**PR:** #7 (`nli/wo-002-canonical-location-model`)
**Starting head:** `be2e68dbb0d4b4f04c80e7829eca65fc30eede40`
**SDA instruction:** prepare the accepted-family convergence mapping pack only. Do not implement a convergence command yet.

## 0. Scope boundary

This document maps the seven accepted Phase A vertical slices into one future shared-database convergence plan.

This checkpoint does **not** modify or authorize changes to:

- `docs/sda/data-model/scripts/authoritative_harness.py`;
- `docs/sda/data-model/fixtures/transform-specs/phase-a-transform-specs.json`;
- `.github/workflows/api-ci.yml`;
- generated evidence reports;
- reviewer oracles;
- accepted identity controls;
- accepted geometry controls;
- the frozen broad specification;
- the broad expected fixture;
- runtime application code;
- executable migrations;
- deployment, publication, production or pilot data;
- PR #8.

The future convergence checkpoint must execute only explicit accepted callables against live reviewed narrow specifications. It must not invoke the generic broad transformer. The frozen broad specification remains exclusively associated with `phase-a-all`.

## 1. Accepted inputs and acceptance records

| Family | Accepted callable | Accepted transform group ID | Accepted oracle / record |
|---|---|---|---|
| Addresses identity | `transform_addresses_identity_crosswalk` | `WO002-R06-identity-crosswalk-addresses` | `docs/sda/acceptance/NLI-WO-002-phase-a-addresses-identity-expected.json` (`518af277e96c94c55808f9ac1e7992059c371bd225d906cf77156c478b0497cd`) and `docs/sda/reviews/NLI-WO-002-phase-a-addresses-identity-pattern-acceptance.md` |
| Address-points geometry | `transform_address_points_geometry` | `WO002-R06-geometry-observation-address_points` | `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-expected.json` (`cf699de04e0ca500c3a7826f257e190d24835356ef96db1650160d7d438edaea`) and `docs/sda/reviews/NLI-WO-002-phase-a-address-points-geometry-pattern-acceptance.md` |
| Address-points observation crosswalk | `transform_address_points_observation_crosswalk` | `WO002-R06-identity-crosswalk-address_points` | `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-observation-crosswalk-expected.json` (`d1b695994ae774a6c54cc99c1e79a0bce023fd5a9a20ec2aee779cfeb10bfa82`) and `docs/sda/reviews/NLI-WO-002-phase-a-address-points-observation-crosswalk-acceptance.md` |
| Address-records identity | `transform_address_records_identity_crosswalk` | `WO002-R06-identity-crosswalk-address_records` | `docs/sda/acceptance/NLI-WO-002-phase-a-address-records-identity-expected.json` (`16d1034b786a77d31b6863774807e66d87a337fa78c1a4202e401fbcddecd06e`) and `docs/sda/reviews/NLI-WO-002-phase-a-address-records-identity-pattern-acceptance.md` |
| Address-records geometry | `transform_address_records_geometry` | `WO002-R06-geometry-observation-address_records` | `docs/sda/acceptance/NLI-WO-002-phase-a-address-records-geometry-expected.json` (`7a5e68c4639fe290fd46c38d41c754ae25737bee8b260278817970e7758d20e2`) and `docs/sda/reviews/NLI-WO-002-phase-a-address-records-geometry-pattern-acceptance.md` |
| Citizen-geotag identity | `transform_citizen_geotag_identity_crosswalk` | `WO002-R06-identity-crosswalk-citizen_geotag_submissions` | `docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-identity-expected.json` (`65e4f2511f70ed1e94562f4973fbbb1ab072592d3b27b94f2a459843647af45e`) and PR review `4710404006` final identity-family acceptance |
| Citizen-geotag geometry | `transform_citizen_geotag_geometry` | `WO002-R06-geometry-observation-citizen_geotag_submissions` | `docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-geometry-expected.json` (`5a09abd8a017dcbf8210040e9311bc4118be82e24c245cafa485987eb5932a46`) and `docs/sda/reviews/NLI-WO-002-phase-a-citizen-geotag-geometry-pattern-acceptance.md` |

## 2. Seven accepted callable mappings

### 2.1 `transform_addresses_identity_crosswalk`

| Field | Accepted mapping |
|---|---|
| Transform group ID | `WO002-R06-identity-crosswalk-addresses` |
| Implementation unit | `impl_wo002_r06_identity_crosswalk_addresses` |
| Source table / identity | `current_source.addresses.id = phase-a-addresses-id` |
| Source key | `addresses:phase-a-addresses-id` |
| Classification | `government-internal` source/evidence; owned target location record is `government-internal` |
| Rows it owns | `proposed_location_record.phase-a-location-address-reference`; `proposed_registry_subject.phase-a-subject-phase-a-location-address-reference`; `proposed_legacy_crosswalk.phase-a-crosswalk-addresses-id-to-location-record` |
| Rows it consumes as prerequisites | current-source `addresses`; reviewed `proposed_source_record.phase-a-source-record-addresses-001`; reviewed `proposed_evidence_object.phase-a-evidence-addresses`; authoritative baseline vocabulary and schema prerequisites |
| Deterministic target IDs | location `phase-a-location-address-reference`; subject `phase-a-subject-phase-a-location-address-reference`; crosswalk `phase-a-crosswalk-addresses-id-to-location-record` |
| Exception ownership | owns no exception; building/road/territory/supersession/public-code/status/publication fields are context or separately reviewed references |
| Expected absences | no migration exception; no non-`id` crosswalk; no location version; no public-code alias; no publication item; no geometry observation |
| First/second run behavior | first run inserts 3; second run inserts 0 and updates 0 |
| Accepted oracle / record | addresses identity expected JSON and addresses identity pattern acceptance |
| Privacy/publication boundary | internal identity only; no public-code issuance or publication consequence |

### 2.2 `transform_address_points_geometry`

| Field | Accepted mapping |
|---|---|
| Transform group ID | `WO002-R06-geometry-observation-address_points` |
| Implementation unit | `impl_wo002_r06_geometry_observation_address_points` |
| Source table / identity | `current_source.address_points.id = phase-a-address-points-id` |
| Source key | `address_points:phase-a-address-points-id` |
| Classification | source/evidence `government-internal`; geometry observation `restricted` |
| Rows it owns | `proposed_geometry_observation.phase-a-geometry-address-points-phase-a-address-points-id`; `proposed_migration_exception.phase-a-exception-geometry-authority-address-points-phase-a-address-points-id` |
| Rows it consumes as prerequisites | `addresses` identity crosswalk to `phase-a-location-address-reference`; active registry subject `phase-a-subject-phase-a-location-address-reference`; source/evidence lineage for `address_points` |
| Deterministic target IDs | observation `phase-a-geometry-address-points-phase-a-address-points-id`; exception `phase-a-exception-geometry-authority-address-points-phase-a-address-points-id` |
| Exception ownership | owns the geometry-authority RFI exception only |
| Expected absences | no geometry version; no quality assessment; no geometry transformation; no per-field location assertion |
| First/second run behavior | first run inserts 2; second run inserts 0 and updates 0 |
| Accepted oracle / record | address-points geometry expected JSON plus correction/final oracles and pattern acceptance |
| Privacy/publication boundary | restricted observation; no canonical promotion or public output |

### 2.3 `transform_address_points_observation_crosswalk`

| Field | Accepted mapping |
|---|---|
| Transform group ID | `WO002-R06-identity-crosswalk-address_points` |
| Implementation unit | `impl_wo002_r06_identity_crosswalk_address_points` |
| Source table / identity | `current_source.address_points.id = phase-a-address-points-id` as observation identity, not location identity |
| Source key | `address_points:phase-a-address-points-id` |
| Classification | source/evidence `government-internal`; target geometry observation remains `restricted` |
| Rows it owns | `proposed_legacy_crosswalk.phase-a-crosswalk-address-points-id-to-geometry-observation` only |
| Rows it consumes as prerequisites | accepted address-points geometry observation `phase-a-geometry-address-points-phase-a-address-points-id`; source/evidence lineage for `address_points` |
| Deterministic target IDs | crosswalk `phase-a-crosswalk-address-points-id-to-geometry-observation`, target entity `geometry_observation`, target ID `phase-a-geometry-address-points-phase-a-address-points-id` |
| Exception ownership | owns no exception because the observation target must exist |
| Expected absences | no point-specific location record, registry subject, migration exception, public-code alias, publication row, location version, or extra geometry observation |
| First/second run behavior | first run inserts 1; second run inserts 0 and updates 0 |
| Accepted oracle / record | address-points observation-crosswalk expected JSON and acceptance record |
| Privacy/publication boundary | does not publish or issue a code; it maps a source observation ID to a restricted geometry observation |

### 2.4 `transform_address_records_identity_crosswalk`

| Field | Accepted mapping |
|---|---|
| Transform group ID | `WO002-R06-identity-crosswalk-address_records` |
| Implementation unit | `impl_wo002_r06_identity_crosswalk_address_records` |
| Source table / identity | `current_source.address_records.id = phase-a-address-records-id` |
| Source key | `address_records:phase-a-address-records-id` |
| Classification | `government-internal` source/evidence and owned target location record |
| Rows it owns | `proposed_location_record.phase-a-location-address-records-id`; `proposed_registry_subject.phase-a-subject-phase-a-location-address-records-id`; `proposed_legacy_crosswalk.phase-a-crosswalk-address-records-id-to-location-record` |
| Rows it consumes as prerequisites | current-source `address_records`; reviewed source/evidence lineage; schema/vocabulary prerequisites |
| Deterministic target IDs | location `phase-a-location-address-records-id`; subject `phase-a-subject-phase-a-location-address-records-id`; crosswalk `phase-a-crosswalk-address-records-id-to-location-record` |
| Exception ownership | owns no identity exception; `source_submission_id`, `territory_id`, address code, publication and geometry fields are context/provenance |
| Expected absences | no identity migration exception; no `source_submission_id`/`territory_id` crosswalk; no location version; no geometry observation; no public-code alias; no publication item |
| First/second run behavior | first run inserts 3; second run inserts 0 and updates 0 |
| Accepted oracle / record | address-records identity expected JSON and pattern acceptance |
| Privacy/publication boundary | internal identity only; no publication/public-code consequence |

### 2.5 `transform_address_records_geometry`

| Field | Accepted mapping |
|---|---|
| Transform group ID | `WO002-R06-geometry-observation-address_records` |
| Implementation unit | `impl_wo002_r06_geometry_observation_address_records` |
| Source table / identity | `current_source.address_records.id = phase-a-address-records-id` |
| Source key | `address_records:phase-a-address-records-id` |
| Classification | source/evidence `government-internal`; geometry observation `restricted` |
| Rows it owns | `proposed_geometry_observation.phase-a-geometry-address-records-phase-a-address-records-id`; `proposed_migration_exception.phase-a-exception-geometry-authority-address-records-phase-a-address-records-id` |
| Rows it consumes as prerequisites | accepted `address_records` identity rows and crosswalk; active registry subject `phase-a-subject-phase-a-location-address-records-id`; source/evidence lineage |
| Deterministic target IDs | observation `phase-a-geometry-address-records-phase-a-address-records-id`; exception `phase-a-exception-geometry-authority-address-records-phase-a-address-records-id` |
| Exception ownership | owns the geometry-authority RFI exception only |
| Expected absences | no geometry version; no quality approval; no geometry transformation; no per-field assertion; no `source_submission_id`-subject geometry |
| First/second run behavior | first run inserts 2; second run inserts 0 and updates 0 |
| Accepted oracle / record | address-records geometry expected JSON plus correction oracle and pattern acceptance |
| Privacy/publication boundary | restricted observation; no canonical promotion or public output |

### 2.6 `transform_citizen_geotag_identity_crosswalk`

| Field | Accepted mapping |
|---|---|
| Transform group ID | `WO002-R06-identity-crosswalk-citizen_geotag_submissions` |
| Implementation unit | `impl_wo002_r06_identity_crosswalk_citizen_geotag_submissions` |
| Source table / identity | `current_source.citizen_geotag_submissions.id = phase-a-geotag-001` |
| Source key | `citizen_geotag_submissions:phase-a-geotag-001` |
| Classification | source/evidence `restricted`; owned target location record `restricted` |
| Rows it owns | `proposed_location_record.phase-a-location-citizen-geotag-001`; `proposed_registry_subject.phase-a-subject-phase-a-location-citizen-geotag-001`; `proposed_legacy_crosswalk.phase-a-crosswalk-citizen-geotag-id-to-location-record` |
| Rows it consumes as prerequisites | current-source citizen geotag row; reviewed restricted source/evidence lineage; schema/vocabulary prerequisites |
| Deterministic target IDs | location `phase-a-location-citizen-geotag-001`; subject `phase-a-subject-phase-a-location-citizen-geotag-001`; crosswalk `phase-a-crosswalk-citizen-geotag-id-to-location-record` |
| Exception ownership | owns no identity exception; non-`id` fields remain restricted context/evidence/provenance/geometry inputs |
| Expected absences | no identity migration exception; zero `citizen_geotag_submissions` non-`id` crosswalks; no versions, geometry output, quality approval, public alias, publication item or non-restricted identity row |
| First/second run behavior | first run inserts 3; second run inserts 0 and updates 0 |
| Accepted oracle / record | citizen-geotag identity expected JSON and final identity-family acceptance at `be2e68d...` |
| Privacy/publication boundary | raw citizen source values are prohibited in committed evidence; no public code, publication, signage or production/pilot use |

### 2.7 `transform_citizen_geotag_geometry`

| Field | Accepted mapping |
|---|---|
| Transform group ID | `WO002-R06-geometry-observation-citizen_geotag_submissions` |
| Implementation unit | `impl_wo002_r06_geometry_observation_citizen_geotag_submissions` |
| Source table / identity | `current_source.citizen_geotag_submissions.id = phase-a-geotag-001` |
| Source key | `citizen_geotag_submissions:phase-a-geotag-001` |
| Classification | source/evidence `restricted`; geometry observation `restricted` |
| Rows it owns | `proposed_geometry_observation.phase-a-geometry-citizen-geotag-submissions-phase-a-geotag-001`; `proposed_migration_exception.phase-a-exception-geometry-authority-citizen-geotag-submissions-phase-a-geotag-001` |
| Rows it consumes as prerequisites | accepted citizen-geotag identity rows and crosswalk; active restricted subject `phase-a-subject-phase-a-location-citizen-geotag-001`; restricted source/evidence lineage |
| Deterministic target IDs | observation `phase-a-geometry-citizen-geotag-submissions-phase-a-geotag-001`; exception `phase-a-exception-geometry-authority-citizen-geotag-submissions-phase-a-geotag-001` |
| Exception ownership | owns the geometry-authority RFI exception only |
| Expected absences | no geometry version; no quality approval; no geometry transformation; no per-field assertion; no publication row; no public-code alias; no non-restricted observation |
| First/second run behavior | first run inserts 2; second run inserts 0 and updates 0 |
| Accepted oracle / record | citizen-geotag geometry expected JSON plus correction oracle and pattern acceptance |
| Privacy/publication boundary | restricted, non-official observation; no public release, no production/pilot citizen-data execution |

## 3. Dependency graph and fail-closed behavior

Required dependency chains:

```text
addresses identity
  -> address_points geometry
  -> address_points observation crosswalk

address_records identity
  -> address_records geometry

citizen-geotag identity
  -> citizen-geotag geometry
```

The three chains are independent of one another. Within each chain, every consumer must execute after its prerequisite producer.

| Consumer | Required prerequisite | Fail-closed behavior if run early |
|---|---|---|
| `transform_address_points_geometry` | `phase-a-crosswalk-addresses-id-to-location-record`, `phase-a-location-address-reference`, `phase-a-subject-phase-a-location-address-reference` | fail before target writes when the address identity crosswalk or active subject is missing, ambiguous, retired, wrong classification or wrong target entity |
| `transform_address_points_observation_crosswalk` | `phase-a-geometry-address-points-phase-a-address-points-id` owned by address-points geometry | fail before target writes when the geometry observation is missing, wrong source/evidence, wrong classification, wrong subject, or multiple matching observations exist |
| `transform_address_records_geometry` | `phase-a-crosswalk-address-records-id-to-location-record`, `phase-a-location-address-records-id`, active subject | fail before target writes when identity rows are missing, conflicting, non-internal, retired, inactive, ambiguous or mapped to the wrong target |
| `transform_citizen_geotag_geometry` | `phase-a-crosswalk-citizen-geotag-id-to-location-record`, `phase-a-location-citizen-geotag-001`, active restricted subject | fail before target writes when restricted identity lineage is missing, non-restricted, retired/inactive, ambiguous, or mapped to a different subject |

## 4. Row-ownership matrix

No target row may have two owners. Consumers may read prerequisite rows but may not update them.

| Target table | Deterministic primary key | Sole producing callable | Consuming callables | Shared across slices | May another slice update it? | Classification | Duplicate/collision rule |
|---|---|---|---|---|---|---|---|
| `proposed_location_record` | `phase-a-location-address-reference` | `transform_addresses_identity_crosswalk` | `transform_address_points_geometry` via address subject resolution | yes, read-only prerequisite | no | `government-internal` | existing exact row may be reused; conflicting PK or wrong classification/record type/retirement fails closed |
| `proposed_registry_subject` | `phase-a-subject-phase-a-location-address-reference` | `transform_addresses_identity_crosswalk` | `transform_address_points_geometry` | yes, read-only prerequisite | no | active location-record subject | conflicting PK, inactive state, retired subject or wrong native ID fails closed |
| `proposed_legacy_crosswalk` | `phase-a-crosswalk-addresses-id-to-location-record` | `transform_addresses_identity_crosswalk` | `transform_address_points_geometry` | yes, read-only prerequisite | no | n/a | unique `(source_table, source_field, legacy_id, target_entity)`; multiple target resolution fails closed |
| `proposed_geometry_observation` | `phase-a-geometry-address-points-phase-a-address-points-id` | `transform_address_points_geometry` | `transform_address_points_observation_crosswalk` | yes, read-only prerequisite | no | `restricted` | conflicting observation PK or extra attributable geometry row fails closed |
| `proposed_migration_exception` | `phase-a-exception-geometry-authority-address-points-phase-a-address-points-id` | `transform_address_points_geometry` | convergence comparator only | no | no | n/a | conflicting exception PK/details/source key fails closed |
| `proposed_legacy_crosswalk` | `phase-a-crosswalk-address-points-id-to-geometry-observation` | `transform_address_points_observation_crosswalk` | convergence comparator only | no | no | n/a | target entity must be `geometry_observation`; any point-to-location crosswalk fails closed |
| `proposed_location_record` | `phase-a-location-address-records-id` | `transform_address_records_identity_crosswalk` | `transform_address_records_geometry` | yes, read-only prerequisite | no | `government-internal` | exact reuse only; conflicting PK/classification/record type/retirement fails closed |
| `proposed_registry_subject` | `phase-a-subject-phase-a-location-address-records-id` | `transform_address_records_identity_crosswalk` | `transform_address_records_geometry` | yes, read-only prerequisite | no | active location-record subject | inactive/wrong native ID/retired subject fails closed |
| `proposed_legacy_crosswalk` | `phase-a-crosswalk-address-records-id-to-location-record` | `transform_address_records_identity_crosswalk` | `transform_address_records_geometry` | yes, read-only prerequisite | no | n/a | unique semantic crosswalk; duplicates/multiple target IDs fail closed |
| `proposed_geometry_observation` | `phase-a-geometry-address-records-phase-a-address-records-id` | `transform_address_records_geometry` | convergence comparator only | no | no | `restricted` | conflicting observation PK or extra attributable geometry row fails closed |
| `proposed_migration_exception` | `phase-a-exception-geometry-authority-address-records-phase-a-address-records-id` | `transform_address_records_geometry` | convergence comparator only | no | no | n/a | conflicting exception PK/details/source key fails closed |
| `proposed_location_record` | `phase-a-location-citizen-geotag-001` | `transform_citizen_geotag_identity_crosswalk` | `transform_citizen_geotag_geometry` | yes, read-only prerequisite | no | `restricted` | exact reuse only; non-restricted/retired/wrong record type fails closed |
| `proposed_registry_subject` | `phase-a-subject-phase-a-location-citizen-geotag-001` | `transform_citizen_geotag_identity_crosswalk` | `transform_citizen_geotag_geometry` | yes, read-only prerequisite | no | active location-record subject | inactive/wrong native ID/retired subject fails closed |
| `proposed_legacy_crosswalk` | `phase-a-crosswalk-citizen-geotag-id-to-location-record` | `transform_citizen_geotag_identity_crosswalk` | `transform_citizen_geotag_geometry` | yes, read-only prerequisite | no | n/a | unique semantic crosswalk; zero non-`id` citizen crosswalks |
| `proposed_geometry_observation` | `phase-a-geometry-citizen-geotag-submissions-phase-a-geotag-001` | `transform_citizen_geotag_geometry` | convergence comparator only | no | no | `restricted` | conflicting observation PK or non-restricted observation fails closed |
| `proposed_migration_exception` | `phase-a-exception-geometry-authority-citizen-geotag-submissions-phase-a-geotag-001` | `transform_citizen_geotag_geometry` | convergence comparator only | no | no | n/a | conflicting exception PK/details/source key fails closed |

Explicit distinctions:

- Identity-owned location records, registry subjects and identity crosswalks are produced only by their identity callables.
- Geometry-owned observations are produced only by their geometry callables.
- Geometry-owned authority exceptions are produced only by their geometry callables.
- The address-points observation crosswalk targets the accepted geometry observation and owns only that crosswalk.

## 5. Fixture boundary reconciliation

Existing broad/current fixture setup has historically pre-created rows that are now accepted-slice outputs. The future convergence checkpoint must narrow the setup boundary rather than reusing broad preconditions blindly.

Known helpers/areas to audit before implementation:

- `expected_target_rows()` currently seeds broad baseline target records including `phase-a-location-address-reference` and its registry subject, plus unrelated `phase-a-location-geotag` rows and broad versions/aliases/relationships.
- Geometry precondition helpers such as address-points setup currently pre-create the addresses identity crosswalk/subject so the geometry slice can run standalone.
- Address-records and citizen-geotag geometry/compatibility helpers pre-create or call identity prerequisites so standalone geometry tests can pass.
- Observation-crosswalk helper preconditions pre-create the geometry observation target so that slice can run standalone.

For the proposed convergence checkpoint, fixture setup may create only:

- current-source rows;
- reviewed `proposed_source_record` lineage;
- reviewed `proposed_evidence_object` rows;
- authoritative vocabulary prerequisites;
- unrelated canonical baseline rows required by schema constraints.

Fixture setup must not pre-create:

- accepted identity location records;
- accepted identity registry subjects;
- accepted identity crosswalks;
- accepted geometry observations;
- accepted geometry authority exceptions;
- the address-points observation crosswalk.

Those rows must be created only by their accepted owner callables. This document does not change the helpers; it records the future convergence cleanup required.

## 6. Proposed shared-database execution sequence

Single fresh disposable database, explicit accepted callables only:

1. Apply target schema and clean fixture boundary.
2. Load current-source rows, source-record lineage, evidence objects, vocabulary prerequisites and unrelated schema baseline rows.
3. Run `transform_addresses_identity_crosswalk` with the live reviewed addresses identity spec.
4. Run `transform_address_points_geometry` with the live reviewed address-points geometry spec.
5. Run `transform_address_points_observation_crosswalk` with the live reviewed address-points observation-crosswalk spec.
6. Run `transform_address_records_identity_crosswalk` with the live reviewed address-records identity spec.
7. Run `transform_address_records_geometry` with the live reviewed address-records geometry spec.
8. Run `transform_citizen_geotag_identity_crosswalk` with the live reviewed citizen-geotag identity spec.
9. Run `transform_citizen_geotag_geometry` with the live reviewed citizen-geotag geometry spec.
10. Commit, then compare the complete accepted union through a separate read-only connection.

Equivalent independent-chain orderings should produce the same final target union as long as each chain preserves internal order. Examples:

- `addresses -> address_points geometry -> address_points crosswalk`, then `address_records -> address_records geometry`, then `citizen identity -> citizen geometry`.
- `address_records -> address_records geometry`, then `citizen identity -> citizen geometry`, then `addresses -> address_points geometry -> address_points crosswalk`.
- `citizen identity -> citizen geometry`, then `addresses -> address_points geometry -> address_points crosswalk`, then `address_records -> address_records geometry`.

## 7. Expected target union after all seven slices execute once

Expected per-table counts:

| Table | Count |
|---|---:|
| `proposed_location_record` | 3 |
| `proposed_registry_subject` | 3 |
| `proposed_legacy_crosswalk` | 4 |
| `proposed_geometry_observation` | 3 |
| `proposed_migration_exception` | 3 |
| `proposed_location_record_version` | 0 |
| `proposed_geometry_version` | 0 |
| `proposed_geometry_quality_assessment` | 0 |
| `proposed_geometry_transformation` | 0 |
| `proposed_location_record_assertion` | 0 for geometry substitute assertions |
| `proposed_public_code_alias` | 0 for accepted-family rows |
| `proposed_publication_release_item` | 0 |

Exact deterministic expected rows:

| Table | Primary key | Owning slice | Classification | Source identity | Prerequisite relationship |
|---|---|---|---|---|---|
| `proposed_location_record` | `phase-a-location-address-reference` | addresses identity | `government-internal` | `addresses:phase-a-addresses-id` | prerequisite for address-points geometry subject resolution |
| `proposed_registry_subject` | `phase-a-subject-phase-a-location-address-reference` | addresses identity | active subject | `addresses:phase-a-addresses-id` | prerequisite for address-points geometry subject resolution |
| `proposed_legacy_crosswalk` | `phase-a-crosswalk-addresses-id-to-location-record` | addresses identity | n/a | `addresses.id = phase-a-addresses-id` | prerequisite for address-points geometry identity resolution |
| `proposed_geometry_observation` | `phase-a-geometry-address-points-phase-a-address-points-id` | address-points geometry | `restricted` | `address_points:phase-a-address-points-id` | requires addresses identity; prerequisite for address-points observation crosswalk |
| `proposed_migration_exception` | `phase-a-exception-geometry-authority-address-points-phase-a-address-points-id` | address-points geometry | n/a | `address_points:phase-a-address-points-id` | paired authority RFI for the address-points observation |
| `proposed_legacy_crosswalk` | `phase-a-crosswalk-address-points-id-to-geometry-observation` | address-points observation crosswalk | n/a | `address_points.id = phase-a-address-points-id` | requires accepted address-points geometry observation |
| `proposed_location_record` | `phase-a-location-address-records-id` | address-records identity | `government-internal` | `address_records:phase-a-address-records-id` | prerequisite for address-records geometry subject resolution |
| `proposed_registry_subject` | `phase-a-subject-phase-a-location-address-records-id` | address-records identity | active subject | `address_records:phase-a-address-records-id` | prerequisite for address-records geometry |
| `proposed_legacy_crosswalk` | `phase-a-crosswalk-address-records-id-to-location-record` | address-records identity | n/a | `address_records.id = phase-a-address-records-id` | prerequisite for address-records geometry |
| `proposed_geometry_observation` | `phase-a-geometry-address-records-phase-a-address-records-id` | address-records geometry | `restricted` | `address_records:phase-a-address-records-id` | requires address-records identity |
| `proposed_migration_exception` | `phase-a-exception-geometry-authority-address-records-phase-a-address-records-id` | address-records geometry | n/a | `address_records:phase-a-address-records-id` | paired authority RFI for address-records geometry |
| `proposed_location_record` | `phase-a-location-citizen-geotag-001` | citizen-geotag identity | `restricted` | `citizen_geotag_submissions:phase-a-geotag-001` | prerequisite for citizen-geotag geometry subject resolution |
| `proposed_registry_subject` | `phase-a-subject-phase-a-location-citizen-geotag-001` | citizen-geotag identity | active subject | `citizen_geotag_submissions:phase-a-geotag-001` | prerequisite for citizen-geotag geometry |
| `proposed_legacy_crosswalk` | `phase-a-crosswalk-citizen-geotag-id-to-location-record` | citizen-geotag identity | n/a | `citizen_geotag_submissions.id = phase-a-geotag-001` | prerequisite for citizen-geotag geometry |
| `proposed_geometry_observation` | `phase-a-geometry-citizen-geotag-submissions-phase-a-geotag-001` | citizen-geotag geometry | `restricted` | `citizen_geotag_submissions:phase-a-geotag-001` | requires restricted citizen identity |
| `proposed_migration_exception` | `phase-a-exception-geometry-authority-citizen-geotag-submissions-phase-a-geotag-001` | citizen-geotag geometry | n/a | `citizen_geotag_submissions:phase-a-geotag-001` | paired authority RFI; public release prohibited |

Expected absence categories across the combined family:

- duplicate identity rows;
- duplicate semantic crosswalks;
- multiple-target resolution for any `(source_table, source_field, legacy_id, target_entity)` tuple;
- non-`id` citizen-geotag crosswalks;
- address reference/context-field alternate crosswalks;
- address-record `source_submission_id` or `territory_id` crosswalks;
- public aliases or publication rows;
- unapproved location versions, geometry versions or quality approvals;
- geometry transformations not authorized by the accepted geometry slices;
- per-field assertion substitutes for geometry output;
- identity-path geometry output;
- cross-slice ownership collisions;
- unexpected migration exceptions beyond the three geometry-authority RFI exceptions;
- non-restricted citizen identity/geometry outputs.

## 8. Proposed future convergence tests

The future convergence comparator must use a separate read-only connection and compare the accepted expected union in both directions: missing expected rows fail, and unexpected actual rows fail.

| Test | Setup | Mutation / condition | Expected failure or success | Rollback proof |
|---|---|---|---|---|
| positive topological convergence | fresh DB, clean fixture boundary, sequence in §6 | none | 16 expected union rows and absence categories match | n/a; positive commits then read-only comparator runs |
| second full-family execution idempotency | run positive sequence once and commit | run all seven callables again | inserts 0, updates 0, union unchanged | compare pre/post union hash in same DB |
| consumer-before-prerequisite: address-points geometry | clean DB without addresses identity output | run address-points geometry first | missing/ambiguous address identity fail-closed before writes | same DB target-union hash unchanged |
| consumer-before-prerequisite: address-points crosswalk | clean DB with addresses identity only, no address-points geometry | run observation crosswalk | missing geometry observation target fail-closed | same DB target-union hash unchanged |
| consumer-before-prerequisite: address-records geometry | clean DB without address-records identity output | run address-records geometry first | missing address-records identity fail-closed | same DB target-union hash unchanged |
| consumer-before-prerequisite: citizen geometry | clean DB without citizen identity output | run citizen geometry first | missing restricted citizen identity fail-closed | same DB target-union hash unchanged |
| independent-chain order invariance | run all valid chain permutations | valid order permutations only | final union hash equal for every valid permutation | compare committed union hashes |
| duplicate row ownership | pre-create any accepted-owned row under a different owner marker or conflicting values | run owner and consumer sequence | owner conflict fails; no consumer may repair/update | same DB hash unchanged |
| conflicting existing location | pre-seed wrong value for any identity-owned location PK | run owning identity callable | conflict fail-closed before writes | same DB attributable hash unchanged |
| conflicting existing subject | pre-seed wrong subject/native/state for any identity-owned subject PK | run owning identity callable | conflict fail-closed | same DB attributable hash unchanged |
| conflicting existing crosswalk | pre-seed wrong target for any identity/observation crosswalk PK | run owning callable | conflict fail-closed | same DB attributable hash unchanged |
| geometry ownership collision | pre-seed geometry observation PK with wrong subject/source/evidence/classification | run geometry owner | conflict fail-closed | same DB attributable hash unchanged |
| observation-crosswalk target collision | pre-seed address-points observation crosswalk with wrong target or pre-seed duplicate semantic crosswalk | run observation-crosswalk owner | fail with collision/multiple target | same DB attributable hash unchanged |
| unexpected union row | insert an extra attributable location/subject/crosswalk/geometry/exception row | run read-only comparator | comparator fails unexpected actual row | no target writes in comparator; read-only proof recorded |
| missing union row | delete one expected row before comparator | run read-only comparator | comparator fails missing expected row | no target writes in comparator; read-only proof recorded |
| classification drift | mutate source/evidence/target identity/geometry classification | run owning/consumer callable | fail for wrong classification before writes | same DB hash unchanged |
| public-output drift | pre-create or produce public alias/publication/non-restricted citizen row | run comparator | public-output absence fails | rollback for mutation; read-only comparator proof |
| citizen privacy drift | inject raw citizen values into proposed report candidate or leaked evidence payload | run evidence privacy validator | structural/differential privacy check fails | no target DB writes required; report candidate discarded |
| accepted-oracle drift | alter accepted expected union hash or source accepted oracle path in test authority | run convergence validator | oracle hash mismatch fails before comparison | n/a |
| accepted-callable drift | registry points an accepted implementation unit to a different callable | run binding validation | callable/binding drift fails before writes | n/a |
| generic-transform invocation | instrument convergence command to detect `transform_group`/broad dispatcher calls | invoke convergence test | fail if generic broad transformer is called | n/a |
| frozen/live specification boundary drift | route a narrow slice to frozen broad spec or phase-a-all to live narrow spec | run boundary validator | fail with specification boundary drift | n/a |
| read-only complete-union comparison | commit positive union | compare via separate read-only connection and attempt blocked write | comparison passes and write is blocked | read-only proof recorded |
| same-database rollback proof | each failing DB mutation test | expected failure occurs | pre-failure and post-rollback attributable row sets/hashes equal before reset | required for every failing DB mutation |

## 9. Future evidence contract

A future convergence report may contain:

- accepted control identifiers and hashes;
- callable and binding names;
- source IDs and source keys;
- canonical target IDs;
- classifications;
- row counts;
- dependency and ownership results;
- expected/actual union hashes;
- rollback evidence hashes and row-count summaries;
- read-only comparator connection proof.

It must not contain:

- raw citizen source rows;
- citizen names, contact values, document fragments or unrestricted citizen-context values;
- pilot/production data;
- secret, credential or environment material.

Citizen-geotag evidence must remain redacted and hash-based, following the accepted C22 proof boundary.

## 10. Decision gates that remain closed

Successful family convergence would still **not** automatically:

- accept broad Phase A;
- close F02 or F14;
- authorize Review 12;
- authorize Phase B;
- authorize deployment;
- authorize merge;
- authorize publication, public-code issuance, certificates, signage or partner release;
- authorize PR #8 or runtime/pilot-data work.

Those require separate SDA decisions.

## 11. Implementation boundary for next step

Current instructed action: accepted identity/geometry family convergence mapping only.

Next instruction required from SDA: **YES — before implementing a convergence harness or any additional transform group.**
