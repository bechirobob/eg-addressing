# SDA Authorization — Citizen-Geotag Geometry Vertical Slice

**Control ID:** `NLI-WO-002-PA-GEO-03-AUTHORIZATION`  
**Work order:** `NLI-WO-002`  
**Pull request:** `#7`  
**Reviewer:** System Design Authority  
**Authorization date:** 2026-07-15  
**Outcome:** `ONE CITIZEN-GEOTAG GEOMETRY SLICE AUTHORIZED`

## 1. Authorization basis

The SDA has accepted the `address_points` and `address_records` geometry transformations as controlled vertical-slice patterns. The prior geometry-family mapping identified the remaining citizen-submission decisions. This authorization resolves those decisions and supplies the group-specific expected-result oracle.

Reviewer-owned oracle:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-geometry-expected.json
```

Control ID:

```text
NLI-WO-002-PA-GEO-03
```

## 2. Technical decisions

### 2.1 Subject identity

The citizen submission creates a **provisional, restricted and non-official location-record identity** for design-harness validation.

Identity path:

```text
citizen_geotag_submissions.id
→ proposed_legacy_crosswalk(source_table=citizen_geotag_submissions, source_field=id)
→ proposed_location_record
→ proposed_registry_subject
```

The geometry transform consumes this identity as a prerequisite. It does not own the identity transformation.

The subject must not be selected from `territory_id`, `field_submission_id`, `grid_code`, citizen identity/contact fields or any later address-record identity.

### 2.2 Capture method

The source contains an explicit capture-method value. The reviewed translation is:

```text
browser-gps → browser-gps
```

The value must already exist in the authoritative target vocabulary. The harness may not insert or repair vocabulary values.

### 2.3 Timing

```text
observed_at = citizen_geotag_submissions.created_at
recorded_at = citizen_geotag_submissions.created_at
```

`field_verified_at` records later verification context. It is not the original observation time and must not replace either target timestamp.

### 2.4 Classification and privacy

The geometry observation, source record and evidence remain `restricted`.

The transform may not create:

- a public classification;
- a public-code alias from `grid_code`;
- a publication release item;
- a canonical geometry version;
- a geometry quality approval;
- a CRS transformation;
- substitute per-field geometry assertions.

Citizen name, contact and identity-document data remain source/evidence context and are not copied into the geometry observation.

### 2.5 Authority

The source may establish an observation only. Canonical geometry promotion remains unauthorized. The transform must create one owned conditional authority exception for each observation.

## 3. Authorized implementation

Authorized transform group only:

```text
WO002-R06-geometry-observation-citizen_geotag_submissions
```

Required explicit binding:

```text
impl_wo002_r06_geometry_observation_citizen_geotag_submissions
→ transform_citizen_geotag_geometry
```

The implementation must follow the accepted geometry-family pattern while applying the citizen-specific identity, timing, capture-method and privacy rules in the oracle.

## 4. Authorization boundary

Authorized:

- the one citizen-geotag transform-spec row;
- one explicit citizen-geotag callable and binding;
- controlled fixture preconditions for the provisional identity, source record and evidence;
- one-slice harness, tests, evidence, task record and non-authoritative CI step.

Not authorized:

- any other transform group;
- modifications to accepted `address_points` or `address_records` controls;
- broad Phase A reassessment or closure of F02/F14;
- Phase B, F04–F12, SDA Review 12 or NLI-WO-002B;
- runtime application/frontend changes, executable migration or migration-runner changes;
- Docker runtime, production/pilot data, secrets, `.env*`, publication, public-code issuance, certificates, signage, partner release or PR #8 changes.

## 5. Decision

`ONE CITIZEN-GEOTAG GEOMETRY SLICE AUTHORIZED`

Implement the single slice, obtain exact-head evidence and stop for SDA pattern assessment.
