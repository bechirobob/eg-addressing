# NLI-WO-002 Phase A administrative hierarchy and reference-identity mapping pack

**Base / continuation commit:** `d3de026620249857a1a858f6b8e1afe04c9dcb4b`

**PR review read:** `4714974768` — C37 accepted; one administrative hierarchy/reference mapping checkpoint authorized; no reviewer oracle, transform, broad Phase A, F02/F14 closure, Review 12, Phase B, deployment, publication, merge, or PR #8 work authorized.

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
| admin_units.id = phase-a-admin-units-id | does not match territories.admin_unit_id = phase-a-admin-unit-id or requested canonical-looking admin-unit references | unresolved source-system relationship; required authority lookup; required future mutation test | yes |
| territories.admin_unit_id = phase-a-admin-unit-id | does not match admin_units.id = phase-a-admin-units-id | deliberately incomplete fixture relationship; malformed generic fixture; required future mutation test | yes |
| admin_units.parent_id = phase-a-parent-id | references no source admin_units.id in the complete fixture | unresolved source-system relationship; required authority lookup; required future mutation test | yes |
| admin_units.province_code = BN | does not match provinces.code = phase-a-provinces-code | required authority lookup; unresolved source-system relationship; required future mutation test | yes |
| territories.province_code = BN | does not match provinces.code = phase-a-provinces-code | required authority lookup; unresolved source-system relationship; required future mutation test | yes |
| provinces.code = phase-a-provinces-code | generic fixture code conflicts with BN used by admin_units/territories/address context fields | malformed generic fixture; required authority lookup; required future mutation test | yes |
| admin_units.level = phase-a admin_units level | not one of target vocabulary country/province/district/municipality/local_council | malformed generic fixture; unresolved authority input; required future mutation test | yes |

## 4. Source-to-subject model alternatives

| model | advantages | contradictions | required target rows | hierarchy behavior | impact on accepted addresses and address_records | authority decisions | privacy/publication implications | negative tests | physical schema supports it |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A — admin_units is canonical | single owner for administrative-unit identity; avoids duplicate subject for the same real-world unit; aligns parent_id and code/name fields around one table | fixture province_code BN conflicts with provinces.code; territories.admin_unit_id mismatch; provinces may be official first-level authority not mere alias | proposed_country prerequisite; proposed_administrative_unit and version from admin_units.id; code history from admin_units.code/province_code after authority; name records from name_es/name_en; crosswalk admin_units.id -> administrative_unit | admin_units.parent_id defines parent once valid; province/territory are context/aliases unless authority promotes them | accepted address/address_record rows remain unchanged; future context integration resolves province_code/territory_id through crosswalks, not accepted identity rows | official hierarchy owner, code owner, level translation, parent-lineage authority required | administrative identity may be public-after-release only after classification/public-release authority; no citizen privacy issue | missing parent, level unsupported, province-code mismatch, duplicate semantic crosswalk, generic subject reuse | yes for administrative_unit/version/code/name/crosswalk; lacks direct admin subject FK for names unless registry_subject decision is made |
| B — all three tables own distinct administrative units | preserves every source table identity; can represent province, admin unit and territory as separate levels if institution confirms hierarchy | territories may be operational rollout areas; provinces.code generic mismatch with BN; duplicate real-world unit risk; parent hierarchy not explicit across all three tables | administrative_unit/version per provinces/admin_units/territories; crosswalk for each source id/code; name records for each; parent relationships between target units | country -> province -> admin_unit -> territory if authority approves; otherwise fails on missing/incorrect links | context fields can resolve to province/territory units but accepted rows stay unchanged; future integration needs new crosswalks | stronger official hierarchy and territory registry authority required before any implementation | publication risk higher because territory may not be official admin geography | duplicate administrative identity, wrong parent level, one source resolving to multiple targets, territory/admin-unit mismatch | partially; administrative_unit/version supports hierarchy, but territory-as-admin requires level translation and authority; operational-area alternative may be better |
| C — split administrative and operational concepts | matches WO-002 requirement to separate administrative units from operational zones; provinces/admin_units can be official geography while territories become locality/operational area/context where appropriate | accepted-context fields currently reference territories; fixture territories.admin_unit_id mismatch still needs authority; territory name/type/readiness must not be silently promoted | proposed_country prerequisite; administrative_unit/version for provinces/admin_units; proposed_locality or proposed_operational_area for territories if authority chooses; crosswalks and names to distinct subject types | country -> province -> district/municipality/local_council through admin units; territories attach as context/coverage to administrative unit or locality when approved | accepted rows remain unchanged; future integration resolves territory_id via operational/locality crosswalk and province_code via admin code history; no accepted identity mutation | territory registry owner, operational-vs-administrative classification, parent-lineage, code history and publication authority required | lowest publication risk; territories remain government-internal until official status confirmed | territory promoted as admin without authority, wrong name subject, public alias output, mismatch between territory/admin-unit and province code | yes conceptually: administrative_unit/version plus proposed_locality/proposed_operational_area exist; exact territory target requires reviewer oracle |

**Recommended model for SDA consideration:** Model C — split administrative and operational concepts.  
**Recommendation confidence:** medium; strongest alignment with WO-002 separation rule, but authority must resolve whether territories are official administrative units, localities, operational areas, or mixed by type. This is not acceptance and not implementation authorization.

## 5. Candidate target row families
Administrative identities must not be represented as address `proposed_location_record` identities unless a later reviewer decision establishes that model. No target row may have two owners.

| target family | owner source table/field | deterministic ID rule | classification | source-record lineage | required authority | consumers | shared | other callable may update | expected absence rules |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| proposed_administrative_unit | admin_units.id for Model A; provinces.code/admin_units.id for Model C province/admin-unit units after authority | admin-unit:{source_table}:{stable source key}; do not use address location_record IDs | identity shell, government-internal until release decision | source_record_id for owning source row plus evidence_object prerequisite | official administrative hierarchy owner | administrative_unit_version, code_history, accepted-context future lookups | yes, one unit may be referenced by multiple context tables | no owner changes; later version/code/name callables may add child facts only | no location_record identity; no public_code_alias; no duplicate unit for same semantic authority identity |
| proposed_administrative_unit_version | admin_units.level,parent_id,status,created_at,updated_at; provinces/territory if selected model authorizes | admin-unit-version:{administrative_unit_id}:{effective_from}:{source_record_id} | effective-dated state/version, not identity | owning source record and source_authority_id required | level translation, parent-lineage, lifecycle/effective-date authority | hierarchy traversal; address/address_record context integration | no; versions are owned by unit/version callable | no mutation; supersession via new version only | reject unsupported level, missing parent without root rule, self/cycle/duplicate current child |
| proposed_administrative_code_history | admin_units.code, admin_units.province_code, provinces.code, territories.province_code if authorized | admin-code:{code_scheme}:{administrative_unit_id}:{normalized_code}:{effective_from} | code history; administrative code not NLI public address code | source_record_id and/or source_id in schema; authority evidence required | province-code owner, admin-unit code owner, code-history authority | future lookup from addresses.province_code/address_records.province_code and source crosswalks | yes as lookup, no as owner | only a future code-history callable may add/supersede codes | no proposed_public_code_alias; reject same code resolving to multiple units unless scope/scheme distinguishes |
| proposed_name_record | admin_units.name_es/name_en; provinces.name; territories.name depending model | name:{subject_id}:{language}:{name_kind}:{normalized_text}:{source_record_id} | name fact; official/provisional status depends on authority | source_record_id required; no unrelated generic subject | bilingual naming authority and classification authority | operator display, future public presentation after release authority | subject may have multiple names, each row has one source owner | no mutation; add/supersede effective-dated name rows | no name row targeting phase-a-subject-phase-a-location-geotag or accepted address subjects |
| proposed_legacy_crosswalk | source stable key: admin_units.id, provinces.code, territories.id/admin_unit_id as context only | crosswalk:{source_table}:{source_field}:{legacy_id}:to:{target_entity}:{target_id} | source identity/linkage; not official semantic proof by itself | source_record_id and exact source_field/source_key required | source-system relationship and target owner decision | future accepted-context dependency integration | lookup shared, row owner unique | no duplicate semantic crosswalk; future callables may read only | reject one source identity resolving to multiple targets and duplicate target semantic crosswalks |
| proposed_registry_subject | derived from approved administrative_unit_id or locality/operational_area id; not directly from address location rows | subject:{subject_entity}:{native_id} | subject anchor for names/future geometry if used | created with identity row lineage; name/geometry rows reference it | registry-subject usage decision for administrative units | proposed_name_record; future geometry_observation/geometry_version for boundaries | yes as subject anchor; one per native entity | no; consumers reference only | do not reuse accepted address/geotag subjects; no one generic subject for multiple admin records |
| proposed_country as prerequisite only | static GQ prerequisite from accepted source authority, not a transform output from admin tables | country:GQ / phase-a-country-gq | legitimate prerequisite | source_authority_id required; no admin source row owns it | country baseline authority already prerequisite; not expanded here | administrative_unit.country_id | yes | no in this checkpoint | do not create extra country rows or mutate accepted prerequisite |

## 6. Registry-subject usage decision

Yes, recommended for SDA consideration: administrative units need proposed_registry_subject rows if proposed_name_record and future geometry observations/versions are to resolve a stable administrative subject. subject_entity should be administrative_unit; native_id should equal proposed_administrative_unit.administrative_unit_id; lifecycle follows the administrative unit lifecycle with retire-only delete policy; administrative_unit_version rows define effective state while names point to the registry subject. If SDA rejects registry_subject for admin units, a different name-subject FK or target vocabulary would be needed; the current physical schema supports name_record.subject_id -> registry_subject, so no-subject mode is not cleanly supported for names/geometry.

## 7. Hierarchy semantics

| rule | definition |
| --- | --- |
| allowed levels | target vocabulary only: country, province, district, municipality, local_council |
| country to province | province versions may have parent_administrative_unit_id null only if country relationship is represented by proposed_administrative_unit.country_id; otherwise parent must be country-level unit if model adds one |
| province to subordinate administrative unit | province may parent district, municipality, or local_council only after level authority; district may parent municipality/local_council; municipality may parent local_council |
| administrative unit to territory | only if territory is authorized as administrative level; otherwise territory maps to locality/operational area coverage referencing administrative_unit_id |
| root behavior | country is root prerequisite; province is first-level root within country unless explicit country-level admin unit model is approved |
| missing parent | fail unless source row is approved root level; missing parent_id in non-root is unresolved authority error |
| parent-cycle prohibition | reject any cycle in parent_administrative_unit_id chain |
| self-parent prohibition | reject parent id equal to child administrative_unit_id |
| duplicate child prohibition | same semantic child cannot have two active parents for overlapping effective interval |
| effective-date behavior | effective_from required; effective_to null means current; overlaps for same unit/version role rejected |
| retirement/supersession | retire with effective_to/recorded_to or new version; never hard-delete referenced units |
| orphan handling | quarantine as authority RFI/migration exception design; do not infer parent from code prefix |

Any source `admin_units.level` value outside `country`, `province`, `district`, `municipality`, `local_council` cannot be translated without authority. The complete fixture value `phase-a admin_units level` is therefore unresolved authority input.

## 8. Code ownership and collision rules

| case | rule |
| --- | --- |
| internal deterministic primary keys | generated target IDs; not public; never exposed as NLI address code |
| source legacy IDs | store in proposed_legacy_crosswalk with source_table/source_field/legacy_id; do not treat as official code |
| province codes | candidate for proposed_administrative_code_history after province-code owner decision; may also be crosswalk source key when code is source PK |
| admin-unit codes | candidate administrative code history after code-history authority; crosswalk if used to resolve legacy record |
| territory IDs | crosswalk source identity for territory/locality/operational-area target; not administrative code unless territory authority says so |
| public codes | not authorized; proposed_public_code_alias must remain absent for this checkpoint |
| same code different tables | collision unless code_scheme/source_table/level scope separates them; require negative test |
| code reused across levels | reject without scoped code_scheme and authority proof |
| code changes over time | new code_history row with effective interval; old row effective_to; no mutation in place |
| case/format differences | normalize for comparison but preserve source value; collision check uses normalized form |
| one code to multiple targets | fail unless authority defines scoped code scheme that disambiguates |

## 9. Bilingual naming

| field | language | name kind | status | normalization | target subject | source lineage | authority status | effective dates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| admin_units.name_es | es | official/admin-name candidate | unresolved-authority/provisional | trim, collapse whitespace, casefold for duplicate check; preserve original text | administrative_unit registry subject for admin_units.id | phase-a-source-record-admin-units-001 | bilingual naming authority required | created_at as candidate effective_from only if authority approves |
| admin_units.name_en | en | official/admin-name candidate | unresolved-authority/provisional | same | administrative_unit registry subject for admin_units.id | phase-a-source-record-admin-units-001 | bilingual naming authority required | created_at candidate |
| provinces.name | undetermined/es-or-en | province name candidate | not assumed official | same; language must be decided or source metadata added | province administrative_unit subject if model includes provinces | phase-a-source-record-provinces-001 | province naming authority required | created_at candidate |
| territories.name | undetermined/es-or-en | territory/locality/operational-area name candidate | not assumed official | same | territory locality/operational_area subject unless territory authorized as admin unit | phase-a-source-record-territories-001 | territory registry/naming authority required | created_at candidate |

No province or territory fixture name is assumed official. No name record may target an unrelated generic subject.

## 10. Accepted-family administrative-context dependencies
The accepted-family convergence union must remain unchanged. Future integration requires new context/crosswalk slices rather than modifying accepted identity rows.

| source field | currently accepted context only | proposed lookup path | expected target entity | failure behavior | accepted rows remain unchanged | future integration requires |
| --- | --- | --- | --- | --- | --- | --- |
| addresses.territory_id | yes | addresses.territory_id -> territory crosswalk -> locality/operational_area or admin unit per Model C | not accepted location_record; future context relation/crosswalk | no match or ambiguous match fails future integration; accepted identity row unchanged | yes | new crosswalk/context slice, not modifying accepted address identity row |
| addresses.province_code | yes | province_code -> administrative_code_history/province crosswalk after authority | administrative_unit/code_history | BN vs phase-a-provinces-code mismatch fails until authority lookup resolves | yes | new admin code/history lookup slice |
| address_records.territory_id | yes | address_records.territory_id -> territory crosswalk -> context target | locality/operational_area or administrative_unit context | ambiguous/missing territory fails future context integration | yes | new crosswalk/context slice |
| address_records.province_code | yes | province_code -> admin code history/province unit | administrative_unit/code_history | mismatch fails without authority mapping | yes | new admin code/history slice |
| roads.territory_id | no; not accepted slice yet | roads.territory_id -> territory crosswalk | context relation for future road identity | future road slice fails if territory unresolved | yes | future roads identity/reference slice |
| buildings.territory_id | no; not accepted slice yet | buildings.territory_id -> territory crosswalk | context relation for future building identity | future building slice fails if territory unresolved | yes | future buildings identity/reference slice |
| field_assignments.territory_id | no | field assignment territory -> operational area/coverage | operational_area coverage or assignment context | field workflow slice fails; not an admin identity failure | yes | future field/operational-area slice |
| field_submissions.territory_id | no | field submission territory -> operational area/locality context | operational_area/locality context | field submission integration fails without territory resolution | yes | future field submission context slice |

## 11. Authority-decision register / RFIs
No implementation may be recommended before identity and hierarchy authority questions are resolved.

| RFI | decision required | proposed institution/role | minimum evidence | affected source fields | affected target rows | work permitted before resolution | work prohibited before resolution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| official administrative hierarchy owner | Which institution owns official country/province/district/municipality/local_council hierarchy? | Ministry/agency responsible for territorial administration and national GIS registry | gazetted hierarchy, current reference dataset, legal mandate | admin_units.level,parent_id,province_code; provinces.code/name; territories.admin_unit_id | administrative_unit/version/code/name/crosswalk | mapping and RFI drafting only | oracle/transform/implementation/publication |
| official province-code owner | Who owns province code values such as BN and their history? | territorial administration / statistics / GIS authority | official code list, effective dates, retired codes | provinces.code, admin_units.province_code, territories.province_code, addresses.province_code | administrative_code_history, legacy_crosswalk | collision analysis only | code-history implementation or public-code issuance |
| official territory registry owner | Are territories official administrative units, localities, or operational rollout areas? | NLI registry/SDA plus territorial administration | territory registry definition, purpose/type vocabulary, relationship to admin units | territories.id,name,type,readiness,admin_unit_id,province_code | administrative_unit or locality/operational_area/crosswalk | model evaluation only | promoting territories into admin units |
| bilingual naming authority | Who approves Spanish/English/undetermined names and language status? | territorial administration + language/publication authority | official bilingual gazette/list, translation policy | admin_units.name_es,name_en; provinces.name; territories.name | name_record | normalization design only | official/public name rows |
| administrative level translation | How does source level string translate to target levels? | SDA + territorial administration | controlled level map | admin_units.level, territories.type | administrative_unit_version.admin_level | unsupported-level test design | fallback mapping |
| parent-lineage authority | Which parent relationships are official and effective-dated? | territorial administration/GIS authority | parent-child hierarchy with effective intervals | admin_units.parent_id, territories.admin_unit_id, province_code fields | administrative_unit_version.parent_administrative_unit_id | cycle/missing-parent test design | parent inference from code |
| code history authority | Who decides code reuse, changes, and schemes? | national code/list owner | code scheme definition and historical list | admin_units.code, provinces.code, territory ids/province_code | administrative_code_history and crosswalks | collision rules design only | code rows or alias rows |
| effective-date authority | Which source dates become effective_from/effective_to vs recorded_at? | SDA + source data owner | temporal policy and source metadata | created_at,updated_at,status,is_archived | versions, code_history, name_record | temporal model design only | using created_at as official effective date |
| classification and public-release authority | Which admin reference facts may be public and when? | Programme Owner/SDA/publication authority | classification policy and release approval | all admin/province/territory rows and names/codes | classification fields; publication rows | classification boundary statement only | public aliases/publication output |

## 12. Future negative tests — designs only

| negative test design | setup | mutation | expected failure | implementation status |
| --- | --- | --- | --- | --- |
| unsupported administrative level | Prepare future reviewed admin mapping fixture with unsupported administrative level condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger unsupported administrative level. | Future oracle/comparator rejects unsupported administrative level; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| missing parent | Prepare future reviewed admin mapping fixture with missing parent condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger missing parent. | Future oracle/comparator rejects missing parent; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| self-parent | Prepare future reviewed admin mapping fixture with self-parent condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger self-parent. | Future oracle/comparator rejects self-parent; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| hierarchy cycle | Prepare future reviewed admin mapping fixture with hierarchy cycle condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger hierarchy cycle. | Future oracle/comparator rejects hierarchy cycle; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| wrong parent level | Prepare future reviewed admin mapping fixture with wrong parent level condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger wrong parent level. | Future oracle/comparator rejects wrong parent level; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| province-code mismatch | Prepare future reviewed admin mapping fixture with province-code mismatch condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger province-code mismatch. | Future oracle/comparator rejects province-code mismatch; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| territory/admin-unit mismatch | Prepare future reviewed admin mapping fixture with territory/admin-unit mismatch condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger territory/admin-unit mismatch. | Future oracle/comparator rejects territory/admin-unit mismatch; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| duplicate administrative identity | Prepare future reviewed admin mapping fixture with duplicate administrative identity condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger duplicate administrative identity. | Future oracle/comparator rejects duplicate administrative identity; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| duplicate semantic crosswalk | Prepare future reviewed admin mapping fixture with duplicate semantic crosswalk condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger duplicate semantic crosswalk. | Future oracle/comparator rejects duplicate semantic crosswalk; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| one source identity resolving to multiple targets | Prepare future reviewed admin mapping fixture with one source identity resolving to multiple targets condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger one source identity resolving to multiple targets. | Future oracle/comparator rejects one source identity resolving to multiple targets; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| one code resolving to multiple units | Prepare future reviewed admin mapping fixture with one code resolving to multiple units condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger one code resolving to multiple units. | Future oracle/comparator rejects one code resolving to multiple units; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| conflicting bilingual name | Prepare future reviewed admin mapping fixture with conflicting bilingual name condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger conflicting bilingual name. | Future oracle/comparator rejects conflicting bilingual name; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| wrong name subject | Prepare future reviewed admin mapping fixture with wrong name subject condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger wrong name subject. | Future oracle/comparator rejects wrong name subject; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| generic geotag-subject reuse | Prepare future reviewed admin mapping fixture with generic geotag-subject reuse condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger generic geotag-subject reuse. | Future oracle/comparator rejects generic geotag-subject reuse; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| classification drift | Prepare future reviewed admin mapping fixture with classification drift condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger classification drift. | Future oracle/comparator rejects classification drift; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| unauthorized public alias | Prepare future reviewed admin mapping fixture with unauthorized public alias condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger unauthorized public alias. | Future oracle/comparator rejects unauthorized public alias; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| unauthorized publication output | Prepare future reviewed admin mapping fixture with unauthorized publication output condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger unauthorized publication output. | Future oracle/comparator rejects unauthorized publication output; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| missing source authority | Prepare future reviewed admin mapping fixture with missing source authority condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger missing source authority. | Future oracle/comparator rejects missing source authority; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| wrong source/evidence lineage | Prepare future reviewed admin mapping fixture with wrong source/evidence lineage condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger wrong source/evidence lineage. | Future oracle/comparator rejects wrong source/evidence lineage; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| unexpected version | Prepare future reviewed admin mapping fixture with unexpected version condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger unexpected version. | Future oracle/comparator rejects unexpected version; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| unexpected decision event | Prepare future reviewed admin mapping fixture with unexpected decision event condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger unexpected decision event. | Future oracle/comparator rejects unexpected decision event; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| second-run idempotency | Prepare future reviewed admin mapping fixture with second-run idempotency condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger second-run idempotency. | Future oracle/comparator rejects second-run idempotency; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| read-only complete comparison | Prepare future reviewed admin mapping fixture with read-only complete comparison condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger read-only complete comparison. | Future oracle/comparator rejects read-only complete comparison; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |
| same-database rollback equality | Prepare future reviewed admin mapping fixture with same-database rollback equality condition; use independent expected source, not transform output. | Mutate only the relevant source/control field to trigger same-database rollback equality. | Future oracle/comparator rejects same-database rollback equality; no target rows persist; rollback/read-only evidence remains equal where applicable. | design only; not authorized |

## 13. Potential slice boundaries — not authorized

| slice | exact source table | covered fields | context fields | target rows | prerequisite slices | authority prerequisite | privacy/publication boundary | expected inserts | expected absences |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| administrative-unit identity and hierarchy | admin_units plus provinces as context if authorized | admin_units.id, level, parent_id, province_code, status, created_at, updated_at; provinces.code as context | country prerequisite, source_authority, source_record/evidence | proposed_administrative_unit, proposed_administrative_unit_version, proposed_legacy_crosswalk, optional proposed_registry_subject | country/source/evidence prerequisites | official hierarchy owner, level translation, parent-lineage authority | government-internal/public-after-release only after authority | one unit, one version, one crosswalk, optional subject for fixture row | no location_record, no public_code_alias, no publication, no decision_event unless future oracle authorizes |
| administrative code history/crosswalk | admin_units, provinces, territories | admin_units.code, admin_units.province_code, provinces.code, territories.province_code, territories.id | resolved administrative_unit_id, code scheme, effective dates | proposed_administrative_code_history, proposed_legacy_crosswalk | administrative-unit identity and hierarchy | province-code owner, code-history authority | administrative codes not NLI public address codes | code history rows only for authority-resolved codes | no proposed_public_code_alias, no duplicate code-to-target rows |
| administrative names | admin_units, provinces, territories | admin_units.name_es, admin_units.name_en, provinces.name, territories.name | registry subject, language decision, name authority, effective dates | proposed_name_record | identity/registry-subject decision | bilingual naming authority | not official/public until publication authority | one or more name rows per approved subject/language | no generic geotag subject; no accepted address subjects |
| accepted-context dependency integration | addresses, address_records, roads, buildings, field_assignments, field_submissions | territory_id, province_code, admin context references | admin/territory crosswalks, code history | future context relationship/crosswalk rows only; accepted identity rows unchanged | identity/hierarchy, code history, territory classification | territory registry owner and context lookup authority | no publication effect | context lookup/crosswalk rows if authorized | no accepted-family convergence union mutation |

**Recommended first potential slice:** administrative-unit identity and hierarchy. It has the highest dependency leverage for accepted-context resolution, but remains unauthorized until SDA approves reviewer-oracle preparation and authority questions are answered.

## 14. F02 / F14 impact and remaining gates

| item | status |
| --- | --- |
| F02 impact | positive design impact only: defines source-row, field, target-family, ownership, authority and negative-test boundaries for admin/reference data; F02 remains partially satisfied and not closed |
| F14 impact | positive design impact only: separates admin/reference authority from generic broad outputs and accepted-family convergence; F14 remains partially satisfied and not closed |
| Remaining closed gates | reviewer-oracle preparation, administrative implementation, another transform group, broad Phase A reassessment, F02/F14 closure, Review 12, Phase B, publication, deployment, merge and PR #8 remain closed |

## 15. Return summary values

| field | value |
| --- | --- |
| Source tables mapped | 3 — admin_units, provinces, territories |
| Source fields mapped | 23 |
| Fixture inconsistencies | 7 |
| Candidate models evaluated | 3 |
| Recommended model | Model C — split administrative and operational concepts |
| Recommendation confidence | medium; strongest alignment with WO-002 separation rule, but authority must resolve whether territories are official administrative units, localities, operational areas, or mixed by type |
| Unresolved authority decisions | 9 |
| Administrative-unit owners | admin_units.id preferred under Model A/C for admin_units; provinces.code may own province unit if authority accepts Model C; territories not admin owner unless authority says so |
| Version owners | administrative-unit version callable/slice owns level/parent/lifecycle/effective state |
| Code-history owners | future code-history slice only; source codes from admin_units/provinces/territories after authority |
| Name-record owners | future naming slice; admin_units/provinces/territories names by subject after authority |
| Crosswalk owners | future identity/hierarchy or code-history slices; no duplicate owners |
| Registry-subject decision | recommended yes for administrative_unit subjects; no reuse of accepted/geotag/generic subjects |
| Country prerequisite | proposed_country is prerequisite only, not admin transform output |
| Hierarchy levels | country, province, district, municipality, local_council |
| Parent rules | 12 |
| Code rules | 11 |
| Name rules | 4 |
| Classification boundary | government-internal or public-after-release only after authority; no publication now |
| Publication boundary | no proposed_public_code_alias, publication_release, release_item or public output authorized |
| Accepted-context dependencies | 8 |
| Accepted rows modified | 0 |
| Accepted convergence modified | no |
| Authority RFIs | 9 |
| Negative tests designed | 24 |
| Potential slice boundaries | 4 |
| Recommended first potential slice | administrative-unit identity and hierarchy |
| F02 impact | design impact only; partially satisfied, not closed |
| F14 impact | design impact only; partially satisfied, not closed |
| Remaining closed gates | oracle preparation, admin implementation, transform groups, broad Phase A, F02/F14 closure, Review 12, Phase B, publication, deployment, merge, PR #8 |
| Current instructed action | Administrative hierarchy and reference-identity mapping only. |
| Next instruction required from SDA | YES — before reviewer-oracle preparation, administrative implementation, another transform group, broad Phase A reassessment, F02/F14 closure, Review 12, Phase B, publication, deployment or merge. |
