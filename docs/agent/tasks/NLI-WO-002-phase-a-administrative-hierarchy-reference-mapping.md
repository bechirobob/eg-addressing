# NLI-WO-002 Phase A administrative hierarchy and reference-identity mapping pack

**Base / continuation commit:** `ed2d2a563720beca3ee09abd487797232e36ece3`

**Reviewed mapping:** `2a14a74e472eda04a06f89f754a145b4450a77f9`. **SDA assessment:** `docs/sda/reviews/NLI-WO-002-administrative-hierarchy-mapping-assessment.json`. Decision: correction required, mapping only, findings C38-C40.

## 0. Scope and closed-gate declaration
This document is a mapping pack only. It does not prepare or approve a reviewer oracle; implement an administrative transform; modify accepted callables or convergence; accept broad Phase A; close F02 or F14; authorize Review 12 or Phase B; authorize public-code issuance or publication; authorize deployment or merge; or modify PR #8.

## 1. Controlling artifacts pinned
| artifact | path | git blob | sha256 |
| --- | --- | --- | --- |
| corrected residual-readiness mapping | docs/agent/tasks/NLI-WO-002-phase-a-residual-control-readiness-mapping.md | 7fcb73f3c99c56ba9c38207c689492a608fe17b7 | d2ae6ffc999c8f59486dcbc7a0d47d62a2465b99ec9aa3cf1116384003526758 |
| current PostgreSQL catalog | docs/sda/data-model/current-pg-catalog.json | 2948290a494c125ce2254ffa8cb7861f4ea8d7cb | 0b022dd03fecb6bdec12baa159c6bb83aaa477fcc3fa35e9ab0110d14a0c52d5 |
| complete current-source fixture | docs/sda/data-model/fixtures/current-source/phase-a-complete-source-records.json | 6e5ad53ba59a12a5db3a5718b94b3ee44886c570 | 6d5daca924bfe5141b7039f4cad06006faf39fd46bd9d4b50c74d273d2d7de10 |
| draft physical target schema | docs/sda/data-model/draft-physical-schema.sql | b92c5343900bfc7cc54f182ca7a6838910f4c8e7 | 902a10ac233301a841c600fe4ea047623b68ae42241c929fcdc358353f33936a |
| live narrow transform specification | docs/sda/data-model/fixtures/transform-specs/phase-a-transform-specs.json | 32b284917bafd5bdc5bef7804230b8eb81033697 | 5f6defcdf1a27f736ee1736a158a15ed83530daed8490af7719f6b9784454fc4 |
| frozen broad transform specification | docs/sda/data-model/fixtures/transform-specs/phase-a-broad-generic-transform-specs-frozen.json | 443de54b6bacf6a12106fdbba5dba1a07955eec4 | b601f4fe1c5676511010d10d5b9e819e83fc50a2bbedce11c324e2f4a05099cf |
| broad expected-target fixture | docs/sda/data-model/fixtures/expected-target/phase-a-expected-target-records.json | 7df5326902315123ebb8bc4970899dd293f30c58 | 4b98cc1b580b2513cd0f1eee3a53af87376a1d6efa7c8792ab1211e38a22ea76 |
| accepted-family convergence mapping | docs/agent/tasks/NLI-WO-002-phase-a-accepted-family-convergence-mapping.md | c984a16f352417b9fde0f8cb9e0536a5e0ab6eb1 | 382c1ccd0de2b90ecb08241d8cf3f6788ae7166ef93f9122bb6ed3b6ed3669ce |
| convergence control | docs/sda/acceptance/NLI-WO-002-phase-a-accepted-family-convergence-control.json | 3c4c59fa5eeb004cfb8ef2520241d74c130fa926 | d714b32ea170e05b5feef240d587d860ed0c712812036f384e357381a60b3b8a |
| accepted convergence report | docs/sda/data-model/phase-a-accepted-family-convergence-report.json | bc0346d30eb49f1d2956b81e6cffa5e3e9933d65 | f28cd006d27cf0d764db1863956d39dc97aa13b11df0d063d8c3b8ad2698a304 |
| accepted addresses identity control | docs/sda/acceptance/NLI-WO-002-phase-a-addresses-identity-expected.json | 4c1d6068bc39da7a8fef7ed3dbaa1454f27282c8 | 518af277e96c94c55808f9ac1e7992059c371bd225d906cf77156c478b0497cd |
| accepted address-records identity control | docs/sda/acceptance/NLI-WO-002-phase-a-address-records-identity-expected.json | 79e3ee0ccccbfad318a61d58ae036ed8170e0a77 | 16d1034b786a77d31b6863774807e66d87a337fa78c1a4202e401fbcddecd06e |
| accepted address-records geometry control | docs/sda/acceptance/NLI-WO-002-phase-a-address-records-geometry-expected.json | bd3e821f07e0a1d3968e3dd6f76e6201ea7229fd | 7a5e68c4639fe290fd46c38d41c754ae25737bee8b260278817970e7758d20e2 |
| accepted address-points observation crosswalk control | docs/sda/acceptance/NLI-WO-002-phase-a-address-points-observation-crosswalk-expected.json | 7d964599a5500aa5430da208aefdc940c3c0af1b | d1b695994ae774a6c54cc99c1e79a0bce023fd5a9a20ec2aee779cfeb10bfa82 |
| accepted address-points geometry control | docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-expected.json | 691d08f09bfd12e227207cd5913b6b54caf59536 | cf699de04e0ca500c3a7826f257e190d24835356ef96db1650160d7d438edaea |
| accepted citizen-geotag identity control | docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-identity-expected.json | 61fb777a2af5a917b4ea7bbff0d6c7dff09241ba | 65e4f2511f70ed1e94562f4973fbbb1ab072592d3b27b94f2a459843647af45e |
| accepted citizen-geotag geometry control | docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-geometry-expected.json | d5ae8a9a859ec466b68365ee006c310a85955504 | 5a09abd8a017dcbf8210040e9311bc4118be82e24c245cafa485987eb5932a46 |
| C38-C40 assessment | docs/sda/reviews/NLI-WO-002-administrative-hierarchy-mapping-assessment.json | d5414abba28489e6032819479ac2c4c8b658a98d | 9baa93e62658e45ea433f6879408628f455ce3b3242768a293668ffa24144d5b |

## 2. Source tables audited
| source table | source key | source_record_id | field | fixture value | classification |
| --- | --- | --- | --- | --- | --- |
| admin_units | admin_units:phase-a-admin-units-001 | phase-a-source-record-admin-units-001 | id | phase-a-admin-units-id | identity candidate |
| admin_units | admin_units:phase-a-admin-units-001 | phase-a-source-record-admin-units-001 | level | phase-a admin_units level | unresolved authority input |
| admin_units | admin_units:phase-a-admin-units-001 | phase-a-source-record-admin-units-001 | code | phase-a-admin-units-code | administrative code |
| admin_units | admin_units:phase-a-admin-units-001 | phase-a-source-record-admin-units-001 | parent_id | phase-a-parent-id | hierarchy reference |
| admin_units | admin_units:phase-a-admin-units-001 | phase-a-source-record-admin-units-001 | province_code | BN | hierarchy reference |
| admin_units | admin_units:phase-a-admin-units-001 | phase-a-source-record-admin-units-001 | name_es | phase-a admin_units name_es | bilingual name |
| admin_units | admin_units:phase-a-admin-units-001 | phase-a-source-record-admin-units-001 | name_en | phase-a admin_units name_en | bilingual name |
| admin_units | admin_units:phase-a-admin-units-001 | phase-a-source-record-admin-units-001 | status | submitted | lifecycle/context |
| admin_units | admin_units:phase-a-admin-units-001 | phase-a-source-record-admin-units-001 | sort_order | 1 | ordering/context |
| admin_units | admin_units:phase-a-admin-units-001 | phase-a-source-record-admin-units-001 | created_at | 2026-07-15T00:00:00Z | temporal context |
| admin_units | admin_units:phase-a-admin-units-001 | phase-a-source-record-admin-units-001 | updated_at | 2026-07-15T00:00:00Z | temporal context |
| provinces | provinces:phase-a-provinces-001 | phase-a-source-record-provinces-001 | code | phase-a-provinces-code | administrative code |
| provinces | provinces:phase-a-provinces-001 | phase-a-source-record-provinces-001 | name | Phase A provinces | bilingual name |
| provinces | provinces:phase-a-provinces-001 | phase-a-source-record-provinces-001 | created_at | 2026-07-15T00:00:00Z | temporal context |
| territories | territories:phase-a-territories-001 | phase-a-source-record-territories-001 | id | phase-a-territories-id | identity candidate |
| territories | territories:phase-a-territories-001 | phase-a-source-record-territories-001 | name | Phase A territories | bilingual name |
| territories | territories:phase-a-territories-001 | phase-a-source-record-territories-001 | province_code | BN | hierarchy reference |
| territories | territories:phase-a-territories-001 | phase-a-source-record-territories-001 | admin_unit_id | phase-a-admin-unit-id | hierarchy reference |
| territories | territories:phase-a-territories-001 | phase-a-source-record-territories-001 | type | phase-a territories type | unresolved authority input |
| territories | territories:phase-a-territories-001 | phase-a-source-record-territories-001 | readiness | phase-a territories readiness | excluded from identity |
| territories | territories:phase-a-territories-001 | phase-a-source-record-territories-001 | is_archived | False | lifecycle/context |
| territories | territories:phase-a-territories-001 | phase-a-source-record-territories-001 | created_at | 2026-07-15T00:00:00Z | temporal context |
| territories | territories:phase-a-territories-001 | phase-a-source-record-territories-001 | updated_at | 2026-07-15T00:00:00Z | temporal context |

## 3. Fixture inconsistencies — recorded, not normalized
| fixture value | finding | mismatch type | do not repair |
| --- | --- | --- | --- |
| admin_units.id = phase-a-admin-units-id | does not match territories.admin_unit_id = phase-a-admin-unit-id | unresolved source-system relationship; required authority lookup; required future mutation test | yes |
| territories.admin_unit_id = phase-a-admin-unit-id | does not match admin_units.id = phase-a-admin-units-id | deliberately incomplete fixture relationship; malformed generic fixture; required future mutation test | yes |
| admin_units.parent_id = phase-a-parent-id | references no source admin_units.id in the complete fixture | unresolved source-system relationship; required authority lookup; required future mutation test | yes |
| admin_units.province_code = BN | does not match provinces.code = phase-a-provinces-code | required authority lookup; unresolved source-system relationship; required future mutation test | yes |
| territories.province_code = BN | does not match provinces.code = phase-a-provinces-code | required authority lookup; unresolved source-system relationship; required future mutation test | yes |
| provinces.code = phase-a-provinces-code | generic fixture code conflicts with BN used by admin_units/territories/address context fields | malformed generic fixture; required authority lookup; required future mutation test | yes |
| admin_units.level = phase-a admin_units level | not one of target vocabulary country/province/district/municipality/local_council | malformed generic fixture; unresolved authority input; required future mutation test | yes |

## 4. Source-to-subject model alternatives
| model | status | summary |
| --- | --- | --- |
| A — admin_units is canonical | evaluated; not selected | admin_units.id owns administrative identity; provinces/territories become aliases/context after authority. Strong single-owner model, but fixture mismatches and province authority remain unresolved. |
| B — all three tables own distinct administrative units | evaluated; not selected | provinces, admin_units and territories each own administrative identities. Preserves source rows but risks duplicate semantic subjects and wrongly promoting operational territories. |
| C — split administrative and operational concepts | preferred working hypothesis | provinces/admin_units are administrative candidates; territories remain locality/operational/context until territory registry authority classifies each row. Accepted address rows remain unchanged. |

**Recommended model:** Model C — split administrative and operational concepts.
**Recommendation confidence:** medium. Model C remains a working hypothesis only; it does not authorize an oracle or implementation.
## 5. C38 physical-lineage matrix
Do not claim target-persisted source-record lineage where no target column exists. Source-record lineage for the administrative identity shell is comparator-enforced, not fully persisted on the identity row.
| target family | actual lineage columns present | source_record_id persisted | evidence_object_id persisted | source_authority_id persisted | source_table/source_field/legacy_id persisted | target row join back to exact source record | evidence only in test_control/reviewer evidence | cannot persist without future schema change |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| proposed_administrative_unit | administrative_unit_id, country_id, created_at, retired_at only | no | no | no | no | none directly; join through proposed_legacy_crosswalk.target_entity=administrative_unit and target_id=administrative_unit_id, then comparator maps source_table/source_field/legacy_id to reviewed source record | source_record/evidence_object proof for identity shell | direct identity-row source_record_id, evidence_object_id, source_authority_id |
| proposed_administrative_unit_version | administrative_unit_version_id, administrative_unit_id, parent_administrative_unit_id, admin_level, lifecycle_state, effective dates, recorded dates, source_authority_id, classification | no | no | yes | no | none directly; only authority can be joined; comparator must prove version values against reviewed source/control inputs | source row/evidence object behind level, parent and effective-date decisions | direct version source_record_id/evidence_object_id or separate version-lineage relation |
| proposed_administrative_code_history | admin_code_history_id, administrative_unit_id, code_scheme, official_code, effective dates, recorded dates, source_id | yes, as source_id referencing proposed_source_record.source_record_id | no | no | no | source_id -> proposed_source_record.source_record_id | evidence_object and authority proof for code scheme/history | direct evidence_object_id/source_authority_id on code-history row |
| proposed_name_record | name_record_id, subject_id, language_code, name_kind, name_status, name_text, normalized_text, source_record_id, effective dates | yes | no | no | no | source_record_id -> proposed_source_record.source_record_id | evidence_object, field-level name authority and language decision | direct evidence_object_id/source_authority_id/source_field on name row |
| proposed_legacy_crosswalk | legacy_crosswalk_id, source_table, source_field, legacy_id, target_entity, target_id, created_at | no | no | no | yes | source_table + source_field + legacy_id can be comparator-matched to reviewed proposed_source_record/source_key but no source_record_id/source_key column exists | proof that legacy tuple corresponds to expected source record and evidence object | direct source_record_id/source_key/evidence_object_id on crosswalk |
| proposed_registry_subject | subject_id, subject_entity, created_at, native_id, subject_state, retired_at, delete_policy | no | no | no | no | none directly; subject native_id joins to administrative_unit_id, then identity lineage is crosswalk/comparator-enforced | subject ownership by identity slice and source/evidence proof | direct subject lineage columns or subject-source relation |

### C38 lineage model evaluation
| lineage model | definition | direct persisted source-record lineage on identity/version | oracle implication |
| --- | --- | --- | --- |
| L1 — Current-schema indirect lineage | Administrative identity is linked by proposed_legacy_crosswalk.source_table/source_field/legacy_id -> target_entity/target_id. The reviewer comparator separately proves that the crosswalk corresponds to the reviewed proposed_source_record and evidence object. | no | possible for an identity-shell oracle without schema change if the oracle explicitly checks crosswalk-to-source-record/evidence in test_control/reviewer evidence |
| L2 — Lineage-bearing fact rows | Identity shell is linked indirectly through crosswalk, while code-history and name facts carry direct source-record lineage via source_id/source_record_id. | no | good for code/name facts, but does not solve direct lineage for administrative_unit, version or registry_subject |
| L3 — Future schema enhancement | Future schema change adds administrative identity/version lineage relation or source_record_id/evidence_object_id columns. | would be yes after change | not authorized now; useful later if SDA requires target-persisted lineage rather than comparator-enforced lineage |

**Recommended lineage model:** L1 — Current-schema indirect lineage, with L2 for name/code fact rows where those rows actually carry source-record columns.
**Oracle possible without schema change:** YES for the administrative identity shell only, if the future reviewer oracle explicitly proves crosswalk-to-source-record/evidence correspondence in comparator/test_control evidence. NO for direct target-persisted identity/version source-record lineage without a future schema change.
## 6. C39 identity stability and registry-subject ownership
### Province source identity
- `provinces.code` is the current-source primary key. It is not automatically the stable canonical administrative identity.
- Separate concepts: current-source row identity = `provinces.code`; stable canonical administrative identity = reviewer/authority-assigned province identity token; official administrative code = code value approved for code history; historical code value = effective-dated code-history row.
- Province-code change outcomes: (1) new source row resolves to same canonical administrative unit if authority proves continuity; (2) new canonical administrative identity if authority says the code change represents a new unit; or (3) unresolved authority event requiring manual linkage.
- Do not derive permanent `administrative_unit_id` directly from mutable normalized `provinces.code` unless the authority explicitly declares the code immutable.
- Province identity is authority-blocked and not oracle-ready until stable canonical identity and code-continuity rules are decided.
### Admin-unit source identity
- `admin_units.id` remains the preferred source identity candidate, subject to official hierarchy authority.
- Target deterministic ID must be independent from name, code, parent and status changes. Candidate rule: `administrative-unit:admin_units:{admin_units.id}` after authority confirms `admin_units.id` is stable enough for the identity shell.
- Name/code/parent/status changes create facts, versions or authority events; they must not rewrite the administrative identity shell ID.
### Territory identity
- Under Model C, territory identity remains distinct from administrative-unit identity until the territory registry authority decides whether each territory is an administrative unit, locality, operational area, or another context entity.
- Territory rows are excluded from the first administrative identity oracle.
### Registry-subject model
**Selected model:** Subject Model S1 — Identity slice owns subject. The administrative identity slice creates the administrative unit, administrative legacy crosswalk and administrative registry subject. The subject is mandatory, not optional. No name or geometry slice may create a subject.
| property | value |
| --- | --- |
| subject_entity | administrative_unit |
| native_id | the owned proposed_administrative_unit.administrative_unit_id |
| subject ID rule | subject:administrative_unit:{administrative_unit_id} |
| state | active on insert; retire-only if administrative unit retires |
| delete policy | retire-only |
| owner slice | Subject Model S1 — identity slice owns subject |
| expected insert count | 1 registry subject per administrative identity shell row |
| expected absence rules | no accepted address subject; no phase-a-subject-phase-a-location-geotag; no generic subject for multiple administrative records; no subject created by name/geometry slice |

### Exact identity-shell rows under S1
| row family | exact count | owner | ID rule |
| --- | --- | --- | --- |
| proposed_administrative_unit | 1 | administrative identity shell slice | administrative-unit:admin_units:phase-a-admin-units-id, only after official hierarchy authority confirms admin_units.id as stable source identity candidate |
| proposed_legacy_crosswalk | 1 | administrative identity shell slice | crosswalk:admin_units:id:phase-a-admin-units-id:to:administrative_unit:{administrative_unit_id} |
| proposed_registry_subject | 1 | administrative identity shell slice under S1 | subject:administrative_unit:{administrative_unit_id} |

## 7. Candidate target row families — corrected ownership and lineage
| target family | owner and deterministic ID rule | lineage statement | expected absences |
| --- | --- | --- | --- |
| proposed_administrative_unit | identity shell slice; administrative-unit:admin_units:{admin_units.id} only after authority approves admin_units.id stability | no persisted source_record/evidence/authority columns; lineage is through crosswalk plus comparator/test_control evidence | no location_record, no name/code/version/publication rows |
| proposed_administrative_unit_version | future hierarchy version slice only after level/parent/effective-date authority | source_authority_id persisted; no source_record_id/evidence_object_id | absent from identity shell |
| proposed_administrative_code_history | future code-history slice; ID includes code_scheme, unit, normalized code and effective_from | source_id persists proposed_source_record; evidence/authority not persisted on row | absent until code authority resolves; no public_code_alias |
| proposed_name_record | future naming slice; ID includes S1 subject, language, kind, normalized text and source record | source_record_id persisted; evidence/authority not persisted on row | no names on generic/accepted address subjects |
| proposed_legacy_crosswalk | identity shell or code/crosswalk slice; tuple source_table/source_field/legacy_id -> target | source tuple persisted but no source_record_id/source_key; comparator enforces exact source-record/evidence match | no duplicate semantic crosswalk; no one source to multiple targets |
| proposed_registry_subject | S1 identity shell; subject:administrative_unit:{administrative_unit_id} | no source-lineage columns; lineage through native_id -> administrative_unit -> crosswalk/comparator proof | not optional; no accepted/geotag/generic subject reuse |

## 8. Hierarchy semantics
| rule | definition |
| --- | --- |
| allowed levels | country, province, district, municipality, local_council only |
| root behavior | country is prerequisite; province is first-level within country unless future authority approves country-level admin unit row |
| missing parent | fail with administrative hierarchy parent missing unless row is approved root |
| self parent | fail with administrative hierarchy self parent prohibited |
| cycle | fail with administrative hierarchy cycle detected |
| wrong parent level | fail with administrative hierarchy parent level mismatch |
| effective dates | blocked until effective-date authority resolves; no version row in identity shell |

## 9. Code ownership and bilingual naming rules
| case | rule |
| --- | --- |
| internal deterministic primary keys | target IDs are internal; not public and not derived from mutable public codes unless authority declares immutability |
| source legacy IDs | persist in proposed_legacy_crosswalk; source_record_id is comparator-enforced, not persisted on crosswalk |
| province codes | provinces.code is current-source PK but not automatically stable canonical identity; code goes to crosswalk/code-history after authority |
| admin-unit codes | candidate code-history value; cannot change administrative_unit_id |
| territory IDs | source identity for territory entity only after classification; outside first administrative identity oracle |
| public codes | not authorized; proposed_public_code_alias absent |
| same code different tables | collision unless authority defines scoped code scheme |
| code reused across levels | reject without scoped scheme and authority proof |
| code changes over time | manual authority event determines same canonical unit vs new unit vs unresolved linkage; record history only after authority |
| case/format differences | preserve source value; compare normalized value for collisions |
| one code to multiple targets | fail with administrative code multiple unit resolution |

| field | language | target subject | lineage | authority |
| --- | --- | --- | --- | --- |
| admin_units.name_es | es | administrative_unit subject owned by S1 identity slice | source_record_id persisted on name_record | bilingual naming authority required |
| admin_units.name_en | en | administrative_unit subject owned by S1 identity slice | source_record_id persisted on name_record | bilingual naming authority required |
| provinces.name | undetermined/es-or-en | province administrative_unit subject only after province canonical identity authority | source_record_id persisted on name_record | province naming/language authority required |
| territories.name | undetermined/es-or-en | territory locality/operational_area/admin subject only after territory classification | source_record_id persisted on name_record | territory registry/naming authority required |

## 10. Accepted-family administrative-context dependencies
Accepted rows and the accepted-family convergence union remain unchanged. Future integration uses new crosswalk/context slices, not accepted identity row mutation.
| source field | currently accepted context only | future lookup path | accepted rows changed |
| --- | --- | --- | --- |
| addresses.territory_id | yes | territory_id -> territory crosswalk after classification -> locality/operational/admin context | no |
| addresses.province_code | yes | province_code -> code-history/crosswalk after province authority | no |
| address_records.territory_id | yes | territory_id -> territory context crosswalk | no |
| address_records.province_code | yes | province_code -> province/admin code-history | no |
| roads.territory_id | no | future roads slice reads territory context crosswalk | no |
| buildings.territory_id | no | future buildings slice reads territory context crosswalk | no |
| field_assignments.territory_id | no | field operational-area/territory coverage after classification | no |
| field_submissions.territory_id | no | field submission territory/locality/operational context | no |

## 11. Authority-decision register / RFIs
| RFI | status |
| --- | --- |
| official administrative hierarchy owner | unresolved; mapping/RFI drafting only; implementation/oracle preparation prohibited until resolved where it affects exact expected rows |
| official province-code owner | unresolved; mapping/RFI drafting only; implementation/oracle preparation prohibited until resolved where it affects exact expected rows |
| official territory registry owner | unresolved; mapping/RFI drafting only; implementation/oracle preparation prohibited until resolved where it affects exact expected rows |
| bilingual naming authority | unresolved; mapping/RFI drafting only; implementation/oracle preparation prohibited until resolved where it affects exact expected rows |
| administrative level translation | unresolved; mapping/RFI drafting only; implementation/oracle preparation prohibited until resolved where it affects exact expected rows |
| parent-lineage authority | unresolved; mapping/RFI drafting only; implementation/oracle preparation prohibited until resolved where it affects exact expected rows |
| code history authority | unresolved; mapping/RFI drafting only; implementation/oracle preparation prohibited until resolved where it affects exact expected rows |
| effective-date authority | unresolved; mapping/RFI drafting only; implementation/oracle preparation prohibited until resolved where it affects exact expected rows |
| classification and public-release authority | unresolved; mapping/RFI drafting only; implementation/oracle preparation prohibited until resolved where it affects exact expected rows |

## 12. C40 exact future negative-test contracts — designs only
These are contract designs only. They do not prepare a reviewer oracle and do not authorize implementation.
| test_id | owning proposed slice | exact baseline source rows and IDs | exact prerequisite target rows | exact mutation value | exact callable or comparator stage | exact expected error string | expected inserted/updated/deleted row sets before failure | same-database rollback proof | read-only comparison expectation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADMIN-NEG-001 | administrative identity shell / future hierarchy version | admin_units:phase-a-admin-units-001; provinces:phase-a-provinces-001 | country prerequisite; source_authority/source_record/evidence prerequisites; identity shell rows if version stage is tested | admin_units.level = unsupported_prefecture | comparator validation before target insert | administrative hierarchy unsupported level | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-002 | administrative hierarchy version | admin_units:phase-a-admin-units-001 | identity shell rows; parent lookup prerequisite intentionally absent | admin_units.parent_id = missing-admin-unit-id | comparator validation before version insert | administrative hierarchy parent missing | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-003 | administrative hierarchy version | admin_units:phase-a-admin-units-001 | identity shell rows for child | admin_units.parent_id = phase-a-admin-units-id | comparator validation before version insert | administrative hierarchy self parent prohibited | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-004 | administrative hierarchy version | admin_units:phase-a-admin-units-001 plus reviewed parent fixture row | identity shell rows for both units | parent row points back to child administrative_unit_id | comparator graph validation before commit | administrative hierarchy cycle detected | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-005 | administrative hierarchy version | admin_units:phase-a-admin-units-001 plus parent unit | identity shell + parent version rows | parent admin_level = local_council while child admin_level = province | comparator hierarchy validation | administrative hierarchy parent level mismatch | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-006 | administrative code/history or context lookup | admin_units:phase-a-admin-units-001; provinces:phase-a-provinces-001 | identity shell rows; province code authority fixture | admin_units.province_code = XX while provinces.code = BN | comparator source relationship validation | administrative hierarchy province code mismatch | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-007 | accepted-context dependency integration / territory classification | territories:phase-a-territories-001; admin_units:phase-a-admin-units-001 | identity shell rows; territory classification prerequisite | territories.admin_unit_id = different-admin-unit-id | comparator territory relationship validation | administrative hierarchy territory relationship mismatch | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-008 | administrative identity shell | admin_units:phase-a-admin-units-001 plus duplicate source row | country/source/evidence prerequisites | two source rows resolve to same administrative_unit_id or subject_id | comparator semantic uniqueness check | administrative identity duplicate semantic subject | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-009 | administrative identity shell | admin_units:phase-a-admin-units-001 | existing crosswalk for same source_table/source_field/legacy_id | same legacy tuple resolves to second target_id | comparator crosswalk uniqueness check | administrative crosswalk multiple target resolution | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-010 | administrative code history/crosswalk | admin_units:phase-a-admin-units-001; provinces:phase-a-provinces-001 | two authority-approved units in same code_scheme | official_code BN resolves to two administrative_unit_id values | comparator code uniqueness check | administrative code multiple unit resolution | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-011 | administrative names | admin_units:phase-a-admin-units-001 | identity shell rows and S1 registry subject | name_record.subject_id = phase-a-subject-phase-a-location-address-reference | comparator name subject validation | administrative name subject mismatch | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-012 | administrative identity shell / names / geometry preparation | admin_units:phase-a-admin-units-001 | identity shell rows | subject_id = phase-a-subject-phase-a-location-geotag | comparator subject ownership validation | administrative generic subject reuse prohibited | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-013 | administrative identity shell / version | admin_units:phase-a-admin-units-001 | authority-approved expected classification | classification = public-after-release before release authority or mismatched government-internal expectation | complete expected/actual comparison | administrative classification drift | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-014 | all administrative slices | admin_units:phase-a-admin-units-001 | identity shell prerequisites only | insert proposed_public_code_alias or proposed_publication_release_item | unexpected-row comparator | administrative public output prohibited | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-015 | administrative hierarchy version / country prerequisite | admin_units:phase-a-admin-units-001 | source_authority prerequisite intentionally absent | source_authority_id = missing-authority-id | precondition comparator | administrative source authority missing | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-016 | administrative identity shell | admin_units:phase-a-admin-units-001 | source_record/evidence prerequisites; crosswalk expected tuple | crosswalk legacy_id = phase-a-admin-units-id but comparator source_record = wrong source record | lineage comparator | administrative lineage mismatch | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |
| ADMIN-NEG-017 | all administrative slices | admin_units:phase-a-admin-units-001 | identity shell expected rows only | extra proposed_decision_event, proposed_migration_exception, proposed_name_record or code_history in identity shell | complete attributable-union comparator | administrative unexpected target row | inserts=0, updates=0, deletes=0 for failing mutation; if failure occurs after staged writes, same transaction must roll back to pre-test attributable set | required: complete pre-test rows/hash equals post-rollback rows/hash | not applicable unless test stage is read-only comparator; read-only comparator must not write |

## 13. C40 positive proof contracts — not failing mutations
| contract_id | proof contract | requirements | not a failing mutation |
| --- | --- | --- | --- |
| ADMIN-POS-001 | second-run idempotency | first-run exact expected inserts; second-run 0 inserts, 0 updates, 0 deletes; identical attributable union and hash | yes |
| ADMIN-POS-002 | read-only complete comparison | separate connection; read-only transaction; attempted write blocked; expected/actual comparison in both directions; complete normalized values compared | yes |
| ADMIN-POS-003 | same-database rollback equality | mandatory evidence for every failing database mutation: complete pre-test rows, complete post-rollback rows, pre/post counts, pre/post hashes, row equality, hash equality | yes |

## 14. Corrected potential slice boundaries — no optional rows
| slice | status | exact source table | exact covered fields | context fields | exact owned rows | prerequisite slices | authority prerequisite | privacy/publication boundary | expected inserts | expected absences |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Administrative identity shell — authority-approved admin_units.id | recommended first potential slice; not authorized | admin_units | admin_units.id only for identity; source_key/source_record/evidence verified by comparator/test_control | proposed_country prerequisite; source authority/source package/source record/evidence prerequisites | one proposed_administrative_unit; one proposed_legacy_crosswalk; one proposed_registry_subject because S1 selected | country/source/evidence prerequisites | official hierarchy owner confirms admin_units.id stable enough for identity shell | government-internal; no public release | 3 exact rows | no location_record; no address subject; no name_record; no code_history; no public_code_alias; no publication; no decision_event; no migration exception unless separately authorized RFI model requires it |
| Administrative hierarchy version | authority-blocked; not first oracle-ready | admin_units | level, parent_id, status, created_at, updated_at after authority | approved identity shell rows; parent identity rows; source_authority_id | conditional exact alternative A: one proposed_administrative_unit_version when level/parent/effective-date authority resolves; alternative B: zero rows and authority-blocked failure | identity shell; parent identity if non-root | level translation, parent-lineage and effective-date authority | no publication | 0 until authority; then exactly 1 version row per approved admin_units row | no inferred parent, no version from unsupported level, no decision_event |
| Province identity | authority-blocked; not oracle-ready | provinces | code as current-source PK only; name as later naming fact | reviewer-assigned canonical province identity token required | conditional exact alternative A: one administrative unit, one crosswalk, one S1 subject after canonical identity authority; alternative B: zero rows while authority-blocked | stable province canonical identity decision | stable identity and code-continuity authority | no public-code issuance | 0 until authority | no ID derived directly from mutable normalized provinces.code |
| Territory identity | outside administrative identity slice under Model C; authority-blocked for classification | territories | id, admin_unit_id, province_code, type, readiness only after classification | territory registry authority and Model C target choice | conditional exact alternative A: locality/operational_area/admin unit rows depending classification; alternative B: zero administrative identity rows | territory classification decision; admin identity/context crosswalks | territory registry owner decides administrative unit vs locality vs operational area vs other context entity | government-internal; no publication | 0 in first administrative identity oracle | no territory rows in first administrative identity oracle |
| Administrative code history/crosswalk | blocked until identity and code authority | admin_units, provinces, territories | admin_units.code, admin_units.province_code, provinces.code, territories.province_code, territories.id | resolved administrative_unit_id; code_scheme; effective dates | conditional exact alternative A: exact proposed_administrative_code_history rows after authority; alternative B: zero rows while code authority unresolved | identity shell and/or province identity | province-code owner and code-history authority | administrative codes are not NLI public address codes | 0 until authority | no proposed_public_code_alias |
| Administrative names | blocked until S1 subject exists and naming authority resolves | admin_units, provinces, territories | admin_units.name_es, admin_units.name_en, provinces.name, territories.name | S1 registry subject, language decision, name authority, effective dates | conditional exact alternative A: exact proposed_name_record rows for approved subject/language; alternative B: zero rows until authority | identity shell with S1 subject; naming authority | bilingual naming authority and subject ownership | not public until release authority | 0 until authority | no names on accepted address/geotag/generic subjects |
| Accepted-context dependency integration | future slice; not authorized | addresses, address_records, roads, buildings, field_assignments, field_submissions | territory_id, province_code | admin/territory crosswalks, code history | conditional exact alternatives depend on future context relation target; accepted identity rows remain unchanged | identity, code history, territory classification | territory registry owner and context lookup authority | no publication | 0 now | no accepted-family convergence union mutation |

**Recommended first potential slice:** Administrative identity shell — authority-approved `admin_units.id`, with S1 mandatory registry subject ownership.
**Authority-blocked slices:** administrative hierarchy version; province identity; territory identity; administrative code history/crosswalk; administrative names; accepted-context dependency integration.
## 15. F02 / F14 impact and remaining gates
| item | status |
| --- | --- |
| Accepted rows modified | 0 |
| Accepted convergence modified | no |
| F02 status | partially satisfied and open; C38-C40 improve mapping contracts only |
| F14 status | partially satisfied and open; no broad reassessment or oracle prepared |
| Remaining closed gates | administrative reviewer-oracle preparation, implementation, another transform group, broad Phase A reassessment, F02/F14 closure, Review 12, Phase B, publication, deployment, merge, PR #8 |

## 16. Return summary values
| field | value |
| --- | --- |
| Lineage matrix rows | 6 |
| Identity persisted source_record | no |
| Version persisted source_record | no |
| Crosswalk persisted source_record | no |
| Subject persisted source_record | no |
| Code-history persisted source_record | yes, as source_id referencing proposed_source_record |
| Name persisted source_record | yes, as source_record_id |
| Recommended lineage model | L1 — Current-schema indirect lineage, plus L2 for code/name fact rows |
| Oracle possible without schema change | YES for administrative identity shell only with comparator-enforced source/evidence lineage; NO for direct persisted identity/version lineage |
| Province source PK | provinces.code |
| Province canonical identity rule | reviewer/authority-assigned canonical province identity token; do not derive permanent ID from mutable normalized code |
| Province code-continuity rule | code change is same unit, new unit, or unresolved manual linkage only by authority decision; province identity remains authority-blocked/not oracle-ready |
| Admin-unit identity rule | admin_units.id preferred source identity; target ID independent from name/code/parent/status changes after hierarchy authority confirms stability |
| Territory identity status | distinct from administrative-unit identity; excluded from first administrative identity oracle under Model C until territory classification authority resolves |
| Registry-subject model | S1 — identity slice owns subject |
| Registry-subject owner | administrative identity shell slice |
| Registry-subject mandatory | yes |
| Subject ID rule | subject:administrative_unit:{administrative_unit_id} |
| Exact identity-shell rows | one proposed_administrative_unit; one proposed_legacy_crosswalk; one proposed_registry_subject |
| Exact negative-test contracts | 17 |
| Exact positive-proof contracts | 3 |
| Idempotency contract | first-run exact expected inserts; second-run 0 inserts/updates/deletes; identical attributable union/hash |
| Read-only contract | separate connection; read-only transaction; attempted write blocked; bidirectional complete normalized comparison |
| Rollback evidence contract | complete pre/post attributable rows, counts, hashes, row equality and hash equality for every failing database mutation |
| Potential slice boundaries | 7 |
| Recommended first potential slice | Administrative identity shell — authority-approved admin_units.id |
| Authority-blocked slices | administrative hierarchy version; province identity; territory identity; administrative code history/crosswalk; administrative names; accepted-context dependency integration |
| Accepted rows modified | 0 |
| Accepted convergence modified | no |
| F02 status | partially satisfied and open |
| F14 status | partially satisfied and open |
| Remaining closed gates | administrative reviewer-oracle preparation, implementation, another transform group, broad Phase A reassessment, F02/F14 closure, Review 12, Phase B, publication, deployment, merge, PR #8 |
| Current instructed action | Correct C38-C40 in the administrative hierarchy and reference-identity mapping only. |
| Next instruction required from SDA | YES — before administrative reviewer-oracle preparation, implementation, another transform group, broad Phase A reassessment, F02/F14 closure, Review 12, Phase B, publication, deployment or merge. |
