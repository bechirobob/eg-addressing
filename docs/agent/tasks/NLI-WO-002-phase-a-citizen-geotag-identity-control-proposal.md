# NLI-WO-002 Phase A — citizen_geotag_submissions identity-control proposal

## Status and boundary

- **Current instructed action:** citizen-geotag identity-control proposal only.
- **Accepted predecessor:** `address_records` identity-foundation slice accepted at `7c9b6c892c458dd48b72d3ae3ae79d4c2ad840d6`.
- **No implementation in this proposal:** do not implement `WO002-R06-identity-crosswalk-citizen_geotag_submissions` until SDA authorizes the implementation lane.
- **No controlled-file changes in this proposal:** no transform spec, harness, CI, reviewer oracle, accepted control, runtime, migration, deployment, production/pilot data, secret, `.env`, or PR #8 changes.

## Proposed identity decision

### Source identity

The only proposed source identity is:

```text
citizen_geotag_submissions.id = phase-a-geotag-001
```

The proposed source-derived identity key is:

```text
citizen_geotag_submissions:phase-a-geotag-001
```

### Target location identity

```json
{
  "table": "proposed_location_record",
  "values": {
    "location_record_id": "phase-a-location-citizen-geotag-001",
    "record_type": "address",
    "classification": "restricted",
    "created_at": "citizen_geotag_submissions.created_at",
    "retired_at": null
  }
}
```

### Target registry subject

```json
{
  "table": "proposed_registry_subject",
  "values": {
    "subject_id": "phase-a-subject-phase-a-location-citizen-geotag-001",
    "subject_entity": "location_record",
    "native_id": "phase-a-location-citizen-geotag-001",
    "subject_state": "active",
    "retired_at": null,
    "delete_policy": "retire-only"
  }
}
```

### Target legacy crosswalk

```json
{
  "table": "proposed_legacy_crosswalk",
  "values": {
    "legacy_crosswalk_id": "phase-a-crosswalk-citizen-geotag-id-to-location-record",
    "source_table": "citizen_geotag_submissions",
    "source_field": "id",
    "legacy_id": "phase-a-geotag-001",
    "target_entity": "location_record",
    "target_id": "phase-a-location-citizen-geotag-001",
    "created_at": "citizen_geotag_submissions.created_at"
  }
}
```

## Required lineage proposal

### Source record

```json
{
  "table": "proposed_source_record",
  "required": {
    "source_record_id": "phase-a-source-record-citizen-geotag-submissions-001",
    "source_key": "citizen_geotag_submissions:phase-a-geotag-001",
    "raw_payload_classification": "restricted"
  }
}
```

The identity implementation must resolve exactly one source record by the source key above. A missing source record, multiple source records, or non-`restricted` source classification must fail closed.

### Evidence object

```json
{
  "table": "proposed_evidence_object",
  "required": {
    "evidence_object_id": "phase-a-evidence-citizen-geotag-submissions",
    "source_record_id": "phase-a-source-record-citizen-geotag-submissions-001",
    "classification": "restricted"
  }
}
```

The identity implementation must resolve exactly one evidence object through `phase-a-source-record-citizen-geotag-submissions-001`. A missing evidence object, multiple evidence objects, or non-`restricted` evidence classification must fail closed.

## Complete source record to document in implementation evidence

The future implementation evidence should query the complete `current_source.citizen_geotag_submissions` row by:

```sql
SELECT ...
FROM current_source.citizen_geotag_submissions
WHERE id = %s
-- parameter: phase-a-geotag-001
```

The evidence report may document field names, synthetic fixture identifiers, classifications, checks, and hashes only. It must not copy raw citizen PII values into a committed report.

Required documented source identity field:

```text
citizen_geotag_submissions.id
```

Required contextual fields to prove exclusion boundaries:

```text
citizen_name
citizen_contact
dip_last4
identity_verification_status
identity_document_verified
identity_verified_at
territory_id
field_submission_id
grid_code
address_label
landmark
map_display_name
road suggestions or attribution
field verification fields
signage_batch
latitude
longitude
accuracy
capture_method
created_at
updated_at
```

## Identity rule

```text
citizen_geotag_submissions.id owns the identity.
```

Only `citizen_geotag_submissions.id = phase-a-geotag-001` may determine:

- `location_record_id = phase-a-location-citizen-geotag-001`
- `subject_id = phase-a-subject-phase-a-location-citizen-geotag-001`
- `legacy_crosswalk_id = phase-a-crosswalk-citizen-geotag-id-to-location-record`

`citizen_geotag_submissions.created_at` may populate `created_at` fields but must not select the identity.

## Identity exclusions and proof obligations

The future implementation must explicitly prove that none of the following fields determine the target identity:

| Field or field family | Allowed role | Identity role |
|---|---|---|
| `citizen_name` | restricted evidence context only | prohibited |
| `citizen_contact` | restricted evidence/contact context only | prohibited |
| `dip_last4` | restricted identity-verification context only | prohibited |
| `identity_verification_status` | verification context only | prohibited |
| `identity_document_verified` | verification context only | prohibited |
| `identity_verified_at` | verification timing context only | prohibited |
| `territory_id` | territorial context only | prohibited |
| `field_submission_id` | provenance reference only | prohibited |
| `grid_code` | non-official fixture/reference context only | prohibited |
| `address_label` | descriptive context only | prohibited |
| `landmark` | descriptive context only | prohibited |
| `map_display_name` | display context only | prohibited |
| road suggestions or attribution | restricted/source attribution context only | prohibited |
| field verification fields | verification context only | prohibited |
| `signage_batch` | signage context only; no signage effect authorized | prohibited |
| `latitude`, `longitude`, `accuracy`, `capture_method` | geometry inputs for the accepted geometry slice only | prohibited |

The proposal specifically rejects alternate crosswalks from:

```text
territory_id
field_submission_id
grid_code
citizen identity fields
citizen contact fields
```

## Privacy boundary

The future implementation must require all of the following:

1. No public-code alias derived from `grid_code`.
2. No publication release item.
3. No public classification.
4. No certificate, signage, partner, pilot, or production effect.
5. No citizen/contact/DIP value in any target identity row.
6. No raw citizen PII copied into the committed identity evidence report.
7. Evidence reports may contain synthetic fixture identifiers, field names, classifications, checks, and hashes only.
8. The command must not run against pilot or production citizen data.
9. The identity rows must remain restricted/non-public until SDA explicitly authorizes a later publication or promotion lane.

## Expected rows

The future authoritative slice should create or idempotently reuse exactly three rows:

1. One restricted `proposed_location_record`:

```text
location_record_id = phase-a-location-citizen-geotag-001
record_type = address
classification = restricted
created_at = citizen_geotag_submissions.created_at
retired_at = null
```

2. One active `proposed_registry_subject`:

```text
subject_id = phase-a-subject-phase-a-location-citizen-geotag-001
subject_entity = location_record
native_id = phase-a-location-citizen-geotag-001
subject_state = active
retired_at = null
delete_policy = retire-only
```

3. One `proposed_legacy_crosswalk`:

```text
legacy_crosswalk_id = phase-a-crosswalk-citizen-geotag-id-to-location-record
source_table = citizen_geotag_submissions
source_field = id
legacy_id = phase-a-geotag-001
target_entity = location_record
target_id = phase-a-location-citizen-geotag-001
created_at = citizen_geotag_submissions.created_at
```

Expected idempotency:

```text
First execution: 3 inserts
Second execution: 0 inserts, 0 updates
```

## Expected absences

The future slice must propose/create no:

- migration exception;
- location-record version;
- geometry observation;
- geometry version;
- geometry quality approval;
- public-code alias;
- publication item;
- alternate crosswalk from `territory_id`;
- alternate crosswalk from `field_submission_id`;
- alternate crosswalk from `grid_code`;
- alternate crosswalk from citizen identity fields;
- alternate crosswalk from contact fields;
- certificate output;
- signage output;
- partner output;
- pilot output;
- production effect.

## Semantic uniqueness and conflict handling proposal

The future implementation must enforce absolute uniqueness for:

```text
(source_table, source_field, legacy_id, target_entity)
```

For this slice:

```text
(citizen_geotag_submissions, id, phase-a-geotag-001, location_record)
```

The tuple must resolve to one `target_id` or no row. It must fail closed on:

- duplicate semantic crosswalks;
- different target IDs for the same semantic tuple;
- conflicting existing location records;
- conflicting existing registry subjects;
- conflicting existing crosswalks.

## Required test proposal

Each failing database mutation must record identical same-database pre-test and post-rollback attributable rows and hashes before any reset.

| Test | Setup | Mutation | Expected failure / proof |
|---|---|---|---|
| positive authoritative slice | Fresh disposable DB with `phase-a-geotag-001`, restricted source record, restricted evidence object | none | Exactly 3 identity rows; no absent/prohibited rows |
| second-run idempotency | Run positive slice once | Run same callable again | `0` inserts, `0` updates |
| missing source | Omit `current_source.citizen_geotag_submissions` target row | ordinary source query | `citizen_geotag_submissions source row not found` |
| missing source lineage | Source row exists; omit proposed source record | ordinary lineage resolution | `citizen_geotag_submissions source record lineage not found` |
| missing evidence | Source and source record exist; omit evidence object | ordinary evidence resolution | `citizen_geotag_submissions evidence object not found` |
| source classification drift | Source record exists with non-`restricted` classification | ordinary lineage validation | `citizen_geotag_submissions source record must remain restricted` |
| evidence classification drift | Evidence object exists with non-`restricted` classification | ordinary evidence validation | `citizen_geotag_submissions evidence object must remain restricted` |
| citizen-name identity substitution | Keep source row; mutate calculated target identity to depend on `citizen_name` | ordinary comparison | `citizen_geotag_submissions identity must derive from citizen_geotag_submissions.id` |
| citizen-contact identity substitution | Keep source row; mutate calculated target identity to depend on `citizen_contact` | ordinary comparison | same identity-derivation failure |
| DIP identity substitution | Keep source row; mutate calculated target identity to depend on `dip_last4` | ordinary comparison | same identity-derivation failure |
| grid-code identity substitution | Keep source row; mutate calculated target identity to depend on `grid_code` | ordinary comparison | same identity-derivation failure |
| field-submission identity substitution | Keep source row; mutate calculated target identity to depend on `field_submission_id` | ordinary comparison | same identity-derivation failure |
| territory identity substitution | Keep source row; mutate calculated target identity to depend on `territory_id` | ordinary comparison | same identity-derivation failure |
| wrong target identity | Keep source identity correct; mutate target location/subject/crosswalk IDs | read-only comparator | `citizen_geotag_submissions identity rows differ from reviewer-owned expected target identity` |
| existing location conflict | Pre-seed same `location_record_id` with conflicting classification/type/state | ordinary insert/reuse path | identity row mismatch/conflict failure; rollback equality |
| existing subject conflict | Pre-seed same `subject_id` pointing to a conflicting native location | ordinary insert/reuse path | identity row mismatch/conflict failure; rollback equality |
| existing crosswalk conflict | Pre-seed same semantic crosswalk to a different `target_id` | semantic uniqueness/conflict check | identity row mismatch/conflict failure; rollback equality |
| unexpected extra crosswalk | Add additional citizen-geotag identity crosswalk from prohibited field | complete-set comparator | `unexpected citizen_geotag_submissions identity-foundation target row` |
| unexpected extra location record | Add orphan source-derived provisional location record | complete-set comparator | same unexpected target row failure |
| unexpected extra registry subject | Add orphan source-derived registry subject | complete-set comparator | same unexpected target row failure |
| semantic duplicate crosswalk | Add duplicate semantic tuple resolving to another target | semantic uniqueness check | `citizen_geotag_submissions identity crosswalk semantic uniqueness violated` |
| transform-spec binding drift | Mutate implementation unit/callable/context/source key/idempotency metadata | spec validator | `citizen_geotag_submissions identity transform specification binding mismatch` |
| second-source identity | Same DB with two synthetic `citizen_geotag_submissions.id` values and distinct restricted lineage/evidence | ordinary callable for both | 2 source IDs, 2 restricted provisional location records, 2 active subjects, 2 distinct ID crosswalks, 0 public output, 0 semantic duplicates, 0 multiple-target resolutions |
| privacy-output boundary | Positive run plus explicit prohibited-output queries | none | 0 public classification, 0 public-code alias, 0 publication item, 0 certificate/signage/partner/pilot/production effect; no citizen/contact/DIP values in target identity rows or committed evidence report |
| read-only complete-set comparison | Commit observed output, open separate read-only connection | Attempt target write and complete-set query | write blocked; expected/actual sets equal both directions; missing/surplus/duplicate/conflict rejected |
| same-database rollback proof | Every failing mutation runs inside isolated transaction | expected failure then rollback | same-database pre-test hash equals post-rollback hash before any reset |

## Second-source identity proposal

The second-source test must run in one disposable database and prove:

```text
2 citizen-geotag source IDs
2 restricted provisional location records
2 active subjects
2 distinct ID crosswalks
0 public output
0 semantic duplicate crosswalks
0 multiple-target resolutions
```

The second synthetic fixture may follow the same deterministic ID pattern with a different synthetic source ID, location ID, subject ID, crosswalk ID, source record ID and evidence object ID. It must not use real citizen data.

## Read-only comparator proposal

After committing observed positive output, the comparator must:

1. Open a separate read-only connection/transaction.
2. Prove target writes are blocked.
3. Query every source-derived citizen-geotag location, subject and crosswalk row.
4. Detect orphan surplus location or subject rows even if no crosswalk points to them.
5. Compare expected and actual sets in both directions.
6. Reject missing, surplus, duplicate, conflicting or incorrect rows.
7. Query expected absences for public output, geometry output, migration exceptions, versions and alternate crosswalks.

The transform/producer must not read any reviewer oracle. Only the comparator/test authority may read future reviewer-owned expected truth after observed rows already exist.

## Accepted geometry compatibility

The accepted citizen-geotag geometry transform already requires these preconditions:

```text
proposed_legacy_crosswalk:
  source_table = citizen_geotag_submissions
  source_field = id
  legacy_id = phase-a-geotag-001
  target_entity = location_record
  target_id = phase-a-location-citizen-geotag-001

proposed_location_record:
  location_record_id = phase-a-location-citizen-geotag-001
  record_type = address
  classification = restricted
  retired_at = null

proposed_registry_subject:
  subject_id = phase-a-subject-phase-a-location-citizen-geotag-001
  subject_entity = location_record
  native_id = phase-a-location-citizen-geotag-001
  subject_state = active
  retired_at = null
```

The proposed identity-control slice creates exactly those three identity rows and therefore satisfies the accepted geometry transform's subject-resolution preconditions without changing:

- the citizen-geotag geometry transform;
- the citizen-geotag geometry oracle;
- geometry timing rules;
- capture-method translation;
- restricted source/evidence requirements;
- privacy/publication controls;
- authority-RFI behavior owned by the accepted geometry slice.

The identity slice must not create the geometry observation or geometry authority exception. The accepted geometry slice remains the sole owner of citizen-geotag geometry output.

## Implementation authorization boundary

Do not implement this proposal until SDA explicitly authorizes the citizen-geotag identity implementation lane.

The next SDA instruction is required before:

- adding or modifying a transform-spec row;
- adding `transform_citizen_geotag_identity_crosswalk` or equivalent callable;
- changing `authoritative_harness.py`;
- wiring CI;
- creating a reviewer oracle;
- running against any pilot or production citizen data.
