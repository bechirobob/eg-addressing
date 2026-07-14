#!/usr/bin/env python3
"""Review 04 semantic artifact checker for NLI-WO-002.

This checker intentionally validates the Review 04 generated artifacts. The heavy
checks that require PostgreSQL/PostGIS and OpenAPI generation happen in
`review04_design_pipeline.py`; this script verifies that those artifacts exist,
are internally consistent, and do not overclaim beyond the pipeline report.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
SDA = ROOT / "docs" / "sda"
DM = SDA / "data-model"
errors: list[str] = []
warnings: list[str] = []


def err(message: str) -> None:
    errors.append(message)


def load_json(rel: str) -> Any:
    path = ROOT / rel
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        err(f"cannot parse {rel}: {exc}")
        return {} if rel.endswith(".json") else None


def read(rel: str) -> str:
    path = ROOT / rel
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        err(f"cannot read {rel}: {exc}")
        return ""


model = load_json("docs/sda/data-model/target-model.json")
registry = load_json("docs/sda/data-model/transformation-registry.json")
reviewed_registry = load_json("docs/sda/data-model/transformation-registry-reviewed.json")
cat = load_json("docs/sda/data-model/current-pg-catalog.json")
openapi_ops = load_json("docs/sda/data-model/openapi-operation-inventory.json")
route_policies = load_json("docs/sda/data-model/openapi-expected-route-policies.json")
target_catalog = load_json("docs/sda/data-model/target-schema-catalog.json")
fixtures = load_json("docs/sda/data-model/representative-records/machine-readable-fixtures.json")
lifecycle_transitions = load_json("docs/sda/data-model/lifecycle-transitions.json")
report_text = read("docs/sda/data-model/review04-semantic-design-report.md")
review_text = read("docs/sda/reviews/NLI-WO-002-review-04.md")
erd_text = read("docs/sda/data-model/canonical-logical-erd.mmd")
api_map_text = read("docs/sda/data-model/api-projection-map.md")

entities = model.get("entities", {}) if isinstance(model, dict) else {}
vocabs = model.get("vocabularies", {}) if isinstance(model, dict) else {}
fields = {f"{entity}.{field.get('name')}": field for entity, meta in entities.items() for field in meta.get("fields", [])}

# Target registry completeness.
required_field_keys = {"name", "pg_type", "nullable", "definition", "authority_owner", "classification", "projection", "temporal_behavior", "constraints"}
allowed_classes = set(vocabs.get("classification", {}).get("values", {}))
for entity, meta in entities.items():
    if not meta.get("description"):
        err(f"entity {entity} missing description")
    for field in meta.get("fields", []):
        fq = f"{entity}.{field.get('name')}"
        missing = required_field_keys - set(field)
        if missing:
            err(f"{fq} missing metadata keys {sorted(missing)}")
        if field.get("classification") not in allowed_classes:
            err(f"{fq} classification {field.get('classification')} not in classification vocabulary")
        vocab = field.get("vocabulary")
        if vocab and vocab not in vocabs:
            err(f"{fq} references missing vocabulary {vocab}")

# Current pg_catalog inventory and transformation coverage.
catalog_tables = cat.get("catalog", {}).get("tables", {}) if isinstance(cat, dict) else {}
current_fields = [f"{table}.{col['column_name']}" for table, meta in catalog_tables.items() for col in meta.get("columns", [])]
if "schema_migrations.execution_context" not in current_fields:
    err("pg_catalog inventory missing schema_migrations.execution_context")
if any(f.startswith("spatial_ref_sys.") for f in current_fields):
    err("pg_catalog inventory includes PostGIS extension internals spatial_ref_sys")
if not current_fields:
    err("pg_catalog current field inventory is empty")
if len(registry) != len(current_fields):
    err(f"transformation registry rows {len(registry)} != current fields {len(current_fields)}")
if len(reviewed_registry) != len(current_fields):
    err(f"reviewed transformation source rows {len(reviewed_registry)} != current fields {len(current_fields)}")
if isinstance(registry, list) and isinstance(reviewed_registry, list):
    if sorted(r.get("current") for r in registry) != sorted(r.get("current") for r in reviewed_registry):
        err("generated transformation registry does not match reviewed source current-field set")
pipeline_text = read("docs/sda/data-model/scripts/review04_design_pipeline.py")
if "def map_target_for(" in pipeline_text:
    err("pipeline still contains map_target_for fallback function")
for forbidden in ["all IDs to crosswalk", "everything else to raw archive", "return \"source_payload_archive.payload_uri\", \"governed-archive/compatibility\""]:
    if forbidden in pipeline_text:
        err(f"pipeline still contains broad fallback marker: {forbidden}")
allowed_dispositions = {"typed-transform", "structured-transform", "controlled-translation", "governed-archive", "formal-exception", "migration-ledger"}
review_required_keys = {"source_row_key", "source_value_semantics", "target_rows_fields", "target_id_generation", "archive_object", "authority_prerequisite", "exception_type_owner", "no_loss_proof", "review_status", "review_owner", "review_decision_id"}
for row in reviewed_registry if isinstance(reviewed_registry, list) else []:
    current = row.get("current")
    if row.get("review_status") not in {"approved-review04-remediation", "approved-manual-exception"}:
        err(f"{current} is not consciously approved in reviewed transformation source")
    missing_review = sorted(k for k in review_required_keys if not row.get(k))
    if missing_review:
        err(f"{current} missing reviewed transformation keys {missing_review}")
for row in registry if isinstance(registry, list) else []:
    current = row.get("current")
    target = row.get("target")
    disposition = row.get("disposition")
    if current not in current_fields:
        err(f"registry current field {current} not in pg_catalog inventory")
    if disposition not in allowed_dispositions:
        err(f"{current} has invalid disposition {disposition}")
    if target not in fields:
        err(f"{current} target {target} not in authoritative target registry")
    for key in ["source_keys", "target_ids_and_crosswalks", "value_preservation", "controlled_value_translation", "authority", "exception_handling", "validation_sql", "compatibility_period", "retirement_condition", "loss_risk"]:
        if not row.get(key):
            err(f"{current} missing {key}")
if not any(row.get("target") == "source_payload_archive.payload_uri" for row in registry if isinstance(registry, list)):
    err("registry does not route any raw restricted/compatibility values to governed source_payload_archive")

# OpenAPI field coverage and auth policy.
ops = openapi_ops.get("operations", []) if isinstance(openapi_ops, dict) else []
if len(ops) < 50:
    err(f"OpenAPI operation inventory too small: {len(ops)}")
for expected_public in ["GET /", "GET /api/v1/health", "POST /api/v1/auth/login"]:
    if route_policies.get(expected_public, {}).get("auth") != "public":
        err(f"{expected_public} expected public auth policy, got {route_policies.get(expected_public)}")
for op in ops:
    route_key = f"{op.get('method')} {op.get('path')}"
    if route_key not in route_policies:
        err(f"OpenAPI operation {route_key} missing expected policy row")
    if not op.get("operation_id") or not op.get("method") or not op.get("path"):
        err(f"OpenAPI operation missing identity: {op}")
    if "policy" not in op or "auth" not in op.get("policy", {}):
        err(f"OpenAPI operation {op.get('operation_id')} missing authorization policy")
    if op.get("policy", {}).get("analysis") != "function-ast-boundary":
        err(f"OpenAPI operation {op.get('operation_id')} policy not derived from precise AST boundary")
    if "responses" not in op or not op["responses"]:
        err(f"OpenAPI operation {op.get('operation_id')} missing response/status inventory")
if "field/geotag-tasks" in api_map_text and "Auth policy" not in api_map_text:
    err("API projection map does not show authorization policy for field routes")

# Physical target schema and fixture validation reports.
physical_report = target_catalog.get("report", {}) if isinstance(target_catalog, dict) else {}
if physical_report.get("missing_fields"):
    err(f"target schema missing fields: {physical_report.get('missing_fields')}")
if physical_report.get("field_parity_errors"):
    parity_errors = physical_report.get("field_parity_errors") or []
    err(f"target schema field parity errors: {parity_errors[:10]}")
if physical_report.get("physical_columns") != len(fields):
    err(f"target physical columns {physical_report.get('physical_columns')} != target fields {len(fields)}")
if physical_report.get("inserted_fixture_rows", 0) < len(entities):
    err("fixture insertion count does not cover every entity")
if len(physical_report.get("scenario_results", {})) != 7:
    err("target report does not show seven independently executed positive scenarios")
if len(physical_report.get("negative_results", {})) != 7:
    err("target report does not show seven negative fixture assertions")
if "Errors: 0" not in report_text:
    err("Review 04 semantic report does not show Errors: 0")
if "Current migrations applied to disposable PostgreSQL/PostGIS" not in report_text:
    err("Review 04 report missing disposable PostGIS assertion")

scenarios = fixtures.get("scenarios", {}) if isinstance(fixtures, dict) else {}
required_scenarios = {"urban-street-address", "rural-landmark-location", "multi-unit-building", "no-formal-road-location", "corrected-superseded-address", "disputed-geometry", "administrative-boundary-change"}
if set(scenarios) != required_scenarios:
    err(f"fixture scenarios mismatch: {sorted(scenarios)}")
for name, records in scenarios.items():
    if id(records) in []:
        err("internal identity check placeholder should never execute")
    missing_core = {"registry_subject", "location_record", "location_record_version"} - set(records)
    if missing_core:
        err(f"fixture {name} missing core entities {sorted(missing_core)}")
scenario_subject_ids = []
for name, records in scenarios.items():
    try:
        scenario_subject_ids.append(records["registry_subject"][0]["subject_id"])
    except Exception:
        err(f"fixture {name} missing registry_subject subject_id")
if len(set(scenario_subject_ids)) != len(scenario_subject_ids):
    err("fixtures are not genuinely independent: duplicate registry_subject ids")
negative_fixtures = fixtures.get("negative_fixtures", {}) if isinstance(fixtures, dict) else {}
for required_negative in ["invalid-cardinality-primary-object", "invalid-temporal-overlap", "invalid-state-transition", "invalid-subject-reference", "invalid-geometry-role-type", "invalid-publication-prerequisite", "invalid-self-supersession"]:
    if required_negative not in negative_fixtures:
        err(f"missing negative fixture {required_negative}")

# Subject registry / code authority / lifecycle separation.
if "administrative_unit.stable_code" in fields:
    err("administrative_unit.stable_code remains as duplicate administrative code authority")
for fq in ["name_record.subject_id", "location_record_object_link.subject_id", "dispute_case.subject_id", "geometry_version.subject_id", "geometry_observation.subject_id"]:
    if fields.get(fq, {}).get("fk") != "registry_subject.subject_id":
        err(f"{fq} must FK to registry_subject.subject_id")
for forbidden_field in ["name_record.subject_entity", "location_record_object_link.object_entity", "location_record_object_link.object_id", "dispute_case.target_entity", "dispute_case.target_id", "geometry_version.subject_entity"]:
    if forbidden_field in fields:
        err(f"{forbidden_field} leaves disconnected polymorphic integrity in target model")
for vocab in ["unit_type", "landmark_type", "non_building_object_type", "entrance_role", "quality_check_result", "canonical_record_lifecycle", "reference_object_lifecycle", "operational_area_lifecycle", "source_authority_lifecycle", "name_lifecycle", "case_lifecycle", "publication_lifecycle", "administrative_unit_lifecycle", "road_lifecycle", "building_lifecycle", "unit_lifecycle", "subject_lifecycle", "delete_policy"]:
    if vocab not in vocabs:
        err(f"missing Review 04 vocabulary {vocab}")
for field, vocab in {
    "unit.unit_type": "unit_type",
    "landmark.landmark_type": "landmark_type",
    "non_building_object.object_type": "non_building_object_type",
    "entrance.entrance_role": "entrance_role",
    "geometry_quality_assessment.check_result": "quality_check_result",
    "administrative_unit_version.lifecycle_state": "administrative_unit_lifecycle",
}.items():
    if fields.get(field, {}).get("vocabulary") != vocab:
        err(f"{field} does not use {vocab}")
if not isinstance(lifecycle_transitions, dict) or not lifecycle_transitions:
    err("missing hand-authored lifecycle-transitions.json")
for vocab, edges in lifecycle_transitions.items() if isinstance(lifecycle_transitions, dict) else []:
    if not isinstance(edges, list) or not edges:
        err(f"{vocab} has no lifecycle edges")
    for edge in edges:
        if not all(edge.get(k) for k in ["from", "to", "event", "actor", "evidence", "time_rule", "invalid_behavior"]):
            err(f"{vocab} lifecycle edge missing required governance metadata: {edge}")
for forbidden in [("approved", "rejected"), ("approved", "draft"), ("closed", "duplicate-review"), ("cancelled", "evidence-approved"), ("accepted-canonical", "disputed")]:
    for vocab, edges in lifecycle_transitions.items() if isinstance(lifecycle_transitions, dict) else []:
        if any((e.get("from"), e.get("to")) == forbidden for e in edges):
            err(f"forbidden lifecycle transition {forbidden[0]}->{forbidden[1]} present in {vocab}")

# ADRs and ERD coverage.
for adr in range(5, 10):
    matches = sorted((SDA / "adrs").glob(f"ADR-{adr:03d}-*.md"))
    if not matches:
        err(f"missing ADR-{adr:03d}")
        continue
    text = matches[0].read_text(encoding="utf-8")
    for heading in ["## Alternatives considered", "## Security and privacy implications", "## Performance and operational trade-offs", "## Migration consequences", "## Failure modes", "## Consequences", "## Acceptance checks"]:
        if heading not in text:
            err(f"{matches[0].name} missing {heading}")
for entity in ["administrative_code_history", "registry_subject", "source_payload_archive", "legacy_crosswalk"]:
    if entity not in erd_text:
        err(f"Mermaid ERD missing entity {entity}")

# Review 04 finding rows.
for i in range(2, 13):
    if not re.search(rf"\| F{i:02d} \| Resolved for SDA Review 05:", review_text):
        err(f"Review 04 resolution row F{i:02d} not updated")

report_lines = [
    "# Design Consistency Report",
    "",
    "Generated checks: 12",
    f"Errors: {len(errors)}",
    f"Warnings: {len(warnings)}",
]
if errors:
    report_lines.extend(["", "## Errors"])
    report_lines.extend(f"- {message}" for message in errors)
else:
    report_lines.extend([
        "",
        "## PASS",
        f"- Current pg_catalog fields: {len(current_fields)}",
        f"- OpenAPI operations: {len(ops)}",
        f"- Transformation rows: {len(registry) if isinstance(registry, list) else 0}",
        f"- Target fields: {len(fields)}",
        f"- Fixture scenarios: {len(scenarios)}",
    ])
report = "\n".join(report_lines) + "\n"
(DM / "design-consistency-report.md").write_text(report, encoding="utf-8")
print(report, end="")
if errors:
    sys.exit(1)
