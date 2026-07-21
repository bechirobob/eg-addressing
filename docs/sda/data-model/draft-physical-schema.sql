-- NON-EXECUTABLE DESIGN ARTIFACT FOR NLI-WO-002 REVIEW 04
-- Safe to execute only in disposable validation schemas/databases. DO NOT APPLY to runtime.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS btree_gist;
DROP SCHEMA IF EXISTS nli_wo002_target CASCADE;
CREATE SCHEMA nli_wo002_target;
SET search_path = nli_wo002_target, public;
CREATE TABLE vocab_admin_level (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_admin_level(value, meaning) VALUES ('country', 'Sovereign country row.');
INSERT INTO vocab_admin_level(value, meaning) VALUES ('district', 'District-level administrative unit.');
INSERT INTO vocab_admin_level(value, meaning) VALUES ('local_council', 'Recognized lower level when authorized.');
INSERT INTO vocab_admin_level(value, meaning) VALUES ('municipality', 'Municipality-level administrative unit.');
INSERT INTO vocab_admin_level(value, meaning) VALUES ('province', 'First-level administrative unit.');
CREATE TABLE vocab_administrative_unit_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_administrative_unit_lifecycle(value, meaning) VALUES ('historical', 'Historical official version.');
INSERT INTO vocab_administrative_unit_lifecycle(value, meaning) VALUES ('official', 'Official active version.');
INSERT INTO vocab_administrative_unit_lifecycle(value, meaning) VALUES ('proposed', 'Proposed administrative version.');
INSERT INTO vocab_administrative_unit_lifecycle(value, meaning) VALUES ('retired', 'Retired version.');
INSERT INTO vocab_administrative_unit_lifecycle(value, meaning) VALUES ('revoked', 'Revoked version.');
CREATE TABLE vocab_building_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_building_lifecycle(value, meaning) VALUES ('active', 'Active building.');
INSERT INTO vocab_building_lifecycle(value, meaning) VALUES ('candidate', 'Candidate building.');
INSERT INTO vocab_building_lifecycle(value, meaning) VALUES ('demolished', 'Demolished building.');
INSERT INTO vocab_building_lifecycle(value, meaning) VALUES ('retired', 'Retired building.');
INSERT INTO vocab_building_lifecycle(value, meaning) VALUES ('revoked', 'Revoked building.');
CREATE TABLE vocab_canonical_record_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_canonical_record_lifecycle(value, meaning) VALUES ('active', 'Current approved canonical state.');
INSERT INTO vocab_canonical_record_lifecycle(value, meaning) VALUES ('candidate', 'Candidate record.');
INSERT INTO vocab_canonical_record_lifecycle(value, meaning) VALUES ('corrected', 'Corrected by later version.');
INSERT INTO vocab_canonical_record_lifecycle(value, meaning) VALUES ('disputed', 'Active dispute.');
INSERT INTO vocab_canonical_record_lifecycle(value, meaning) VALUES ('retired', 'Retired.');
INSERT INTO vocab_canonical_record_lifecycle(value, meaning) VALUES ('revoked', 'Revoked.');
INSERT INTO vocab_canonical_record_lifecycle(value, meaning) VALUES ('superseded', 'Superseded.');
INSERT INTO vocab_canonical_record_lifecycle(value, meaning) VALUES ('under-review', 'Registry review.');
CREATE TABLE vocab_capture_method (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_capture_method(value, meaning) VALUES ('browser-gps', 'Browser GPS coordinate.');
INSERT INTO vocab_capture_method(value, meaning) VALUES ('derived-from-source', 'Derived from source geometry.');
INSERT INTO vocab_capture_method(value, meaning) VALUES ('field-device-gps', 'Field device GPS.');
INSERT INTO vocab_capture_method(value, meaning) VALUES ('imported-geometry', 'Imported geometry.');
INSERT INTO vocab_capture_method(value, meaning) VALUES ('manual-map-point', 'Manual map correction.');
INSERT INTO vocab_capture_method(value, meaning) VALUES ('surveyed', 'Surveyed/authoritative capture.');
CREATE TABLE vocab_case_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_case_lifecycle(value, meaning) VALUES ('approved', 'Approved.');
INSERT INTO vocab_case_lifecycle(value, meaning) VALUES ('closed', 'Closed.');
INSERT INTO vocab_case_lifecycle(value, meaning) VALUES ('needs-evidence', 'Needs evidence.');
INSERT INTO vocab_case_lifecycle(value, meaning) VALUES ('rejected', 'Rejected.');
INSERT INTO vocab_case_lifecycle(value, meaning) VALUES ('resolved', 'Resolved.');
INSERT INTO vocab_case_lifecycle(value, meaning) VALUES ('submitted', 'Submitted.');
INSERT INTO vocab_case_lifecycle(value, meaning) VALUES ('under-review', 'Under review.');
CREATE TABLE vocab_case_state (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_case_state(value, meaning) VALUES ('approved', 'Approved.');
INSERT INTO vocab_case_state(value, meaning) VALUES ('closed', 'Closed.');
INSERT INTO vocab_case_state(value, meaning) VALUES ('needs-evidence', 'More evidence required.');
INSERT INTO vocab_case_state(value, meaning) VALUES ('rejected', 'Rejected.');
INSERT INTO vocab_case_state(value, meaning) VALUES ('resolved', 'Resolved.');
INSERT INTO vocab_case_state(value, meaning) VALUES ('submitted', 'Case submitted.');
INSERT INTO vocab_case_state(value, meaning) VALUES ('under-review', 'Under review.');
CREATE TABLE vocab_classification (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_classification(value, meaning) VALUES ('government-internal', 'Internal government/operator use.');
INSERT INTO vocab_classification(value, meaning) VALUES ('highly-restricted', 'Identity/security-sensitive data.');
INSERT INTO vocab_classification(value, meaning) VALUES ('public', 'Approved public data.');
INSERT INTO vocab_classification(value, meaning) VALUES ('public-after-release', 'Internal until published through release.');
INSERT INTO vocab_classification(value, meaning) VALUES ('restricted', 'Sensitive operational/evidence/location data.');
INSERT INTO vocab_classification(value, meaning) VALUES ('security-internal', 'Security/session credential data.');
CREATE TABLE vocab_correction_type (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_correction_type(value, meaning) VALUES ('administrative-context', 'Admin/locality context correction.');
INSERT INTO vocab_correction_type(value, meaning) VALUES ('classification', 'Classification/visibility correction.');
INSERT INTO vocab_correction_type(value, meaning) VALUES ('duplicate', 'Duplicate/merge correction.');
INSERT INTO vocab_correction_type(value, meaning) VALUES ('geometry', 'Geometry correction.');
INSERT INTO vocab_correction_type(value, meaning) VALUES ('label', 'Label/name correction.');
CREATE TABLE vocab_country_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_country_lifecycle(value, meaning) VALUES ('active', 'Active country authority row.');
INSERT INTO vocab_country_lifecycle(value, meaning) VALUES ('retired', 'Retired historical country row.');
CREATE TABLE vocab_coverage_role (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_coverage_role(value, meaning) VALUES ('context', 'Context only.');
INSERT INTO vocab_coverage_role(value, meaning) VALUES ('excluded', 'Explicitly excluded area.');
INSERT INTO vocab_coverage_role(value, meaning) VALUES ('partial', 'Partially covered unit.');
INSERT INTO vocab_coverage_role(value, meaning) VALUES ('primary', 'Primary covered unit.');
CREATE TABLE vocab_decision_type (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_decision_type(value, meaning) VALUES ('approve-geometry', 'Approve geometry version.');
INSERT INTO vocab_decision_type(value, meaning) VALUES ('approve-publication', 'Approve release.');
INSERT INTO vocab_decision_type(value, meaning) VALUES ('correct-record', 'Apply correction.');
INSERT INTO vocab_decision_type(value, meaning) VALUES ('promote-record', 'Promote candidate to canonical.');
INSERT INTO vocab_decision_type(value, meaning) VALUES ('resolve-dispute', 'Resolve dispute.');
INSERT INTO vocab_decision_type(value, meaning) VALUES ('supersede-record', 'Supersede record/version.');
INSERT INTO vocab_decision_type(value, meaning) VALUES ('withdraw-publication', 'Withdraw release.');
CREATE TABLE vocab_delete_policy (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_delete_policy(value, meaning) VALUES ('cascade-prohibited', 'Reject delete while dependent links exist.');
INSERT INTO vocab_delete_policy(value, meaning) VALUES ('merge-required', 'Merge/supersession required before retirement.');
INSERT INTO vocab_delete_policy(value, meaning) VALUES ('retire-only', 'Do not hard delete; retire and preserve links.');
CREATE TABLE vocab_dispute_type (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_dispute_type(value, meaning) VALUES ('authority', 'Authority/source dispute.');
INSERT INTO vocab_dispute_type(value, meaning) VALUES ('duplicate', 'Duplicate/supersession dispute.');
INSERT INTO vocab_dispute_type(value, meaning) VALUES ('geometry', 'Geometry dispute.');
INSERT INTO vocab_dispute_type(value, meaning) VALUES ('name', 'Name/label dispute.');
INSERT INTO vocab_dispute_type(value, meaning) VALUES ('publication', 'Publication/projection dispute.');
CREATE TABLE vocab_entrance_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_entrance_lifecycle(value, meaning) VALUES ('active', 'Active entrance.');
INSERT INTO vocab_entrance_lifecycle(value, meaning) VALUES ('candidate', 'Candidate entrance.');
INSERT INTO vocab_entrance_lifecycle(value, meaning) VALUES ('retired', 'Retired entrance.');
INSERT INTO vocab_entrance_lifecycle(value, meaning) VALUES ('revoked', 'Revoked entrance.');
CREATE TABLE vocab_entrance_role (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_entrance_role(value, meaning) VALUES ('emergency', 'Emergency entrance.');
INSERT INTO vocab_entrance_role(value, meaning) VALUES ('gate', 'Compound/gate access.');
INSERT INTO vocab_entrance_role(value, meaning) VALUES ('main', 'Main entrance.');
INSERT INTO vocab_entrance_role(value, meaning) VALUES ('secondary', 'Secondary entrance.');
INSERT INTO vocab_entrance_role(value, meaning) VALUES ('service', 'Service entrance.');
CREATE TABLE vocab_field_verification_state (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_field_verification_state(value, meaning) VALUES ('assigned', 'Assigned to field team.');
INSERT INTO vocab_field_verification_state(value, meaning) VALUES ('cancelled', 'Cancelled.');
INSERT INTO vocab_field_verification_state(value, meaning) VALUES ('evidence-approved', 'Approved as evidence.');
INSERT INTO vocab_field_verification_state(value, meaning) VALUES ('evidence-rejected', 'Rejected evidence.');
INSERT INTO vocab_field_verification_state(value, meaning) VALUES ('evidence-under-review', 'Supervisor review.');
INSERT INTO vocab_field_verification_state(value, meaning) VALUES ('field-captured', 'Evidence captured.');
INSERT INTO vocab_field_verification_state(value, meaning) VALUES ('in-progress', 'Capture in progress.');
INSERT INTO vocab_field_verification_state(value, meaning) VALUES ('linked-to-canonical', 'Linked to canonical record.');
INSERT INTO vocab_field_verification_state(value, meaning) VALUES ('needs-recapture', 'Recapture required.');
CREATE TABLE vocab_geometry_quality_state (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_geometry_quality_state(value, meaning) VALUES ('accepted-canonical', 'Approved canonical geometry.');
INSERT INTO vocab_geometry_quality_state(value, meaning) VALUES ('disputed', 'Dispute unresolved.');
INSERT INTO vocab_geometry_quality_state(value, meaning) VALUES ('observed', 'Raw observation captured.');
INSERT INTO vocab_geometry_quality_state(value, meaning) VALUES ('quality-checked', 'Automated checks passed or recorded.');
INSERT INTO vocab_geometry_quality_state(value, meaning) VALUES ('rejected', 'Rejected for canonical use.');
INSERT INTO vocab_geometry_quality_state(value, meaning) VALUES ('reviewed', 'Human/system authority reviewed.');
INSERT INTO vocab_geometry_quality_state(value, meaning) VALUES ('superseded', 'Replaced by newer geometry version.');
INSERT INTO vocab_geometry_quality_state(value, meaning) VALUES ('valid-with-warning', 'Approved with documented warning.');
CREATE TABLE vocab_geometry_role (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_geometry_role(value, meaning) VALUES ('admin-boundary', 'Administrative polygon/multipolygon.');
INSERT INTO vocab_geometry_role(value, meaning) VALUES ('building-footprint', 'Building polygon/multipolygon.');
INSERT INTO vocab_geometry_role(value, meaning) VALUES ('building-point', 'Building representative point.');
INSERT INTO vocab_geometry_role(value, meaning) VALUES ('entrance-point', 'Entrance/access point.');
INSERT INTO vocab_geometry_role(value, meaning) VALUES ('landmark-area', 'Landmark polygon/multipolygon.');
INSERT INTO vocab_geometry_role(value, meaning) VALUES ('landmark-point', 'Landmark point.');
INSERT INTO vocab_geometry_role(value, meaning) VALUES ('location-point', 'Address/location point.');
INSERT INTO vocab_geometry_role(value, meaning) VALUES ('operational-boundary', 'Operational area polygon/multipolygon.');
INSERT INTO vocab_geometry_role(value, meaning) VALUES ('parcel-boundary', 'External parcel polygon when authorized.');
INSERT INTO vocab_geometry_role(value, meaning) VALUES ('road-centerline', 'Road or segment line/multiline.');
CREATE TABLE vocab_intake_state (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_intake_state(value, meaning) VALUES ('closed', 'Closed without promotion.');
INSERT INTO vocab_intake_state(value, meaning) VALUES ('duplicate-review', 'Possible duplicate.');
INSERT INTO vocab_intake_state(value, meaning) VALUES ('needs-field-check', 'Needs field verification.');
INSERT INTO vocab_intake_state(value, meaning) VALUES ('promoted-to-canonical', 'Promoted to canonical record.');
INSERT INTO vocab_intake_state(value, meaning) VALUES ('rejected', 'Rejected.');
INSERT INTO vocab_intake_state(value, meaning) VALUES ('submitted', 'Submitted by citizen/operator/import.');
INSERT INTO vocab_intake_state(value, meaning) VALUES ('under-review', 'Under review.');
CREATE TABLE vocab_landmark_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_landmark_lifecycle(value, meaning) VALUES ('candidate', 'Candidate landmark.');
INSERT INTO vocab_landmark_lifecycle(value, meaning) VALUES ('official', 'Official landmark.');
INSERT INTO vocab_landmark_lifecycle(value, meaning) VALUES ('retired', 'Retired landmark.');
INSERT INTO vocab_landmark_lifecycle(value, meaning) VALUES ('revoked', 'Revoked landmark.');
CREATE TABLE vocab_landmark_type (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_landmark_type(value, meaning) VALUES ('clinic', 'Clinic/health point.');
INSERT INTO vocab_landmark_type(value, meaning) VALUES ('market', 'Market.');
INSERT INTO vocab_landmark_type(value, meaning) VALUES ('natural-feature', 'Natural feature.');
INSERT INTO vocab_landmark_type(value, meaning) VALUES ('other', 'Other approved landmark.');
INSERT INTO vocab_landmark_type(value, meaning) VALUES ('public-office', 'Public office.');
INSERT INTO vocab_landmark_type(value, meaning) VALUES ('religious-site', 'Religious site.');
INSERT INTO vocab_landmark_type(value, meaning) VALUES ('school', 'School.');
CREATE TABLE vocab_lifecycle_state (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_lifecycle_state(value, meaning) VALUES ('active', 'Current active canonical state.');
INSERT INTO vocab_lifecycle_state(value, meaning) VALUES ('corrected', 'Corrected by later version.');
INSERT INTO vocab_lifecycle_state(value, meaning) VALUES ('disputed', 'Subject to unresolved dispute.');
INSERT INTO vocab_lifecycle_state(value, meaning) VALUES ('draft-candidate', 'Candidate not yet under authority review.');
INSERT INTO vocab_lifecycle_state(value, meaning) VALUES ('registry-ready', 'Approved for internal registry use only.');
INSERT INTO vocab_lifecycle_state(value, meaning) VALUES ('registry-review', 'Under registry review.');
INSERT INTO vocab_lifecycle_state(value, meaning) VALUES ('retired', 'No longer valid for current use.');
INSERT INTO vocab_lifecycle_state(value, meaning) VALUES ('revoked', 'Invalidated by authority.');
INSERT INTO vocab_lifecycle_state(value, meaning) VALUES ('superseded', 'Replaced by successor record or version.');
CREATE TABLE vocab_locality_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_locality_lifecycle(value, meaning) VALUES ('candidate', 'Candidate locality.');
INSERT INTO vocab_locality_lifecycle(value, meaning) VALUES ('official', 'Official locality.');
INSERT INTO vocab_locality_lifecycle(value, meaning) VALUES ('renamed', 'Renamed locality.');
INSERT INTO vocab_locality_lifecycle(value, meaning) VALUES ('retired', 'Retired locality.');
CREATE TABLE vocab_locality_type (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_locality_type(value, meaning) VALUES ('informal_area', 'Recognized operational/local context pending authority.');
INSERT INTO vocab_locality_type(value, meaning) VALUES ('neighbourhood', 'Neighbourhood not necessarily legal hierarchy.');
INSERT INTO vocab_locality_type(value, meaning) VALUES ('quarter', 'Urban quarter/barrio.');
INSERT INTO vocab_locality_type(value, meaning) VALUES ('settlement', 'Settlement/locality context.');
INSERT INTO vocab_locality_type(value, meaning) VALUES ('village', 'Village/local reference.');
CREATE TABLE vocab_name_kind (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_name_kind(value, meaning) VALUES ('alternate', 'Alternate known spelling/name.');
INSERT INTO vocab_name_kind(value, meaning) VALUES ('historical', 'Former name retained for history.');
INSERT INTO vocab_name_kind(value, meaning) VALUES ('local', 'Local/community name.');
INSERT INTO vocab_name_kind(value, meaning) VALUES ('normalized-search', 'Search-only normalized value, not authoritative display.');
INSERT INTO vocab_name_kind(value, meaning) VALUES ('official-en', 'Approved English presentation.');
INSERT INTO vocab_name_kind(value, meaning) VALUES ('official-es', 'Official Spanish written form.');
CREATE TABLE vocab_name_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_name_lifecycle(value, meaning) VALUES ('alternate', 'Alternate.');
INSERT INTO vocab_name_lifecycle(value, meaning) VALUES ('candidate', 'Candidate.');
INSERT INTO vocab_name_lifecycle(value, meaning) VALUES ('disputed', 'Disputed.');
INSERT INTO vocab_name_lifecycle(value, meaning) VALUES ('official-current', 'Current official.');
INSERT INTO vocab_name_lifecycle(value, meaning) VALUES ('official-historical', 'Historical official.');
INSERT INTO vocab_name_lifecycle(value, meaning) VALUES ('rejected', 'Rejected.');
INSERT INTO vocab_name_lifecycle(value, meaning) VALUES ('retired', 'Retired.');
CREATE TABLE vocab_name_status (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_name_status(value, meaning) VALUES ('alternate', 'Allowed alternate display/search name.');
INSERT INTO vocab_name_status(value, meaning) VALUES ('candidate', 'Suggested name.');
INSERT INTO vocab_name_status(value, meaning) VALUES ('disputed', 'Name dispute unresolved.');
INSERT INTO vocab_name_status(value, meaning) VALUES ('official-current', 'Current approved name.');
INSERT INTO vocab_name_status(value, meaning) VALUES ('official-historical', 'Previously approved name.');
INSERT INTO vocab_name_status(value, meaning) VALUES ('rejected', 'Rejected candidate.');
INSERT INTO vocab_name_status(value, meaning) VALUES ('retired', 'No longer used.');
INSERT INTO vocab_name_status(value, meaning) VALUES ('under-review', 'Name under review.');
CREATE TABLE vocab_non_building_object_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_non_building_object_lifecycle(value, meaning) VALUES ('active', 'Active object.');
INSERT INTO vocab_non_building_object_lifecycle(value, meaning) VALUES ('candidate', 'Candidate object.');
INSERT INTO vocab_non_building_object_lifecycle(value, meaning) VALUES ('retired', 'Retired object.');
INSERT INTO vocab_non_building_object_lifecycle(value, meaning) VALUES ('revoked', 'Revoked object.');
CREATE TABLE vocab_non_building_object_type (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_non_building_object_type(value, meaning) VALUES ('delivery-point', 'Delivery point.');
INSERT INTO vocab_non_building_object_type(value, meaning) VALUES ('infrastructure-node', 'Infrastructure node.');
INSERT INTO vocab_non_building_object_type(value, meaning) VALUES ('other', 'Other approved object.');
INSERT INTO vocab_non_building_object_type(value, meaning) VALUES ('public-space', 'Public space.');
INSERT INTO vocab_non_building_object_type(value, meaning) VALUES ('utility-asset', 'Utility asset.');
CREATE TABLE vocab_object_role (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_object_role(value, meaning) VALUES ('access-point', 'Access/entrance object.');
INSERT INTO vocab_object_role(value, meaning) VALUES ('context-locality', 'Locality context.');
INSERT INTO vocab_object_role(value, meaning) VALUES ('context-road', 'Road/segment context.');
INSERT INTO vocab_object_role(value, meaning) VALUES ('external-parcel-reference', 'Optional external parcel context.');
INSERT INTO vocab_object_role(value, meaning) VALUES ('nearby-landmark', 'Landmark used for description.');
INSERT INTO vocab_object_role(value, meaning) VALUES ('parent-building', 'Parent building for unit.');
INSERT INTO vocab_object_role(value, meaning) VALUES ('primary-subject', 'Main object represented by the record version.');
CREATE TABLE vocab_operational_area_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_operational_area_lifecycle(value, meaning) VALUES ('active', 'Active.');
INSERT INTO vocab_operational_area_lifecycle(value, meaning) VALUES ('archived', 'Archived.');
INSERT INTO vocab_operational_area_lifecycle(value, meaning) VALUES ('closed', 'Closed.');
INSERT INTO vocab_operational_area_lifecycle(value, meaning) VALUES ('planned', 'Planned.');
INSERT INTO vocab_operational_area_lifecycle(value, meaning) VALUES ('suspended', 'Suspended.');
CREATE TABLE vocab_operational_area_type (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_operational_area_type(value, meaning) VALUES ('campaign', 'Field campaign area.');
INSERT INTO vocab_operational_area_type(value, meaning) VALUES ('incident', 'Temporary incident/project zone.');
INSERT INTO vocab_operational_area_type(value, meaning) VALUES ('rollout', 'Rollout sequence area.');
INSERT INTO vocab_operational_area_type(value, meaning) VALUES ('routing', 'Intake routing area.');
INSERT INTO vocab_operational_area_type(value, meaning) VALUES ('service', 'Service coverage area.');
CREATE TABLE vocab_projection_type (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_projection_type(value, meaning) VALUES ('operator-case-file', 'Protected operator case file.');
INSERT INTO vocab_projection_type(value, meaning) VALUES ('partner-api', 'Partner-scoped API projection.');
INSERT INTO vocab_projection_type(value, meaning) VALUES ('public-lookup', 'Public lookup/proof.');
INSERT INTO vocab_projection_type(value, meaning) VALUES ('signage-export', 'Signage/export projection.');
INSERT INTO vocab_projection_type(value, meaning) VALUES ('statistics', 'Aggregated/statistical projection.');
CREATE TABLE vocab_public_code_state (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_public_code_state(value, meaning) VALUES ('active-public', 'Currently released public code.');
INSERT INTO vocab_public_code_state(value, meaning) VALUES ('blocked', 'Reserved to prevent future use.');
INSERT INTO vocab_public_code_state(value, meaning) VALUES ('reserved-internal', 'Reserved but not public.');
INSERT INTO vocab_public_code_state(value, meaning) VALUES ('retired', 'No longer assigned to current records.');
INSERT INTO vocab_public_code_state(value, meaning) VALUES ('revoked', 'Invalidated by authority.');
INSERT INTO vocab_public_code_state(value, meaning) VALUES ('superseded', 'Replaced by a successor alias.');
CREATE TABLE vocab_publication_item_state (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_publication_item_state(value, meaning) VALUES ('included', 'Included in release manifest.');
INSERT INTO vocab_publication_item_state(value, meaning) VALUES ('redacted', 'Included with redaction.');
INSERT INTO vocab_publication_item_state(value, meaning) VALUES ('superseded', 'Replaced by later release item.');
INSERT INTO vocab_publication_item_state(value, meaning) VALUES ('withdrawn', 'Removed from public/partner projection.');
CREATE TABLE vocab_publication_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_publication_lifecycle(value, meaning) VALUES ('approval-requested', 'Submitted for authority approval.');
INSERT INTO vocab_publication_lifecycle(value, meaning) VALUES ('approved', 'Approved for release but not yet published.');
INSERT INTO vocab_publication_lifecycle(value, meaning) VALUES ('draft', 'Release being prepared.');
INSERT INTO vocab_publication_lifecycle(value, meaning) VALUES ('published', 'Published to named audience.');
INSERT INTO vocab_publication_lifecycle(value, meaning) VALUES ('suspended', 'Temporarily hidden or restricted.');
INSERT INTO vocab_publication_lifecycle(value, meaning) VALUES ('withdrawn', 'Release withdrawn by authority.');
CREATE TABLE vocab_publication_release_state (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_publication_release_state(value, meaning) VALUES ('approval-requested', 'Submitted for authority approval.');
INSERT INTO vocab_publication_release_state(value, meaning) VALUES ('approved', 'Approved for release but not yet published.');
INSERT INTO vocab_publication_release_state(value, meaning) VALUES ('draft', 'Release being prepared.');
INSERT INTO vocab_publication_release_state(value, meaning) VALUES ('published', 'Published to named audience.');
INSERT INTO vocab_publication_release_state(value, meaning) VALUES ('suspended', 'Temporarily hidden or restricted.');
INSERT INTO vocab_publication_release_state(value, meaning) VALUES ('withdrawn', 'Release withdrawn by authority.');
CREATE TABLE vocab_quality_check_result (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_quality_check_result(value, meaning) VALUES ('failed', 'Check failed.');
INSERT INTO vocab_quality_check_result(value, meaning) VALUES ('not-applicable', 'Check not applicable.');
INSERT INTO vocab_quality_check_result(value, meaning) VALUES ('passed', 'Check passed.');
INSERT INTO vocab_quality_check_result(value, meaning) VALUES ('passed-with-warning', 'Check passed with warning.');
CREATE TABLE vocab_record_type (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_record_type(value, meaning) VALUES ('address', 'Address/location record with public/protected lookup purpose.');
INSERT INTO vocab_record_type(value, meaning) VALUES ('building', 'Building-level canonical location.');
INSERT INTO vocab_record_type(value, meaning) VALUES ('entrance', 'Separately addressable entrance/access point.');
INSERT INTO vocab_record_type(value, meaning) VALUES ('landmark', 'Landmark-based location.');
INSERT INTO vocab_record_type(value, meaning) VALUES ('non-building-object', 'Other authorized addressable object.');
INSERT INTO vocab_record_type(value, meaning) VALUES ('service-location', 'Service/delivery location not tied to building.');
INSERT INTO vocab_record_type(value, meaning) VALUES ('unit', 'Separately addressable unit/sub-address.');
CREATE TABLE vocab_reference_object_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_reference_object_lifecycle(value, meaning) VALUES ('active', 'Active object.');
INSERT INTO vocab_reference_object_lifecycle(value, meaning) VALUES ('candidate', 'Candidate reference object.');
INSERT INTO vocab_reference_object_lifecycle(value, meaning) VALUES ('corrected', 'Corrected by later object version.');
INSERT INTO vocab_reference_object_lifecycle(value, meaning) VALUES ('retired', 'Retired.');
INSERT INTO vocab_reference_object_lifecycle(value, meaning) VALUES ('revoked', 'Revoked.');
INSERT INTO vocab_reference_object_lifecycle(value, meaning) VALUES ('superseded', 'Superseded.');
CREATE TABLE vocab_relationship_type (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_relationship_type(value, meaning) VALUES ('contains', 'Container relationship.');
INSERT INTO vocab_relationship_type(value, meaning) VALUES ('corrects', 'Record/version corrects another.');
INSERT INTO vocab_relationship_type(value, meaning) VALUES ('duplicates', 'Potential/confirmed duplicate.');
INSERT INTO vocab_relationship_type(value, meaning) VALUES ('near', 'Nearby/context relationship.');
INSERT INTO vocab_relationship_type(value, meaning) VALUES ('served-by', 'Service/access relationship.');
INSERT INTO vocab_relationship_type(value, meaning) VALUES ('supersedes', 'Record replaces another.');
CREATE TABLE vocab_retention_state (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_retention_state(value, meaning) VALUES ('active', 'Retained for active use.');
INSERT INTO vocab_retention_state(value, meaning) VALUES ('disposed-metadata-retained', 'Object disposed, metadata retained.');
INSERT INTO vocab_retention_state(value, meaning) VALUES ('legal-hold', 'Held by legal/audit requirement.');
INSERT INTO vocab_retention_state(value, meaning) VALUES ('scheduled-disposal', 'Scheduled for disposal after approval.');
CREATE TABLE vocab_road_class (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_road_class(value, meaning) VALUES ('path', 'Pedestrian or local path.');
INSERT INTO vocab_road_class(value, meaning) VALUES ('road', 'General road.');
INSERT INTO vocab_road_class(value, meaning) VALUES ('service-road', 'Service/access road.');
INSERT INTO vocab_road_class(value, meaning) VALUES ('street', 'Urban street.');
INSERT INTO vocab_road_class(value, meaning) VALUES ('track', 'Track/unpaved access.');
INSERT INTO vocab_road_class(value, meaning) VALUES ('unknown', 'Unknown class pending validation.');
CREATE TABLE vocab_road_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_road_lifecycle(value, meaning) VALUES ('candidate', 'Candidate road.');
INSERT INTO vocab_road_lifecycle(value, meaning) VALUES ('field-verified', 'Field verified road.');
INSERT INTO vocab_road_lifecycle(value, meaning) VALUES ('official', 'Official road.');
INSERT INTO vocab_road_lifecycle(value, meaning) VALUES ('retired', 'Retired road.');
INSERT INTO vocab_road_lifecycle(value, meaning) VALUES ('superseded', 'Superseded road.');
CREATE TABLE vocab_road_segment_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_road_segment_lifecycle(value, meaning) VALUES ('active', 'Active segment.');
INSERT INTO vocab_road_segment_lifecycle(value, meaning) VALUES ('draft', 'Draft segment.');
INSERT INTO vocab_road_segment_lifecycle(value, meaning) VALUES ('realigned', 'Realigned segment.');
INSERT INTO vocab_road_segment_lifecycle(value, meaning) VALUES ('retired', 'Retired segment.');
CREATE TABLE vocab_source_authority_class (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_source_authority_class(value, meaning) VALUES ('citizen-submitted', 'Citizen submission.');
INSERT INTO vocab_source_authority_class(value, meaning) VALUES ('derived-system', 'System-derived value.');
INSERT INTO vocab_source_authority_class(value, meaning) VALUES ('external-map-suggestion', 'External map/geocoder suggestion.');
INSERT INTO vocab_source_authority_class(value, meaning) VALUES ('fixture-training', 'Fixture/training data.');
INSERT INTO vocab_source_authority_class(value, meaning) VALUES ('gis-data-authority', 'GIS/data steward.');
INSERT INTO vocab_source_authority_class(value, meaning) VALUES ('imported-provisional', 'Imported provisional source.');
INSERT INTO vocab_source_authority_class(value, meaning) VALUES ('official-government', 'Official government source.');
INSERT INTO vocab_source_authority_class(value, meaning) VALUES ('registry-authority', 'Registry decision.');
INSERT INTO vocab_source_authority_class(value, meaning) VALUES ('unverified-field', 'Unverified field observation.');
INSERT INTO vocab_source_authority_class(value, meaning) VALUES ('verified-field', 'Verified field observation.');
CREATE TABLE vocab_source_authority_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_source_authority_lifecycle(value, meaning) VALUES ('candidate', 'Candidate source.');
INSERT INTO vocab_source_authority_lifecycle(value, meaning) VALUES ('deprecated', 'Deprecated source.');
INSERT INTO vocab_source_authority_lifecycle(value, meaning) VALUES ('revoked', 'Revoked source.');
INSERT INTO vocab_source_authority_lifecycle(value, meaning) VALUES ('trusted', 'Trusted source.');
CREATE TABLE vocab_subject_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_subject_lifecycle(value, meaning) VALUES ('active', 'Subject can receive links.');
INSERT INTO vocab_subject_lifecycle(value, meaning) VALUES ('deleted-prohibited', 'Delete attempted but policy requires retirement.');
INSERT INTO vocab_subject_lifecycle(value, meaning) VALUES ('merged', 'Subject merged into successor.');
INSERT INTO vocab_subject_lifecycle(value, meaning) VALUES ('retired', 'Subject retained but not assignable.');
CREATE TABLE vocab_unit_lifecycle (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_unit_lifecycle(value, meaning) VALUES ('active', 'Active unit.');
INSERT INTO vocab_unit_lifecycle(value, meaning) VALUES ('candidate', 'Candidate unit.');
INSERT INTO vocab_unit_lifecycle(value, meaning) VALUES ('merged', 'Merged unit.');
INSERT INTO vocab_unit_lifecycle(value, meaning) VALUES ('retired', 'Retired unit.');
INSERT INTO vocab_unit_lifecycle(value, meaning) VALUES ('split', 'Split unit.');
CREATE TABLE vocab_unit_type (value text PRIMARY KEY, meaning text NOT NULL);
INSERT INTO vocab_unit_type(value, meaning) VALUES ('apartment', 'Apartment/flat.');
INSERT INTO vocab_unit_type(value, meaning) VALUES ('compound-unit', 'Compound/yard unit.');
INSERT INTO vocab_unit_type(value, meaning) VALUES ('office-suite', 'Office suite.');
INSERT INTO vocab_unit_type(value, meaning) VALUES ('room', 'Room-level unit.');
INSERT INTO vocab_unit_type(value, meaning) VALUES ('shop-unit', 'Shop/commercial unit.');
CREATE TABLE proposed_administrative_code_history (
  admin_code_history_id text NOT NULL,
  administrative_unit_id text NOT NULL,
  code_scheme text NOT NULL DEFAULT 'national-admin-code',
  official_code text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  recorded_from timestamptz NOT NULL DEFAULT now(),
  recorded_to timestamptz,
  source_id text NOT NULL,
  CONSTRAINT proposed_administrative_code_history_pk PRIMARY KEY (admin_code_history_id)
);
CREATE TABLE proposed_administrative_unit (
  administrative_unit_id text NOT NULL,
  country_id text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  retired_at timestamptz,
  CONSTRAINT proposed_administrative_unit_pk PRIMARY KEY (administrative_unit_id)
);
CREATE TABLE proposed_administrative_unit_version (
  administrative_unit_version_id text NOT NULL,
  administrative_unit_id text NOT NULL,
  parent_administrative_unit_id text,
  admin_level text NOT NULL,
  lifecycle_state text NOT NULL DEFAULT 'active',
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  recorded_to timestamptz,
  source_authority_id text NOT NULL,
  classification text NOT NULL DEFAULT 'public-after-release',
  CONSTRAINT proposed_administrative_unit_version_pk PRIMARY KEY (administrative_unit_version_id)
);
CREATE TABLE proposed_building (
  building_id text NOT NULL,
  usage_class text,
  lifecycle_state text NOT NULL,
  source_authority_id text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_building_pk PRIMARY KEY (building_id)
);
CREATE TABLE proposed_building_primary_entrance (
  building_primary_entrance_id text NOT NULL,
  building_id text NOT NULL,
  entrance_id text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_building_primary_entrance_pk PRIMARY KEY (building_primary_entrance_id)
);
CREATE TABLE proposed_correction_case (
  correction_case_id text NOT NULL,
  target_location_record_id text,
  target_public_code text,
  correction_type text NOT NULL,
  case_state text NOT NULL,
  submitted_at timestamptz NOT NULL,
  resolved_at timestamptz,
  resolution_event_id text,
  CONSTRAINT proposed_correction_case_pk PRIMARY KEY (correction_case_id)
);
CREATE TABLE proposed_country (
  country_id text NOT NULL,
  iso2_code char(2) NOT NULL,
  official_name_es text NOT NULL,
  official_name_en text NOT NULL,
  lifecycle_state text NOT NULL DEFAULT 'active',
  source_authority_id text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT proposed_country_pk PRIMARY KEY (country_id)
);
CREATE TABLE proposed_decision_event (
  decision_event_id text NOT NULL,
  decision_type text NOT NULL,
  actor_id text NOT NULL,
  authority_id text NOT NULL,
  reason_code text NOT NULL,
  details_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  effective_at timestamptz NOT NULL,
  recorded_at timestamptz NOT NULL,
  decision_outcome text NOT NULL,
  CONSTRAINT proposed_decision_event_pk PRIMARY KEY (decision_event_id)
);
CREATE TABLE proposed_dispute_case (
  dispute_case_id text NOT NULL,
  dispute_type text NOT NULL,
  case_state text NOT NULL,
  opened_at timestamptz NOT NULL,
  resolved_at timestamptz,
  resolution_event_id text,
  subject_id text NOT NULL,
  CONSTRAINT proposed_dispute_case_pk PRIMARY KEY (dispute_case_id)
);
CREATE TABLE proposed_entrance (
  entrance_id text NOT NULL,
  building_id text NOT NULL,
  entrance_role text NOT NULL DEFAULT 'access-point',
  lifecycle_state text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_entrance_pk PRIMARY KEY (entrance_id)
);
CREATE TABLE proposed_evidence_object (
  evidence_object_id text NOT NULL,
  source_record_id text NOT NULL,
  storage_uri text NOT NULL,
  content_hash text NOT NULL,
  media_type text NOT NULL,
  classification text NOT NULL,
  captured_at timestamptz,
  retention_state text NOT NULL,
  CONSTRAINT proposed_evidence_object_pk PRIMARY KEY (evidence_object_id)
);
CREATE TABLE proposed_field_assignment (
  assignment_id text NOT NULL,
  operational_area_id text NOT NULL,
  task_type text NOT NULL,
  team text NOT NULL,
  priority text NOT NULL,
  assignment_state text NOT NULL,
  created_at timestamptz NOT NULL,
  closed_at timestamptz,
  CONSTRAINT proposed_field_assignment_pk PRIMARY KEY (assignment_id)
);
CREATE TABLE proposed_field_observation (
  field_observation_id text NOT NULL,
  intake_case_id text,
  assignment_id text,
  observation_type text NOT NULL,
  verification_state text NOT NULL,
  source_record_id text NOT NULL,
  geometry_observation_id text,
  notes_classification text NOT NULL,
  recorded_at timestamptz NOT NULL,
  CONSTRAINT proposed_field_observation_pk PRIMARY KEY (field_observation_id)
);
CREATE TABLE proposed_geometry_observation (
  geometry_observation_id text NOT NULL,
  observed_geom geometry(geometry,4326) NOT NULL,
  geometry_role text NOT NULL,
  capture_method text NOT NULL,
  horizontal_accuracy_m numeric(10,2),
  source_record_id text NOT NULL,
  evidence_object_id text,
  licence_id text,
  observed_at timestamptz NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  classification text NOT NULL DEFAULT 'restricted',
  subject_id text NOT NULL,
  CONSTRAINT proposed_geometry_observation_pk PRIMARY KEY (geometry_observation_id)
);
CREATE TABLE proposed_geometry_quality_assessment (
  quality_assessment_id text NOT NULL,
  geometry_version_id text NOT NULL,
  check_name text NOT NULL,
  check_result text NOT NULL,
  tolerance_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  measured_value_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  assessed_at timestamptz NOT NULL,
  assessed_by_actor_id text NOT NULL,
  CONSTRAINT proposed_geometry_quality_assessment_pk PRIMARY KEY (quality_assessment_id)
);
CREATE TABLE proposed_geometry_transformation (
  transformation_id text NOT NULL,
  source_crs text NOT NULL,
  target_crs text NOT NULL,
  algorithm text NOT NULL,
  algorithm_version text NOT NULL,
  parameters_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  performed_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT proposed_geometry_transformation_pk PRIMARY KEY (transformation_id)
);
CREATE TABLE proposed_geometry_version (
  geometry_version_id text NOT NULL,
  subject_id text NOT NULL,
  geometry_role text NOT NULL,
  geom geometry(geometry,4326) NOT NULL,
  source_observation_id text NOT NULL,
  transformation_id text,
  validation_method text NOT NULL,
  validated_by_actor_id text NOT NULL,
  quality_state text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  recorded_to timestamptz,
  superseded_by_geometry_version_id text,
  dispute_case_id text,
  classification text NOT NULL DEFAULT 'restricted',
  promotion_decision_event_id text NOT NULL,
  promotion_evidence_object_id text NOT NULL,
  promotion_authority_scope text NOT NULL,
  CONSTRAINT proposed_geometry_version_pk PRIMARY KEY (geometry_version_id)
);
CREATE TABLE proposed_intake_case (
  intake_case_id text NOT NULL,
  source_record_id text NOT NULL,
  submitted_label text NOT NULL,
  intake_state text NOT NULL,
  provisional_code text,
  created_at timestamptz NOT NULL,
  closed_at timestamptz,
  CONSTRAINT proposed_intake_case_pk PRIMARY KEY (intake_case_id)
);
CREATE TABLE proposed_landmark (
  landmark_id text NOT NULL,
  landmark_type text NOT NULL DEFAULT 'landmark',
  lifecycle_state text NOT NULL,
  source_authority_id text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_landmark_pk PRIMARY KEY (landmark_id)
);
CREATE TABLE proposed_legacy_crosswalk (
  legacy_crosswalk_id text NOT NULL,
  source_table text NOT NULL,
  source_field text NOT NULL,
  legacy_id text NOT NULL,
  target_entity text NOT NULL,
  target_id text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT proposed_legacy_crosswalk_pk PRIMARY KEY (legacy_crosswalk_id)
);
CREATE TABLE proposed_licence (
  licence_id text NOT NULL,
  licence_name text NOT NULL,
  licence_uri text,
  usage_restriction text NOT NULL,
  classification text NOT NULL DEFAULT 'government-internal',
  CONSTRAINT proposed_licence_pk PRIMARY KEY (licence_id)
);
CREATE TABLE proposed_locality (
  locality_id text NOT NULL,
  administrative_unit_id text NOT NULL,
  locality_type text NOT NULL,
  lifecycle_state text NOT NULL,
  source_authority_id text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_locality_pk PRIMARY KEY (locality_id)
);
CREATE TABLE proposed_location_record (
  location_record_id text NOT NULL,
  record_type text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  retired_at timestamptz,
  classification text NOT NULL DEFAULT 'government-internal',
  CONSTRAINT proposed_location_record_pk PRIMARY KEY (location_record_id)
);
CREATE TABLE proposed_location_record_assertion (
  assertion_id text NOT NULL,
  location_record_version_id text NOT NULL,
  target_entity text NOT NULL,
  target_field text NOT NULL,
  value_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  source_record_id text NOT NULL,
  evidence_object_id text,
  decision_event_id text NOT NULL,
  classification text NOT NULL,
  CONSTRAINT proposed_location_record_assertion_pk PRIMARY KEY (assertion_id)
);
CREATE TABLE proposed_location_record_object_link (
  link_id text NOT NULL,
  location_record_version_id text NOT NULL,
  object_role text NOT NULL,
  cardinality_rank integer NOT NULL DEFAULT 1,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  subject_id text NOT NULL,
  CONSTRAINT proposed_location_record_object_link_pk PRIMARY KEY (link_id)
);
CREATE TABLE proposed_location_record_relationship (
  relationship_id text NOT NULL,
  from_location_record_id text NOT NULL,
  to_location_record_id text NOT NULL,
  relationship_type text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  source_decision_event_id text NOT NULL,
  CONSTRAINT proposed_location_record_relationship_pk PRIMARY KEY (relationship_id)
);
CREATE TABLE proposed_location_record_version (
  location_record_version_id text NOT NULL,
  location_record_id text NOT NULL,
  version_number integer NOT NULL,
  lifecycle_state text NOT NULL,
  display_label_es text NOT NULL,
  display_label_en text,
  administrative_unit_version_id text NOT NULL,
  locality_id text,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  recorded_to timestamptz,
  predecessor_version_id text,
  successor_version_id text,
  correction_case_id text,
  supersession_reason text,
  source_decision_event_id text NOT NULL,
  CONSTRAINT proposed_location_record_version_pk PRIMARY KEY (location_record_version_id)
);
CREATE TABLE proposed_migration_exception (
  migration_exception_id text NOT NULL,
  batch_id text NOT NULL,
  source_table text NOT NULL,
  source_field text,
  source_key text NOT NULL,
  exception_type text NOT NULL,
  severity text NOT NULL,
  details_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  owner text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  resolved_at timestamptz,
  CONSTRAINT proposed_migration_exception_pk PRIMARY KEY (migration_exception_id)
);
CREATE TABLE proposed_name_record (
  name_record_id text NOT NULL,
  subject_id text NOT NULL,
  language_code text NOT NULL,
  name_kind text NOT NULL,
  name_status text NOT NULL,
  name_text text NOT NULL,
  normalized_text text NOT NULL,
  source_record_id text,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_name_record_pk PRIMARY KEY (name_record_id)
);
CREATE TABLE proposed_non_building_object (
  object_id text NOT NULL,
  object_type text NOT NULL,
  lifecycle_state text NOT NULL,
  source_authority_id text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_non_building_object_pk PRIMARY KEY (object_id)
);
CREATE TABLE proposed_operational_area (
  operational_area_id text NOT NULL,
  area_type text NOT NULL,
  name_record_id text,
  purpose text NOT NULL,
  lifecycle_state text NOT NULL,
  authority_owner text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  classification text NOT NULL DEFAULT 'government-internal',
  CONSTRAINT proposed_operational_area_pk PRIMARY KEY (operational_area_id)
);
CREATE TABLE proposed_operational_area_coverage (
  coverage_id text NOT NULL,
  operational_area_id text NOT NULL,
  administrative_unit_id text,
  geometry_version_id text,
  coverage_role text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_operational_area_coverage_pk PRIMARY KEY (coverage_id)
);
CREATE TABLE proposed_parcel_reference (
  parcel_reference_id text NOT NULL,
  external_parcel_id text NOT NULL,
  source_authority_id text NOT NULL,
  classification text NOT NULL DEFAULT 'restricted',
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_parcel_reference_pk PRIMARY KEY (parcel_reference_id)
);
CREATE TABLE proposed_partner_projection (
  partner_projection_id text NOT NULL,
  publication_release_item_id text NOT NULL,
  partner_scope text NOT NULL,
  response_field_set jsonb NOT NULL DEFAULT '[]'::jsonb,
  classification text NOT NULL,
  expires_at timestamptz,
  CONSTRAINT proposed_partner_projection_pk PRIMARY KEY (partner_projection_id)
);
CREATE TABLE proposed_public_code_alias (
  public_code_alias_id text NOT NULL,
  location_record_id text NOT NULL,
  public_code text NOT NULL,
  code_scheme text NOT NULL DEFAULT 'nli-reserved-v1',
  code_state text NOT NULL,
  reserved_at timestamptz NOT NULL,
  issued_at timestamptz,
  retired_at timestamptz,
  predecessor_alias_id text,
  successor_alias_id text,
  CONSTRAINT proposed_public_code_alias_pk PRIMARY KEY (public_code_alias_id)
);
CREATE TABLE proposed_publication_release (
  publication_release_id text NOT NULL,
  release_state text NOT NULL,
  authority_reference text NOT NULL,
  projection_type text NOT NULL,
  effective_at timestamptz NOT NULL,
  recorded_at timestamptz NOT NULL,
  immutable_manifest_hash text NOT NULL,
  manifest_storage_uri text NOT NULL,
  created_by_actor_id text NOT NULL,
  CONSTRAINT proposed_publication_release_pk PRIMARY KEY (publication_release_id)
);
CREATE TABLE proposed_publication_release_item (
  publication_release_item_id text NOT NULL,
  publication_release_id text NOT NULL,
  location_record_id text NOT NULL,
  location_record_version_id text NOT NULL,
  public_code_alias_id text NOT NULL,
  projection_payload_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  projection_payload_hash text NOT NULL,
  projection_state text NOT NULL,
  published_label text NOT NULL,
  published_geometry_policy text NOT NULL,
  CONSTRAINT proposed_publication_release_item_pk PRIMARY KEY (publication_release_item_id)
);
CREATE TABLE proposed_registry_subject (
  subject_id text NOT NULL,
  subject_entity text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  native_id text NOT NULL,
  subject_state text NOT NULL DEFAULT 'active',
  retired_at timestamptz,
  delete_policy text NOT NULL DEFAULT 'retire-only',
  CONSTRAINT proposed_registry_subject_pk PRIMARY KEY (subject_id)
);
CREATE TABLE proposed_road (
  road_id text NOT NULL,
  road_class text NOT NULL DEFAULT 'unknown',
  lifecycle_state text NOT NULL,
  source_authority_id text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT proposed_road_pk PRIMARY KEY (road_id)
);
CREATE TABLE proposed_road_segment (
  road_segment_id text NOT NULL,
  road_id text NOT NULL,
  sequence_number integer,
  measured_length_m numeric(12,2),
  lifecycle_state text NOT NULL,
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_road_segment_pk PRIMARY KEY (road_segment_id)
);
CREATE TABLE proposed_source_authority (
  source_authority_id text NOT NULL,
  authority_name text NOT NULL,
  authority_class text NOT NULL,
  legal_basis text,
  status text NOT NULL,
  CONSTRAINT proposed_source_authority_pk PRIMARY KEY (source_authority_id)
);
CREATE TABLE proposed_source_package (
  source_package_id text NOT NULL,
  source_authority_id text NOT NULL,
  package_name text NOT NULL,
  package_checksum text NOT NULL,
  licence_id text,
  loaded_at timestamptz NOT NULL,
  load_context jsonb NOT NULL DEFAULT '{}'::jsonb,
  CONSTRAINT proposed_source_package_pk PRIMARY KEY (source_package_id)
);
CREATE TABLE proposed_source_payload_archive (
  archive_id text NOT NULL,
  source_record_id text NOT NULL,
  payload_uri text NOT NULL,
  payload_hash_sha256 text NOT NULL,
  classification text NOT NULL DEFAULT 'restricted',
  retention_state text NOT NULL DEFAULT 'active',
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT proposed_source_payload_archive_pk PRIMARY KEY (archive_id)
);
CREATE TABLE proposed_source_record (
  source_record_id text NOT NULL,
  source_package_id text NOT NULL,
  source_key text NOT NULL,
  raw_payload_hash text NOT NULL,
  raw_payload_classification text NOT NULL,
  recorded_at timestamptz NOT NULL,
  CONSTRAINT proposed_source_record_pk PRIMARY KEY (source_record_id)
);
CREATE TABLE proposed_unit (
  unit_id text NOT NULL,
  building_id text NOT NULL,
  parent_unit_id text,
  unit_label text NOT NULL,
  unit_type text NOT NULL DEFAULT 'unit',
  lifecycle_state text NOT NULL,
  classification text NOT NULL DEFAULT 'government-internal',
  effective_from timestamptz NOT NULL,
  effective_to timestamptz,
  CONSTRAINT proposed_unit_pk PRIMARY KEY (unit_id)
);
ALTER TABLE proposed_administrative_code_history ADD CONSTRAINT proposed_administrative_code_history_administrative_unit_id_fk FOREIGN KEY (administrative_unit_id) REFERENCES proposed_administrative_unit(administrative_unit_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_administrative_code_history ADD CONSTRAINT proposed_administrative_code_history_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_administrative_code_history ADD CONSTRAINT proposed_administrative_code_history_recorded_interval_ck CHECK (recorded_to IS NULL OR recorded_from < recorded_to);
ALTER TABLE proposed_administrative_code_history ADD CONSTRAINT proposed_administrative_code_history_source_id_fk FOREIGN KEY (source_id) REFERENCES proposed_source_record(source_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_administrative_unit ADD CONSTRAINT proposed_administrative_unit_country_id_fk FOREIGN KEY (country_id) REFERENCES proposed_country(country_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_administrative_unit_version ADD CONSTRAINT proposed_administrative_unit_version_administrative_unit_id_fk FOREIGN KEY (administrative_unit_id) REFERENCES proposed_administrative_unit(administrative_unit_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_administrative_unit_version ADD CONSTRAINT proposed_administrative_unit_version_parent_administrative_unit_id_fk FOREIGN KEY (parent_administrative_unit_id) REFERENCES proposed_administrative_unit(administrative_unit_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_administrative_unit_version ADD CONSTRAINT proposed_administrative_unit_version_admin_level_vocab_fk FOREIGN KEY (admin_level) REFERENCES vocab_admin_level(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_administrative_unit_version ADD CONSTRAINT proposed_administrative_unit_version_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_administrative_unit_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_administrative_unit_version ADD CONSTRAINT proposed_administrative_unit_version_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_administrative_unit_version ADD CONSTRAINT proposed_administrative_unit_version_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_administrative_unit_version ADD CONSTRAINT proposed_administrative_unit_version_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_building ADD CONSTRAINT proposed_building_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_building_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_building ADD CONSTRAINT proposed_building_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_building ADD CONSTRAINT proposed_building_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_building_primary_entrance ADD CONSTRAINT proposed_building_primary_entrance_building_id_fk FOREIGN KEY (building_id) REFERENCES proposed_building(building_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_building_primary_entrance ADD CONSTRAINT proposed_building_primary_entrance_entrance_id_fk FOREIGN KEY (entrance_id) REFERENCES proposed_entrance(entrance_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_building_primary_entrance ADD CONSTRAINT proposed_building_primary_entrance_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_correction_case ADD CONSTRAINT proposed_correction_case_target_location_record_id_fk FOREIGN KEY (target_location_record_id) REFERENCES proposed_location_record(location_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_correction_case ADD CONSTRAINT proposed_correction_case_correction_type_vocab_fk FOREIGN KEY (correction_type) REFERENCES vocab_correction_type(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_correction_case ADD CONSTRAINT proposed_correction_case_case_state_vocab_fk FOREIGN KEY (case_state) REFERENCES vocab_case_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_correction_case ADD CONSTRAINT proposed_correction_case_resolution_event_id_fk FOREIGN KEY (resolution_event_id) REFERENCES proposed_decision_event(decision_event_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_country ADD CONSTRAINT proposed_country_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_country_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_country ADD CONSTRAINT proposed_country_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_decision_event ADD CONSTRAINT proposed_decision_event_decision_type_vocab_fk FOREIGN KEY (decision_type) REFERENCES vocab_decision_type(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_decision_event ADD CONSTRAINT proposed_decision_event_authority_id_fk FOREIGN KEY (authority_id) REFERENCES proposed_source_authority(source_authority_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_dispute_case ADD CONSTRAINT proposed_dispute_case_dispute_type_vocab_fk FOREIGN KEY (dispute_type) REFERENCES vocab_dispute_type(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_dispute_case ADD CONSTRAINT proposed_dispute_case_case_state_vocab_fk FOREIGN KEY (case_state) REFERENCES vocab_case_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_dispute_case ADD CONSTRAINT proposed_dispute_case_resolution_event_id_fk FOREIGN KEY (resolution_event_id) REFERENCES proposed_decision_event(decision_event_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_dispute_case ADD CONSTRAINT proposed_dispute_case_subject_id_fk FOREIGN KEY (subject_id) REFERENCES proposed_registry_subject(subject_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_entrance ADD CONSTRAINT proposed_entrance_building_id_fk FOREIGN KEY (building_id) REFERENCES proposed_building(building_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_entrance ADD CONSTRAINT proposed_entrance_entrance_role_vocab_fk FOREIGN KEY (entrance_role) REFERENCES vocab_entrance_role(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_entrance ADD CONSTRAINT proposed_entrance_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_entrance_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_entrance ADD CONSTRAINT proposed_entrance_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_evidence_object ADD CONSTRAINT proposed_evidence_object_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_evidence_object ADD CONSTRAINT proposed_evidence_object_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_evidence_object ADD CONSTRAINT proposed_evidence_object_retention_state_vocab_fk FOREIGN KEY (retention_state) REFERENCES vocab_retention_state(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_field_assignment ADD CONSTRAINT proposed_field_assignment_operational_area_id_fk FOREIGN KEY (operational_area_id) REFERENCES proposed_operational_area(operational_area_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_field_assignment ADD CONSTRAINT proposed_field_assignment_assignment_state_vocab_fk FOREIGN KEY (assignment_state) REFERENCES vocab_field_verification_state(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_field_observation ADD CONSTRAINT proposed_field_observation_intake_case_id_fk FOREIGN KEY (intake_case_id) REFERENCES proposed_intake_case(intake_case_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_field_observation ADD CONSTRAINT proposed_field_observation_assignment_id_fk FOREIGN KEY (assignment_id) REFERENCES proposed_field_assignment(assignment_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_field_observation ADD CONSTRAINT proposed_field_observation_verification_state_vocab_fk FOREIGN KEY (verification_state) REFERENCES vocab_field_verification_state(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_field_observation ADD CONSTRAINT proposed_field_observation_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_field_observation ADD CONSTRAINT proposed_field_observation_geometry_observation_id_fk FOREIGN KEY (geometry_observation_id) REFERENCES proposed_geometry_observation(geometry_observation_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_field_observation ADD CONSTRAINT proposed_field_observation_notes_classification_vocab_fk FOREIGN KEY (notes_classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_observation ADD CONSTRAINT proposed_geometry_observation_observed_geom_valid_ck CHECK (observed_geom IS NULL OR (ST_IsValid(observed_geom) AND ST_SRID(observed_geom) = 4326));
CREATE INDEX proposed_geometry_observation_observed_geom_gist ON proposed_geometry_observation USING GIST (observed_geom);
ALTER TABLE proposed_geometry_observation ADD CONSTRAINT proposed_geometry_observation_geometry_role_vocab_fk FOREIGN KEY (geometry_role) REFERENCES vocab_geometry_role(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_observation ADD CONSTRAINT proposed_geometry_observation_capture_method_vocab_fk FOREIGN KEY (capture_method) REFERENCES vocab_capture_method(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_observation ADD CONSTRAINT proposed_geometry_observation_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_observation ADD CONSTRAINT proposed_geometry_observation_evidence_object_id_fk FOREIGN KEY (evidence_object_id) REFERENCES proposed_evidence_object(evidence_object_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_observation ADD CONSTRAINT proposed_geometry_observation_licence_id_fk FOREIGN KEY (licence_id) REFERENCES proposed_licence(licence_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_observation ADD CONSTRAINT proposed_geometry_observation_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_observation ADD CONSTRAINT proposed_geometry_observation_subject_id_fk FOREIGN KEY (subject_id) REFERENCES proposed_registry_subject(subject_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_quality_assessment ADD CONSTRAINT proposed_geometry_quality_assessment_geometry_version_id_fk FOREIGN KEY (geometry_version_id) REFERENCES proposed_geometry_version(geometry_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_quality_assessment ADD CONSTRAINT proposed_geometry_quality_assessment_check_result_vocab_fk FOREIGN KEY (check_result) REFERENCES vocab_quality_check_result(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_subject_id_fk FOREIGN KEY (subject_id) REFERENCES proposed_registry_subject(subject_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_geometry_role_vocab_fk FOREIGN KEY (geometry_role) REFERENCES vocab_geometry_role(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_geom_valid_ck CHECK (geom IS NULL OR (ST_IsValid(geom) AND ST_SRID(geom) = 4326));
CREATE INDEX proposed_geometry_version_geom_gist ON proposed_geometry_version USING GIST (geom);
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_source_observation_id_fk FOREIGN KEY (source_observation_id) REFERENCES proposed_geometry_observation(geometry_observation_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_transformation_id_fk FOREIGN KEY (transformation_id) REFERENCES proposed_geometry_transformation(transformation_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_quality_state_vocab_fk FOREIGN KEY (quality_state) REFERENCES vocab_geometry_quality_state(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_superseded_by_geometry_version_id_fk FOREIGN KEY (superseded_by_geometry_version_id) REFERENCES proposed_geometry_version(geometry_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_dispute_case_id_fk FOREIGN KEY (dispute_case_id) REFERENCES proposed_dispute_case(dispute_case_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_promotion_decision_event_id_fk FOREIGN KEY (promotion_decision_event_id) REFERENCES proposed_decision_event(decision_event_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_promotion_evidence_object_id_fk FOREIGN KEY (promotion_evidence_object_id) REFERENCES proposed_evidence_object(evidence_object_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_intake_case ADD CONSTRAINT proposed_intake_case_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_intake_case ADD CONSTRAINT proposed_intake_case_intake_state_vocab_fk FOREIGN KEY (intake_state) REFERENCES vocab_intake_state(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_landmark ADD CONSTRAINT proposed_landmark_landmark_type_vocab_fk FOREIGN KEY (landmark_type) REFERENCES vocab_landmark_type(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_landmark ADD CONSTRAINT proposed_landmark_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_landmark_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_landmark ADD CONSTRAINT proposed_landmark_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_landmark ADD CONSTRAINT proposed_landmark_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_licence ADD CONSTRAINT proposed_licence_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_locality ADD CONSTRAINT proposed_locality_administrative_unit_id_fk FOREIGN KEY (administrative_unit_id) REFERENCES proposed_administrative_unit(administrative_unit_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_locality ADD CONSTRAINT proposed_locality_locality_type_vocab_fk FOREIGN KEY (locality_type) REFERENCES vocab_locality_type(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_locality ADD CONSTRAINT proposed_locality_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_locality_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_locality ADD CONSTRAINT proposed_locality_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_locality ADD CONSTRAINT proposed_locality_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_location_record ADD CONSTRAINT proposed_location_record_record_type_vocab_fk FOREIGN KEY (record_type) REFERENCES vocab_record_type(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record ADD CONSTRAINT proposed_location_record_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_assertion ADD CONSTRAINT proposed_location_record_assertion_location_record_version_id_fk FOREIGN KEY (location_record_version_id) REFERENCES proposed_location_record_version(location_record_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_assertion ADD CONSTRAINT proposed_location_record_assertion_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_assertion ADD CONSTRAINT proposed_location_record_assertion_evidence_object_id_fk FOREIGN KEY (evidence_object_id) REFERENCES proposed_evidence_object(evidence_object_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_assertion ADD CONSTRAINT proposed_location_record_assertion_decision_event_id_fk FOREIGN KEY (decision_event_id) REFERENCES proposed_decision_event(decision_event_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_assertion ADD CONSTRAINT proposed_location_record_assertion_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_object_link ADD CONSTRAINT proposed_location_record_object_link_location_record_version_id_fk FOREIGN KEY (location_record_version_id) REFERENCES proposed_location_record_version(location_record_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_object_link ADD CONSTRAINT proposed_location_record_object_link_object_role_vocab_fk FOREIGN KEY (object_role) REFERENCES vocab_object_role(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_object_link ADD CONSTRAINT proposed_location_record_object_link_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_location_record_object_link ADD CONSTRAINT proposed_location_record_object_link_subject_id_fk FOREIGN KEY (subject_id) REFERENCES proposed_registry_subject(subject_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_relationship ADD CONSTRAINT proposed_location_record_relationship_from_location_record_id_fk FOREIGN KEY (from_location_record_id) REFERENCES proposed_location_record(location_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_relationship ADD CONSTRAINT proposed_location_record_relationship_to_location_record_id_fk FOREIGN KEY (to_location_record_id) REFERENCES proposed_location_record(location_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_relationship ADD CONSTRAINT proposed_location_record_relationship_relationship_type_vocab_fk FOREIGN KEY (relationship_type) REFERENCES vocab_relationship_type(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_relationship ADD CONSTRAINT proposed_location_record_relationship_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_location_record_relationship ADD CONSTRAINT proposed_location_record_relationship_source_decision_event_id_fk FOREIGN KEY (source_decision_event_id) REFERENCES proposed_decision_event(decision_event_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_location_record_id_fk FOREIGN KEY (location_record_id) REFERENCES proposed_location_record(location_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_canonical_record_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_administrative_unit_version_id_fk FOREIGN KEY (administrative_unit_version_id) REFERENCES proposed_administrative_unit_version(administrative_unit_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_locality_id_fk FOREIGN KEY (locality_id) REFERENCES proposed_locality(locality_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_predecessor_version_id_fk FOREIGN KEY (predecessor_version_id) REFERENCES proposed_location_record_version(location_record_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_successor_version_id_fk FOREIGN KEY (successor_version_id) REFERENCES proposed_location_record_version(location_record_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_correction_case_id_fk FOREIGN KEY (correction_case_id) REFERENCES proposed_correction_case(correction_case_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_source_decision_event_id_fk FOREIGN KEY (source_decision_event_id) REFERENCES proposed_decision_event(decision_event_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_name_record ADD CONSTRAINT proposed_name_record_subject_id_fk FOREIGN KEY (subject_id) REFERENCES proposed_registry_subject(subject_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_name_record ADD CONSTRAINT proposed_name_record_name_kind_vocab_fk FOREIGN KEY (name_kind) REFERENCES vocab_name_kind(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_name_record ADD CONSTRAINT proposed_name_record_name_status_vocab_fk FOREIGN KEY (name_status) REFERENCES vocab_name_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_name_record ADD CONSTRAINT proposed_name_record_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_name_record ADD CONSTRAINT proposed_name_record_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_non_building_object ADD CONSTRAINT proposed_non_building_object_object_type_vocab_fk FOREIGN KEY (object_type) REFERENCES vocab_non_building_object_type(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_non_building_object ADD CONSTRAINT proposed_non_building_object_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_non_building_object_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_non_building_object ADD CONSTRAINT proposed_non_building_object_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_non_building_object ADD CONSTRAINT proposed_non_building_object_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_operational_area ADD CONSTRAINT proposed_operational_area_area_type_vocab_fk FOREIGN KEY (area_type) REFERENCES vocab_operational_area_type(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_operational_area ADD CONSTRAINT proposed_operational_area_name_record_id_fk FOREIGN KEY (name_record_id) REFERENCES proposed_name_record(name_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_operational_area ADD CONSTRAINT proposed_operational_area_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_operational_area_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_operational_area ADD CONSTRAINT proposed_operational_area_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_operational_area ADD CONSTRAINT proposed_operational_area_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_operational_area_coverage ADD CONSTRAINT proposed_operational_area_coverage_operational_area_id_fk FOREIGN KEY (operational_area_id) REFERENCES proposed_operational_area(operational_area_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_operational_area_coverage ADD CONSTRAINT proposed_operational_area_coverage_administrative_unit_id_fk FOREIGN KEY (administrative_unit_id) REFERENCES proposed_administrative_unit(administrative_unit_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_operational_area_coverage ADD CONSTRAINT proposed_operational_area_coverage_geometry_version_id_fk FOREIGN KEY (geometry_version_id) REFERENCES proposed_geometry_version(geometry_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_operational_area_coverage ADD CONSTRAINT proposed_operational_area_coverage_coverage_role_vocab_fk FOREIGN KEY (coverage_role) REFERENCES vocab_coverage_role(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_operational_area_coverage ADD CONSTRAINT proposed_operational_area_coverage_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_parcel_reference ADD CONSTRAINT proposed_parcel_reference_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_parcel_reference ADD CONSTRAINT proposed_parcel_reference_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_parcel_reference ADD CONSTRAINT proposed_parcel_reference_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_partner_projection ADD CONSTRAINT proposed_partner_projection_publication_release_item_id_fk FOREIGN KEY (publication_release_item_id) REFERENCES proposed_publication_release_item(publication_release_item_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_partner_projection ADD CONSTRAINT proposed_partner_projection_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_public_code_alias ADD CONSTRAINT proposed_public_code_alias_location_record_id_fk FOREIGN KEY (location_record_id) REFERENCES proposed_location_record(location_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_public_code_alias ADD CONSTRAINT proposed_public_code_alias_code_state_vocab_fk FOREIGN KEY (code_state) REFERENCES vocab_public_code_state(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_public_code_alias ADD CONSTRAINT proposed_public_code_alias_predecessor_alias_id_fk FOREIGN KEY (predecessor_alias_id) REFERENCES proposed_public_code_alias(public_code_alias_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_public_code_alias ADD CONSTRAINT proposed_public_code_alias_successor_alias_id_fk FOREIGN KEY (successor_alias_id) REFERENCES proposed_public_code_alias(public_code_alias_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_publication_release ADD CONSTRAINT proposed_publication_release_release_state_vocab_fk FOREIGN KEY (release_state) REFERENCES vocab_publication_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_publication_release ADD CONSTRAINT proposed_publication_release_projection_type_vocab_fk FOREIGN KEY (projection_type) REFERENCES vocab_projection_type(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_publication_release_item ADD CONSTRAINT proposed_publication_release_item_publication_release_id_fk FOREIGN KEY (publication_release_id) REFERENCES proposed_publication_release(publication_release_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_publication_release_item ADD CONSTRAINT proposed_publication_release_item_location_record_id_fk FOREIGN KEY (location_record_id) REFERENCES proposed_location_record(location_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_publication_release_item ADD CONSTRAINT proposed_publication_release_item_location_record_version_id_fk FOREIGN KEY (location_record_version_id) REFERENCES proposed_location_record_version(location_record_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_publication_release_item ADD CONSTRAINT proposed_publication_release_item_public_code_alias_id_fk FOREIGN KEY (public_code_alias_id) REFERENCES proposed_public_code_alias(public_code_alias_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_publication_release_item ADD CONSTRAINT proposed_publication_release_item_projection_state_vocab_fk FOREIGN KEY (projection_state) REFERENCES vocab_publication_item_state(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_registry_subject ADD CONSTRAINT proposed_registry_subject_subject_state_vocab_fk FOREIGN KEY (subject_state) REFERENCES vocab_subject_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_registry_subject ADD CONSTRAINT proposed_registry_subject_delete_policy_vocab_fk FOREIGN KEY (delete_policy) REFERENCES vocab_delete_policy(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_road ADD CONSTRAINT proposed_road_road_class_vocab_fk FOREIGN KEY (road_class) REFERENCES vocab_road_class(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_road ADD CONSTRAINT proposed_road_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_road_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_road ADD CONSTRAINT proposed_road_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_road_segment ADD CONSTRAINT proposed_road_segment_road_id_fk FOREIGN KEY (road_id) REFERENCES proposed_road(road_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_road_segment ADD CONSTRAINT proposed_road_segment_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_road_segment_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_road_segment ADD CONSTRAINT proposed_road_segment_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
ALTER TABLE proposed_source_authority ADD CONSTRAINT proposed_source_authority_authority_class_vocab_fk FOREIGN KEY (authority_class) REFERENCES vocab_source_authority_class(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_source_authority ADD CONSTRAINT proposed_source_authority_status_vocab_fk FOREIGN KEY (status) REFERENCES vocab_source_authority_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_source_package ADD CONSTRAINT proposed_source_package_source_authority_id_fk FOREIGN KEY (source_authority_id) REFERENCES proposed_source_authority(source_authority_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_source_package ADD CONSTRAINT proposed_source_package_licence_id_fk FOREIGN KEY (licence_id) REFERENCES proposed_licence(licence_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_source_payload_archive ADD CONSTRAINT proposed_source_payload_archive_source_record_id_fk FOREIGN KEY (source_record_id) REFERENCES proposed_source_record(source_record_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_source_payload_archive ADD CONSTRAINT proposed_source_payload_archive_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_source_payload_archive ADD CONSTRAINT proposed_source_payload_archive_retention_state_vocab_fk FOREIGN KEY (retention_state) REFERENCES vocab_retention_state(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_source_record ADD CONSTRAINT proposed_source_record_source_package_id_fk FOREIGN KEY (source_package_id) REFERENCES proposed_source_package(source_package_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_source_record ADD CONSTRAINT proposed_source_record_raw_payload_classification_vocab_fk FOREIGN KEY (raw_payload_classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_unit ADD CONSTRAINT proposed_unit_building_id_fk FOREIGN KEY (building_id) REFERENCES proposed_building(building_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_unit ADD CONSTRAINT proposed_unit_parent_unit_id_fk FOREIGN KEY (parent_unit_id) REFERENCES proposed_unit(unit_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_unit ADD CONSTRAINT proposed_unit_unit_type_vocab_fk FOREIGN KEY (unit_type) REFERENCES vocab_unit_type(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_unit ADD CONSTRAINT proposed_unit_lifecycle_state_vocab_fk FOREIGN KEY (lifecycle_state) REFERENCES vocab_unit_lifecycle(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_unit ADD CONSTRAINT proposed_unit_classification_vocab_fk FOREIGN KEY (classification) REFERENCES vocab_classification(value) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_unit ADD CONSTRAINT proposed_unit_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
CREATE TABLE subject_entity_registry(entity_name text PRIMARY KEY, pk_column text NOT NULL);
INSERT INTO subject_entity_registry(entity_name, pk_column) VALUES ('location_record','location_record_id'),('administrative_unit','administrative_unit_id'),('operational_area','operational_area_id'),('road','road_id'),('road_segment','road_segment_id'),('building','building_id'),('unit','unit_id'),('entrance','entrance_id'),('landmark','landmark_id'),('non_building_object','object_id'),('locality','locality_id'),('geometry_version','geometry_version_id');
CREATE TABLE record_object_role_matrix(record_type text NOT NULL, object_role text NOT NULL, required boolean NOT NULL, min_count integer NOT NULL, max_count integer NOT NULL, allowed_subject_entities text[] NOT NULL, retirement_behavior text NOT NULL, merge_behavior text NOT NULL, PRIMARY KEY(record_type, object_role));
INSERT INTO record_object_role_matrix VALUES ('address','primary-subject',true,1,1,ARRAY['building','unit','non_building_object','landmark','location_record'],'retire-link-with-record-version','repoint-through-successor-subject'),('address','context-road',false,0,1,ARRAY['road','road_segment'],'retain-history-disable-current','repoint-on-approved-merge'),('address','context-locality',false,0,1,ARRAY['locality','administrative_unit'],'retain-history-disable-current','repoint-on-approved-merge'),('address','access-point',false,0,4,ARRAY['entrance'],'retire-link','repoint-on-approved-merge'),('address','nearby-landmark',false,0,5,ARRAY['landmark'],'retain-context','repoint-on-approved-merge'),('building','primary-subject',true,1,1,ARRAY['building'],'retire-link-with-record-version','repoint-through-successor-subject'),('building','access-point',false,0,12,ARRAY['entrance'],'retire-link','repoint-on-approved-merge'),('unit','primary-subject',true,1,1,ARRAY['unit'],'retire-link-with-record-version','repoint-through-successor-subject'),('unit','parent-building',true,1,1,ARRAY['building'],'retain-history-disable-current','repoint-on-approved-merge'),('entrance','primary-subject',true,1,1,ARRAY['entrance'],'retire-link-with-record-version','repoint-through-successor-subject'),('landmark','primary-subject',true,1,1,ARRAY['landmark'],'retire-link-with-record-version','repoint-through-successor-subject'),('non-building-object','primary-subject',true,1,1,ARRAY['non_building_object'],'retire-link-with-record-version','repoint-through-successor-subject'),('service-location','primary-subject',true,1,1,ARRAY['location_record','non_building_object','administrative_unit'],'retire-link-with-record-version','repoint-through-successor-subject'),('service-location','external-parcel-reference',false,0,1,ARRAY['location_record'],'retain-context','repoint-on-approved-merge');
CREATE TABLE geometry_role_matrix(geometry_role text PRIMARY KEY, geometry_types text[] NOT NULL, subject_entities text[] NOT NULL, observation_allowed boolean NOT NULL, promotion_permission text NOT NULL);
INSERT INTO geometry_role_matrix VALUES ('building-point',ARRAY['POINT'],ARRAY['building'],true,'geometry.promote'),('entrance-point',ARRAY['POINT'],ARRAY['entrance','unit','building'],true,'geometry.promote'),('location-point',ARRAY['POINT'],ARRAY['location_record','non_building_object'],true,'geometry.promote'),('landmark-point',ARRAY['POINT'],ARRAY['landmark'],true,'geometry.promote'),('road-centerline',ARRAY['LINESTRING','MULTILINESTRING'],ARRAY['road','road_segment'],true,'geometry.promote'),('admin-boundary',ARRAY['POLYGON','MULTIPOLYGON'],ARRAY['administrative_unit'],true,'geometry.promote'),('operational-boundary',ARRAY['POLYGON','MULTIPOLYGON'],ARRAY['operational_area'],true,'geometry.promote'),('building-footprint',ARRAY['POLYGON','MULTIPOLYGON'],ARRAY['building'],true,'geometry.promote'),('parcel-boundary',ARRAY['POLYGON','MULTIPOLYGON'],ARRAY['location_record'],true,'geometry.promote');
CREATE OR REPLACE FUNCTION enforce_registry_subject_native() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE pk text; found_row boolean; BEGIN SELECT pk_column INTO pk FROM subject_entity_registry WHERE entity_name=NEW.subject_entity; IF pk IS NULL THEN RAISE EXCEPTION 'unknown subject entity %', NEW.subject_entity; END IF; EXECUTE format('SELECT EXISTS (SELECT 1 FROM proposed_%I WHERE %I = $1)', NEW.subject_entity, pk) INTO found_row USING NEW.native_id; IF NOT found_row THEN RAISE EXCEPTION 'registry subject native target %.% does not exist', NEW.subject_entity, NEW.native_id; END IF; RETURN NEW; END $$;
CREATE CONSTRAINT TRIGGER registry_subject_native_trg AFTER INSERT OR UPDATE ON proposed_registry_subject DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_native();
CREATE OR REPLACE FUNCTION enforce_registry_subject_link() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.subject_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_registry_subject s WHERE s.subject_id = NEW.subject_id AND s.subject_state IN ('active','retired','merged')) THEN RAISE EXCEPTION 'registry subject % missing or not linkable', NEW.subject_id; END IF; RETURN NEW; END $$;
CREATE TRIGGER name_record_subject_trg BEFORE INSERT OR UPDATE ON proposed_name_record FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_link();
CREATE TRIGGER object_link_subject_trg BEFORE INSERT OR UPDATE ON proposed_location_record_object_link FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_link();
CREATE TRIGGER dispute_case_subject_trg BEFORE INSERT OR UPDATE ON proposed_dispute_case FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_link();
CREATE TRIGGER geometry_version_subject_trg BEFORE INSERT OR UPDATE ON proposed_geometry_version FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_link();
CREATE TRIGGER geometry_observation_subject_trg BEFORE INSERT OR UPDATE ON proposed_geometry_observation FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_link();
CREATE OR REPLACE FUNCTION reject_subject_delete_with_dependents() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF EXISTS (SELECT 1 FROM proposed_name_record WHERE subject_id=OLD.subject_id) OR EXISTS (SELECT 1 FROM proposed_geometry_version WHERE subject_id=OLD.subject_id) OR EXISTS (SELECT 1 FROM proposed_geometry_observation WHERE subject_id=OLD.subject_id) OR EXISTS (SELECT 1 FROM proposed_dispute_case WHERE subject_id=OLD.subject_id) OR EXISTS (SELECT 1 FROM proposed_location_record_object_link WHERE subject_id=OLD.subject_id) THEN RAISE EXCEPTION 'subject % must be retired or merged, not deleted', OLD.subject_id; END IF; RETURN OLD; END $$;
CREATE TRIGGER registry_subject_delete_policy_trg BEFORE DELETE ON proposed_registry_subject FOR EACH ROW EXECUTE FUNCTION reject_subject_delete_with_dependents();
CREATE OR REPLACE FUNCTION enforce_object_role_cardinality() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE rule record; v_subject_entity text; v_record_type text; current_count integer; v_from timestamptz; v_to timestamptz; BEGIN SELECT lr.record_type INTO v_record_type FROM proposed_location_record_version lrv JOIN proposed_location_record lr ON lr.location_record_id=lrv.location_record_id WHERE lrv.location_record_version_id=NEW.location_record_version_id; SELECT * INTO rule FROM record_object_role_matrix WHERE record_object_role_matrix.record_type=v_record_type AND object_role=NEW.object_role; IF rule.object_role IS NULL THEN RAISE EXCEPTION 'invalid object role %', NEW.object_role; END IF; SELECT s.subject_entity INTO v_subject_entity FROM proposed_registry_subject s WHERE s.subject_id=NEW.subject_id; IF v_subject_entity IS NULL OR NOT (v_subject_entity = ANY(rule.allowed_subject_entities)) THEN RAISE EXCEPTION 'subject type % not allowed for object role %', v_subject_entity, NEW.object_role; END IF; SELECT effective_from, effective_to INTO v_from, v_to FROM proposed_location_record_version WHERE location_record_version_id=NEW.location_record_version_id; IF v_from IS NULL THEN RAISE EXCEPTION 'owning record version missing for object link'; END IF; IF NEW.effective_from < v_from OR (v_to IS NOT NULL AND COALESCE(NEW.effective_to, v_to) > v_to) THEN RAISE EXCEPTION 'object link interval outside owning record version'; END IF; SELECT COUNT(*) INTO current_count FROM proposed_location_record_object_link l WHERE l.location_record_version_id=NEW.location_record_version_id AND l.object_role=NEW.object_role AND l.link_id<>NEW.link_id AND (l.effective_to IS NULL OR l.effective_to > NEW.effective_from); IF current_count + 1 > rule.max_count THEN RAISE EXCEPTION 'object role % exceeds max count %', NEW.object_role, rule.max_count; END IF; RETURN NEW; END $$;
CREATE TRIGGER object_role_cardinality_trg BEFORE INSERT OR UPDATE ON proposed_location_record_object_link FOR EACH ROW EXECUTE FUNCTION enforce_object_role_cardinality();
CREATE OR REPLACE FUNCTION enforce_required_object_roles() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE missing_role text; rt text; BEGIN SELECT lr.record_type INTO rt FROM proposed_location_record lr WHERE lr.location_record_id=NEW.location_record_id; SELECT m.object_role INTO missing_role FROM record_object_role_matrix m WHERE m.record_type=rt AND m.required AND NOT EXISTS (SELECT 1 FROM proposed_location_record_object_link l WHERE l.location_record_version_id=NEW.location_record_version_id AND l.object_role=m.object_role AND (l.effective_to IS NULL OR l.effective_to > NEW.effective_from)) LIMIT 1; IF missing_role IS NOT NULL THEN RAISE EXCEPTION 'location record version requires role % for record type %', missing_role, rt; END IF; RETURN NEW; END $$;
CREATE CONSTRAINT TRIGGER required_object_roles_trg AFTER INSERT OR UPDATE ON proposed_location_record_version DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION enforce_required_object_roles();
CREATE OR REPLACE FUNCTION enforce_current_official_name() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.name_kind LIKE 'official%' AND NEW.name_status='official-current' AND EXISTS (SELECT 1 FROM proposed_name_record n WHERE n.subject_id=NEW.subject_id AND n.language_code=NEW.language_code AND n.name_kind LIKE 'official%' AND n.name_status='official-current' AND n.name_record_id<>NEW.name_record_id AND (n.effective_to IS NULL OR n.effective_to > NEW.effective_from)) THEN RAISE EXCEPTION 'subject % already has current official name for language %', NEW.subject_id, NEW.language_code; END IF; RETURN NEW; END $$;
CREATE TRIGGER current_official_name_trg BEFORE INSERT OR UPDATE ON proposed_name_record FOR EACH ROW EXECUTE FUNCTION enforce_current_official_name();
CREATE OR REPLACE FUNCTION enforce_geometry_version_semantics() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE rule record; v_subject_entity text; obs record; decision_row record; BEGIN SELECT * INTO rule FROM geometry_role_matrix WHERE geometry_role=NEW.geometry_role; IF rule.geometry_role IS NULL THEN RAISE EXCEPTION 'unknown geometry role %', NEW.geometry_role; END IF; SELECT s.subject_entity INTO v_subject_entity FROM proposed_registry_subject s WHERE s.subject_id=NEW.subject_id; IF v_subject_entity IS NULL OR NOT (v_subject_entity = ANY(rule.subject_entities)) THEN RAISE EXCEPTION 'subject type % not allowed for geometry role %', v_subject_entity, NEW.geometry_role; END IF; IF GeometryType(NEW.geom) <> ALL(rule.geometry_types) THEN RAISE EXCEPTION 'invalid geometry type for role %', NEW.geometry_role; END IF; IF ST_NDims(NEW.geom) <> 2 OR ST_SRID(NEW.geom) <> 4326 OR NOT ST_IsValid(NEW.geom) THEN RAISE EXCEPTION 'invalid geometry dimensionality/SRID/validity'; END IF; IF NEW.superseded_by_geometry_version_id = NEW.geometry_version_id THEN RAISE EXCEPTION 'geometry version cannot supersede itself'; END IF; IF NEW.superseded_by_geometry_version_id IS NOT NULL AND EXISTS (WITH RECURSIVE chain(id) AS (SELECT NEW.superseded_by_geometry_version_id UNION ALL SELECT g.superseded_by_geometry_version_id FROM proposed_geometry_version g JOIN chain c ON g.geometry_version_id=c.id WHERE g.superseded_by_geometry_version_id IS NOT NULL) SELECT 1 FROM chain WHERE id=NEW.geometry_version_id) THEN RAISE EXCEPTION 'geometry supersession cycle'; END IF; SELECT * INTO obs FROM proposed_geometry_observation WHERE geometry_observation_id=NEW.source_observation_id; IF obs.geometry_observation_id IS NULL OR obs.subject_id<>NEW.subject_id OR obs.geometry_role<>NEW.geometry_role THEN RAISE EXCEPTION 'geometry promotion requires same-subject same-role observation'; END IF; IF obs.evidence_object_id IS DISTINCT FROM NEW.promotion_evidence_object_id THEN RAISE EXCEPTION 'geometry promotion evidence must match source observation evidence'; END IF; IF NEW.promotion_decision_event_id IS NULL OR NEW.promotion_evidence_object_id IS NULL OR COALESCE(NEW.promotion_authority_scope,'')='' THEN RAISE EXCEPTION 'geometry promotion requires authorized decision, evidence and authority scope'; END IF; SELECT * INTO decision_row FROM proposed_decision_event d WHERE d.decision_event_id=NEW.promotion_decision_event_id; IF decision_row.decision_event_id IS NULL OR decision_row.decision_type <> 'approve-geometry' OR decision_row.decision_outcome NOT IN ('approved','accepted') THEN RAISE EXCEPTION 'geometry promotion decision is not authorized'; END IF; IF decision_row.details_json->>'permission_key' IS DISTINCT FROM rule.promotion_permission THEN RAISE EXCEPTION 'geometry promotion actor lacks required permission %', rule.promotion_permission; END IF; IF COALESCE(decision_row.details_json->>'institution_id','') = '' OR COALESCE(decision_row.details_json->>'territorial_scope','') = '' OR decision_row.details_json->>'territorial_scope' IS DISTINCT FROM NEW.promotion_authority_scope THEN RAISE EXCEPTION 'geometry promotion institution or territorial scope mismatch'; END IF; IF decision_row.details_json->>'quality_authority_actor_id' IS DISTINCT FROM NEW.validated_by_actor_id THEN RAISE EXCEPTION 'geometry quality authority actor mismatch'; END IF; IF decision_row.details_json->>'evidence_object_id' IS DISTINCT FROM NEW.promotion_evidence_object_id THEN RAISE EXCEPTION 'geometry decision evidence link mismatch'; END IF; IF decision_row.details_json->>'source_observation_id' IS DISTINCT FROM NEW.source_observation_id THEN RAISE EXCEPTION 'geometry decision observation link mismatch'; END IF; IF NEW.superseded_by_geometry_version_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_geometry_version s WHERE s.geometry_version_id=NEW.superseded_by_geometry_version_id AND s.subject_id=NEW.subject_id AND s.geometry_role=NEW.geometry_role) THEN RAISE EXCEPTION 'geometry supersession successor must share subject and role'; END IF; IF NEW.quality_state NOT IN ('accepted-canonical','valid-with-warning') THEN RAISE EXCEPTION 'geometry promotion requires accepted quality decision'; END IF; RETURN NEW; END $$;
CREATE TRIGGER geometry_version_semantics_trg BEFORE INSERT OR UPDATE ON proposed_geometry_version FOR EACH ROW EXECUTE FUNCTION enforce_geometry_version_semantics();
CREATE OR REPLACE FUNCTION enforce_geometry_observation_semantics() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE rule record; v_subject_entity text; BEGIN SELECT * INTO rule FROM geometry_role_matrix WHERE geometry_role=NEW.geometry_role; IF rule.geometry_role IS NULL OR NOT rule.observation_allowed THEN RAISE EXCEPTION 'geometry observation role not allowed %', NEW.geometry_role; END IF; SELECT s.subject_entity INTO v_subject_entity FROM proposed_registry_subject s WHERE s.subject_id=NEW.subject_id; IF v_subject_entity IS NULL OR NOT (v_subject_entity = ANY(rule.subject_entities)) THEN RAISE EXCEPTION 'subject type % not allowed for observation role %', v_subject_entity, NEW.geometry_role; END IF; IF GeometryType(NEW.observed_geom) <> ALL(rule.geometry_types) OR ST_NDims(NEW.observed_geom)<>2 OR ST_SRID(NEW.observed_geom)<>4326 OR NOT ST_IsValid(NEW.observed_geom) THEN RAISE EXCEPTION 'invalid observation geometry'; END IF; RETURN NEW; END $$;
CREATE TRIGGER geometry_observation_semantics_trg BEFORE INSERT OR UPDATE ON proposed_geometry_observation FOR EACH ROW EXECUTE FUNCTION enforce_geometry_observation_semantics();
CREATE OR REPLACE FUNCTION enforce_version_chain() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.predecessor_version_id = NEW.location_record_version_id OR NEW.successor_version_id = NEW.location_record_version_id THEN RAISE EXCEPTION 'version chain cannot self-reference'; END IF; IF NEW.predecessor_version_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_location_record_version p WHERE p.location_record_version_id=NEW.predecessor_version_id AND p.location_record_id=NEW.location_record_id AND p.successor_version_id=NEW.location_record_version_id) THEN RAISE EXCEPTION 'predecessor must reciprocally point to this version and share owner'; END IF; IF NEW.successor_version_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_location_record_version s WHERE s.location_record_version_id=NEW.successor_version_id AND s.location_record_id=NEW.location_record_id AND s.predecessor_version_id=NEW.location_record_version_id) THEN RAISE EXCEPTION 'successor must reciprocally point to this version and share owner'; END IF; IF EXISTS (WITH RECURSIVE chain(id) AS (SELECT NEW.successor_version_id UNION ALL SELECT v.successor_version_id FROM proposed_location_record_version v JOIN chain c ON v.location_record_version_id=c.id WHERE v.successor_version_id IS NOT NULL) SELECT 1 FROM chain WHERE id=NEW.location_record_version_id) THEN RAISE EXCEPTION 'version chain cycle'; END IF; RETURN NEW; END $$;
CREATE CONSTRAINT TRIGGER location_record_version_chain_trg AFTER INSERT OR UPDATE ON proposed_location_record_version DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION enforce_version_chain();
CREATE OR REPLACE FUNCTION enforce_alias_chain() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.predecessor_alias_id = NEW.public_code_alias_id OR NEW.successor_alias_id = NEW.public_code_alias_id THEN RAISE EXCEPTION 'alias chain cannot self-reference'; END IF; IF NEW.predecessor_alias_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_public_code_alias p WHERE p.public_code_alias_id=NEW.predecessor_alias_id AND p.location_record_id=NEW.location_record_id AND p.successor_alias_id=NEW.public_code_alias_id) THEN RAISE EXCEPTION 'predecessor alias must reciprocally point to this alias and share owner'; END IF; IF NEW.successor_alias_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_public_code_alias s WHERE s.public_code_alias_id=NEW.successor_alias_id AND s.location_record_id=NEW.location_record_id AND s.predecessor_alias_id=NEW.public_code_alias_id) THEN RAISE EXCEPTION 'successor alias must reciprocally point to this alias and share owner'; END IF; IF EXISTS (WITH RECURSIVE chain(id) AS (SELECT NEW.successor_alias_id UNION ALL SELECT a.successor_alias_id FROM proposed_public_code_alias a JOIN chain c ON a.public_code_alias_id=c.id WHERE a.successor_alias_id IS NOT NULL) SELECT 1 FROM chain WHERE id=NEW.public_code_alias_id) THEN RAISE EXCEPTION 'public code alias cycle'; END IF; RETURN NEW; END $$;
CREATE CONSTRAINT TRIGGER public_code_alias_chain_trg AFTER INSERT OR UPDATE ON proposed_public_code_alias DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION enforce_alias_chain();
CREATE OR REPLACE FUNCTION enforce_publication_prerequisite() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NOT EXISTS (SELECT 1 FROM proposed_publication_release r WHERE r.publication_release_id=NEW.publication_release_id AND r.release_state IN ('approved','published')) THEN RAISE EXCEPTION 'publication prerequisite not met'; END IF; RETURN NEW; END $$;
CREATE CONSTRAINT TRIGGER publication_prerequisite_trg AFTER INSERT OR UPDATE ON proposed_publication_release_item DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION enforce_publication_prerequisite();
CREATE TABLE lifecycle_transition_policy(vocab text NOT NULL, from_state text NOT NULL, to_state text NOT NULL, permission_key text NOT NULL, evidence text NOT NULL, audit_event text NOT NULL, public_effect text NOT NULL, terminal boolean NOT NULL DEFAULT false, PRIMARY KEY(vocab, from_state, to_state));
CREATE OR REPLACE FUNCTION validate_lifecycle_transition(vocab text, from_state text, to_state text) RETURNS boolean LANGUAGE plpgsql AS $$ BEGIN IF EXISTS (SELECT 1 FROM lifecycle_transition_policy p WHERE p.vocab=validate_lifecycle_transition.vocab AND p.from_state=validate_lifecycle_transition.from_state AND p.to_state=validate_lifecycle_transition.to_state) THEN RETURN true; END IF; RAISE EXCEPTION 'forbidden transition %.% -> %', vocab, from_state, to_state; END $$;
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_recorded_excl EXCLUDE USING gist (location_record_id WITH =, tstzrange(recorded_at, COALESCE(recorded_to, 'infinity'::timestamptz), '[)') WITH &&) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_effective_excl EXCLUDE USING gist (location_record_id WITH =, tstzrange(effective_from, COALESCE(effective_to, 'infinity'::timestamptz), '[)') WITH &&) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_administrative_code_history ADD CONSTRAINT proposed_admin_code_history_effective_excl EXCLUDE USING gist (administrative_unit_id WITH =, code_scheme WITH =, tstzrange(effective_from, COALESCE(effective_to, 'infinity'::timestamptz), '[)') WITH &&) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_effective_excl EXCLUDE USING gist (subject_id WITH =, geometry_role WITH =, tstzrange(effective_from, COALESCE(effective_to, 'infinity'::timestamptz), '[)') WITH &&) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE proposed_location_record_object_link ADD CONSTRAINT proposed_object_link_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);
CREATE UNIQUE INDEX proposed_location_record_version_one_current ON proposed_location_record_version(location_record_id) WHERE recorded_to IS NULL;
CREATE UNIQUE INDEX proposed_geometry_version_one_current ON proposed_geometry_version(subject_id, geometry_role) WHERE recorded_to IS NULL;
CREATE UNIQUE INDEX proposed_name_record_one_current_official ON proposed_name_record(subject_id, language_code) WHERE name_kind LIKE 'official%' AND name_status='official-current';
CREATE UNIQUE INDEX proposed_public_code_alias_one_current ON proposed_public_code_alias(location_record_id) WHERE successor_alias_id IS NULL AND code_state='active-public';
CREATE UNIQUE INDEX proposed_admin_code_history_one_current ON proposed_administrative_code_history(administrative_unit_id, code_scheme) WHERE recorded_to IS NULL AND effective_to IS NULL;
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('administrative_unit_lifecycle', 'proposed', 'official', 'admin.unit.approve', 'official gazette/source record', 'admin.official', 'eligible for government projection', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('administrative_unit_lifecycle', 'official', 'historical', 'admin.unit.replace', 'new version and boundary evidence', 'admin.historical', 'current public switches after release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('administrative_unit_lifecycle', 'official', 'retired', 'admin.unit.retire', 'retirement order', 'admin.retire', 'not current public', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('administrative_unit_lifecycle', 'proposed', 'revoked', 'admin.unit.reject', 'review denial', 'admin.reject', 'never public', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('building_lifecycle', 'candidate', 'active', 'building.approve', 'field point/footprint evidence', 'building.approve', 'public after address release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('building_lifecycle', 'active', 'demolished', 'building.demolish', 'demolition evidence', 'building.demolish', 'remove current public after release', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('building_lifecycle', 'active', 'retired', 'building.retire', 'retirement decision', 'building.retire', 'remove current', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('building_lifecycle', 'candidate', 'revoked', 'building.reject', 'review reason', 'building.reject', 'never public', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('canonical_record_lifecycle', 'candidate', 'under-review', 'registry.record.submit', 'citizen/field intake evidence', 'canonical.submit', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('canonical_record_lifecycle', 'under-review', 'active', 'registry.record.approve', 'approved verification bundle', 'canonical.approve', 'eligible for release after publication item', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('canonical_record_lifecycle', 'under-review', 'disputed', 'registry.dispute.open', 'dispute submission', 'canonical.dispute.open', 'not public unless already released', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('canonical_record_lifecycle', 'active', 'corrected', 'registry.record.correct', 'correction case + before/after proof', 'canonical.correct', 'new version required before public change', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('canonical_record_lifecycle', 'active', 'superseded', 'registry.record.supersede', 'successor record/version link', 'canonical.supersede', 'old public alias retained as historical', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('canonical_record_lifecycle', 'active', 'retired', 'registry.record.retire', 'retirement authority decision', 'canonical.retire', 'remove from current public release after withdrawal', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('canonical_record_lifecycle', 'candidate', 'revoked', 'registry.record.reject', 'review denial reason', 'canonical.reject', 'never public', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('case_lifecycle', 'submitted', 'under-review', 'case.triage', 'case submission', 'case.triage', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('case_lifecycle', 'under-review', 'needs-evidence', 'case.request_evidence', 'evidence request', 'case.evidence.request', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('case_lifecycle', 'needs-evidence', 'under-review', 'case.evidence.receive', 'submitted evidence', 'case.evidence.receive', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('case_lifecycle', 'under-review', 'approved', 'case.approve', 'decision record', 'case.approve', 'may affect public after release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('case_lifecycle', 'under-review', 'rejected', 'case.reject', 'denial reason', 'case.reject', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('case_lifecycle', 'approved', 'resolved', 'case.resolve', 'applied change proof', 'case.resolve', 'public only through release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('case_lifecycle', 'rejected', 'closed', 'case.close', 'closure note', 'case.close', 'none', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('case_lifecycle', 'resolved', 'closed', 'case.close', 'closure note', 'case.close', 'none', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('country_lifecycle', 'active', 'retired', 'country.retire', 'retirement decision', 'country.retire', 'not current', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('entrance_lifecycle', 'candidate', 'active', 'entrance.approve', 'entrance evidence', 'entrance.approve', 'public through address release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('entrance_lifecycle', 'active', 'retired', 'entrance.retire', 'retirement decision', 'entrance.retire', 'not current', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('entrance_lifecycle', 'candidate', 'revoked', 'entrance.reject', 'rejection reason', 'entrance.reject', 'never public', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('field_verification_state', 'assigned', 'in-progress', 'field.start', 'assignment', 'field.start', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('field_verification_state', 'in-progress', 'field-captured', 'field.capture', 'GPS/photo/evidence', 'field.capture', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('field_verification_state', 'field-captured', 'evidence-under-review', 'field.submit_review', 'submitted evidence', 'field.review.submit', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('field_verification_state', 'evidence-under-review', 'evidence-approved', 'field.evidence.approve', 'approval record', 'field.evidence.approve', 'eligible canonical evidence', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('field_verification_state', 'evidence-under-review', 'evidence-rejected', 'field.evidence.reject', 'rejection reason', 'field.evidence.reject', 'not public', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('field_verification_state', 'evidence-rejected', 'needs-recapture', 'field.recapture.request', 'recapture task', 'field.recapture', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('field_verification_state', 'needs-recapture', 'in-progress', 'field.restart', 'restart assignment', 'field.restart', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('field_verification_state', 'evidence-approved', 'linked-to-canonical', 'field.link', 'canonical link', 'field.link', 'operator-only/public via release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('field_verification_state', 'assigned', 'cancelled', 'field.cancel', 'cancel reason', 'field.cancel', 'operator-only', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('geometry_quality_state', 'observed', 'quality-checked', 'geometry.quality.run', 'quality check output', 'geometry.quality.run', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('geometry_quality_state', 'quality-checked', 'reviewed', 'geometry.quality.review', 'review decision', 'geometry.quality.review', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('geometry_quality_state', 'reviewed', 'accepted-canonical', 'geometry.promote', 'accepted quality + evidence bundle', 'geometry.promote', 'eligible for release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('geometry_quality_state', 'reviewed', 'valid-with-warning', 'geometry.accept.warning', 'warning decision', 'geometry.warning', 'operator warning', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('geometry_quality_state', 'reviewed', 'rejected', 'geometry.reject', 'rejection reason', 'geometry.reject', 'not public', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('geometry_quality_state', 'reviewed', 'disputed', 'geometry.dispute.open', 'geometry dispute case', 'geometry.dispute', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('geometry_quality_state', 'accepted-canonical', 'superseded', 'geometry.supersede', 'successor geometry', 'geometry.supersede', 'old geometry historical', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('geometry_quality_state', 'disputed', 'reviewed', 'geometry.dispute.resolve', 'resolution evidence', 'geometry.dispute.resolve', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('intake_state', 'submitted', 'under-review', 'intake.triage', 'submission', 'intake.triage', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('intake_state', 'under-review', 'duplicate-review', 'intake.duplicate', 'duplicate evidence', 'intake.duplicate', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('intake_state', 'under-review', 'needs-field-check', 'intake.field_check', 'field task request', 'intake.field_check', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('intake_state', 'needs-field-check', 'under-review', 'intake.field_return', 'field evidence', 'intake.field_return', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('intake_state', 'duplicate-review', 'under-review', 'intake.clear_duplicate', 'clearance note', 'intake.clear_duplicate', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('intake_state', 'under-review', 'promoted-to-canonical', 'intake.promote', 'canonical link', 'intake.promote', 'public after release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('intake_state', 'under-review', 'rejected', 'intake.reject', 'denial reason', 'intake.reject', 'not public', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('intake_state', 'promoted-to-canonical', 'closed', 'intake.close', 'closure note', 'intake.close', 'none', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('intake_state', 'rejected', 'closed', 'intake.close', 'closure note', 'intake.close', 'none', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('landmark_lifecycle', 'candidate', 'official', 'landmark.approve', 'landmark evidence', 'landmark.approve', 'public after release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('landmark_lifecycle', 'official', 'retired', 'landmark.retire', 'retirement decision', 'landmark.retire', 'not current', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('landmark_lifecycle', 'candidate', 'revoked', 'landmark.reject', 'rejection reason', 'landmark.reject', 'never public', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('locality_lifecycle', 'candidate', 'official', 'locality.approve', 'locality authority evidence', 'locality.approve', 'public after release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('locality_lifecycle', 'official', 'renamed', 'locality.rename', 'name replacement', 'locality.rename', 'new name after release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('locality_lifecycle', 'official', 'retired', 'locality.retire', 'retirement decision', 'locality.retire', 'remove current', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('name_lifecycle', 'candidate', 'official-current', 'name.approve.official', 'language/name authority evidence', 'name.approve', 'public after release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('name_lifecycle', 'official-current', 'official-historical', 'name.replace.official', 'replacement name', 'name.replace', 'old name historical', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('name_lifecycle', 'candidate', 'alternate', 'name.approve.alternate', 'alternate name evidence', 'name.alternate', 'operator/public if release allows', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('name_lifecycle', 'official-current', 'disputed', 'name.dispute.open', 'dispute case', 'name.dispute', 'operator warning', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('name_lifecycle', 'disputed', 'official-current', 'name.dispute.resolve', 'resolution decision', 'name.resolve', 'restore public if released', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('name_lifecycle', 'candidate', 'rejected', 'name.reject', 'denial reason', 'name.reject', 'never public', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('name_lifecycle', 'alternate', 'retired', 'name.retire', 'retirement reason', 'name.retire', 'not current', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('non_building_object_lifecycle', 'candidate', 'active', 'object.approve', 'object evidence', 'object.approve', 'public through release if allowed', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('non_building_object_lifecycle', 'active', 'retired', 'object.retire', 'retirement decision', 'object.retire', 'not current', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('non_building_object_lifecycle', 'candidate', 'revoked', 'object.reject', 'rejection reason', 'object.reject', 'never public', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('operational_area_lifecycle', 'planned', 'active', 'ops.area.activate', 'work plan approval', 'ops.area.activate', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('operational_area_lifecycle', 'active', 'suspended', 'ops.area.suspend', 'suspension reason', 'ops.area.suspend', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('operational_area_lifecycle', 'suspended', 'active', 'ops.area.reactivate', 'reactivation approval', 'ops.area.reactivate', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('operational_area_lifecycle', 'active', 'closed', 'ops.area.close', 'closure report', 'ops.area.close', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('operational_area_lifecycle', 'closed', 'archived', 'ops.area.archive', 'archive approval', 'ops.area.archive', 'operator-only', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('publication_lifecycle', 'draft', 'approval-requested', 'publication.request', 'release package', 'publication.request', 'not public', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('publication_lifecycle', 'approval-requested', 'approved', 'publication.approve', 'approval record', 'publication.approve', 'ready to publish', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('publication_lifecycle', 'approval-requested', 'withdrawn', 'publication.withdraw', 'withdrawal note', 'publication.withdraw', 'not public', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('publication_lifecycle', 'approved', 'published', 'publication.publish', 'published manifest', 'publication.publish', 'public release active', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('publication_lifecycle', 'published', 'suspended', 'publication.suspend', 'suspension reason', 'publication.suspend', 'public hidden/suspended', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('publication_lifecycle', 'suspended', 'published', 'publication.reinstate', 'reinstatement decision', 'publication.reinstate', 'public active', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('publication_lifecycle', 'published', 'withdrawn', 'publication.withdraw', 'withdrawal decision', 'publication.withdraw', 'public withdrawn', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('road_lifecycle', 'candidate', 'field-verified', 'road.verify', 'field geometry and name evidence', 'road.verify', 'operator-only', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('road_lifecycle', 'field-verified', 'official', 'road.approve', 'approved geometry/name', 'road.approve', 'public only after release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('road_lifecycle', 'official', 'superseded', 'road.supersede', 'replacement road link', 'road.supersede', 'historical public if released', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('road_lifecycle', 'official', 'retired', 'road.retire', 'retirement evidence', 'road.retire', 'remove from current public after release', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('road_segment_lifecycle', 'draft', 'active', 'road.segment.approve', 'segment geometry', 'segment.approve', 'operator until release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('road_segment_lifecycle', 'active', 'realigned', 'road.segment.realign', 'new segment geometry', 'segment.realign', 'public after release', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('road_segment_lifecycle', 'active', 'retired', 'road.segment.retire', 'retirement decision', 'segment.retire', 'remove current', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('source_authority_lifecycle', 'candidate', 'trusted', 'source.approve', 'source accreditation', 'source.approve', 'operator authority list', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('source_authority_lifecycle', 'trusted', 'deprecated', 'source.deprecate', 'deprecation decision', 'source.deprecate', 'operator warning', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('source_authority_lifecycle', 'trusted', 'revoked', 'source.revoke', 'revocation decision', 'source.revoke', 'not used for new facts', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('source_authority_lifecycle', 'candidate', 'revoked', 'source.reject', 'review denial', 'source.reject', 'never trusted', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('unit_lifecycle', 'candidate', 'active', 'unit.approve', 'building and unit evidence', 'unit.approve', 'public after release if allowed', false);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('unit_lifecycle', 'active', 'merged', 'unit.merge', 'merge decision and successor', 'unit.merge', 'historical only', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('unit_lifecycle', 'active', 'split', 'unit.split', 'split decision and successors', 'unit.split', 'historical only', true);
INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ('unit_lifecycle', 'active', 'retired', 'unit.retire', 'retirement evidence', 'unit.retire', 'remove current', true);
