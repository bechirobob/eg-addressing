# NLI-WO-002 Phase A residual-control and broad-readiness mapping pack — C32-C36 correction

**Reviewed base mapping commit:** `50837a3c8053a0a79dbf0d57321d3b49407929ef`

**Reviewer-controlled synchronization head:** `eeb6fbdbd5269c6d41e7696331c2e33f1d4f2578`

**Assessment read:** `docs/sda/reviews/NLI-WO-002-phase-a-residual-readiness-mapping-assessment.json`

**PR review read:** `4714329154` — mapping-only correction required; no transform group or broad reassessment authorized.

## 0. Closed-boundary declaration
This correction changes this mapping document only. It does **not** modify `authoritative_harness.py`, any generated report, transform specification, fixture, `api-ci.yml`, reviewer controls/oracles, accepted callables, runtime application code, executable migrations, deployment/publication code, or PR #8. It does **not** authorize reviewer-oracle preparation, another transform group, broad Phase A reassessment, F02/F14 closure, Review 12, Phase B, deployment or merge.

## 1. Pinned authorities

| authority | path | git blob | sha256 |
| --- | --- | --- | --- |
| reviewer residual assessment | docs/sda/reviews/NLI-WO-002-phase-a-residual-readiness-mapping-assessment.json | bed631ea0e6059dd8d4f3278a203fce81058e8f4 | 9d85539af98070aa1d13f8d151bdb982dd1fe37800db306d786a144e3c3fc82e |
| accepted-family convergence mapping | docs/agent/tasks/NLI-WO-002-phase-a-accepted-family-convergence-mapping.md | c984a16f352417b9fde0f8cb9e0536a5e0ab6eb1 | 382c1ccd0de2b90ecb08241d8cf3f6788ae7166ef93f9122bb6ed3b6ed3669ce |
| convergence control | docs/sda/acceptance/NLI-WO-002-phase-a-accepted-family-convergence-control.json | 3c4c59fa5eeb004cfb8ef2520241d74c130fa926 | d714b32ea170e05b5feef240d587d860ed0c712812036f384e357381a60b3b8a |
| accepted convergence report | docs/sda/data-model/phase-a-accepted-family-convergence-report.json | bc0346d30eb49f1d2956b81e6cffa5e3e9933d65 | f28cd006d27cf0d764db1863956d39dc97aa13b11df0d063d8c3b8ad2698a304 |
| frozen broad transform spec | docs/sda/data-model/fixtures/transform-specs/phase-a-broad-generic-transform-specs-frozen.json | 443de54b6bacf6a12106fdbba5dba1a07955eec4 | b601f4fe1c5676511010d10d5b9e819e83fc50a2bbedce11c324e2f4a05099cf |
| live narrow transform spec | docs/sda/data-model/fixtures/transform-specs/phase-a-transform-specs.json | 32b284917bafd5bdc5bef7804230b8eb81033697 | 5f6defcdf1a27f736ee1736a158a15ed83530daed8490af7719f6b9784454fc4 |
| broad expected-target fixture | docs/sda/data-model/fixtures/expected-target/phase-a-expected-target-records.json | 7df5326902315123ebb8bc4970899dd293f30c58 | 4b98cc1b580b2513cd0f1eee3a53af87376a1d6efa7c8792ab1211e38a22ea76 |
| current PostgreSQL catalog | docs/sda/data-model/current-pg-catalog.json | 2948290a494c125ce2254ffa8cb7861f4ea8d7cb | 0b022dd03fecb6bdec12baa159c6bb83aaa477fcc3fa35e9ab0110d14a0c52d5 |

## 2. C32 — active accepted groups versus frozen broad variants

### 2.1 Active live narrow authority records

| accepted transform group | active live narrow authority | accepted callable | accepted implementation unit | accepted oracle/correction chain | accepted target-row ownership | accepted convergence participation | residual candidate | historical-only | new implementation required |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WO002-R06-geometry-observation-address_points | active authoritative status | transform_address_points_geometry | impl_wo002_r06_geometry_observation_address_points | NLI-WO-002-phase-a-address-points-geometry-expected.json + address-points correction/final-correction oracles | owned by accepted callable in accepted-family ownership registry | yes; included in accepted-family convergence at ca39c11 | no | no | no |
| WO002-R06-geometry-observation-address_records | active authoritative status | transform_address_records_geometry | impl_wo002_r06_geometry_observation_address_records | NLI-WO-002-phase-a-address-records-geometry-expected.json + address-records correction oracle | owned by accepted callable in accepted-family ownership registry | yes; included in accepted-family convergence at ca39c11 | no | no | no |
| WO002-R06-geometry-observation-citizen_geotag_submissions | active authoritative status | transform_citizen_geotag_geometry | impl_wo002_r06_geometry_observation_citizen_geotag_submissions | NLI-WO-002-phase-a-citizen-geotag-geometry-expected.json + citizen-geotag correction oracle | owned by accepted callable in accepted-family ownership registry | yes; included in accepted-family convergence at ca39c11 | no | no | no |
| WO002-R06-identity-crosswalk-address_points | active authoritative status | transform_address_points_observation_crosswalk | impl_wo002_r06_identity_crosswalk_address_points | NLI-WO-002-phase-a-address-points-observation-crosswalk-expected.json | owned by accepted callable in accepted-family ownership registry | yes; included in accepted-family convergence at ca39c11 | no | no | no |
| WO002-R06-identity-crosswalk-address_records | active authoritative status | transform_address_records_identity_crosswalk | impl_wo002_r06_identity_crosswalk_address_records | NLI-WO-002-phase-a-address-records-identity-expected.json | owned by accepted callable in accepted-family ownership registry | yes; included in accepted-family convergence at ca39c11 | no | no | no |
| WO002-R06-identity-crosswalk-addresses | active authoritative status | transform_addresses_identity_crosswalk | impl_wo002_r06_identity_crosswalk_addresses | NLI-WO-002-phase-a-addresses-identity-expected.json | owned by accepted callable in accepted-family ownership registry | yes; included in accepted-family convergence at ca39c11 | no | no | no |
| WO002-R06-identity-crosswalk-citizen_geotag_submissions | active authoritative status | transform_citizen_geotag_identity_crosswalk | impl_wo002_r06_identity_crosswalk_citizen_geotag_submissions | NLI-WO-002-phase-a-citizen-geotag-identity-expected.json | owned by accepted callable in accepted-family ownership registry | yes; included in accepted-family convergence at ca39c11 | no | no | no |

### 2.2 Frozen broad representation records

| accepted transform group | frozen covered fields | frozen targets | frozen dispositions | exact contradiction with accepted narrow decision | historical-only status | prohibited from governing future broad acceptance | rows must be removed from future broad expected truth |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WO002-R06-geometry-observation-address_points | address_points.accuracy_meters, address_points.latitude, address_points.longitude | geometry_observation | structured-transform | frozen broad representation is superseded; not allowed to govern acceptance even where fields look similar | yes; frozen representation only | yes | yes where frozen rows pre-create/supersede accepted-owned outputs or accepted absence controls; otherwise re-author under future reviewer oracle |
| WO002-R06-geometry-observation-address_records | address_records.accuracy_meters, address_records.latitude, address_records.longitude | geometry_observation | structured-transform | frozen broad representation is superseded; not allowed to govern acceptance even where fields look similar | yes; frozen representation only | yes | yes where frozen rows pre-create/supersede accepted-owned outputs or accepted absence controls; otherwise re-author under future reviewer oracle |
| WO002-R06-geometry-observation-citizen_geotag_submissions | citizen_geotag_submissions.accuracy_meters, citizen_geotag_submissions.latitude, citizen_geotag_submissions.longitude | geometry_observation | structured-transform | frozen broad representation is superseded; not allowed to govern acceptance even where fields look similar | yes; frozen representation only | yes | yes where frozen rows pre-create/supersede accepted-owned outputs or accepted absence controls; otherwise re-author under future reviewer oracle |
| WO002-R06-identity-crosswalk-address_points | address_points.address_id, address_points.id | legacy_crosswalk | structured-transform | exact frozen/live contradiction in covered fields/targets/dispositions | yes; frozen representation only | yes | yes where frozen rows pre-create/supersede accepted-owned outputs or accepted absence controls; otherwise re-author under future reviewer oracle |
| WO002-R06-identity-crosswalk-address_records | address_records.id, address_records.source_submission_id, address_records.territory_id | legacy_crosswalk, migration_exception | formal-exception, structured-transform | exact frozen/live contradiction in covered fields/targets/dispositions | yes; frozen representation only | yes | yes where frozen rows pre-create/supersede accepted-owned outputs or accepted absence controls; otherwise re-author under future reviewer oracle |
| WO002-R06-identity-crosswalk-addresses | addresses.building_id, addresses.id, addresses.road_id, addresses.superseded_by_address_id, addresses.territory_id | legacy_crosswalk, migration_exception | formal-exception, structured-transform | exact frozen/live contradiction in covered fields/targets/dispositions | yes; frozen representation only | yes | yes where frozen rows pre-create/supersede accepted-owned outputs or accepted absence controls; otherwise re-author under future reviewer oracle |
| WO002-R06-identity-crosswalk-citizen_geotag_submissions | citizen_geotag_submissions.field_submission_id, citizen_geotag_submissions.id, citizen_geotag_submissions.territory_id | legacy_crosswalk, migration_exception | formal-exception, structured-transform | exact frozen/live contradiction in covered fields/targets/dispositions | yes; frozen representation only | yes | yes where frozen rows pre-create/supersede accepted-owned outputs or accepted absence controls; otherwise re-author under future reviewer oracle |

**Correction:** active accepted groups are not residual candidates and are not assigned “retain as frozen historical baseline only.” Only their superseded frozen broad representations are historical-only.

## 3. C34 — mutually exclusive transform-group Phase A scope dispositions

| transform_group_id | source_table | implementation_unit | covered_fields | target_entities | phase_a_scope_disposition |
| --- | --- | --- | --- | --- | --- |
| WO002-R06-correction-case-address_corrections | address_corrections | impl_wo002_r06_correction_case_address_corrections | address_corrections.correction_type, address_corrections.public_code, address_corrections.status | correction_case | field/correction workflow candidate |
| WO002-R06-correction-case-archive-address_corrections | address_corrections | impl_wo002_r06_correction_case_archive_address_corrections | address_corrections.note, address_corrections.query, address_corrections.reason, address_corrections.reporter_name, address_corrections.reviewer_note | source_payload_archive | field/correction workflow candidate |
| WO002-R06-identity-crosswalk-address_corrections | address_corrections | impl_wo002_r06_identity_crosswalk_address_corrections | address_corrections.address_id, address_corrections.id | legacy_crosswalk | field/correction workflow candidate |
| WO002-R06-identity-crosswalk-address_record_events | address_record_events | impl_wo002_r06_identity_crosswalk_address_record_events | address_record_events.actor_id, address_record_events.address_record_id, address_record_events.id | legacy_crosswalk, migration_exception | field/correction workflow candidate |
| WO002-R06-identity-crosswalk-admin_units | admin_units | impl_wo002_r06_identity_crosswalk_admin_units | admin_units.id, admin_units.parent_id | legacy_crosswalk, migration_exception | administrative/reference-domain candidate |
| WO002-R06-identity-crosswalk-audit_logs | audit_logs | impl_wo002_r06_identity_crosswalk_audit_logs | audit_logs.actor_user_id, audit_logs.entity_id, audit_logs.id | legacy_crosswalk, migration_exception | audit/assurance domain — outside location semantics |
| WO002-R06-identity-crosswalk-auth_tokens | auth_tokens | impl_wo002_r06_identity_crosswalk_auth_tokens | auth_tokens.user_id | legacy_crosswalk | security/credential domain — outside location-model scope |
| WO002-R06-identity-crosswalk-buildings | buildings | impl_wo002_r06_identity_crosswalk_buildings | buildings.id, buildings.road_id, buildings.territory_id | legacy_crosswalk | core-location-domain candidate |
| WO002-R06-identity-crosswalk-development_fixture_batches | development_fixture_batches | impl_wo002_r06_identity_crosswalk_development_fixture_batches | development_fixture_batches.batch_id | migration_exception | development/test infrastructure — outside production Phase A |
| WO002-R06-identity-crosswalk-development_fixture_records | development_fixture_records | impl_wo002_r06_identity_crosswalk_development_fixture_records | development_fixture_records.batch_id, development_fixture_records.record_id | migration_exception | development/test infrastructure — outside production Phase A |
| WO002-R06-identity-crosswalk-field_assignments | field_assignments | impl_wo002_r06_identity_crosswalk_field_assignments | field_assignments.assignment_id, field_assignments.territory_id | legacy_crosswalk, migration_exception | field/correction workflow candidate |
| WO002-R06-identity-crosswalk-field_submissions | field_submissions | impl_wo002_r06_identity_crosswalk_field_submissions | field_submissions.assignment_id, field_submissions.id, field_submissions.registry_entity_id, field_submissions.territory_id | legacy_crosswalk, migration_exception | field/correction workflow candidate |
| WO002-R06-identity-crosswalk-import_jobs | import_jobs | impl_wo002_r06_identity_crosswalk_import_jobs | import_jobs.id | legacy_crosswalk | provenance/control prerequisite |
| WO002-R06-identity-crosswalk-import_rows | import_rows | impl_wo002_r06_identity_crosswalk_import_rows | import_rows.committed_submission_id, import_rows.job_id, import_rows.territory_id | legacy_crosswalk, migration_exception | provenance/control prerequisite |
| WO002-R06-identity-crosswalk-publication_pack_addresses | publication_pack_addresses | impl_wo002_r06_identity_crosswalk_publication_pack_addresses | publication_pack_addresses.address_id, publication_pack_addresses.publication_pack_id | legacy_crosswalk, migration_exception | publication/release domain |
| WO002-R06-identity-crosswalk-publication_packs | publication_packs | impl_wo002_r06_identity_crosswalk_publication_packs | publication_packs.id | legacy_crosswalk | publication/release domain |
| WO002-R06-identity-crosswalk-reference_data_load_history | reference_data_load_history | impl_wo002_r06_identity_crosswalk_reference_data_load_history | reference_data_load_history.id, reference_data_load_history.package_id | legacy_crosswalk, migration_exception | provenance/control prerequisite |
| WO002-R06-identity-crosswalk-reference_data_loads | reference_data_loads | impl_wo002_r06_identity_crosswalk_reference_data_loads | reference_data_loads.package_id | migration_exception | provenance/control prerequisite |
| WO002-R06-identity-crosswalk-roads | roads | impl_wo002_r06_identity_crosswalk_roads | roads.id, roads.territory_id | legacy_crosswalk | core-location-domain candidate |
| WO002-R06-identity-crosswalk-territories | territories | impl_wo002_r06_identity_crosswalk_territories | territories.admin_unit_id, territories.id | legacy_crosswalk | administrative/reference-domain candidate |
| WO002-R06-identity-crosswalk-users | users | impl_wo002_r06_identity_crosswalk_users | users.id | legacy_crosswalk | security/credential domain — outside location-model scope |
| WO002-R06-name-record-address_record_events | address_record_events | impl_wo002_r06_name_record_address_record_events | address_record_events.actor_username | name_record | field/correction workflow candidate |
| WO002-R06-name-record-address_records | address_records | impl_wo002_r06_name_record_address_records | address_records.address_label | name_record | core-location-domain candidate |
| WO002-R06-name-record-admin_units | admin_units | impl_wo002_r06_name_record_admin_units | admin_units.name_en, admin_units.name_es | name_record | administrative/reference-domain candidate |
| WO002-R06-name-record-audit_logs | audit_logs | impl_wo002_r06_name_record_audit_logs | audit_logs.actor_username | name_record | audit/assurance domain — outside location semantics |
| WO002-R06-name-record-buildings | buildings | impl_wo002_r06_name_record_buildings | buildings.label | name_record | core-location-domain candidate |
| WO002-R06-name-record-citizen_geotag_submissions | citizen_geotag_submissions | impl_wo002_r06_name_record_citizen_geotag_submissions | citizen_geotag_submissions.address_label, citizen_geotag_submissions.citizen_name, citizen_geotag_submissions.map_display_name, citizen_geotag_submissions.reviewed_road_name, citizen_geotag_submissions.suggested_place_name, citizen_geotag_submissions.suggested_road_name | name_record | privacy review required |
| WO002-R06-name-record-development_fixture_records | development_fixture_records | impl_wo002_r06_name_record_development_fixture_records | development_fixture_records.table_name | name_record | development/test infrastructure — outside production Phase A |
| WO002-R06-name-record-field_submissions | field_submissions | impl_wo002_r06_name_record_field_submissions | field_submissions.candidate_name | name_record | field/correction workflow candidate |
| WO002-R06-name-record-import_jobs | import_jobs | impl_wo002_r06_name_record_import_jobs | import_jobs.name, import_jobs.source_name | name_record | provenance/control prerequisite |
| WO002-R06-name-record-import_rows | import_rows | impl_wo002_r06_name_record_import_rows | import_rows.candidate_name | name_record | provenance/control prerequisite |
| WO002-R06-name-record-provinces | provinces | impl_wo002_r06_name_record_provinces | provinces.name | name_record | administrative/reference-domain candidate |
| WO002-R06-name-record-publication_packs | publication_packs | impl_wo002_r06_name_record_publication_packs | publication_packs.name | name_record | publication/release domain |
| WO002-R06-name-record-roads | roads | impl_wo002_r06_name_record_roads | roads.name | name_record | core-location-domain candidate |
| WO002-R06-name-record-territories | territories | impl_wo002_r06_name_record_territories | territories.name | name_record | administrative/reference-domain candidate |
| WO002-R06-name-record-users | users | impl_wo002_r06_name_record_users | users.full_name, users.username | name_record | security/credential domain — outside location-model scope |
| WO002-R06-public-code-alias-addresses | addresses | impl_wo002_r06_public_code_alias_addresses | addresses.public_code | public_code_alias | publication/release domain |
| WO002-R06-public-code-alias-admin_units | admin_units | impl_wo002_r06_public_code_alias_admin_units | admin_units.code | public_code_alias | publication/release domain |
| WO002-R06-public-code-alias-provinces | provinces | impl_wo002_r06_public_code_alias_provinces | provinces.code | public_code_alias | publication/release domain |
| WO002-R06-recorded-time-address_corrections | address_corrections | impl_wo002_r06_recorded_time_address_corrections | address_corrections.created_at, address_corrections.updated_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-address_points | address_points | impl_wo002_r06_recorded_time_address_points | address_points.created_at, address_points.updated_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-address_record_events | address_record_events | impl_wo002_r06_recorded_time_address_record_events | address_record_events.created_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-address_records | address_records | impl_wo002_r06_recorded_time_address_records | address_records.created_at, address_records.updated_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-addresses | addresses | impl_wo002_r06_recorded_time_addresses | addresses.created_at, addresses.updated_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-admin_units | admin_units | impl_wo002_r06_recorded_time_admin_units | admin_units.created_at, admin_units.updated_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-audit_logs | audit_logs | impl_wo002_r06_recorded_time_audit_logs | audit_logs.created_at | decision_event | audit/assurance domain — outside location semantics |
| WO002-R06-recorded-time-auth_tokens | auth_tokens | impl_wo002_r06_recorded_time_auth_tokens | auth_tokens.created_at, auth_tokens.expires_at, auth_tokens.last_seen_at, auth_tokens.revoked_at | decision_event | security/credential domain — outside location-model scope |
| WO002-R06-recorded-time-buildings | buildings | impl_wo002_r06_recorded_time_buildings | buildings.created_at, buildings.updated_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-citizen_geotag_submissions | citizen_geotag_submissions | impl_wo002_r06_recorded_time_citizen_geotag_submissions | citizen_geotag_submissions.created_at, citizen_geotag_submissions.field_verified_at, citizen_geotag_submissions.identity_verified_at, citizen_geotag_submissions.updated_at | decision_event | privacy review required |
| WO002-R06-recorded-time-development_fixture_batches | development_fixture_batches | impl_wo002_r06_recorded_time_development_fixture_batches | development_fixture_batches.cleaned_at, development_fixture_batches.loaded_at | decision_event | development/test infrastructure — outside production Phase A |
| WO002-R06-recorded-time-development_fixture_records | development_fixture_records | impl_wo002_r06_recorded_time_development_fixture_records | development_fixture_records.created_by_batch, development_fixture_records.recorded_at | decision_event | development/test infrastructure — outside production Phase A |
| WO002-R06-recorded-time-field_assignments | field_assignments | impl_wo002_r06_recorded_time_field_assignments | field_assignments.created_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-field_submissions | field_submissions | impl_wo002_r06_recorded_time_field_submissions | field_submissions.created_at, field_submissions.submitted_by, field_submissions.updated_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-import_jobs | import_jobs | impl_wo002_r06_recorded_time_import_jobs | import_jobs.created_at, import_jobs.updated_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-provinces | provinces | impl_wo002_r06_recorded_time_provinces | provinces.created_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-publication_packs | publication_packs | impl_wo002_r06_recorded_time_publication_packs | publication_packs.created_at, publication_packs.updated_at | decision_event | publication/release domain |
| WO002-R06-recorded-time-reference_data_load_history | reference_data_load_history | impl_wo002_r06_recorded_time_reference_data_load_history | reference_data_load_history.loaded_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-reference_data_loads | reference_data_loads | impl_wo002_r06_recorded_time_reference_data_loads | reference_data_loads.loaded_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-roads | roads | impl_wo002_r06_recorded_time_roads | roads.created_at, roads.updated_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-territories | territories | impl_wo002_r06_recorded_time_territories | territories.created_at, territories.updated_at | decision_event | provenance/control prerequisite |
| WO002-R06-recorded-time-users | users | impl_wo002_r06_recorded_time_users | users.created_at | decision_event | security/credential domain — outside location-model scope |
| WO002-R06-source-archive-address_corrections | address_corrections | impl_wo002_r06_source_archive_address_corrections | address_corrections.reporter_contact | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-address_points | address_points | impl_wo002_r06_source_archive_address_points | address_points.is_active, address_points.source_method | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-address_record_events | address_record_events | impl_wo002_r06_source_archive_address_record_events | address_record_events.actor_role, address_record_events.details, address_record_events.event_type | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-address_records | address_records | impl_wo002_r06_source_archive_address_records | address_records.address_code, address_records.geom, address_records.is_archived, address_records.province_code, address_records.publication_state, address_records.record_bundle, address_records.search_text, address_records.status | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-addresses | addresses | impl_wo002_r06_source_archive_addresses | addresses.formatted, addresses.is_archived, addresses.issuance_method, addresses.province_code, addresses.publication_state, addresses.source, addresses.status, addresses.verification_status | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-admin_units | admin_units | impl_wo002_r06_source_archive_admin_units | admin_units.level, admin_units.province_code, admin_units.sort_order, admin_units.status | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-audit_logs | audit_logs | impl_wo002_r06_source_archive_audit_logs | audit_logs.action, audit_logs.actor_role, audit_logs.details, audit_logs.entity_type | source_payload_archive | audit/assurance domain — outside location semantics |
| WO002-R06-source-archive-auth_tokens | auth_tokens | impl_wo002_r06_source_archive_auth_tokens | auth_tokens.token | source_payload_archive | security/credential domain — outside location-model scope |
| WO002-R06-source-archive-buildings | buildings | impl_wo002_r06_source_archive_buildings | buildings.is_archived, buildings.spatial_evidence, buildings.status, buildings.usage | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-citizen_geotag_submissions | citizen_geotag_submissions | impl_wo002_r06_source_archive_citizen_geotag_submissions | citizen_geotag_submissions.capture_method, citizen_geotag_submissions.citizen_contact, citizen_geotag_submissions.dip_last4, citizen_geotag_submissions.duplicate_hint, citizen_geotag_submissions.field_note, citizen_geotag_submissions.field_status, citizen_geotag_submissions.grid_code, citizen_geotag_submissions.identity_document_verified, citizen_geotag_submissions.identity_verification_status, citizen_geotag_submissions.landmark, citizen_geotag_submissions.reviewer_note, citizen_geotag_submissions.road_suggestion_attribution, citizen_geotag_submissions.road_suggestion_source, citizen_geotag_submissions.road_suggestion_status, citizen_geotag_submissions.signage_batch, citizen_geotag_submissions.status, citizen_geotag_submissions.suggested_local_area | source_payload_archive | privacy review required |
| WO002-R06-source-archive-development_fixture_batches | development_fixture_batches | impl_wo002_r06_source_archive_development_fixture_batches | development_fixture_batches.environment, development_fixture_batches.execution_context, development_fixture_batches.fixture_version | source_payload_archive | development/test infrastructure — outside production Phase A |
| WO002-R06-source-archive-field_assignments | field_assignments | impl_wo002_r06_source_archive_field_assignments | field_assignments.priority, field_assignments.task, field_assignments.team, field_assignments.territory | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-field_submissions | field_submissions | impl_wo002_r06_source_archive_field_submissions | field_submissions.candidate_status, field_submissions.notes, field_submissions.review_status, field_submissions.reviewer_note, field_submissions.spatial_evidence, field_submissions.submission_type | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-import_jobs | import_jobs | impl_wo002_r06_source_archive_import_jobs | import_jobs.imported_count, import_jobs.status | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-import_rows | import_rows | impl_wo002_r06_source_archive_import_rows | import_rows.candidate_status, import_rows.notes, import_rows.row_number, import_rows.submission_type, import_rows.validation_message, import_rows.validation_status | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-publication_packs | publication_packs | impl_wo002_r06_source_archive_publication_packs | publication_packs.audience, publication_packs.status | source_payload_archive | publication/release domain |
| WO002-R06-source-archive-reference_data_load_history | reference_data_load_history | impl_wo002_r06_source_archive_reference_data_load_history | reference_data_load_history.authority_status, reference_data_load_history.execution_context, reference_data_load_history.package_checksum, reference_data_load_history.package_version, reference_data_load_history.source | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-reference_data_loads | reference_data_loads | impl_wo002_r06_source_archive_reference_data_loads | reference_data_loads.authority_status, reference_data_loads.execution_context, reference_data_loads.package_checksum, reference_data_loads.package_version, reference_data_loads.source | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-roads | roads | impl_wo002_r06_source_archive_roads | roads.is_archived, roads.length_km, roads.spatial_evidence, roads.status | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-schema_migrations | schema_migrations | impl_wo002_r06_source_archive_schema_migrations | schema_migrations.applied_at, schema_migrations.checksum, schema_migrations.execution_context, schema_migrations.filename, schema_migrations.version | source_payload_archive | migration-governance domain — outside location semantics |
| WO002-R06-source-archive-territories | territories | impl_wo002_r06_source_archive_territories | territories.is_archived, territories.province_code, territories.readiness, territories.type | source_payload_archive | provenance/control prerequisite |
| WO002-R06-source-archive-users | users | impl_wo002_r06_source_archive_users | users.is_active, users.password_hash, users.role | source_payload_archive | security/credential domain — outside location-model scope |

### 3.1 Transform-group disposition counts

| disposition | count |
| --- | --- |
| administrative/reference-domain candidate | 5 |
| audit/assurance domain — outside location semantics | 4 |
| core-location-domain candidate | 5 |
| development/test infrastructure — outside production Phase A | 6 |
| field/correction workflow candidate | 8 |
| migration-governance domain — outside location semantics | 1 |
| privacy review required | 3 |
| provenance/control prerequisite | 36 |
| publication/release domain | 8 |
| security/credential domain — outside location-model scope | 7 |

### 3.2 Replacement queues

| queue | count | members |
| --- | --- | --- |
| narrow reviewer-oracle candidates | 18 | WO002-R06-correction-case-address_corrections, WO002-R06-correction-case-archive-address_corrections, WO002-R06-identity-crosswalk-address_corrections, WO002-R06-identity-crosswalk-address_record_events, WO002-R06-identity-crosswalk-admin_units, WO002-R06-identity-crosswalk-buildings, WO002-R06-identity-crosswalk-field_assignments, WO002-R06-identity-crosswalk-field_submissions, WO002-R06-identity-crosswalk-roads, WO002-R06-identity-crosswalk-territories, WO002-R06-name-record-address_record_events, WO002-R06-name-record-address_records, WO002-R06-name-record-admin_units, WO002-R06-name-record-buildings, WO002-R06-name-record-field_submissions, WO002-R06-name-record-provinces, WO002-R06-name-record-roads, WO002-R06-name-record-territories |
| prerequisite/control-review candidates | 36 | WO002-R06-identity-crosswalk-import_jobs, WO002-R06-identity-crosswalk-import_rows, WO002-R06-identity-crosswalk-reference_data_load_history, WO002-R06-identity-crosswalk-reference_data_loads, WO002-R06-name-record-import_jobs, WO002-R06-name-record-import_rows, WO002-R06-recorded-time-address_corrections, WO002-R06-recorded-time-address_points, WO002-R06-recorded-time-address_record_events, WO002-R06-recorded-time-address_records, WO002-R06-recorded-time-addresses, WO002-R06-recorded-time-admin_units, WO002-R06-recorded-time-buildings, WO002-R06-recorded-time-field_assignments, WO002-R06-recorded-time-field_submissions, WO002-R06-recorded-time-import_jobs, WO002-R06-recorded-time-provinces, WO002-R06-recorded-time-reference_data_load_history, WO002-R06-recorded-time-reference_data_loads, WO002-R06-recorded-time-roads, WO002-R06-recorded-time-territories, WO002-R06-source-archive-address_corrections, WO002-R06-source-archive-address_points, WO002-R06-source-archive-address_record_events, WO002-R06-source-archive-address_records, WO002-R06-source-archive-addresses, WO002-R06-source-archive-admin_units, WO002-R06-source-archive-buildings, WO002-R06-source-archive-field_assignments, WO002-R06-source-archive-field_submissions, WO002-R06-source-archive-import_jobs, WO002-R06-source-archive-import_rows, WO002-R06-source-archive-reference_data_load_history, WO002-R06-source-archive-reference_data_loads, WO002-R06-source-archive-roads, WO002-R06-source-archive-territories |
| authority-decision queue | 66 | WO002-R06-correction-case-address_corrections, WO002-R06-correction-case-archive-address_corrections, WO002-R06-identity-crosswalk-address_corrections, WO002-R06-identity-crosswalk-address_record_events, WO002-R06-identity-crosswalk-admin_units, WO002-R06-identity-crosswalk-audit_logs, WO002-R06-identity-crosswalk-buildings, WO002-R06-identity-crosswalk-field_submissions, WO002-R06-identity-crosswalk-import_jobs, WO002-R06-identity-crosswalk-import_rows, WO002-R06-identity-crosswalk-publication_pack_addresses, WO002-R06-identity-crosswalk-publication_packs, WO002-R06-identity-crosswalk-reference_data_load_history, WO002-R06-identity-crosswalk-reference_data_loads, WO002-R06-identity-crosswalk-roads, WO002-R06-identity-crosswalk-territories, WO002-R06-name-record-address_record_events, WO002-R06-name-record-address_records, WO002-R06-name-record-admin_units, WO002-R06-name-record-audit_logs, WO002-R06-name-record-buildings, WO002-R06-name-record-citizen_geotag_submissions, WO002-R06-name-record-field_submissions, WO002-R06-name-record-import_jobs, WO002-R06-name-record-import_rows, WO002-R06-name-record-provinces, WO002-R06-name-record-publication_packs, WO002-R06-name-record-roads, WO002-R06-name-record-territories, WO002-R06-public-code-alias-addresses, WO002-R06-public-code-alias-admin_units, WO002-R06-public-code-alias-provinces, WO002-R06-recorded-time-address_corrections, WO002-R06-recorded-time-address_points, WO002-R06-recorded-time-address_record_events, WO002-R06-recorded-time-address_records, WO002-R06-recorded-time-addresses, WO002-R06-recorded-time-admin_units, WO002-R06-recorded-time-audit_logs, WO002-R06-recorded-time-buildings, WO002-R06-recorded-time-citizen_geotag_submissions, WO002-R06-recorded-time-field_submissions, WO002-R06-recorded-time-import_jobs, WO002-R06-recorded-time-provinces, WO002-R06-recorded-time-publication_packs, WO002-R06-recorded-time-reference_data_load_history, WO002-R06-recorded-time-reference_data_loads, WO002-R06-recorded-time-roads, WO002-R06-recorded-time-territories, WO002-R06-source-archive-address_corrections, WO002-R06-source-archive-address_points, WO002-R06-source-archive-address_record_events, WO002-R06-source-archive-address_records, WO002-R06-source-archive-addresses, WO002-R06-source-archive-admin_units, WO002-R06-source-archive-audit_logs, WO002-R06-source-archive-buildings, WO002-R06-source-archive-citizen_geotag_submissions, WO002-R06-source-archive-field_submissions, WO002-R06-source-archive-import_jobs, WO002-R06-source-archive-import_rows, WO002-R06-source-archive-publication_packs, WO002-R06-source-archive-reference_data_load_history, WO002-R06-source-archive-reference_data_loads, WO002-R06-source-archive-roads, WO002-R06-source-archive-territories |
| privacy-review queue | 3 | WO002-R06-name-record-citizen_geotag_submissions, WO002-R06-recorded-time-citizen_geotag_submissions, WO002-R06-source-archive-citizen_geotag_submissions |
| explicitly out-of-scope groups | 18 | WO002-R06-identity-crosswalk-audit_logs, WO002-R06-identity-crosswalk-auth_tokens, WO002-R06-identity-crosswalk-development_fixture_batches, WO002-R06-identity-crosswalk-development_fixture_records, WO002-R06-identity-crosswalk-users, WO002-R06-name-record-audit_logs, WO002-R06-name-record-development_fixture_records, WO002-R06-name-record-users, WO002-R06-recorded-time-audit_logs, WO002-R06-recorded-time-auth_tokens, WO002-R06-recorded-time-development_fixture_batches, WO002-R06-recorded-time-development_fixture_records, WO002-R06-recorded-time-users, WO002-R06-source-archive-audit_logs, WO002-R06-source-archive-auth_tokens, WO002-R06-source-archive-development_fixture_batches, WO002-R06-source-archive-schema_migrations, WO002-R06-source-archive-users |
| deferred groups | 0 |  |
| historical-only groups | 0 | active groups excluded; see frozen-variant inventory, count scope is variants not groups |

## 4. C33 — authority-decision register and recalculated authority inventories

| category | group or row | exact blocked decision | proposed decision owner | evidence required | affects F02 | affects F14 | work can proceed before decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| administrative hierarchy authority | WO002-R06-identity-crosswalk-admin_units | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | WO002-R06-identity-crosswalk-territories | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | WO002-R06-name-record-admin_units | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | WO002-R06-name-record-provinces | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | WO002-R06-name-record-territories | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | WO002-R06-public-code-alias-admin_units | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | WO002-R06-public-code-alias-provinces | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | WO002-R06-recorded-time-admin_units | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | WO002-R06-recorded-time-provinces | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | WO002-R06-recorded-time-territories | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | WO002-R06-source-archive-admin_units | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | WO002-R06-source-archive-territories | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-identity-crosswalk-buildings | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-identity-crosswalk-roads | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-name-record-address_records | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-name-record-buildings | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-name-record-roads | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-public-code-alias-addresses | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-recorded-time-address_records | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-recorded-time-addresses | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-recorded-time-buildings | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-recorded-time-roads | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-source-archive-address_records | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-source-archive-addresses | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-source-archive-buildings | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | WO002-R06-source-archive-roads | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| geometry-promotion authority | WO002-R06-name-record-address_records | which typed authority can promote observed coordinates/evidence into geometry versions/quality decisions | SDA + geometry/trust authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| geometry-promotion authority | WO002-R06-name-record-citizen_geotag_submissions | which typed authority can promote observed coordinates/evidence into geometry versions/quality decisions | SDA + geometry/trust authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| geometry-promotion authority | WO002-R06-recorded-time-address_points | which typed authority can promote observed coordinates/evidence into geometry versions/quality decisions | SDA + geometry/trust authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| geometry-promotion authority | WO002-R06-recorded-time-address_records | which typed authority can promote observed coordinates/evidence into geometry versions/quality decisions | SDA + geometry/trust authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| geometry-promotion authority | WO002-R06-recorded-time-citizen_geotag_submissions | which typed authority can promote observed coordinates/evidence into geometry versions/quality decisions | SDA + geometry/trust authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| geometry-promotion authority | WO002-R06-source-archive-address_points | which typed authority can promote observed coordinates/evidence into geometry versions/quality decisions | SDA + geometry/trust authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| geometry-promotion authority | WO002-R06-source-archive-address_records | which typed authority can promote observed coordinates/evidence into geometry versions/quality decisions | SDA + geometry/trust authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| geometry-promotion authority | WO002-R06-source-archive-citizen_geotag_submissions | which typed authority can promote observed coordinates/evidence into geometry versions/quality decisions | SDA + geometry/trust authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| public-code issuance authority | WO002-R06-correction-case-address_corrections | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-correction-case-archive-address_corrections | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-identity-crosswalk-address_corrections | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-identity-crosswalk-admin_units | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-name-record-admin_units | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-name-record-provinces | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-public-code-alias-addresses | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-public-code-alias-admin_units | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-public-code-alias-provinces | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-recorded-time-address_corrections | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-recorded-time-addresses | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-recorded-time-admin_units | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-recorded-time-provinces | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-source-archive-address_corrections | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-source-archive-addresses | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| public-code issuance authority | WO002-R06-source-archive-admin_units | whether public codes/aliases can be issued, retained, retired or exposed in Phase A | SDA + publication/public-code authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-identity-crosswalk-publication_pack_addresses | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-identity-crosswalk-publication_packs | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-name-record-address_records | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-name-record-citizen_geotag_submissions | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-name-record-publication_packs | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-public-code-alias-addresses | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-recorded-time-address_records | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-recorded-time-addresses | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-recorded-time-citizen_geotag_submissions | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-recorded-time-publication_packs | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-source-archive-address_records | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-source-archive-addresses | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-source-archive-citizen_geotag_submissions | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| publication/release authority | WO002-R06-source-archive-publication_packs | whether publication packs/release rows are in scope before public release authorization | SDA + publication governance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| citizen evidence and identity authority | WO002-R06-identity-crosswalk-field_submissions | how citizen name/contact/DIP/identity evidence may be retained, redacted or transformed | SDA + identity/privacy authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| citizen evidence and identity authority | WO002-R06-name-record-citizen_geotag_submissions | how citizen name/contact/DIP/identity evidence may be retained, redacted or transformed | SDA + identity/privacy authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| citizen evidence and identity authority | WO002-R06-name-record-field_submissions | how citizen name/contact/DIP/identity evidence may be retained, redacted or transformed | SDA + identity/privacy authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| citizen evidence and identity authority | WO002-R06-recorded-time-citizen_geotag_submissions | how citizen name/contact/DIP/identity evidence may be retained, redacted or transformed | SDA + identity/privacy authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| citizen evidence and identity authority | WO002-R06-recorded-time-field_submissions | how citizen name/contact/DIP/identity evidence may be retained, redacted or transformed | SDA + identity/privacy authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| citizen evidence and identity authority | WO002-R06-source-archive-citizen_geotag_submissions | how citizen name/contact/DIP/identity evidence may be retained, redacted or transformed | SDA + identity/privacy authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| citizen evidence and identity authority | WO002-R06-source-archive-field_submissions | how citizen name/contact/DIP/identity evidence may be retained, redacted or transformed | SDA + identity/privacy authority owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | no |
| operational provenance authority | WO002-R06-identity-crosswalk-address_record_events | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-identity-crosswalk-audit_logs | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-identity-crosswalk-import_jobs | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-identity-crosswalk-import_rows | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-identity-crosswalk-reference_data_load_history | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-identity-crosswalk-reference_data_loads | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-name-record-address_record_events | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-name-record-audit_logs | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-name-record-import_jobs | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-name-record-import_rows | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-recorded-time-address_record_events | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-recorded-time-audit_logs | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-recorded-time-import_jobs | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-recorded-time-reference_data_load_history | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-recorded-time-reference_data_loads | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-source-archive-address_record_events | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-source-archive-audit_logs | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-source-archive-import_jobs | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-source-archive-import_rows | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-source-archive-reference_data_load_history | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| operational provenance authority | WO002-R06-source-archive-reference_data_loads | what provenance/control records are retained as operational evidence versus target-domain entities | SDA + operations/provenance owner | reviewer-owned oracle, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | row:proposed_legacy_crosswalk {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-admin-units"} | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | row-level reviewer-owned expected truth, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | row:proposed_legacy_crosswalk {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-buildings"} | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | row-level reviewer-owned expected truth, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| roads/buildings/territorial reference authority | row:proposed_legacy_crosswalk {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-roads"} | which registry authority can promote roads, buildings and territorial references as location-model subjects | SDA + NLI domain authority owner | row-level reviewer-owned expected truth, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | row:proposed_legacy_crosswalk {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-territories"} | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | row-level reviewer-owned expected truth, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |
| administrative hierarchy authority | row:proposed_migration_exception {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-admin-units"} | which government authority owns provisional official hierarchy/reference rows and parent/territory lineage | SDA + government administrative-authority RFI owner | row-level reviewer-owned expected truth, source lineage, target owner, privacy/publication classification, negative controls | True | True | only mapping/oracle drafting; no implementation |

### 4.1 Authority inventory scopes

| metric | scope | count |
| --- | --- | --- |
| authority-blocked transform groups | unique transform groups that depend on an authority decision overlay | 66 |
| authority-blocked broad expected rows | mutually exclusive row category `authority blocked` | 5 |
| unresolved-owner rows | mutually exclusive row category `unresolved after analysis` | 1 |
| authority-decision families | register categories | 7 |
| privacy-and-authority dependent items | unique transform groups in privacy queue plus authority overlay, plus row-level authority entries | 71 |

## 5. C35 — historical-only inventories

### 5.1 Historical transform-group variants

| accepted transform group | frozen covered fields | exact contradiction with accepted narrow decision | historical-only status |
| --- | --- | --- | --- |
| WO002-R06-geometry-observation-address_points | address_points.accuracy_meters, address_points.latitude, address_points.longitude | frozen broad representation is superseded; not allowed to govern acceptance even where fields look similar | yes; frozen representation only |
| WO002-R06-geometry-observation-address_records | address_records.accuracy_meters, address_records.latitude, address_records.longitude | frozen broad representation is superseded; not allowed to govern acceptance even where fields look similar | yes; frozen representation only |
| WO002-R06-geometry-observation-citizen_geotag_submissions | citizen_geotag_submissions.accuracy_meters, citizen_geotag_submissions.latitude, citizen_geotag_submissions.longitude | frozen broad representation is superseded; not allowed to govern acceptance even where fields look similar | yes; frozen representation only |
| WO002-R06-identity-crosswalk-address_points | address_points.address_id, address_points.id | exact frozen/live contradiction in covered fields/targets/dispositions | yes; frozen representation only |
| WO002-R06-identity-crosswalk-address_records | address_records.id, address_records.source_submission_id, address_records.territory_id | exact frozen/live contradiction in covered fields/targets/dispositions | yes; frozen representation only |
| WO002-R06-identity-crosswalk-addresses | addresses.building_id, addresses.id, addresses.road_id, addresses.superseded_by_address_id, addresses.territory_id | exact frozen/live contradiction in covered fields/targets/dispositions | yes; frozen representation only |
| WO002-R06-identity-crosswalk-citizen_geotag_submissions | citizen_geotag_submissions.field_submission_id, citizen_geotag_submissions.id, citizen_geotag_submissions.territory_id | exact frozen/live contradiction in covered fields/targets/dispositions | yes; frozen representation only |

### 5.2 Historical broad expected row families

| row family | counting scope | count |
| --- | --- | --- |
| proposed_geometry_observation | rows classified as frozen/prohibited/structurally invalid broad history | 2 |
| proposed_legacy_crosswalk | rows classified as frozen/prohibited/structurally invalid broad history | 8 |
| proposed_location_record_object_link | rows classified as frozen/prohibited/structurally invalid broad history | 1 |
| proposed_location_record_relationship | rows classified as frozen/prohibited/structurally invalid broad history | 1 |
| proposed_location_record_version | rows classified as frozen/prohibited/structurally invalid broad history | 1 |
| proposed_migration_exception | rows classified as frozen/prohibited/structurally invalid broad history | 6 |
| proposed_name_record | rows classified as frozen/prohibited/structurally invalid broad history | 14 |
| proposed_registry_subject | rows classified as frozen/prohibited/structurally invalid broad history | 1 |
| proposed_source_payload_archive | rows classified as frozen/prohibited/structurally invalid broad history | 16 |

### 5.3 Individual historical/prohibited broad expected rows

| category | table | primary key | source table | recommended disposition |
| --- | --- | --- | --- | --- |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-correction-case-archive-address-corrections"} | address_corrections | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-address-corrections"} | address_corrections | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-address-points"} | address_points | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-address-record-events"} | address_record_events | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-address-records"} | address_records | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-addresses"} | addresses | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-admin-units"} | admin_units | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-buildings"} | buildings | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-field-assignments"} | field_assignments | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-field-submissions"} | field_submissions | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-import-jobs"} | import_jobs | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-import-rows"} | import_rows | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-reference-data-load-history"} | reference_data_load_history | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-reference-data-loads"} | reference_data_loads | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-roads"} | roads | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-territories"} | territories | historical-only broad retention evidence; do not govern future acceptance |
| explicitly prohibited row | proposed_location_record_version | {"location_record_version_id": "phase-a-version-phase-a-location-address-reference"} |  | remove from future broad acceptance scope |
| explicitly prohibited row | proposed_location_record_relationship | {"relationship_id": "phase-a-relationship-geotag-near-address-reference"} |  | remove from future broad acceptance scope |

### 5.4 Historical generic harness behaviors

| behavior | scope | historical-only | future action |
| --- | --- | --- | --- |
| generic fixture pre-creation around accepted identities | broad fixture behavior | yes | remove or re-author under reviewer-owned oracle |
| prohibited accepted-identity version/alias/publication behavior | broad row family | yes | remove from future broad expected truth |
| generic-transform self-authority | broad harness behavior | yes | prohibit as acceptance evidence |
| raw/generic citizen evidence behavior | citizen/privacy broad behavior | yes | privacy review required before any target truth |

## 6. C36 — structurally invalid generic target rows

| table | primary key | source table | current target | reason invalid | affected accepted control | recommended disposition |
| --- | --- | --- | --- | --- | --- | --- |
| proposed_geometry_observation | {"geometry_observation_id": "phase-a-geometry-wo002-r06-geometry-observation-address-points"} | address_points | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_geometry_observation | {"geometry_observation_id": "phase-a-geometry-wo002-r06-geometry-observation-address-records"} | address_records | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-audit-logs"} | audit_logs | location_record | generic crosswalk resolves operational/control source audit_logs to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-auth-tokens"} | auth_tokens | location_record | generic crosswalk resolves operational/control source auth_tokens to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-import-jobs"} | import_jobs | location_record | generic crosswalk resolves operational/control source import_jobs to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-import-rows"} | import_rows | location_record | generic crosswalk resolves operational/control source import_rows to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-publication-pack-addresses"} | publication_pack_addresses | location_record | generic crosswalk resolves operational/control source publication_pack_addresses to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-publication-packs"} | publication_packs | location_record | generic crosswalk resolves operational/control source publication_packs to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-reference-data-load-history"} | reference_data_load_history | location_record | generic crosswalk resolves operational/control source reference_data_load_history to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-users"} | users | location_record | generic crosswalk resolves operational/control source users to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_location_record_object_link | {"link_id": "phase-a-link-phase-a-location-geotag-primary-subject"} |  | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-audit-logs"} | audit_logs | n/a | generic migration exception for audit_logs exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-development-fixture-batches"} | development_fixture_batches | n/a | generic migration exception for development_fixture_batches exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-development-fixture-records"} | development_fixture_records | n/a | generic migration exception for development_fixture_records exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-import-rows"} | import_rows | n/a | generic migration exception for import_rows exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-reference-data-load-history"} | reference_data_load_history | n/a | generic migration exception for reference_data_load_history exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-reference-data-loads"} | reference_data_loads | n/a | generic migration exception for reference_data_loads exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-address-record-events"} | address_record_events | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-address-records"} | address_records | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-admin-units"} | admin_units | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-audit-logs"} | audit_logs | phase-a-subject-phase-a-location-geotag | name record sourced from audit_logs is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-buildings"} | buildings | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-development-fixture-records"} | development_fixture_records | phase-a-subject-phase-a-location-geotag | name record sourced from development_fixture_records is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-field-submissions"} | field_submissions | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-import-jobs"} | import_jobs | phase-a-subject-phase-a-location-geotag | name record sourced from import_jobs is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-import-rows"} | import_rows | phase-a-subject-phase-a-location-geotag | name record sourced from import_rows is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-provinces"} | provinces | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-publication-packs"} | publication_packs | phase-a-subject-phase-a-location-geotag | name record sourced from publication_packs is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-roads"} | roads | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-territories"} | territories | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-users"} | users | phase-a-subject-phase-a-location-geotag | name record sourced from users is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| proposed_registry_subject | {"subject_id": "phase-a-subject-phase-a-location-geotag"} |  | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |

## 7. Reconciled 199 broad expected rows

| category | count |
| --- | --- |
| accepted-family row represented consistently | 2 |
| authority blocked | 5 |
| explicitly prohibited row | 2 |
| frozen historical row | 16 |
| future location-domain candidate | 11 |
| future workflow candidate | 9 |
| legitimate prerequisite | 104 |
| privacy blocked | 6 |
| publication/release candidate | 6 |
| security/audit/development/migration out-of-scope | 5 |
| structurally invalid generic output | 32 |
| unresolved after analysis | 1 |

### 7.1 Complete row inventory

| category | table | primary key | source table | current target | reason invalid | affected accepted control | recommended disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| future location-domain candidate | proposed_administrative_unit | {"administrative_unit_id": "phase-a-admin-bioko-norte"} |  | n/a |  | n/a | requires future reviewer-owned location/reference oracle |
| future location-domain candidate | proposed_administrative_unit_version | {"administrative_unit_version_id": "phase-a-admin-bioko-norte-v1"} |  | n/a |  | n/a | requires future reviewer-owned location/reference oracle |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-correction-case-archive-address-corrections"} | address_corrections | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-address-corrections"} | address_corrections | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-address-points"} | address_points | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-address-record-events"} | address_record_events | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-address-records"} | address_records | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-addresses"} | addresses | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-admin-units"} | admin_units | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| security/audit/development/migration out-of-scope | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-audit-logs"} | audit_logs | n/a |  | n/a | remove from Phase A location-model acceptance scope |
| security/audit/development/migration out-of-scope | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-auth-tokens"} | auth_tokens | n/a |  | n/a | remove from Phase A location-model acceptance scope |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-buildings"} | buildings | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| privacy blocked | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-citizen-geotag-submissions"} | citizen_geotag_submissions | n/a |  | n/a | privacy review required before any oracle |
| security/audit/development/migration out-of-scope | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-development-fixture-batches"} | development_fixture_batches | n/a |  | n/a | remove from Phase A location-model acceptance scope |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-field-assignments"} | field_assignments | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-field-submissions"} | field_submissions | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-import-jobs"} | import_jobs | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-import-rows"} | import_rows | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| publication/release candidate | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-publication-packs"} | publication_packs | n/a |  | n/a | defer until publication authority |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-reference-data-load-history"} | reference_data_load_history | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-reference-data-loads"} | reference_data_loads | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-roads"} | roads | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| security/audit/development/migration out-of-scope | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-schema-migrations"} | schema_migrations | n/a |  | n/a | remove from Phase A location-model acceptance scope |
| frozen historical row | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-territories"} | territories | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | historical-only broad retention evidence; do not govern future acceptance |
| security/audit/development/migration out-of-scope | proposed_source_payload_archive | {"archive_id": "phase-a-archive-wo002-r06-source-archive-users"} | users | n/a |  | n/a | remove from Phase A location-model acceptance scope |
| future workflow candidate | proposed_correction_case | {"correction_case_id": "phase-a-correction-case-001"} |  | phase-a-location-geotag |  | n/a | requires future workflow oracle |
| legitimate prerequisite | proposed_country | {"country_id": "phase-a-country-gq"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-correction-001"} | address_corrections | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-phase-a-location-address-reference"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-phase-a-location-geotag"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-address-corrections"} | address_corrections | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-address-points"} | address_points | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-address-record-events"} | address_record_events | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-address-records"} | address_records | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-addresses"} | addresses | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-admin-units"} | admin_units | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-audit-logs"} | audit_logs | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-auth-tokens"} | auth_tokens | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-buildings"} | buildings | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-citizen-geotag-submissions"} | citizen_geotag_submissions | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-development-fixture-batches"} | development_fixture_batches | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-development-fixture-records"} | development_fixture_records | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-field-assignments"} | field_assignments | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-field-submissions"} | field_submissions | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-import-jobs"} | import_jobs | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-provinces"} | provinces | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-publication-packs"} | publication_packs | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-reference-data-load-history"} | reference_data_load_history | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-reference-data-loads"} | reference_data_loads | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-roads"} | roads | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-territories"} | territories | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_decision_event | {"decision_event_id": "phase-a-decision-wo002-r06-recorded-time-users"} | users | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-address-corrections"} | address_corrections | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-address-points"} | address_points | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-address-record-events"} | address_record_events | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-address-records"} | address_records | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-addresses"} | addresses | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-admin-units"} | admin_units | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-audit-logs"} | audit_logs | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-auth-tokens"} | auth_tokens | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-buildings"} | buildings | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-citizen-geotag-submissions"} | citizen_geotag_submissions | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-development-fixture-batches"} | development_fixture_batches | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-development-fixture-records"} | development_fixture_records | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-field-assignments"} | field_assignments | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-field-submissions"} | field_submissions | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-import-jobs"} | import_jobs | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-import-rows"} | import_rows | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-provinces"} | provinces | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-publication-pack-addresses"} | publication_pack_addresses | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-publication-packs"} | publication_packs | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-reference-data-load-history"} | reference_data_load_history | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-reference-data-loads"} | reference_data_loads | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-roads"} | roads | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-schema-migrations"} | schema_migrations | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-territories"} | territories | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_evidence_object | {"evidence_object_id": "phase-a-evidence-users"} | users | n/a |  | n/a | retain only as prerequisite, not output ownership |
| structurally invalid generic output | proposed_geometry_observation | {"geometry_observation_id": "phase-a-geometry-wo002-r06-geometry-observation-address-points"} | address_points | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_geometry_observation | {"geometry_observation_id": "phase-a-geometry-wo002-r06-geometry-observation-address-records"} | address_records | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| privacy blocked | proposed_geometry_observation | {"geometry_observation_id": "phase-a-geometry-wo002-r06-geometry-observation-citizen-geotag-submissions"} | citizen_geotag_submissions | phase-a-subject-phase-a-location-geotag |  | n/a | privacy review required before any oracle |
| future workflow candidate | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-address-corrections-correction-case"} | address_corrections | correction_case |  | n/a | requires future workflow oracle |
| future workflow candidate | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-address-corrections"} | address_corrections | location_record |  | n/a | requires future workflow oracle |
| future location-domain candidate | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-address-points"} | address_points | location_record |  | n/a | requires future reviewer-owned location/reference oracle |
| future workflow candidate | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-address-record-events"} | address_record_events | location_record |  | n/a | requires future workflow oracle |
| future location-domain candidate | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-address-records"} | address_records | location_record |  | n/a | requires future reviewer-owned location/reference oracle |
| future location-domain candidate | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-addresses"} | addresses | location_record |  | n/a | requires future reviewer-owned location/reference oracle |
| authority blocked | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-admin-units"} | admin_units | location_record |  | n/a | authority decision required before implementation |
| structurally invalid generic output | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-audit-logs"} | audit_logs | location_record | generic crosswalk resolves operational/control source audit_logs to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-auth-tokens"} | auth_tokens | location_record | generic crosswalk resolves operational/control source auth_tokens to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| authority blocked | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-buildings"} | buildings | location_record |  | n/a | authority decision required before implementation |
| privacy blocked | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-citizen-geotag-submissions"} | citizen_geotag_submissions | location_record |  | n/a | privacy review required before any oracle |
| future workflow candidate | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-field-assignments"} | field_assignments | location_record |  | n/a | requires future workflow oracle |
| future workflow candidate | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-field-submissions"} | field_submissions | location_record |  | n/a | requires future workflow oracle |
| structurally invalid generic output | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-import-jobs"} | import_jobs | location_record | generic crosswalk resolves operational/control source import_jobs to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-import-rows"} | import_rows | location_record | generic crosswalk resolves operational/control source import_rows to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-publication-pack-addresses"} | publication_pack_addresses | location_record | generic crosswalk resolves operational/control source publication_pack_addresses to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-publication-packs"} | publication_packs | location_record | generic crosswalk resolves operational/control source publication_packs to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-reference-data-load-history"} | reference_data_load_history | location_record | generic crosswalk resolves operational/control source reference_data_load_history to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| authority blocked | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-roads"} | roads | location_record |  | n/a | authority decision required before implementation |
| authority blocked | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-territories"} | territories | location_record |  | n/a | authority decision required before implementation |
| structurally invalid generic output | proposed_legacy_crosswalk | {"legacy_crosswalk_id": "phase-a-crosswalk-wo002-r06-identity-crosswalk-users"} | users | location_record | generic crosswalk resolves operational/control source users to a target without reviewed subject-resolution semantics | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| future location-domain candidate | proposed_location_record_object_link | {"link_id": "phase-a-link-phase-a-location-address-reference-primary-subject"} |  | phase-a-subject-phase-a-location-address-reference |  | n/a | requires future reviewer-owned location/reference oracle |
| structurally invalid generic output | proposed_location_record_object_link | {"link_id": "phase-a-link-phase-a-location-geotag-primary-subject"} |  | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| accepted-family row represented consistently | proposed_location_record | {"location_record_id": "phase-a-location-address-reference"} |  | n/a |  | n/a | retain active accepted proof only |
| future location-domain candidate | proposed_location_record | {"location_record_id": "phase-a-location-geotag"} |  | n/a |  | n/a | requires future reviewer-owned location/reference oracle |
| explicitly prohibited row | proposed_location_record_version | {"location_record_version_id": "phase-a-version-phase-a-location-address-reference"} |  | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | remove from future broad acceptance scope |
| unresolved after analysis | proposed_location_record_version | {"location_record_version_id": "phase-a-version-phase-a-location-geotag"} |  | n/a |  | n/a | do not accept; SDA classification required |
| future location-domain candidate | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-geometry-authority-wo002-r06-geometry-observation-address-points"} | address_points | n/a |  | n/a | requires future reviewer-owned location/reference oracle |
| future location-domain candidate | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-geometry-authority-wo002-r06-geometry-observation-address-records"} | address_records | n/a |  | n/a | requires future reviewer-owned location/reference oracle |
| privacy blocked | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-geometry-authority-wo002-r06-geometry-observation-citizen-geotag-submissions"} | citizen_geotag_submissions | n/a |  | n/a | privacy review required before any oracle |
| future workflow candidate | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-address-record-events"} | address_record_events | n/a |  | n/a | requires future workflow oracle |
| future location-domain candidate | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-address-records"} | address_records | n/a |  | n/a | requires future reviewer-owned location/reference oracle |
| future location-domain candidate | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-addresses"} | addresses | n/a |  | n/a | requires future reviewer-owned location/reference oracle |
| authority blocked | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-admin-units"} | admin_units | n/a |  | n/a | authority decision required before implementation |
| structurally invalid generic output | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-audit-logs"} | audit_logs | n/a | generic migration exception for audit_logs exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| privacy blocked | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-citizen-geotag-submissions"} | citizen_geotag_submissions | n/a |  | n/a | privacy review required before any oracle |
| structurally invalid generic output | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-development-fixture-batches"} | development_fixture_batches | n/a | generic migration exception for development_fixture_batches exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-development-fixture-records"} | development_fixture_records | n/a | generic migration exception for development_fixture_records exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| future workflow candidate | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-field-assignments"} | field_assignments | n/a |  | n/a | requires future workflow oracle |
| future workflow candidate | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-field-submissions"} | field_submissions | n/a |  | n/a | requires future workflow oracle |
| structurally invalid generic output | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-import-rows"} | import_rows | n/a | generic migration exception for import_rows exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| publication/release candidate | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-publication-pack-addresses"} | publication_pack_addresses | n/a |  | n/a | defer until publication authority |
| structurally invalid generic output | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-reference-data-load-history"} | reference_data_load_history | n/a | generic migration exception for reference_data_load_history exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_migration_exception | {"migration_exception_id": "phase-a-exception-wo002-r06-identity-crosswalk-reference-data-loads"} | reference_data_loads | n/a | generic migration exception for reference_data_loads exists solely because broad transformer could not establish a reviewed target identity | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-address-record-events"} | address_record_events | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-address-records"} | address_records | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-admin-units"} | admin_units | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-audit-logs"} | audit_logs | phase-a-subject-phase-a-location-geotag | name record sourced from audit_logs is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-buildings"} | buildings | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| privacy blocked | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-citizen-geotag-submissions"} | citizen_geotag_submissions | phase-a-subject-phase-a-location-geotag |  | n/a | privacy review required before any oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-development-fixture-records"} | development_fixture_records | phase-a-subject-phase-a-location-geotag | name record sourced from development_fixture_records is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-field-submissions"} | field_submissions | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-import-jobs"} | import_jobs | phase-a-subject-phase-a-location-geotag | name record sourced from import_jobs is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-import-rows"} | import_rows | phase-a-subject-phase-a-location-geotag | name record sourced from import_rows is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-provinces"} | provinces | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-publication-packs"} | publication_packs | phase-a-subject-phase-a-location-geotag | name record sourced from publication_packs is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-roads"} | roads | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-territories"} | territories | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| structurally invalid generic output | proposed_name_record | {"name_record_id": "phase-a-name-wo002-r06-name-record-users"} | users | phase-a-subject-phase-a-location-geotag | name record sourced from users is not a reviewed location subject/name lineage | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |
| publication/release candidate | proposed_public_code_alias | {"public_code_alias_id": "phase-a-alias-geotag"} |  | n/a |  | n/a | defer until publication authority |
| publication/release candidate | proposed_public_code_alias | {"public_code_alias_id": "phase-a-alias-wo002-r06-public-code-alias-addresses"} | addresses | n/a |  | n/a | defer until publication authority |
| publication/release candidate | proposed_public_code_alias | {"public_code_alias_id": "phase-a-alias-wo002-r06-public-code-alias-admin-units"} | units | n/a |  | n/a | defer until publication authority |
| publication/release candidate | proposed_public_code_alias | {"public_code_alias_id": "phase-a-alias-wo002-r06-public-code-alias-provinces"} | provinces | n/a |  | n/a | defer until publication authority |
| explicitly prohibited row | proposed_location_record_relationship | {"relationship_id": "phase-a-relationship-geotag-near-address-reference"} |  | n/a |  | accepted-family ownership/absence/privacy/generic-transform prohibition | remove from future broad acceptance scope |
| legitimate prerequisite | proposed_source_authority | {"source_authority_id": "phase-a-authority-citizen-evidence"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_authority | {"source_authority_id": "phase-a-authority-conditional-admin-reference"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_authority | {"source_authority_id": "phase-a-authority-operational-control"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-address-corrections"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-address-points"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-address-record-events"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-address-records"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-addresses"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-admin-units"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-audit-logs"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-auth-tokens"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-buildings"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-citizen-geotag-submissions"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-development-fixture-batches"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-development-fixture-records"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-field-assignments"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-field-submissions"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-import-jobs"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-import-rows"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-provinces"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-publication-pack-addresses"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-publication-packs"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-reference-data-load-history"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-reference-data-loads"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-roads"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-schema-migrations"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-territories"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_package | {"source_package_id": "phase-a-source-package-users"} |  | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-address-corrections-001"} | address_corrections | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-address-points-001"} | address_points | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-address-record-events-001"} | address_record_events | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-address-records-001"} | address_records | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-addresses-001"} | addresses | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-admin-units-001"} | admin_units | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-audit-logs-001"} | audit_logs | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-auth-tokens-001"} | auth_tokens | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-buildings-001"} | buildings | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-citizen-geotag-submissions-001"} | citizen_geotag_submissions | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-development-fixture-batches-001"} | development_fixture_batches | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-development-fixture-records-001"} | development_fixture_records | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-field-assignments-001"} | field_assignments | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-field-submissions-001"} | field_submissions | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-import-jobs-001"} | import_jobs | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-import-rows-001"} | import_rows | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-provinces-001"} | provinces | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-publication-pack-addresses-001"} | publication_pack_addresses | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-publication-packs-001"} | publication_packs | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-reference-data-load-history-001"} | reference_data_load_history | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-reference-data-loads-001"} | reference_data_loads | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-roads-001"} | roads | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-schema-migrations-001"} | schema_migrations | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-territories-001"} | territories | n/a |  | n/a | retain only as prerequisite, not output ownership |
| legitimate prerequisite | proposed_source_record | {"source_record_id": "phase-a-source-record-users-001"} | users | n/a |  | n/a | retain only as prerequisite, not output ownership |
| accepted-family row represented consistently | proposed_registry_subject | {"subject_id": "phase-a-subject-phase-a-location-address-reference"} |  | phase-a-subject-phase-a-location-address-reference |  | n/a | retain active accepted proof only |
| structurally invalid generic output | proposed_registry_subject | {"subject_id": "phase-a-subject-phase-a-location-geotag"} |  | phase-a-subject-phase-a-location-geotag | generic row targets phase-a-subject-phase-a-location-geotag from an unrelated source | accepted-family ownership/absence/privacy/generic-transform prohibition | remove/redesign/defer; require reviewer-owned subject-resolution oracle |

## 8. Reconciled 237 catalog fields

This reconciliation is separate from frozen/live transform-spec coverage. A field can be syntactically covered by a broad group while remaining semantically out of scope or blocked. Each catalog field appears exactly once below.

| status | count |
| --- | --- |
| accepted context only | 56 |
| audit/assurance | 9 |
| authority blocked | 18 |
| development/test | 11 |
| direct accepted owner | 13 |
| location/reference candidate | 30 |
| migration governance | 5 |
| provenance/control only | 32 |
| publication/release | 9 |
| security/credential | 13 |
| workflow candidate | 41 |

| field | status |
| --- | --- |
| address_corrections.id | workflow candidate |
| address_corrections.address_id | workflow candidate |
| address_corrections.public_code | publication/release |
| address_corrections.query | workflow candidate |
| address_corrections.correction_type | workflow candidate |
| address_corrections.reason | workflow candidate |
| address_corrections.note | workflow candidate |
| address_corrections.reporter_name | workflow candidate |
| address_corrections.reporter_contact | workflow candidate |
| address_corrections.status | workflow candidate |
| address_corrections.created_at | workflow candidate |
| address_corrections.updated_at | workflow candidate |
| address_corrections.reviewer_note | workflow candidate |
| address_points.id | direct accepted owner |
| address_points.address_id | accepted context only |
| address_points.latitude | direct accepted owner |
| address_points.longitude | direct accepted owner |
| address_points.accuracy_meters | direct accepted owner |
| address_points.source_method | accepted context only |
| address_points.is_active | accepted context only |
| address_points.created_at | accepted context only |
| address_points.updated_at | accepted context only |
| address_record_events.id | workflow candidate |
| address_record_events.address_record_id | workflow candidate |
| address_record_events.event_type | workflow candidate |
| address_record_events.actor_id | workflow candidate |
| address_record_events.actor_username | workflow candidate |
| address_record_events.actor_role | workflow candidate |
| address_record_events.details | workflow candidate |
| address_record_events.created_at | workflow candidate |
| address_records.id | direct accepted owner |
| address_records.address_code | accepted context only |
| address_records.source_submission_id | accepted context only |
| address_records.province_code | accepted context only |
| address_records.territory_id | accepted context only |
| address_records.address_label | accepted context only |
| address_records.status | accepted context only |
| address_records.publication_state | accepted context only |
| address_records.latitude | direct accepted owner |
| address_records.longitude | direct accepted owner |
| address_records.accuracy_meters | direct accepted owner |
| address_records.search_text | location/reference candidate |
| address_records.record_bundle | location/reference candidate |
| address_records.is_archived | accepted context only |
| address_records.created_at | accepted context only |
| address_records.updated_at | accepted context only |
| address_records.geom | accepted context only |
| addresses.id | direct accepted owner |
| addresses.formatted | accepted context only |
| addresses.territory_id | accepted context only |
| addresses.road_id | accepted context only |
| addresses.building_id | accepted context only |
| addresses.province_code | authority blocked |
| addresses.public_code | accepted context only |
| addresses.issuance_method | location/reference candidate |
| addresses.source | location/reference candidate |
| addresses.verification_status | location/reference candidate |
| addresses.superseded_by_address_id | accepted context only |
| addresses.status | accepted context only |
| addresses.publication_state | accepted context only |
| addresses.is_archived | accepted context only |
| addresses.created_at | accepted context only |
| addresses.updated_at | accepted context only |
| admin_units.id | authority blocked |
| admin_units.level | authority blocked |
| admin_units.code | authority blocked |
| admin_units.parent_id | authority blocked |
| admin_units.province_code | authority blocked |
| admin_units.name_es | authority blocked |
| admin_units.name_en | authority blocked |
| admin_units.status | location/reference candidate |
| admin_units.sort_order | location/reference candidate |
| admin_units.created_at | location/reference candidate |
| admin_units.updated_at | location/reference candidate |
| audit_logs.id | audit/assurance |
| audit_logs.actor_user_id | audit/assurance |
| audit_logs.actor_username | audit/assurance |
| audit_logs.actor_role | audit/assurance |
| audit_logs.action | audit/assurance |
| audit_logs.entity_type | audit/assurance |
| audit_logs.entity_id | audit/assurance |
| audit_logs.details | audit/assurance |
| audit_logs.created_at | audit/assurance |
| auth_tokens.token | security/credential |
| auth_tokens.user_id | security/credential |
| auth_tokens.created_at | security/credential |
| auth_tokens.expires_at | security/credential |
| auth_tokens.revoked_at | security/credential |
| auth_tokens.last_seen_at | security/credential |
| buildings.id | location/reference candidate |
| buildings.label | location/reference candidate |
| buildings.territory_id | authority blocked |
| buildings.road_id | authority blocked |
| buildings.status | location/reference candidate |
| buildings.usage | location/reference candidate |
| buildings.spatial_evidence | location/reference candidate |
| buildings.is_archived | location/reference candidate |
| buildings.created_at | location/reference candidate |
| buildings.updated_at | location/reference candidate |
| citizen_geotag_submissions.id | direct accepted owner |
| citizen_geotag_submissions.territory_id | accepted context only |
| citizen_geotag_submissions.address_label | accepted context only |
| citizen_geotag_submissions.citizen_name | accepted context only |
| citizen_geotag_submissions.citizen_contact | accepted context only |
| citizen_geotag_submissions.dip_last4 | accepted context only |
| citizen_geotag_submissions.identity_verification_status | accepted context only |
| citizen_geotag_submissions.identity_document_verified | accepted context only |
| citizen_geotag_submissions.identity_verified_at | accepted context only |
| citizen_geotag_submissions.landmark | accepted context only |
| citizen_geotag_submissions.latitude | direct accepted owner |
| citizen_geotag_submissions.longitude | direct accepted owner |
| citizen_geotag_submissions.accuracy_meters | direct accepted owner |
| citizen_geotag_submissions.capture_method | accepted context only |
| citizen_geotag_submissions.grid_code | accepted context only |
| citizen_geotag_submissions.status | accepted context only |
| citizen_geotag_submissions.duplicate_hint | accepted context only |
| citizen_geotag_submissions.reviewer_note | accepted context only |
| citizen_geotag_submissions.suggested_road_name | accepted context only |
| citizen_geotag_submissions.suggested_local_area | accepted context only |
| citizen_geotag_submissions.suggested_place_name | accepted context only |
| citizen_geotag_submissions.map_display_name | accepted context only |
| citizen_geotag_submissions.road_suggestion_source | accepted context only |
| citizen_geotag_submissions.road_suggestion_attribution | accepted context only |
| citizen_geotag_submissions.road_suggestion_status | accepted context only |
| citizen_geotag_submissions.reviewed_road_name | accepted context only |
| citizen_geotag_submissions.field_submission_id | accepted context only |
| citizen_geotag_submissions.field_status | accepted context only |
| citizen_geotag_submissions.field_note | accepted context only |
| citizen_geotag_submissions.field_verified_at | accepted context only |
| citizen_geotag_submissions.signage_batch | accepted context only |
| citizen_geotag_submissions.created_at | accepted context only |
| citizen_geotag_submissions.updated_at | accepted context only |
| development_fixture_batches.batch_id | development/test |
| development_fixture_batches.fixture_version | development/test |
| development_fixture_batches.environment | development/test |
| development_fixture_batches.loaded_at | development/test |
| development_fixture_batches.cleaned_at | development/test |
| development_fixture_batches.execution_context | development/test |
| development_fixture_records.batch_id | development/test |
| development_fixture_records.table_name | development/test |
| development_fixture_records.record_id | development/test |
| development_fixture_records.created_by_batch | development/test |
| development_fixture_records.recorded_at | development/test |
| field_assignments.assignment_id | workflow candidate |
| field_assignments.territory_id | workflow candidate |
| field_assignments.territory | workflow candidate |
| field_assignments.task | workflow candidate |
| field_assignments.team | workflow candidate |
| field_assignments.priority | workflow candidate |
| field_assignments.created_at | workflow candidate |
| field_submissions.id | workflow candidate |
| field_submissions.assignment_id | workflow candidate |
| field_submissions.territory_id | workflow candidate |
| field_submissions.submission_type | workflow candidate |
| field_submissions.candidate_name | workflow candidate |
| field_submissions.candidate_status | workflow candidate |
| field_submissions.notes | workflow candidate |
| field_submissions.submitted_by | workflow candidate |
| field_submissions.review_status | workflow candidate |
| field_submissions.reviewer_note | workflow candidate |
| field_submissions.registry_entity_id | workflow candidate |
| field_submissions.spatial_evidence | workflow candidate |
| field_submissions.created_at | workflow candidate |
| field_submissions.updated_at | workflow candidate |
| import_jobs.id | provenance/control only |
| import_jobs.name | provenance/control only |
| import_jobs.source_name | provenance/control only |
| import_jobs.status | provenance/control only |
| import_jobs.imported_count | provenance/control only |
| import_jobs.created_at | provenance/control only |
| import_jobs.updated_at | provenance/control only |
| import_rows.job_id | provenance/control only |
| import_rows.row_number | provenance/control only |
| import_rows.submission_type | provenance/control only |
| import_rows.territory_id | provenance/control only |
| import_rows.candidate_name | provenance/control only |
| import_rows.candidate_status | provenance/control only |
| import_rows.notes | provenance/control only |
| import_rows.validation_status | provenance/control only |
| import_rows.validation_message | provenance/control only |
| import_rows.committed_submission_id | provenance/control only |
| provinces.code | authority blocked |
| provinces.name | authority blocked |
| provinces.created_at | location/reference candidate |
| publication_pack_addresses.publication_pack_id | publication/release |
| publication_pack_addresses.address_id | publication/release |
| publication_packs.id | publication/release |
| publication_packs.name | publication/release |
| publication_packs.status | publication/release |
| publication_packs.audience | publication/release |
| publication_packs.created_at | publication/release |
| publication_packs.updated_at | publication/release |
| reference_data_load_history.id | provenance/control only |
| reference_data_load_history.package_id | provenance/control only |
| reference_data_load_history.package_version | provenance/control only |
| reference_data_load_history.source | provenance/control only |
| reference_data_load_history.authority_status | provenance/control only |
| reference_data_load_history.package_checksum | provenance/control only |
| reference_data_load_history.loaded_at | provenance/control only |
| reference_data_load_history.execution_context | provenance/control only |
| reference_data_loads.package_id | provenance/control only |
| reference_data_loads.package_version | provenance/control only |
| reference_data_loads.source | provenance/control only |
| reference_data_loads.authority_status | provenance/control only |
| reference_data_loads.package_checksum | provenance/control only |
| reference_data_loads.loaded_at | provenance/control only |
| reference_data_loads.execution_context | provenance/control only |
| roads.id | location/reference candidate |
| roads.name | location/reference candidate |
| roads.territory_id | authority blocked |
| roads.status | location/reference candidate |
| roads.length_km | location/reference candidate |
| roads.spatial_evidence | location/reference candidate |
| roads.is_archived | location/reference candidate |
| roads.created_at | location/reference candidate |
| roads.updated_at | location/reference candidate |
| schema_migrations.version | migration governance |
| schema_migrations.filename | migration governance |
| schema_migrations.checksum | migration governance |
| schema_migrations.applied_at | migration governance |
| schema_migrations.execution_context | migration governance |
| territories.id | authority blocked |
| territories.name | authority blocked |
| territories.province_code | authority blocked |
| territories.admin_unit_id | authority blocked |
| territories.type | authority blocked |
| territories.readiness | location/reference candidate |
| territories.is_archived | location/reference candidate |
| territories.created_at | location/reference candidate |
| territories.updated_at | location/reference candidate |
| users.id | security/credential |
| users.username | security/credential |
| users.full_name | security/credential |
| users.role | security/credential |
| users.password_hash | security/credential |
| users.is_active | security/credential |
| users.created_at | security/credential |

## 9. F02 and F14 residual reconstruction

| finding | status | residual scope | closure boundary |
| --- | --- | --- | --- |
| F02 | partially satisfied; not closed | all non-accepted groups/fields, broad expected truth, row ownership, privacy/publication/authority decisions, structurally invalid generic outputs, and non-generic broad reassessment remain residual | SDA instruction required; not closed by this mapping |
| F14 | partially satisfied; not closed | broad harness architecture for non-accepted groups, full source-field coverage, row ownership, rollback/read-only comparison, authority/privacy controls, and generic-transform prohibition beyond accepted family remain residual | SDA instruction required; not closed by this mapping |

## 10. Wave 1 shortlist — no implementation authorized

| rank | checkpoint | national-location relevance | dependency leverage | authority readiness | privacy risk | F02 reduction | F14 reduction | target ownership clarity | publication effects | why |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | administrative-unit / province / territory reference identity and naming | 5 | 5 | 2 | 1 | 4 | 4 | 3 | none if public aliases excluded | foundational hierarchy for all locations; authority requirement explicit |
| 2 | roads identity and name reference mapping | 5 | 4 | 3 | 1 | 4 | 3 | 3 | none if public-code issuance excluded | location-reference backbone with clear subject semantics |
| 3 | buildings identity and label reference mapping | 5 | 4 | 3 | 1 | 4 | 3 | 3 | none if release rows excluded | connects addresses to addressable objects without citizen-sensitive evidence |
| 4 | territorial-reference crosswalks for accepted address/address-record dependencies | 4 | 4 | 2 | 1 | 3 | 4 | 3 | none | reduces accepted-context dependency ambiguity for territory/province references |
| 5 | reference-data load provenance/control prerequisite review | 3 | 3 | 4 | 1 | 2 | 4 | 4 | none | clarifies source package/provenance control without pretending it is a location identity |

**Recommended first mapping checkpoint:** administrative-unit / province / territory reference identity and naming
**Recommendation rationale:** foundational hierarchy for all locations; authority requirement explicit

## 11. Required corrected return values

| field | value |
| --- | --- |
| Active accepted groups | 7 |
| Historical frozen variants | 7 |
| Core-location candidates | 5 |
| Administrative/reference candidates | 5 |
| Workflow candidates | 8 |
| Provenance/control groups | 36 |
| Publication/release groups | 8 |
| Security/credential out-of-scope | 7 |
| Audit/assurance out-of-scope | 4 |
| Development/test out-of-scope | 6 |
| Migration-governance out-of-scope | 1 |
| Privacy-blocked groups | 3 |
| Authority-blocked groups | 66 |
| Deferred groups | 0 |
| Broad expected rows total | 199 |
| Accepted-consistent rows | 2 |
| Legitimate prerequisites | 104 |
| Location/workflow candidates | 20 |
| Publication/release candidates | 6 |
| Out-of-scope rows | 5 |
| Privacy-blocked rows | 6 |
| Authority-blocked rows | 5 |
| Historical rows | 16 |
| Prohibited rows | 2 |
| Structurally invalid generic rows | 32 |
| Unresolved rows | 1 |
| Row-category sum | 199 |
| Catalog field total | 237 |
| Direct accepted fields | 13 |
| Accepted-context fields | 56 |
| Location/reference candidates | 30 |
| Workflow candidates (fields) | 41 |
| Provenance/control fields | 32 |
| Publication/release fields | 9 |
| Security/credential fields | 13 |
| Audit/assurance fields | 9 |
| Development/test fields | 11 |
| Migration-governance fields | 5 |
| Privacy-blocked fields | 0 |
| Authority-blocked fields | 18 |
| Unresolved fields | 0 |
| Field-status sum | 237 |
| F02 status | partially satisfied; not closed |
| F02 residual scope | all non-accepted groups/fields, broad expected truth, row ownership, privacy/publication/authority decisions, structurally invalid generic outputs, and non-generic broad reassessment remain residual |
| F14 status | partially satisfied; not closed |
| F14 residual scope | broad harness architecture for non-accepted groups, full source-field coverage, row ownership, rollback/read-only comparison, authority/privacy controls, and generic-transform prohibition beyond accepted family remain residual |
| Wave 1 shortlist | 1. administrative-unit / province / territory reference identity and naming; 2. roads identity and name reference mapping; 3. buildings identity and label reference mapping; 4. territorial-reference crosswalks for accepted address/address-record dependencies; 5. reference-data load provenance/control prerequisite review |
| Recommended first mapping checkpoint | administrative-unit / province / territory reference identity and naming |
| Recommendation rationale | foundational hierarchy for all locations; authority requirement explicit |
| Current instructed action | Correct the Phase A residual-control and broad-readiness mapping only. |
| Next instruction required from SDA | YES — before reviewer-oracle preparation, another transform group, broad Phase A reassessment, F02/F14 closure, Review 12, Phase B, deployment or merge. |


## Current instructed action
Correct the Phase A residual-control and broad-readiness mapping only.

## Next instruction required from SDA
YES — before reviewer-oracle preparation, another transform group, broad Phase A reassessment, F02/F14 closure, Review 12, Phase B, deployment or merge.
