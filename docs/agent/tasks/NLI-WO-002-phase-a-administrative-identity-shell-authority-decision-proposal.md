# NLI-WO-002 Phase A administrative identity-shell authority-decision proposal

**Continuation commit:** `2fbff25215c78e538a8dd5070ca37967ce966409`

**PR review read:** `4716640719` — C38-C40 mapping accepted; next scope is authority-decision proposal only; no oracle or implementation authorization.

## 0. Scope and closed-gate declaration
This proposal does not approve Option A, B or C; prepare or approve a reviewer oracle; implement an administrative transform; modify accepted callables or convergence; authorize another transform group; accept broad Phase A; close F02 or F14; authorize Review 12 or Phase B; authorize public-code issuance or publication; authorize deployment or merge; or modify PR #8.

## 1. Controlling authorities pinned
| authority | path | git blob | sha256 |
| --- | --- | --- | --- |
| accepted administrative hierarchy/reference mapping | docs/agent/tasks/NLI-WO-002-phase-a-administrative-hierarchy-reference-mapping.md | f75f06f99a680337faed59e4b2fb31bc92d4104a | b75ed951a98d55987edb19b29f020486fbad661b31dd4acb109b5b6d14094b8e |
| C38-C40 reviewer assessment | docs/sda/reviews/NLI-WO-002-administrative-hierarchy-mapping-assessment.json | d5414abba28489e6032819479ac2c4c8b658a98d | 9baa93e62658e45ea433f6879408628f455ce3b3242768a293668ffa24144d5b |
| corrected residual-readiness mapping | docs/agent/tasks/NLI-WO-002-phase-a-residual-control-readiness-mapping.md | 7fcb73f3c99c56ba9c38207c689492a608fe17b7 | d2ae6ffc999c8f59486dcbc7a0d47d62a2465b99ec9aa3cf1116384003526758 |
| current PostgreSQL catalog | docs/sda/data-model/current-pg-catalog.json | 2948290a494c125ce2254ffa8cb7861f4ea8d7cb | 0b022dd03fecb6bdec12baa159c6bb83aaa477fcc3fa35e9ab0110d14a0c52d5 |
| complete current-source fixture | docs/sda/data-model/fixtures/current-source/phase-a-complete-source-records.json | 6e5ad53ba59a12a5db3a5718b94b3ee44886c570 | 6d5daca924bfe5141b7039f4cad06006faf39fd46bd9d4b50c74d273d2d7de10 |
| draft physical target schema | docs/sda/data-model/draft-physical-schema.sql | b92c5343900bfc7cc54f182ca7a6838910f4c8e7 | 902a10ac233301a841c600fe4ea047623b68ae42241c929fcdc358353f33936a |
| accepted-family convergence mapping | docs/agent/tasks/NLI-WO-002-phase-a-accepted-family-convergence-mapping.md | c984a16f352417b9fde0f8cb9e0536a5e0ab6eb1 | 382c1ccd0de2b90ecb08241d8cf3f6788ae7166ef93f9122bb6ed3b6ed3669ce |
| accepted-family convergence control | docs/sda/acceptance/NLI-WO-002-phase-a-accepted-family-convergence-control.json | 3c4c59fa5eeb004cfb8ef2520241d74c130fa926 | d714b32ea170e05b5feef240d587d860ed0c712812036f384e357381a60b3b8a |
| accepted convergence report | docs/sda/data-model/phase-a-accepted-family-convergence-report.json | bc0346d30eb49f1d2956b81e6cffa5e3e9933d65 | f28cd006d27cf0d764db1863956d39dc97aa13b11df0d063d8c3b8ad2698a304 |
| accepted addresses identity control | docs/sda/acceptance/NLI-WO-002-phase-a-addresses-identity-expected.json | 4c1d6068bc39da7a8fef7ed3dbaa1454f27282c8 | 518af277e96c94c55808f9ac1e7992059c371bd225d906cf77156c478b0497cd |
| accepted address-records identity control | docs/sda/acceptance/NLI-WO-002-phase-a-address-records-identity-expected.json | 79e3ee0ccccbfad318a61d58ae036ed8170e0a77 | 16d1034b786a77d31b6863774807e66d87a337fa78c1a4202e401fbcddecd06e |
| accepted address-records geometry control | docs/sda/acceptance/NLI-WO-002-phase-a-address-records-geometry-expected.json | bd3e821f07e0a1d3968e3dd6f76e6201ea7229fd | 7a5e68c4639fe290fd46c38d41c754ae25737bee8b260278817970e7758d20e2 |
| accepted address-points observation crosswalk control | docs/sda/acceptance/NLI-WO-002-phase-a-address-points-observation-crosswalk-expected.json | 7d964599a5500aa5430da208aefdc940c3c0af1b | d1b695994ae774a6c54cc99c1e79a0bce023fd5a9a20ec2aee779cfeb10bfa82 |
| accepted address-points geometry control | docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-expected.json | 691d08f09bfd12e227207cd5913b6b54caf59536 | cf699de04e0ca500c3a7826f257e190d24835356ef96db1650160d7d438edaea |
| accepted citizen-geotag identity control | docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-identity-expected.json | 61fb777a2af5a917b4ea7bbff0d6c7dff09241ba | 65e4f2511f70ed1e94562f4973fbbb1ab072592d3b27b94f2a459843647af45e |
| accepted citizen-geotag geometry control | docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-geometry-expected.json | d5ae8a9a859ec466b68365ee006c310a85955504 | 5a09abd8a017dcbf8210040e9311bc4118be82e24c245cafa485987eb5932a46 |
| live narrow transform specification | docs/sda/data-model/fixtures/transform-specs/phase-a-transform-specs.json | 32b284917bafd5bdc5bef7804230b8eb81033697 | 5f6defcdf1a27f736ee1736a158a15ed83530daed8490af7719f6b9784454fc4 |
| frozen broad transform specification | docs/sda/data-model/fixtures/transform-specs/phase-a-broad-generic-transform-specs-frozen.json | 443de54b6bacf6a12106fdbba5dba1a07955eec4 | b601f4fe1c5676511010d10d5b9e819e83fc50a2bbedce11c324e2f4a05099cf |
| broad expected-target fixture | docs/sda/data-model/fixtures/expected-target/phase-a-expected-target-records.json | 7df5326902315123ebb8bc4970899dd293f30c58 | 4b98cc1b580b2513cd0f1eee3a53af87376a1d6efa7c8792ab1211e38a22ea76 |

## 2. Exact decision requested
The requested decision for SDA and programme authority is:

> May `current_source.admin_units.id` anchor a provisional government-internal administrative identity shell before official hierarchy, level, parent, code, naming, version and publication authority are resolved?

Authorization would establish only: a stable internal administrative identity; its exact source ID crosswalk; and its mandatory registry subject.

Authorization would not establish: an official administrative level; an official parent relationship; an official province relationship; an official administrative code; an official name; an effective-dated version; official public status; geometry; publication; or a public code.
## 3. Exact source row and lineage authorities
| field | value |
| --- | --- |
| source_table | admin_units |
| source identity field | id |
| source identity value | phase-a-admin-units-id |
| source key | admin_units:phase-a-admin-units-001 |
| source record | phase-a-source-record-admin-units-001 |
| source package | phase-a-source-package-admin-units |
| source authority | phase-a-authority-conditional-admin-reference |
| evidence object | phase-a-evidence-admin-units |
| source-record raw-payload classification | government-internal |
| evidence classification | government-internal |
| fixture authority | SDA Review 11 Phase A correction complete-source fixture authority |
| source row record hash | be29aa1db6cca1b47d756b8197ef5c07fad2be0970dc6821d36f9d924255eeec |
| source row values/content hash | 9eaf7f3c59593dcec1fba87d252a51ab7e379d26747c1eb01e6fb2746495eb6a |
| source_record.raw_payload_hash | 9eaf7f3c59593dcec1fba87d252a51ab7e379d26747c1eb01e6fb2746495eb6a |
| source_package.package_checksum | 9eaf7f3c59593dcec1fba87d252a51ab7e379d26747c1eb01e6fb2746495eb6a |
| evidence.content_hash | 9eaf7f3c59593dcec1fba87d252a51ab7e379d26747c1eb01e6fb2746495eb6a |
| archive.payload_hash_sha256 | 6e3b0735f0fa4c7adb2a6beca91800d8388b43090a7a7d3b72c37b2180361190 |

Only `admin_units.id = phase-a-admin-units-id` is an identity determinant. The proposal intentionally excludes `name_es`, `name_en`, `code`, `level`, `parent_id`, `province_code`, `status`, `sort_order`, `created_at` and `updated_at` as identity determinants.
| lineage item | table | primary key | values | values sha256 | row sha256 |
| --- | --- | --- | --- | --- | --- |
| source record | proposed_source_record | {"source_record_id": "phase-a-source-record-admin-units-001"} | {"raw_payload_classification": "government-internal", "raw_payload_hash": "9eaf7f3c59593dcec1fba87d252a51ab7e379d26747c1eb01e6fb2746495eb6a", "recorded_at": "2026-07-15T00:00:00Z", "source_key": "admin_units:phase-a-admin-units-001", "source_package_id": "phase-a-source-package-admin-units", "source_record_id": "phase-a-source-record-admin-units-001"} | 547e600c6bac68b9c4dece32e7bab126e9c58d5ea8cfbd05f2d3bd0f6efacc6c | 7c6ea175107d9d2998bb8c0ff44e1773c2707d7ce68a9f558b7e52e3a1a9d021 |
| source package | proposed_source_package | {"source_package_id": "phase-a-source-package-admin-units"} | {"licence_id": null, "load_context": {"phase": "A", "source_table": "admin_units"}, "loaded_at": "2026-07-15T00:00:00Z", "package_checksum": "9eaf7f3c59593dcec1fba87d252a51ab7e379d26747c1eb01e6fb2746495eb6a", "package_name": "Phase A source package admin_units", "source_authority_id": "phase-a-authority-conditional-admin-reference", "source_package_id": "phase-a-source-package-admin-units"} | 69dc6d140a6ee2f62ab1df999f270f90a868a8c11f8f9625c33025e8447c8bdf | be5af1735627a73a883a6cd443ff150569a71507a7e1f4301624cdb32679fd82 |
| source authority | proposed_source_authority | {"source_authority_id": "phase-a-authority-conditional-admin-reference"} | {"authority_class": "registry-authority", "authority_name": "Phase A conditional administrative reference authority", "legal_basis": "Conditional/provisional non-official government reference fixture linked to authority RFI", "source_authority_id": "phase-a-authority-conditional-admin-reference", "status": "candidate"} | 4e3c346da1e13e3c130d72a84e6f0f93d4595db344fd98d63faaf3c732f22598 | d16c8a8377fa6d0ddc656e18ed2195ae78755f839a263c7e71e84e5d6f7dcb60 |
| evidence object | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-admin-units"} | {"captured_at": "2026-07-15T00:00:00Z", "classification": "government-internal", "content_hash": "9eaf7f3c59593dcec1fba87d252a51ab7e379d26747c1eb01e6fb2746495eb6a", "evidence_object_id": "phase-a-evidence-admin-units", "media_type": "application/json", "retention_state": "active", "source_record_id": "phase-a-source-record-admin-units-001", "storage_uri": "phase-a://evidence/admin_units:phase-a-admin-units-001"} | 6b1ba0f0548d4e4134006c34c08d372599e446efda199efa865f2e5ea08aadcf | 2777b8f45761a6ef657d4117f6edb54fe81b0e20b90225b50baedfce268ec043 |
| source payload archive | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-admin-units"} | {"archive_id": "phase-a-archive-wo002-r06-source-archive-admin-units", "classification": "restricted", "created_at": "2026-07-15T00:00:00Z", "payload_hash_sha256": "6e3b0735f0fa4c7adb2a6beca91800d8388b43090a7a7d3b72c37b2180361190", "payload_uri": "phase-a://archive/WO002-R06-source-archive-admin_units", "retention_state": "active", "source_record_id": "phase-a-source-record-admin-units-001"} | 853488990516946f384cbba60c62590eefea74f4db7f33b7c32ac0427a3ed457 | 834481f08034f4888b9cce11911f0882f930b51794fa175e7a5be13d4fda9020 |
| country prerequisite | proposed_country | {"country_id": "phase-a-country-gq"} | {"country_id": "phase-a-country-gq", "created_at": "2026-07-15T00:00:00Z", "iso2_code": "GQ", "lifecycle_state": "active", "official_name_en": "Equatorial Guinea", "official_name_es": "Guinea Ecuatorial", "source_authority_id": "phase-a-authority-conditional-admin-reference"} | 6a0d2b7b7c2358a78e4c933bea462c4f05817041b04852ac413d634204c0eeed | 4905e79a53eafa45fd2314c899c6a2daf7d400e4411b1579bef18af042e90f50 |

## 4. Authority options evaluated
| option | benefits | risks | governance implications | F02 impact | F14 impact | dependency impact | reversible versus irreversible decisions | work permitted | work prohibited |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Option A — Authorize provisional internal identity shell | Unblocks a narrow stable internal anchor for later roads, buildings, address context and field workflow references without declaring official hierarchy facts. | If authority later rejects admin_units.id stability, an internal shell would require explicit retirement/supersession handling rather than silent replacement. | Requires SDA/programme authority to approve provisional government-internal identity only, Lineage Model L1 and Subject Model S1; does not approve official hierarchy. | Positive design impact: creates a narrow ownership boundary for source identity and expected absences; F02 remains open. | Positive design impact: separates internal identity from broad generic hierarchy/name/code/publication outputs; F14 remains open. | Reduces dependency blockage for later context integration while preserving authority gates for hierarchy/version/code/name/publication. | Identity string should be durable; row can be retired/superseded, but no later decision may silently replace it. Official facts remain reversible/not created. | Future proposal acceptance would permit only identity shell oracle preparation for exactly three rows and expected absences. | No hierarchy version, code history, name record, geometry, publication, public alias, accepted convergence change or transform implementation in this checkpoint. |
| Option B — Defer identity until official hierarchy authority | Avoids creating even a provisional identity until the institution confirms source-system stability, hierarchy ownership, level translation and parent lineage. | Keeps dependent roads, buildings, address province/territory context and field workflow links blocked or forced into unresolved mapping queues. | Conservative: all admin identity work waits for formal hierarchy owner and source-stability decision. | Keeps F02 residual administrative ownership unresolved; no new narrow identity control can reduce the residual. | Avoids any chance of broad/identity contradiction but leaves administrative broad-readiness dependency unresolved. | Highest dependency cost: roads, buildings, accepted address context, field assignments/submissions and territory lookup cannot anchor to admin identity. | Fully reversible because no target rows are created; cost is schedule/dependency delay. | Mapping/RFI drafting and authority evidence collection only. | No administrative identity row, crosswalk, subject, oracle or implementation. |
| Option C — Require schema-enhanced direct lineage first | Provides strongest target-persisted lineage model before any identity oracle, satisfying direct source/evidence traceability concerns. | Introduces schema-design work before proving the narrow identity shell; expands scope and delays dependency consumers. | Requires future schema decision for direct source-record/evidence lineage on administrative identity model; this checkpoint does not propose a migration. | Clarifies a stricter lineage prerequisite but leaves F02 open and unadvanced operationally. | Protects against broad generic lineage ambiguity, but does not reduce current broad-readiness blockers. | Blocks identity shell until schema-enhancement work item is authorized; roads/buildings/context/workflows remain dependent. | Design-only and reversible; future schema change would be irreversible enough to need separate review/migration control. | Design discussion of lineage requirements only. | No migration, schema spec edit, oracle, transform, fixture or implementation in this checkpoint. |

**Recommended option:** Option A — Authorize provisional internal identity shell.

**Recommendation confidence:** medium. It best reduces dependency blockage while preserving all hierarchy/code/name/publication gates, but it still requires explicit authority acceptance before any oracle or implementation work.
## 5. Exact proposed target IDs for Option A
| target | exact ID | derivation rule |
| --- | --- | --- |
| Administrative unit | administrative-unit:admin_units:phase-a-admin-units-id | Derived only from admin_units.id = phase-a-admin-units-id |
| Legacy crosswalk | crosswalk:admin_units:id:phase-a-admin-units-id:to:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id | Deterministic source tuple admin_units/id/phase-a-admin-units-id to target administrative_unit/administrative-unit:admin_units:phase-a-admin-units-id |
| Registry subject | subject:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id | Subject entity administrative_unit plus native administrative unit ID |

Do not use name, code, level, parent, province code, status, sort order or dates in any identity ID.
## 6. Exact proposed normalized row objects for Option A
```json
{
  "proposed_administrative_unit": {
    "administrative_unit_id": "administrative-unit:admin_units:phase-a-admin-units-id",
    "country_id": "phase-a-country-gq",
    "created_at": "2026-07-15T00:00:00Z",
    "retired_at": null
  },
  "proposed_legacy_crosswalk": {
    "created_at": "2026-07-15T00:00:00Z",
    "legacy_crosswalk_id": "crosswalk:admin_units:id:phase-a-admin-units-id:to:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id",
    "legacy_id": "phase-a-admin-units-id",
    "source_field": "id",
    "source_table": "admin_units",
    "target_entity": "administrative_unit",
    "target_id": "administrative-unit:admin_units:phase-a-admin-units-id"
  },
  "proposed_registry_subject": {
    "created_at": "2026-07-15T00:00:00Z",
    "delete_policy": "retire-only",
    "native_id": "administrative-unit:admin_units:phase-a-admin-units-id",
    "retired_at": null,
    "subject_entity": "administrative_unit",
    "subject_id": "subject:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id",
    "subject_state": "active"
  }
}
```
Timestamp handling: `created_at` is a physical default in all three tables, but a future oracle must use a deterministic controlled timestamp of `2026-07-15T00:00:00Z` or a comparator-normalized fixed equivalent. A future harness, if later authorized, must inject a fixed timestamp or the comparator must normalize database defaults to that controlled timestamp. No value is derived from observed generic broad output.
## 7. Lineage proof under Lineage Model L1
| fact | persisted on target rows | persisted on prerequisite lineage rows | reviewer-oracle assertions | comparator/test-control assertions |
| --- | --- | --- | --- | --- |
| admin_units.id tuple | no | source_record.source_key and raw_payload_hash; evidence.source_record_id/content_hash; source_package/source_authority | exact reviewed source row has source_table=admin_units, source field id, identity value phase-a-admin-units-id | source tuple matches reviewed source_record, package, authority and evidence; no unrelated source fields determine ID |
| legacy crosswalk | yes: source_table, source_field, legacy_id, target_entity, target_id | no direct source_record_id on crosswalk | crosswalk tuple is the only source ID link for the identity shell | crosswalk source tuple resolves to exactly one target and exactly one reviewed source record/evidence chain |
| administrative-unit target ID | yes: proposed_administrative_unit.administrative_unit_id and crosswalk.target_id | no | ID derived only from admin_units.id value | ID does not include name, code, level, parent, province_code, status, sort_order or dates |
| registry subject native_id | yes: proposed_registry_subject.native_id | no | subject_entity=administrative_unit; native_id equals proposed administrative-unit ID | no accepted/geotag/generic subject reuse; exactly one subject for shell |

Direct persisted source-record lineage limitations: `proposed_administrative_unit` and `proposed_registry_subject` do not contain `source_record_id`, `evidence_object_id`, `source_authority_id`, `source_table`, `source_field` or `legacy_id` columns. The future comparator must enforce the source/evidence chain through prerequisites and crosswalk semantics.
## 8. Classification boundary
| mechanism | detail |
| --- | --- |
| source-record classification | proposed_source_record.raw_payload_classification remains government-internal and must be comparator-checked. |
| evidence classification | proposed_evidence_object.classification remains government-internal and content_hash matches admin_units source values. |
| target-table limitation | proposed_administrative_unit, proposed_legacy_crosswalk and proposed_registry_subject have no general classification column; do not claim one is persisted. |
| expected absences | No name/code/version/geometry/publication/public-alias rows, no address/geotag subjects and no decision/migration rows. |
| command/report privacy boundary | Future command/report must remain operator/reviewer-internal and must not expose shell as public reference data. |
| reviewer-owned absence checks | Future expected fixture/control must check every expected absence in this proposal. |

## 9. Exact expected absences for Option A
| expected absence | required count | scope |
| --- | --- | --- |
| proposed_administrative_unit_version | 0 | attributable to administrative identity-shell slice |
| proposed_administrative_code_history | 0 | attributable to administrative identity-shell slice |
| proposed_name_record | 0 | attributable to administrative identity-shell slice |
| proposed_location_record | 0 | attributable to administrative identity-shell slice |
| address/geotag registry subjects | 0 | attributable to administrative identity-shell slice |
| proposed_geometry_observation | 0 | attributable to administrative identity-shell slice |
| proposed_geometry_version | 0 | attributable to administrative identity-shell slice |
| proposed_decision_event | 0 | attributable to administrative identity-shell slice |
| proposed_migration_exception | 0 | attributable to administrative identity-shell slice |
| proposed_public_code_alias | 0 | attributable to administrative identity-shell slice |
| proposed_publication_release | 0 | attributable to administrative identity-shell slice |
| proposed_publication_release_item | 0 | attributable to administrative identity-shell slice |
| province-owned administrative identities | 0 | attributable to administrative identity-shell slice |
| territory-owned administrative identities | 0 | attributable to administrative identity-shell slice |
| non-ID admin_units crosswalks | 0 | attributable to administrative identity-shell slice |
| one source ID resolving to multiple targets | 0 | attributable to administrative identity-shell slice |
| duplicate administrative semantic subjects | 0 | attributable to administrative identity-shell slice |
| generic geotag-subject reuse | 0 | attributable to administrative identity-shell slice |

## 10. Exact future proof contract — proposal only
| contract | exact requirement |
| --- | --- |
| positive execution | Fixture prerequisites: phase-a-country-gq, phase-a-source-record-admin-units-001, phase-a-source-package-admin-units, phase-a-authority-conditional-admin-reference and phase-a-evidence-admin-units present and matched. First-run inserts=3, updates=0, deletes=0. Keys: administrative-unit:admin_units:phase-a-admin-units-id; crosswalk:admin_units:id:phase-a-admin-units-id:to:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id; subject:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id. Complete normalized values equal the three row objects in this proposal. Attributable union scope is proposed_administrative_unit, proposed_legacy_crosswalk and proposed_registry_subject rows keyed by those IDs only, plus expected absence scans listed here. |
| idempotency | Second-run inserts=0, updates=0, deletes=0; complete attributable union and normalized hash identical to first-run post-state. |
| read-only comparison | Use separate database connection; start read-only transaction; attempted write to a target table is blocked; compare expected->actual and actual->expected; compare every normalized physical column for all three expected rows and every expected absence. |
| rollback | For every failing database mutation: capture complete pre-test rows, complete post-rollback rows, pre/post row counts, pre/post hashes, row equality and hash equality. |

## 11. Exact future negative-test contracts — designs only
These are designs only. They do not implement tests, prepare an oracle, create fixtures or modify a harness.
| test id | case | baseline source IDs | mutation value | expected row deltas | exact error |
| --- | --- | --- | --- | --- | --- |
| AIS-NEG-001 | missing country prerequisite | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | delete or omit proposed_country.country_id=phase-a-country-gq | inserts=0 updates=0 deletes=0 | administrative identity shell missing country prerequisite |
| AIS-NEG-002 | missing reviewed source record | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | delete or omit proposed_source_record.source_record_id=phase-a-source-record-admin-units-001 | inserts=0 updates=0 deletes=0 | administrative identity shell missing reviewed source record |
| AIS-NEG-003 | wrong source package | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | set proposed_source_record.source_package_id=wrong-source-package | inserts=0 updates=0 deletes=0 | administrative identity shell wrong source package |
| AIS-NEG-004 | wrong source authority | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | set proposed_source_package.source_authority_id=wrong-source-authority | inserts=0 updates=0 deletes=0 | administrative identity shell wrong source authority |
| AIS-NEG-005 | wrong evidence object | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | use evidence_object_id=wrong-evidence-object or evidence row not linked to source record | inserts=0 updates=0 deletes=0 | administrative identity shell wrong evidence object |
| AIS-NEG-006 | source/evidence classification drift | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | set source raw_payload_classification=public or evidence.classification=public | inserts=0 updates=0 deletes=0 | administrative identity shell classification drift |
| AIS-NEG-007 | wrong source table | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | crosswalk.source_table=provinces | rollback to pre-test state | administrative identity shell wrong source table |
| AIS-NEG-008 | wrong source field | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | crosswalk.source_field=code | rollback to pre-test state | administrative identity shell wrong source field |
| AIS-NEG-009 | wrong legacy ID | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | crosswalk.legacy_id=phase-a-admin-units-code | rollback to pre-test state | administrative identity shell wrong legacy ID |
| AIS-NEG-010 | one source ID resolving to multiple targets | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | same source_table/source_field/legacy_id also resolves to second target_id | rollback to pre-test state | administrative identity shell one source ID resolving to multiple targets |
| AIS-NEG-011 | duplicate administrative identity | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | second proposed_administrative_unit for same admin_units.id | rollback to pre-test state | administrative identity shell duplicate administrative identity |
| AIS-NEG-012 | duplicate administrative registry subject | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | second proposed_registry_subject with same native_id or semantic admin subject | rollback to pre-test state | administrative identity shell duplicate administrative registry subject |
| AIS-NEG-013 | wrong subject entity | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | subject_entity=location_record | rollback to pre-test state | administrative identity shell wrong subject entity |
| AIS-NEG-014 | wrong subject native ID | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | native_id does not equal administrative-unit:admin_units:phase-a-admin-units-id | rollback to pre-test state | administrative identity shell wrong subject native ID |
| AIS-NEG-015 | accepted address subject reuse | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | subject_id=phase-a-subject-phase-a-location-address-reference | rollback to pre-test state | administrative identity shell accepted address subject reuse |
| AIS-NEG-016 | generic geotag-subject reuse | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | subject_id=phase-a-subject-phase-a-location-geotag | rollback to pre-test state | administrative identity shell generic geotag-subject reuse |
| AIS-NEG-017 | unexpected administrative version | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | insert proposed_administrative_unit_version for administrative-unit:admin_units:phase-a-admin-units-id | rollback to pre-test state | administrative identity shell unexpected administrative version |
| AIS-NEG-018 | unexpected code-history row | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | insert proposed_administrative_code_history for administrative-unit:admin_units:phase-a-admin-units-id | rollback to pre-test state | administrative identity shell unexpected code-history row |
| AIS-NEG-019 | unexpected name row | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | insert proposed_name_record for subject:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id | rollback to pre-test state | administrative identity shell unexpected name row |
| AIS-NEG-020 | unexpected decision event | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | insert proposed_decision_event attributable to admin_units identity shell | rollback to pre-test state | administrative identity shell unexpected decision event |
| AIS-NEG-021 | unexpected migration exception | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | insert proposed_migration_exception attributable to admin_units identity shell | rollback to pre-test state | administrative identity shell unexpected migration exception |
| AIS-NEG-022 | unauthorized public alias | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | insert proposed_public_code_alias for administrative-unit:admin_units:phase-a-admin-units-id | rollback to pre-test state | administrative identity shell unauthorized public alias |
| AIS-NEG-023 | unauthorized publication row | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | insert proposed_publication_release or proposed_publication_release_item | rollback to pre-test state | administrative identity shell unauthorized publication row |
| AIS-NEG-024 | unexpected province identity | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | insert province-owned proposed_administrative_unit from provinces.code | rollback to pre-test state | administrative identity shell unexpected province identity |
| AIS-NEG-025 | unexpected territory identity | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | insert territory-owned proposed_administrative_unit from territories.id or territories.admin_unit_id | rollback to pre-test state | administrative identity shell unexpected territory identity |
| AIS-NEG-026 | unexpected attributable target row | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | insert any attributable row outside the exact three expected rows | rollback to pre-test state | administrative identity shell unexpected attributable target row |
| AIS-NEG-027 | missing expected identity-shell row | admin_units:phase-a-admin-units-001; phase-a-source-record-admin-units-001; phase-a-source-package-admin-units; phase-a-authority-conditional-admin-reference; phase-a-evidence-admin-units | delete/omit one of the three expected rows | complete comparison reports missing row; no commit | administrative identity shell missing expected identity-shell row |

## 12. Decision evidence requirements
| requirement | proposed decision owner |
| --- | --- |
| Confirm admin_units.id is a stable source-system record identity | SDA plus territorial-administration / source-system owner role |
| Confirm internal identity shell does not declare official hierarchy status | SDA plus programme authority role |
| Approve Lineage Model L1 for this narrow shell | SDA data governance / reviewer authority role |
| Approve Subject Model S1: identity slice owns mandatory administrative_unit subject | SDA registry model owner role |
| Approve hierarchy version, code, name and publication remain absent | Programme authority plus SDA reviewer role |
| Approve later hierarchy decisions cannot silently replace the shell identity | SDA data governance / change-control owner role |

**Proposed decision owner:** SDA data governance / programme authority role, with territorial-administration or source-system owner participation for source identity stability. No person is invented here.
## 13. Preserved blocked slices
| blocked slice | status |
| --- | --- |
| administrative hierarchy version | blocked; no oracle or implementation may include it |
| province identity | blocked; no oracle or implementation may include it |
| territory identity | blocked; no oracle or implementation may include it |
| administrative code history | blocked; no oracle or implementation may include it |
| administrative names | blocked; no oracle or implementation may include it |
| accepted-context integration | blocked; no oracle or implementation may include it |

## 14. Preserved closed gates
This proposal does not approve Option A, B or C; prepare or approve a reviewer oracle; implement an administrative transform; modify accepted callables or convergence; authorize another transform group; accept broad Phase A; close F02 or F14; authorize Review 12 or Phase B; authorize public-code issuance or publication; authorize deployment or merge; or modify PR #8.
## 15. Return summary values
| field | value |
| --- | --- |
| Decision requested | May current_source.admin_units.id anchor a provisional government-internal administrative identity shell before official hierarchy, level, parent, code, naming, version and publication authority are resolved? |
| Options evaluated | 3 — Option A, Option B, Option C |
| Recommended option | Option A — Authorize provisional internal identity shell |
| Recommendation confidence | medium |
| Source identity | admin_units.id = phase-a-admin-units-id |
| Source key | admin_units:phase-a-admin-units-001 |
| Source record | phase-a-source-record-admin-units-001 |
| Source package | phase-a-source-package-admin-units |
| Source authority | phase-a-authority-conditional-admin-reference |
| Evidence object | phase-a-evidence-admin-units |
| Source classification | government-internal |
| Evidence classification | government-internal |
| Administrative-unit ID | administrative-unit:admin_units:phase-a-admin-units-id |
| Crosswalk ID | crosswalk:admin_units:id:phase-a-admin-units-id:to:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id |
| Subject ID | subject:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id |
| Exact proposed rows | 3 complete normalized row objects: proposed_administrative_unit, proposed_legacy_crosswalk, proposed_registry_subject |
| Expected insert count | 3 |
| Persisted lineage | crosswalk source_table/source_field/legacy_id/target_entity/target_id; subject native_id; unit administrative_unit_id/country_id; prerequisite source/evidence rows carry source_record/package/authority/evidence facts |
| Comparator-enforced lineage | admin_units.id tuple -> proposed_legacy_crosswalk -> administrative_unit target_id -> registry_subject.native_id plus independent proof of source_record/source_package/source_authority/evidence_object |
| Direct lineage limitations | no direct persisted source_record/evidence/authority on administrative-unit or registry-subject rows; no source_record_id on crosswalk |
| Classification enforcement | source/evidence classification plus expected absences and internal command/report boundaries; no target-row classification column claim |
| Expected absences | 18 absence families require zero attributable rows |
| Negative-test contracts | 27 |
| Positive execution contract | fixture prerequisites present; first-run inserts=3 updates=0 deletes=0; exact keys and normalized values; attributable-union scope limited to three row families plus absence scans |
| Idempotency contract | second-run inserts=0 updates=0 deletes=0; identical complete union and hash |
| Read-only contract | separate connection; read-only transaction; attempted target write blocked; bidirectional complete normalized comparison |
| Rollback contract | for every failing database mutation: complete pre/post rows, counts, hashes, row equality, hash equality |
| Authority evidence required | 6 minimum authority evidence items |
| Proposed decision owner | SDA data governance / programme authority role, with territorial-administration or source-system owner participation for source identity stability |
| Authority-blocked slices | administrative hierarchy version; province identity; territory identity; administrative code history; administrative names; accepted-context integration |
| Accepted rows modified | 0 |
| Accepted convergence modified | no |
| F02 status | partially satisfied and open |
| F14 status | partially satisfied and open |
| Remaining closed gates | reviewer-oracle preparation, administrative implementation, another transform group, broad Phase A reassessment, F02/F14 closure, Review 12, Phase B, publication, deployment, merge, PR #8 |
| Current instructed action | Prepare one administrative identity-shell authority-decision proposal only. |
| Next instruction required from SDA | YES — before reviewer-oracle preparation, administrative implementation, another transform group, broad Phase A reassessment, F02/F14 closure, Review 12, Phase B, publication, deployment or merge. |

