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
assertion_registry: list[dict[str, str]] = []


def err(message: str) -> None:
    errors.append(message)


def gate(assertion_id: str, finding: str, condition: bool, message: str, evidence_path: str) -> None:
    assertion_registry.append({
        "assertion_id": assertion_id,
        "finding": finding,
        "status": "passed" if condition else "failed",
        "evidence_path": evidence_path,
    })
    if not condition:
        err(f"{assertion_id}: {message}")


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
reviewed_route_policies = load_json("docs/sda/data-model/openapi-reviewed-route-policies.json")
projection_contracts = load_json("docs/sda/data-model/openapi-reviewed-projection-contracts.json")
api_projection_assertions = load_json("docs/sda/data-model/openapi-policy-projection-assertions.json")
api_projection_summary = api_projection_assertions.get("summary", {}) if isinstance(api_projection_assertions, dict) else {}
semantic_mutation_report = load_json("docs/sda/data-model/semantic-mutation-test-report.json")
adr_matrix_text = read("docs/sda/data-model/adr-005-009-evidence-matrix.md")
target_catalog = load_json("docs/sda/data-model/target-schema-catalog.json")
fixtures = load_json("docs/sda/data-model/representative-records/machine-readable-fixtures.json")
current_semantics = load_json("docs/sda/data-model/current-field-semantics-reviewed.json")
transform_fixtures = load_json("docs/sda/data-model/transformation-fixtures-reviewed.json")
transform_fixture_report = load_json("docs/sda/data-model/transformation-fixture-report.json")
reviewed_convergence_units = load_json("docs/sda/data-model/schema-convergence-units-reviewed.json")
convergence_units = load_json("docs/sda/data-model/schema-convergence-units.json")
lifecycle_transitions = load_json("docs/sda/data-model/lifecycle-transitions.json")
report_text = read("docs/sda/data-model/review04-semantic-design-report.md")
physical_sql = read("docs/sda/data-model/draft-physical-schema.sql")
review_text = read("docs/sda/reviews/NLI-WO-002-review-06.md")
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
    if row.get("review_status") not in {"approved-review07-reviewed-source", "approved-review06-reviewed-source", "approved-review04-remediation", "approved-manual-exception"}:
        err(f"{current} is not consciously approved in reviewed transformation source")
    missing_review = sorted(k for k in review_required_keys if not row.get(k))
    if missing_review:
        err(f"{current} missing reviewed transformation keys {missing_review}")
    if not row.get("transform_group_id") or not str(row.get("transform_group_id")).startswith(("WO002-R06-", "WO002-R07-")):
        err(f"{current} missing Review 06 transform group id")
    if row.get("source_row_key") == current and not (current.endswith((".id", "_id")) or current.endswith(".code") or current.endswith(".public_code")):
        err(f"{current} source_row_key is the transformed field, not stable source row key")
    if not row.get("example_input_output"):
        err(f"{current} missing example input/output values")
    if not row.get("executable_no_loss_assertion"):
        err(f"{current} missing executable no-loss assertion")
    if row.get("disposition") in {"governed-archive", "formal-exception"} and not str(row.get("archive_value_reference", "")).startswith("source_payload_archive"):
        err(f"{current} archive/exception row missing governed original value reference")
    if "ASSERT " in str(row.get("executable_no_loss_assertion", "")) or not str(row.get("executable_no_loss_assertion", "")).lstrip().upper().startswith("SELECT"):
        err(f"{current} executable_no_loss_assertion must be executable SELECT, not pseudo assertion")
    if row.get("disposition") == "controlled-translation":
        target_vocab = fields.get(row.get("target"), {}).get("vocabulary")
        allowed = set(vocabs.get(target_vocab, {}).get("values", {})) if target_vocab else set()
        for src, dst in (row.get("controlled_value_map") or {}).items():
            if allowed and dst not in allowed:
                err(f"{current} controlled map output {dst!r} is outside target vocabulary {target_vocab}")
        ex = row.get("example_input_output") or {}
        if ex and allowed and ex.get("output") not in allowed:
            err(f"{current} example output {ex.get('output')!r} is outside target vocabulary {target_vocab}")
    if (current.endswith('_id') or current.split('.',1)[1].endswith('_id')) and current != 'schema_migrations.version':
        if not row.get("reference_crosswalk_join") and row.get("target") != "schema_migrations.version":
            err(f"{current} reference transform missing exact reference_crosswalk_join")

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


# Review 05 exact transformation defect checks.
by_current = {r.get("current"): r for r in reviewed_registry if isinstance(reviewed_registry, list)}
if by_current.get("address_corrections.correction_type", {}).get("target") != "correction_case.correction_type":
    err("address_corrections.correction_type must map to correction_case.correction_type, not generic archive")
if by_current.get("address_corrections.correction_type", {}).get("controlled_value_map", {}).get("record-update") != "label":
    err("address_corrections.correction_type must map observed record-update to valid target correction_type label")
for note_field in ["address_corrections.note", "address_corrections.reviewer_note", "address_corrections.reporter_name"]:
    row = by_current.get(note_field, {})
    if row.get("target") != "source_payload_archive.payload_uri" or not str(row.get("archive_value_reference", "")).startswith("source_payload_archive"):
        err(f"{note_field} must preserve original value through governed archive reference")
if len({r.get("transform_group_id") for r in reviewed_registry if isinstance(reviewed_registry, list)}) < 10:
    err("reviewed transformation registry is not grouped into meaningful migration units")

# Review 07 F02 reviewed current-field semantics and executable transformation fixture evidence.
semantics_by_current = {r.get("current"): r for r in current_semantics if isinstance(current_semantics, list) and isinstance(r, dict)}
gate("F02-reviewed-current-semantics-cover-current-fields", "F02", len(semantics_by_current) == len(current_fields) and set(semantics_by_current) == set(current_fields), "reviewed current-field semantics must cover every pg_catalog field exactly once", "docs/sda/data-model/current-field-semantics-reviewed.json")
for current in current_fields:
    row = semantics_by_current.get(current, {})
    gate(f"F02-reviewed-current-semantic-{current.replace('.', '-').replace('_', '-')}", "F02", row.get("review_status") == "approved-review07-field-semantic-source" and bool(row.get("review_decision_id")) and bool(row.get("classification")), f"{current} lacks reviewed semantic classification source", "docs/sda/data-model/current-field-semantics-reviewed.json")
    if any(token in current.lower() for token in ["password", "token", "authorization", "auth_", "session", "csrf", "cookie"]):
        gate(f"F02-security-boundary-{current.replace('.', '-').replace('_', '-')}", "F02", row.get("classification") == "security-internal" and "do not migrate" in str(row.get("migration_boundary", "")).lower(), f"{current} security field must have explicit do-not-migrate boundary", "docs/sda/data-model/current-field-semantics-reviewed.json")
fixture_groups = {f.get("transform_group_id") for f in transform_fixtures.get("fixtures", [])} if isinstance(transform_fixtures, dict) else set()
registry_groups = {r.get("transform_group_id") for r in reviewed_registry if isinstance(reviewed_registry, list)}
gate("F02-reviewed-fixtures-cover-transform-groups", "F02", fixture_groups == registry_groups, "reviewed transformation fixtures must cover every transform group", "docs/sda/data-model/transformation-fixtures-reviewed.json")
summary = transform_fixture_report.get("summary", {}) if isinstance(transform_fixture_report, dict) else {}
report_assertions = transform_fixture_report.get("assertions", []) if isinstance(transform_fixture_report, dict) else []
gate("F02-transform-fixture-report-clean", "F02", summary.get("errors") == [] and summary.get("transform_groups") == len(registry_groups) and summary.get("fixtures_executed") == len(registry_groups), "transformation fixture report must execute cleanly for every group", "docs/sda/data-model/transformation-fixture-report.json")
gate("F02-review08-execution-mode", "F02", summary.get("execution_mode") == "actual-disposable-source-target-transformation", "F02 must run actual disposable source-to-target transformation execution, not assertion-ID presence reporting", "docs/sda/data-model/transformation-fixture-report.json")
gate("F02-review08-source-target-row-counts", "F02", summary.get("source_rows_inserted") == len(current_fields) and summary.get("target_rows_inserted") == len(current_fields), "F02 must insert and query source and target rows for every current field", "docs/sda/data-model/transformation-fixture-report.json")
gate("F02-review08-idempotent-rerun", "F02", summary.get("idempotent_rerun") is True, "F02 must prove idempotent rerun behavior", "docs/sda/data-model/transformation-fixture-report.json")
gate("F02-review08-failure-probes", "F02", summary.get("failure_tests", 0) >= 8 and summary.get("failure_tests") == summary.get("failure_tests_caught"), "F02 must catch wrong value, translation, FK, archive, exception, duplicate, relationship and hash mutations", "docs/sda/data-model/transformation-fixture-report.json")
required_f02_classes = {"source-row-identity", "target-value", "reference-final-fk", "archive-created", "owned-exception", "no-loss-count", "no-loss-value-hash", "reviewed-classification"}
seen_f02_classes = {a.get("assertion_class") for a in report_assertions if isinstance(a, dict) and a.get("status") == "passed"}
gate("F02-transform-fixture-required-assertion-classes", "F02", required_f02_classes <= seen_f02_classes, f"missing F02 assertion classes {sorted(required_f02_classes - seen_f02_classes)}", "docs/sda/data-model/transformation-fixture-report.json")
for assertion in report_assertions if isinstance(report_assertions, list) else []:
    if not isinstance(assertion, dict):
        continue
    evidence = assertion.get("evidence") or {}
    gate(assertion.get("assertion_id", "F02-unnamed-transform-assertion"), "F02", assertion.get("status") == "passed" and bool(evidence) and bool(assertion.get("transform_group_id")) and evidence.get("execution_mode") == "review08-disposable-source-to-target-db-execution" and bool(evidence.get("target_output_id")) and bool(evidence.get("source_value_hash")) and bool(evidence.get("target_value_hash")), "named transform assertion must come from disposable DB execution with source/target hashes and output IDs", "docs/sda/data-model/transformation-fixture-report.json")
for row in reviewed_registry if isinstance(reviewed_registry, list) else []:
    ref = row.get("reference_crosswalk_join")
    if isinstance(ref, dict):
        gate(f"F02-final-fk-output-{row.get('current','unknown').replace('.', '-').replace('_', '-')}", "F02", ref.get("final_target_fk_output") not in {"legacy_crosswalk.legacy_id", "proposed_legacy_crosswalk.legacy_id"}, f"{row.get('current')} still treats legacy_crosswalk.legacy_id as final FK output", "docs/sda/data-model/transformation-registry-reviewed.json")

# Review 07 F09 convergence units must be reviewed implementation-authority units tied to passing F02 assertions.
reviewed_units = reviewed_convergence_units.get("migration_units", []) if isinstance(reviewed_convergence_units, dict) else []
generated_units = convergence_units.get("migration_units", []) if isinstance(convergence_units, dict) else []
reviewed_unit_groups = {u.get("transform_group_id") for u in reviewed_units if isinstance(u, dict)}
generated_unit_groups = {u.get("transform_group_id") for u in generated_units if isinstance(u, dict)}
passed_f02_assertions = {a.get("assertion_id") for a in report_assertions if isinstance(a, dict) and a.get("status") == "passed"}
gate("F09-reviewed-convergence-covers-transform-groups", "F09", reviewed_unit_groups == registry_groups and generated_unit_groups == registry_groups, "reviewed and generated convergence units must exactly cover transform groups", "docs/sda/data-model/schema-convergence-units-reviewed.json")
gate("F09-generated-convergence-derived-from-reviewed-source", "F09", reviewed_convergence_units == convergence_units, "generated schema-convergence-units.json must match reviewed convergence source", "docs/sda/data-model/schema-convergence-units.json")
required_unit_keys = {"unit_id", "transform_group_id", "review_status", "review_owner", "depends_on", "source_fields", "target_fields", "transform_assertion_ids", "application_version_matrix", "write_ownership", "exception_schema_sla", "idempotency", "conflict_precedence", "validation", "recovery", "monitoring_window", "cutover_abort_gates", "retirement_proof", "scale_assumption_status"}
unit_ids = {u.get("unit_id") for u in reviewed_units if isinstance(u, dict)}
for unit in reviewed_units if isinstance(reviewed_units, list) else []:
    if not isinstance(unit, dict):
        continue
    uid = unit.get("unit_id", "F09-unnamed-unit")
    missing = sorted(k for k in required_unit_keys if k not in unit or unit.get(k) in (None, "") or (k != "depends_on" and unit.get(k) == []))
    gate(f"F09-unit-required-fields-{uid}", "F09", not missing, f"{uid} missing required convergence fields {missing}", "docs/sda/data-model/schema-convergence-units-reviewed.json")
    gate(f"F09-unit-review-status-{uid}", "F09", unit.get("review_status") == "approved-review07-convergence-unit" and bool(unit.get("review_owner")), f"{uid} lacks reviewed source provenance", "docs/sda/data-model/schema-convergence-units-reviewed.json")
    assertion_ids = set(unit.get("transform_assertion_ids") or [])
    gate(f"F09-unit-f02-assertions-passed-{uid}", "F09", bool(assertion_ids) and assertion_ids <= passed_f02_assertions, f"{uid} must reference only passing F02 assertion IDs", "docs/sda/data-model/transformation-fixture-report.json")
    if any(isinstance(r.get("reference_crosswalk_join"), dict) for r in reviewed_registry if r.get("transform_group_id") == unit.get("transform_group_id")):
        gate(f"F09-unit-final-fk-outputs-{uid}", "F09", bool(unit.get("final_fk_outputs")) and not any(x in {"legacy_crosswalk.legacy_id", "proposed_legacy_crosswalk.legacy_id"} for x in unit.get("final_fk_outputs", [])), f"{uid} must declare concrete final FK outputs or owned exception outputs", "docs/sda/data-model/schema-convergence-units-reviewed.json")
    matrix = unit.get("application_version_matrix", {})
    gate(f"F09-unit-app-version-matrix-{uid}", "F09", all(k in matrix for k in ["current", "expand", "migrate", "contract"]) and "PR #7" in str(matrix) and "WO-002B" in str(matrix), f"{uid} missing no-runtime-change / future WO-002B matrix", "docs/sda/data-model/schema-convergence-units-reviewed.json")
    gate(f"F09-unit-write-ownership-{uid}", "F09", "unauthorized" in str(unit.get("write_ownership", {})).lower(), f"{uid} must state target writes unauthorized in PR #7", "docs/sda/data-model/schema-convergence-units-reviewed.json")
    gate(f"F09-unit-exception-sla-{uid}", "F09", "owner" in str(unit.get("exception_schema_sla", {})).lower() and "abort" in str(unit.get("exception_schema_sla", {})).lower(), f"{uid} exception schema/SLA must include owner and abort condition", "docs/sda/data-model/schema-convergence-units-reviewed.json")
    gate(f"F09-unit-idempotency-{uid}", "F09", "source_row_key" in str(unit.get("idempotency", {})), f"{uid} must use source-row idempotency key", "docs/sda/data-model/schema-convergence-units-reviewed.json")
    gate(f"F09-unit-recovery-boundary-{uid}", "F09", "no production rollback" in str(unit.get("recovery", {})).lower() and "design only" in str(unit.get("recovery", {})).lower(), f"{uid} must not claim production rollback/migration authority", "docs/sda/data-model/schema-convergence-units-reviewed.json")
    gate(f"F09-unit-cutover-gates-{uid}", "F09", any("SDA" in g for g in unit.get("cutover_abort_gates", [])) and any("WO-002B" in g for g in unit.get("cutover_abort_gates", [])), f"{uid} cutover gates must preserve SDA and future WO-002B authority", "docs/sda/data-model/schema-convergence-units-reviewed.json")
    gate(f"F09-unit-scale-status-{uid}", "F09", unit.get("scale_assumption_status") == "owner-pending; not national production readiness evidence", f"{uid} overclaims scale readiness", "docs/sda/data-model/schema-convergence-units-reviewed.json")

# OpenAPI field coverage and auth policy.
ops = openapi_ops.get("operations", []) if isinstance(openapi_ops, dict) else []
if len(ops) < 50:
    err(f"OpenAPI operation inventory too small: {len(ops)}")
for expected_public in ["GET /", "GET /api/v1/health", "POST /api/v1/auth/login"]:
    if route_policies.get(expected_public, {}).get("auth") != "public":
        err(f"{expected_public} expected public auth policy, got {route_policies.get(expected_public)}")
if route_policies != reviewed_route_policies:
    err("openapi-expected-route-policies must exactly mirror independently reviewed route policy registry")
for route_key, row in reviewed_route_policies.items() if isinstance(reviewed_route_policies, dict) else []:
    gate(f"F08-reviewed-route-policy-{route_key.replace(' ', '-').replace('/', '-')}", "F08", row.get("policy_source") == "human-reviewed-route-policy-source" and row.get("review_owner") and row.get("review_decision_id") and "generated from exact FastAPI" not in str(row).lower(), "route policy must be independently reviewed and not claim observed AST as expected authority", "docs/sda/data-model/openapi-reviewed-route-policies.json")
for key, roles in {"GET /api/v1/addresses": {"viewer","editor","admin"}, "GET /api/v1/addresses/{address_id}": {"viewer","editor","admin"}}.items():
    if set(route_policies.get(key, {}).get("roles", [])) != roles:
        err(f"{key} roles must be viewer/editor/admin")
if route_policies.get("POST /api/v1/auth/logout", {}).get("auth") != "session-required":
    err("logout must be classified session-required, not public")
gate("F08-review08-api-contract-summary", "F08", api_projection_summary.get("execution_mode") == "review08-independent-api-projection-contracts" and api_projection_summary.get("operations") == len(ops) and api_projection_summary.get("generic_success_payloads") == 0 and api_projection_summary.get("errors") == [], "F08 API projection assertions must be Review 08 independent contracts with no generic successful payload envelopes", "docs/sda/data-model/openapi-policy-projection-assertions.json")
for op in ops:
    route_key = f"{op.get('method')} {op.get('path')}"
    if route_key not in route_policies:
        err(f"OpenAPI operation {route_key} missing expected policy row")

    expected = route_policies.get(route_key, {})
    if expected.get("method") != op.get("method") or expected.get("path") != op.get("path") or expected.get("operation_id") != op.get("operation_id"):
        err(f"route policy identity mismatch for {route_key}")
    observed = expected.get("observed") or op.get("policy", {}).get("observed") or {}
    if observed and (expected.get("handler") != observed.get("handler") or expected.get("method") != observed.get("method")):
        err(f"route policy reviewed row disagrees with observed AST handler/method for {route_key}")

    contract = projection_contracts.get(op.get("operation_id"), {}) if isinstance(projection_contracts, dict) else {}
    if contract.get("review_status") not in {"reviewed-api-projection-r08"}:
        err(f"OpenAPI operation {op.get('operation_id')} missing reviewed projection contract")
    gate(f"F08-reviewed-projection-contract-{op.get('operation_id')}", "F08", bool(contract.get("policy_source") == "human-reviewed-field-projection-source" and contract.get("review_owner") and contract.get("review_decision_id")), "projection contract must be independently reviewed with owner and decision id", "docs/sda/data-model/openapi-reviewed-projection-contracts.json")
    for field in contract.get("fields", []) if isinstance(contract, dict) else []:
        fname = str(field.get("field", "")).lower()
        direction = str(field.get("direction", ""))
        target_projection = str(field.get("target_projection", ""))
        gate(f"F08-field-projection-{field.get('test', op.get('operation_id'))}", "F08", bool(field.get("review_status") and field.get("classification_owner") and field.get("target_projection") and field.get("adapter") and field.get("deprecation_rule")), "field projection must include reviewed status, classification owner, target projection, adapter, and deprecation rule", "docs/sda/data-model/openapi-reviewed-projection-contracts.json")
        if any(tok in fname for tok in ["authorization", "cookie", "token", "password", "csrf", "session"]):
            gate(f"F08-security-field-not-migrated-{field.get('test', op.get('operation_id'))}", "F08", "not-migrated" in target_projection and "business" in target_projection and field.get("classification") == "security-internal", "credential/header/session fields must not be business-data migrated or archived", "docs/sda/data-model/openapi-reviewed-projection-contracts.json")
        if direction.startswith("response:"):
            gate(f"F08-response-field-not-generic-{field.get('test', op.get('operation_id'))}", "F08", not (fname == "response" and field.get("type") == "object") and "source_payload_archive or typed target projection" not in target_projection, "response projections must not remain generic response:object placeholders", "docs/sda/data-model/openapi-reviewed-projection-contracts.json")
    contract_fields = contract.get("fields", []) if isinstance(contract, dict) else []
    if not contract_fields:
        err(f"OpenAPI operation {op.get('operation_id')} projection contract has no fields")
    for resp in op.get("responses", []):
        if str(resp.get("status", "")).startswith("2") and not resp.get("fields"):
            bad = [cf for cf in contract_fields if cf.get("direction") == f"response:{resp.get('status')}" and cf.get("field") == "<empty/error envelope>"]
            if bad:
                err(f"OpenAPI operation {op.get('operation_id')} has generic empty 2xx projection contract")
    for cf in contract_fields:
        for req_key in ["classification", "target_projection", "release_prerequisite", "compatibility_impact", "adapter", "deprecation_rule", "test"]:
            if not cf.get(req_key):
                err(f"OpenAPI contract {op.get('operation_id')} field {cf.get('field')} missing {req_key}")
    if not op.get("operation_id") or not op.get("method") or not op.get("path"):
        err(f"OpenAPI operation missing identity: {op}")
    if "policy" not in op or "auth" not in op.get("policy", {}):
        err(f"OpenAPI operation {op.get('operation_id')} missing authorization policy")
    observed_policy = op.get("policy", {}).get("observed", {}) if isinstance(op.get("policy"), dict) else {}
    if observed_policy.get("analysis") != "function-ast-boundary":
        err(f"OpenAPI operation {op.get('operation_id')} observed policy not derived from precise AST boundary")
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
if physical_report.get("missing_required_triggers"):
    err(f"target schema missing required semantic triggers: {physical_report.get('missing_required_triggers')}")
if physical_report.get("trigger_count", 0) < 7:
    err("target schema does not catalog required semantic triggers")
if len(target_catalog.get("constraints", [])) < physical_report.get("constraint_count", 0):
    err("target catalog missing constraint detail rows")
if len(target_catalog.get("indexes", [])) < physical_report.get("index_count", 0):
    err("target catalog missing index detail rows")
if len(physical_report.get("scenario_results", {})) != 7:
    err("target report does not show seven independently executed positive scenarios")
if len(physical_report.get("negative_results", {})) < 11:
    err("target report does not show required negative fixture assertions, including Review 07 F06 authority negatives")
lifecycle_assertions = physical_report.get("lifecycle_transition_assertions", {}) if isinstance(physical_report, dict) else {}
expected_lifecycle_edges = sum(len(edges) for edges in lifecycle_transitions.values()) if isinstance(lifecycle_transitions, dict) else 0
gate("F07-lifecycle-positive-graph-executed", "F07", expected_lifecycle_edges > 0 and len(lifecycle_assertions) == expected_lifecycle_edges and all(v.get("status") == "passed" for v in lifecycle_assertions.values()), "every authored lifecycle transition must be loaded into lifecycle_transition_policy and pass validate_lifecycle_transition", "docs/sda/data-model/target-schema-catalog.json")
for assertion_id, result in lifecycle_assertions.items() if isinstance(lifecycle_assertions, dict) else []:
    gate(assertion_id, "F07", result.get("status") == "passed" and result.get("permission_key") and result.get("authority") and result.get("audit_event") and result.get("public_effect"), "lifecycle assertion must include permission, authority, audit, and public-effect metadata", "docs/sda/data-model/target-schema-catalog.json")
review07_scenario_assertions = physical_report.get("review07_scenario_assertions", {}) if isinstance(physical_report, dict) else {}
review08_scenario_query_results = physical_report.get("review08_scenario_query_results", {}) if isinstance(physical_report, dict) else {}
review08_query_assertions = [a for scenario in review08_scenario_query_results.values() if isinstance(scenario, dict) for a in scenario.get("assertions", {}).values()]
gate("F10-review08-persisted-scenario-query-results", "F10", len(review08_scenario_query_results) == 7 and len(review08_query_assertions) >= 63 and all(v.get("status") == "passed" for v in review08_scenario_query_results.values()), "Review 08 F10 must query persisted target DB state for all seven scenarios", "docs/sda/data-model/review08-scenario-query-report.json")
for scenario, result in review08_scenario_query_results.items() if isinstance(review08_scenario_query_results, dict) else []:
    required_sections = ["entity_ids", "relationship_edges", "geometry_and_provenance", "publication_releases", "public_projection", "operator_projection", "historical_output"]
    gate(f"F10-review08-query-sections-{scenario}", "F10", result.get("status") == "passed" and all(result.get(section) for section in required_sections) and result.get("queried_fixture_rows", 0) == result.get("expected_fixture_rows", -1), "F10 scenario must include persisted query evidence for entities, relationships, geometry, publication, projections and history", "docs/sda/data-model/review08-scenario-query-report.json")
gate("F04-F05-F10-review07-scenario-assertions-present", "F04/F05/F10", len(review07_scenario_assertions) >= 49 and all(v.get("status") == "passed" for v in review07_scenario_assertions.values()), "Review 07 F04/F05/F10 named scenario/temporal assertions must all pass", "docs/sda/data-model/target-schema-catalog.json")
for assertion_id, result in review07_scenario_assertions.items() if isinstance(review07_scenario_assertions, dict) else []:
    gate(assertion_id, result.get("finding", "F04/F05/F10"), result.get("status") == "passed", "Review 07 scenario/cardinality/temporal assertion failed", "docs/sda/data-model/review07-scenario-temporal-assertions.md")
harness_regression = physical_report.get("negative_harness_regression") or {}
if harness_regression.get("status") != "passed" or harness_regression.get("error_class") != "NegativeFixtureDidNotFail":
    err("negative harness false-pass regression did not prove successful invalid actions fail outside the exception handler")
for neg_name, neg_result in (physical_report.get("negative_results", {}) or {}).items():
    if not isinstance(neg_result, dict):
        err(f"negative fixture {neg_name} used legacy string result instead of expected exception metadata")
        continue
    if neg_result.get("status") != "rejected-by-real-execution":
        err(f"negative fixture {neg_name} was not produced by real SQL/policy execution: {neg_result}")
    if not neg_result.get("expected_message") or not neg_result.get("error_class"):
        err(f"negative fixture {neg_name} missing expected error message/class metadata")
required_f06_negatives = {"invalid-geometry-decision-type", "invalid-geometry-permission", "invalid-geometry-territorial-scope", "invalid-geometry-evidence-link"}
negative_results = physical_report.get("negative_results", {}) or {}
gate("F06-geometry-authority-negative-suite", "F06", required_f06_negatives <= set(negative_results), "geometry promotion must reject wrong decision type, permission, territorial scope, and evidence link", "docs/sda/data-model/target-schema-catalog.json")
for neg_name in sorted(required_f06_negatives):
    result = negative_results.get(neg_name, {}) if isinstance(negative_results, dict) else {}
    gate(f"F06-{neg_name}", "F06", bool(isinstance(result, dict) and result.get("status") == "rejected-by-real-execution" and result.get("error_class")), "F06 negative authority fixture must be rejected by real SQL trigger execution", "docs/sda/data-model/target-schema-catalog.json")
if "decision_row.details_json->>'permission_key' IS DISTINCT FROM rule.promotion_permission" not in physical_sql:
    err("geometry promotion trigger does not bind actor permission to geometry_role_matrix promotion_permission")
if "decision_row.decision_type <> 'approve-geometry'" not in physical_sql or "geometry promotion institution or territorial scope mismatch" not in physical_sql:
    err("geometry promotion trigger does not bind approve-geometry decision type and territorial scope")
if "geometry decision evidence link mismatch" not in physical_sql or "geometry decision observation link mismatch" not in physical_sql:
    err("geometry promotion trigger does not bind evidence and observation links")
if "geometry quality authority actor mismatch" not in physical_sql:
    err("geometry promotion trigger does not bind quality authority actor")
if "Errors: 0" not in report_text:
    err("Review 06 semantic report does not show Errors: 0")
if "Current migrations applied to disposable PostgreSQL/PostGIS" not in report_text:
    err("Review 06 report missing disposable PostGIS assertion")

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
if len(scenarios.get("multi-unit-building", {}).get("unit", [])) < 2:
    err("multi-unit-building scenario must contain multiple unit rows")
if len(scenarios.get("corrected-superseded-address", {}).get("location_record_version", [])) < 2:
    err("corrected-superseded-address scenario must contain at least two linked versions")
if len(scenarios.get("corrected-superseded-address", {}).get("publication_release", [])) < 2:
    err("corrected-superseded-address scenario must contain release history")
if len(scenarios.get("administrative-boundary-change", {}).get("administrative_unit_version", [])) < 2:
    err("administrative-boundary-change scenario must contain old and new admin versions")
# Review 07 F04/F10: multi-unit scenario must prove separate canonical unit records, aliases, release items, and parent-building links.
multi_unit = scenarios.get("multi-unit-building", {})
mu_records = [r for r in (multi_unit.get("location_record", []) if isinstance(multi_unit, dict) else []) if r.get("record_type") == "unit"]
mu_versions_all = multi_unit.get("location_record_version", []) if isinstance(multi_unit, dict) else []
mu_unit_record_ids = {r.get("location_record_id") for r in mu_records}
mu_versions = [v for v in mu_versions_all if v.get("location_record_id") in mu_unit_record_ids]
mu_aliases = multi_unit.get("public_code_alias", []) if isinstance(multi_unit, dict) else []
mu_items = multi_unit.get("publication_release_item", []) if isinstance(multi_unit, dict) else []
mu_links = multi_unit.get("location_record_object_link", []) if isinstance(multi_unit, dict) else []
gate("F04-multi-unit-independent-canonical-records", "F04", len(mu_records) >= 2 and len({r.get("location_record_id") for r in mu_records}) >= 2 and all(r.get("record_type") == "unit" for r in mu_records), "multi-unit-building must contain at least two independent canonical unit location_records", "docs/sda/data-model/representative-records/machine-readable-fixtures.json")
gate("F10-multi-unit-distinct-aliases-release-items", "F10", len(mu_aliases) >= 2 and len(mu_items) >= 2 and len({a.get("location_record_id") for a in mu_aliases}) >= 2 and len({i.get("location_record_id") for i in mu_items}) >= 2, "multi-unit-building must have distinct aliases and release items per canonical unit", "docs/sda/data-model/representative-records/machine-readable-fixtures.json")
version_ids = {v.get("location_record_version_id") for v in mu_versions}
versions_with_primary = {l.get("location_record_version_id") for l in mu_links if l.get("object_role") == "primary-subject"}
versions_with_parent = {l.get("location_record_version_id") for l in mu_links if l.get("object_role") == "parent-building"}
gate("F04-multi-unit-parent-building-links", "F04", len(version_ids) >= 2 and version_ids <= versions_with_primary and version_ids <= versions_with_parent, "each multi-unit canonical unit version must have primary-subject and parent-building links", "docs/sda/data-model/representative-records/machine-readable-fixtures.json")
negative_fixtures = fixtures.get("negative_fixtures", {}) if isinstance(fixtures, dict) else {}
for required_negative in ["invalid-cardinality-primary-object", "invalid-temporal-overlap", "invalid-state-transition", "invalid-subject-reference", "invalid-geometry-role-type", "invalid-publication-prerequisite", "invalid-self-supersession"]:
    if required_negative not in negative_fixtures:
        err(f"missing negative fixture {required_negative}")

# Subject registry / code authority / lifecycle separation.
if "administrative_unit.stable_code" in fields:
    err("administrative_unit.stable_code remains as duplicate administrative code authority")
if "registry_subject.subject_native_id" in fields:
    err("registry_subject must be normalized to one native identifier; subject_native_id remains")
if "registry_subject.native_id" not in fields:
    err("registry_subject.native_id missing")
for fq, vocab in (model.get("lifecycle_field_bindings", {}) if isinstance(model, dict) else {}).items():
    if fields.get(fq, {}).get("vocabulary") != vocab or fields.get(fq, {}).get("lifecycle_graph") != vocab:
        err(f"{fq} is not bound to lifecycle graph {vocab}")
stateful = [fq for fq, f in fields.items() if fq.split('.',1)[1] in {"lifecycle_state","case_state","release_state","quality_state","authority_state","name_status"}]
for fq in stateful:
    if fq not in (model.get("lifecycle_field_bindings", {}) if isinstance(model, dict) else {}):
        err(f"stateful field {fq} missing authoritative lifecycle_field_bindings entry")
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
        for required_edge_key in ["from", "to", "event", "permission_key", "institutional_scope", "authority", "evidence", "audit_event", "public_effect", "reversal", "denial_behavior", "time_rule", "invalid_behavior"]:
            if not edge.get(required_edge_key):
                err(f"{vocab} lifecycle edge missing {required_edge_key}: {edge}")
for forbidden in [("approved", "rejected"), ("approved", "draft"), ("closed", "duplicate-review"), ("cancelled", "evidence-approved"), ("accepted-canonical", "disputed")]:
    for vocab, edges in lifecycle_transitions.items() if isinstance(lifecycle_transitions, dict) else []:
        if any((e.get("from"), e.get("to")) == forbidden for e in edges):
            err(f"forbidden lifecycle transition {forbidden[0]}->{forbidden[1]} present in {vocab}")


# Review 06 exact model semantic gates.
record_types = set(vocabs.get("record_type", {}).get("values", {}))
cardinality = model.get("record_object_cardinality", {}) if isinstance(model, dict) else {}
if "standard-address" in cardinality:
    err("record_object_cardinality must not use non-vocabulary standard-address")
missing_record_types = record_types - set(cardinality)
if missing_record_types:
    err(f"record_object_cardinality missing canonical record types {sorted(missing_record_types)}")
for rt, roles in cardinality.items():
    if rt not in record_types:
        err(f"record_object_cardinality key {rt} not in record_type vocabulary")
    if not any(v.get("required") and v.get("min") == 1 and v.get("max") >= 1 for v in roles.values() if isinstance(v, dict)):
        err(f"record_object_cardinality {rt} has no required role with min/max")
for fq in ["geometry_version.promotion_decision_event_id", "geometry_version.promotion_evidence_object_id", "geometry_version.promotion_authority_scope"]:
    if fq not in fields:
        err(f"geometry promotion authority field missing: {fq}")
catalog_tables_seen = {c.get("table_name") for c in (target_catalog.get("columns", []) if isinstance(target_catalog, dict) else [])}
if "lifecycle_transition_policy" not in catalog_tables_seen:
    err("target schema does not include executable lifecycle_transition_policy table")

# ADR Review 07 reconciliation must cite named assertions, not aggregate-only evidence.
mutation_summary = semantic_mutation_report.get("summary", {}) if isinstance(semantic_mutation_report, dict) else {}
gate("F12-semantic-mutation-suite-passed", "F12", mutation_summary.get("status") == "passed" and mutation_summary.get("mutations", 0) >= 8 and mutation_summary.get("failed") == 0, "semantic mutation suite must catch all required defect classes", "docs/sda/data-model/semantic-mutation-test-report.json")
mutation_names = {r.get("mutation") for r in semantic_mutation_report.get("results", [])} if isinstance(semantic_mutation_report, dict) else set()
for required_mutation in ["incorrect-transformation-final-fk-output", "missing-required-semantic-trigger", "wrong-route-policy-source", "credential-projection-business-archive", "invalid-multi-unit-scenario", "temporal-chain-reciprocity-break", "unexpected-negative-operation-success", "geometry-permission-binding-removed"]:
    gate(f"F12-mutation-{required_mutation}", "F12", required_mutation in mutation_names, f"semantic mutation report missing {required_mutation}", "docs/sda/data-model/semantic-mutation-test-report.json")

# ADR Review 07 reconciliation must cite named assertions, not aggregate-only evidence.
if "Generated checks: 41" in adr_matrix_text or "Errors: 0`" in adr_matrix_text:
    err("ADR evidence matrix must not cite stale aggregate check counts as acceptance evidence")
for adr_id in ["ADR-005", "ADR-006", "ADR-007", "ADR-008", "ADR-009"]:
    if adr_id not in adr_matrix_text:
        err(f"ADR evidence matrix missing {adr_id}")
for required in ["F02-source-row-identity", "F04-cardinality-positive", "F05-admin-boundary", "F06-geometry-authority", "F07-lifecycle-positive", "F09-reviewed", "F10-scenario"]:
    if required not in adr_matrix_text:
        err(f"ADR evidence matrix missing named assertion family {required}")

# ADRs and ERD coverage.
if 'write(f"docs/sda/adrs/' in pipeline_text or 'write("docs/sda/adrs/' in pipeline_text:
    err("ADRs 005-009 must not be generated output from pipeline")
for adr in range(5, 10):
    matches = sorted((SDA / "adrs").glob(f"ADR-{adr:03d}-*.md"))
    if not matches:
        err(f"missing ADR-{adr:03d}")
        continue
    text = matches[0].read_text(encoding="utf-8")
    for heading in ["## Alternatives considered", "## Security and privacy implications", "## Performance and operational trade-offs", "## Migration consequences", "## Failure modes", "## Consequences", "## Acceptance checks", "## Evidence-linked conditions", "## Unresolved RFIs", "## Acceptance tests"]:
        if heading not in text:
            err(f"{matches[0].name} missing {heading}")
for entity in ["administrative_code_history", "registry_subject", "source_payload_archive", "legacy_crosswalk"]:
    if entity not in erd_text:
        err(f"Mermaid ERD missing entity {entity}")

# Review 05 finding rows.
for i in [2,4,5,6,7,8,9,10,11,12,13]:
    if not re.search(rf"\| F{i:02d} \| Resolved for SDA Review 07:", review_text):
        err(f"Review 06 resolution row F{i:02d} not updated for Review 07")

report_lines = [
    "# Design Consistency Report",
    "",
    f"Generated checks: {len(assertion_registry)}",
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
        f"- Named assertion gates: {len(assertion_registry)}",
        f"- F02 transform assertions: {summary.get('assertions_executed', 0)}",
        f"- F02 source/target rows executed: {summary.get('source_rows_inserted', 0)}/{summary.get('target_rows_inserted', 0)}",
        f"- F02 failure probes caught: {summary.get('failure_tests_caught', 0)}/{summary.get('failure_tests', 0)}",
        f"- F09 convergence units: {len(reviewed_units) if isinstance(reviewed_units, list) else 0}",
        f"- Multi-unit canonical records: {len(mu_records)}",
        f"- F07 lifecycle transitions executed: {len(lifecycle_assertions) if isinstance(lifecycle_assertions, dict) else 0}",
        f"- F04/F05/F10 scenario assertions: {len(review07_scenario_assertions) if isinstance(review07_scenario_assertions, dict) else 0}",
        f"- F10 persisted scenario DB query assertions: {sum(len(v.get('assertions', {})) for v in physical_report.get('review08_scenario_query_results', {}).values()) if isinstance(physical_report.get('review08_scenario_query_results', {}), dict) else 0}",
        f"- F06 geometry authority negatives: {len(required_f06_negatives & set(negative_results)) if isinstance(negative_results, dict) else 0}",
        f"- F08 API projection assertions: {api_projection_assertions.get('summary', {}).get('assertions', 0) if isinstance(api_projection_assertions, dict) else 0}",
        f"- F12 semantic mutations caught: {mutation_summary.get('caught', 0) if isinstance(mutation_summary, dict) else 0}",
    ])
report = "\n".join(report_lines) + "\n"
(DM / "design-consistency-report.md").write_text(report, encoding="utf-8")
print(report, end="")
if errors:
    sys.exit(1)
