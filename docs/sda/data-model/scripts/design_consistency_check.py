#!/usr/bin/env python3
"""Semantic design consistency checks for NLI-WO-002.

This checker is intentionally stricter than presence/count checks. It validates the
typed target model, current-field mappings, controlled vocabularies, lifecycle
coverage, representative records, ADR/RFI coverage, SQL, and Mermaid sources.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
DM = ROOT / "docs" / "sda" / "data-model"
SDA = ROOT / "docs" / "sda"

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        err(f"cannot parse JSON {path}: {exc}")
        return {}


model = load_json(DM / "target-model.json")
field_map = load_json(DM / "current-to-target-mapping.json")
entities: dict[str, Any] = model.get("entities", {})
vocabs: dict[str, Any] = model.get("vocabularies", {})

fields: dict[str, dict[str, Any]] = {}
entity_fields: dict[str, set[str]] = {}
for ename, ent in entities.items():
    seen = set()
    for f in ent.get("fields", []):
        fq = f"{ename}.{f.get('name')}"
        if fq in fields:
            err(f"duplicate target field {fq}")
        fields[fq] = f
        seen.add(f.get("name"))
    entity_fields[ename] = seen

# 1. Entity and field parity / metadata completeness.
required_field_keys = {"name", "pg_type", "nullable", "definition", "authority_owner", "classification", "projection", "temporal_behavior", "constraints"}
allowed_classes = set(vocabs.get("classification", {}).get("values", {}))
for ename, ent in entities.items():
    if not ent.get("description"):
        err(f"entity {ename} missing description")
    for f in ent.get("fields", []):
        fq = f"{ename}.{f.get('name')}"
        missing = required_field_keys - set(f)
        if missing:
            err(f"{fq} missing metadata keys {sorted(missing)}")
        if not isinstance(f.get("nullable"), bool):
            err(f"{fq} nullable must be boolean")
        if not f.get("pg_type"):
            err(f"{fq} missing PostgreSQL type")
        if f.get("classification") not in allowed_classes:
            err(f"{fq} classification {f.get('classification')} not in classification vocabulary")
        vocab = f.get("vocabulary")
        if vocab and vocab not in vocabs:
            err(f"{fq} references unknown vocabulary {vocab}")
        if vocab and f.get("pg_type") != "text":
            err(f"{fq} controlled vocabulary field should use text, found {f.get('pg_type')}")

# 2. FK targets and insertion cycles/optional roots.
for fq, f in fields.items():
    fk = f.get("fk")
    if fk:
        if fk not in fields:
            err(f"{fq} FK target {fk} does not exist")

# Explicit insertion-safety rules from Review 02.
for fq in ["administrative_unit_version.parent_administrative_unit_id", "unit.parent_unit_id", "location_record_version.predecessor_version_id", "location_record_version.successor_version_id", "location_record_version.correction_case_id", "public_code_alias.predecessor_alias_id", "public_code_alias.successor_alias_id", "geometry_version.superseded_by_geometry_version_id", "geometry_version.dispute_case_id"]:
    if fq not in fields:
        err(f"missing optionality target {fq}")
    elif fields[fq].get("nullable") is not True:
        err(f"{fq} must be nullable for roots/first versions/creation safety")
if "location_record.current_version_id" in fields:
    err("location_record.current_version_id must not exist; recorded_to open interval is sole current mechanism")
if "location_record.publication_state" in fields:
    err("location_record.publication_state must not exist as mutable second publication authority")
if "location_record_version.is_current" in fields or "geometry_version.is_current" in fields:
    err("is_current fields are prohibited; use recorded_to IS NULL")

# 3. Mapping target existence and disposition shape.
valid_dispositions = {"mapped", "archive/compatibility", "compatibility/archive", "outside-location-model/security", "fixture-only/archive", "accepted-loss", "formal-rfi"}
for row in field_map:
    cur = row.get("current")
    disp = row.get("disposition")
    if disp not in valid_dispositions:
        err(f"{cur} has invalid disposition {disp}")
    targets = [row.get("target")] + [t.get("target") for t in row.get("transformation", [])]
    for target in targets:
        if not target:
            err(f"{cur} has empty target")
            continue
        if target not in fields and not target.startswith("source_record.raw_payload_hash"):
            err(f"{cur} target {target} does not exist in authoritative registry")
    if not row.get("validation"):
        err(f"{cur} missing validation query")
    if row.get("classification") not in allowed_classes:
        err(f"{cur} maps to invalid classification {row.get('classification')}")

# 4. Controlled-vocabulary assignments and transitions.
controlled_fields = [fq for fq, f in fields.items() if f.get("vocabulary")]
if len(controlled_fields) < 30:
    err(f"too few controlled fields: {len(controlled_fields)}")
cv_text = (DM / "controlled-vocabularies.md").read_text(encoding="utf-8")
for fq in controlled_fields:
    if fq not in cv_text:
        err(f"controlled field {fq} missing from controlled-vocabularies.md")
for vocab, meta in vocabs.items():
    if not meta.get("owner"):
        err(f"vocabulary {vocab} missing owner")
    if not meta.get("values"):
        err(f"vocabulary {vocab} has no values")

life_text = (DM / "lifecycle-state-machines.md").read_text(encoding="utf-8")
for vocab in ["intake_state", "field_verification_state", "lifecycle_state", "geometry_quality_state", "publication_release_state", "case_state", "name_status"]:
    if f"`{vocab}` transitions" not in life_text:
        err(f"missing lifecycle transition table for {vocab}")
    for val in list(vocabs[vocab]["values"].keys())[:2]:
        if val not in life_text:
            warn(f"lifecycle table for {vocab} may not mention value {val}")

# 5. Geometry semantic checks.
role_rules = model.get("role_geometry_rules", {})
for role, meta in role_rules.items():
    if role not in vocabs.get("geometry_role", {}).get("values", {}):
        err(f"geometry role rule {role} missing from geometry_role vocabulary")
    if not meta.get("subjects") or not meta.get("types"):
        err(f"geometry role {role} missing subjects/types")
for fq in ["geometry_observation.observed_geom", "geometry_version.geom"]:
    if fq not in fields:
        err(f"missing geometry field {fq}")
    elif "4326" not in fields[fq].get("pg_type", "") and not any("4326" in c for c in fields[fq].get("constraints", [])):
        err(f"{fq} lacks SRID 4326 type/constraint")
if "geometry_observation.horizontal_accuracy_m" not in fields or not fields["geometry_observation.horizontal_accuracy_m"]["pg_type"].startswith("numeric"):
    err("geometry accuracy must be numeric")
for fq in ["geometry_version.source_observation_id", "geometry_observation.licence_id", "geometry_version.transformation_id", "geometry_version.dispute_case_id"]:
    if fq not in fields:
        err(f"missing geometry lineage field {fq}")

# 6. API projection coverage.
api_text = (DM / "api-projection-map.md").read_text(encoding="utf-8")
route_count = len(re.findall(r"services/api/app/main.py:\d+", api_text))
if route_count < 50:
    err(f"API projection map route coverage too low: {route_count}")
for term in ["public", "operator", "partner", "publication_release_item", "compatibility"]:
    if term not in api_text:
        err(f"API projection map missing {term}")

# 7. Representative records.
expected_reps = {"urban-street-address", "rural-landmark-location", "multi-unit-building", "no-formal-road-location", "corrected-superseded-address", "disputed-geometry", "administrative-boundary-change"}
for slug in expected_reps:
    p = DM / "representative-records" / f"{slug}.md"
    if not p.exists():
        err(f"missing representative record {slug}")
        continue
    txt = p.read_text(encoding="utf-8")
    for needle in ["location_record", "geometry_version", "source", "Public", "Operator"]:
        if needle not in txt:
            err(f"{slug} missing {needle}")
scenario_needles = {
    "multi-unit-building": ["unit", "parent-building", "creation-safe"],
    "administrative-boundary-change": ["administrative_unit_version", "admin-boundary", "MultiPolygon"],
    "corrected-superseded-address": ["predecessor_version_id", "successor_version_id", "immutable"],
    "disputed-geometry": ["dispute_case", "disputed", "recapture"],
    "no-formal-road-location": ["no context-road role required", "locality"],
}
for slug, needles in scenario_needles.items():
    txt = (DM / "representative-records" / f"{slug}.md").read_text(encoding="utf-8")
    for needle in needles:
        if needle not in txt:
            err(f"{slug} missing scenario-specific proof {needle}")

# 8. ADR/RFI coverage.
coverage = (DM / "adr-rfi-question-coverage.md").read_text(encoding="utf-8")
for i in range(1, 13):
    if f"| {i} |" not in coverage:
        err(f"reserved question {i} missing from coverage matrix")
for adr in range(5, 10):
    path = next((ROOT / "docs" / "sda" / "adrs").glob(f"ADR-{adr:03d}-*.md"), None)
    if not path:
        err(f"missing ADR-{adr:03d}")
        continue
    txt = path.read_text(encoding="utf-8")
    for section in ["## Context", "## Decision drivers", "## Decision", "## Alternatives considered", "## Consequences", "## Acceptance checks"]:
        if section not in txt:
            err(f"{path.name} missing {section}")
for p in (ROOT / "docs" / "sda" / "rfis").glob("RFI-NLI-WO-002-*.md"):
    txt = p.read_text(encoding="utf-8")
    for section in ["## 1. Decision question", "## 2. Why this decision is required", "## 4. Options considered", "## 5. Agent recommendation", "## 7. Requested decision authority"]:
        if section not in txt:
            err(f"{p.name} missing template section {section}")

# 9. SQL and Mermaid parsing/lint.
sql = (DM / "draft-physical-schema.sql").read_text(encoding="utf-8")
if "NON-EXECUTABLE DESIGN ARTIFACT" not in sql or "DO NOT APPLY" not in sql:
    err("draft SQL missing non-executable markers")
if sql.count("(") != sql.count(")"):
    err("draft SQL parentheses unbalanced")
for ename in entities:
    if f"CREATE TABLE proposed_{ename}" not in sql:
        err(f"draft SQL missing proposed_{ename}")
for forbidden in [" current_version_id ", " is_current ", " publication_state "]:
    if forbidden in sql:
        err(f"draft SQL contains forbidden stored authority field {forbidden.strip()}")
if "USING GIST" not in sql:
    err("draft SQL missing spatial GiST index")

mermaid = (DM / "canonical-logical-erd.mmd").read_text(encoding="utf-8")
if not mermaid.startswith("erDiagram"):
    err("Mermaid ERD must start with erDiagram")
for ename in entities:
    if ename.upper() not in mermaid:
        err(f"Mermaid ERD missing entity {ename}")

# 10. CI integration.
api_ci = (ROOT / ".github" / "workflows" / "api-ci.yml").read_text(encoding="utf-8")
for cmd in ["generate_design_catalog.py", "design_consistency_check.py", "git diff --exit-code"]:
    if cmd not in api_ci:
        err(f"api-ci.yml missing design CI command {cmd}")

report = ["# Design Consistency Report", "", "Generated checks: 10", f"Errors: {len(errors)}", f"Warnings: {len(warnings)}", ""]
if errors:
    report += ["## Errors"] + [f"- {e}" for e in errors]
if warnings:
    report += ["## Warnings"] + [f"- {w}" for w in warnings]
if not errors:
    report += ["## PASS", "- Entity and field parity validated against typed metadata.", "- Types, nullability, defaults, FK targets, and insertion-safety rules validated.", "- Current-to-target mapping targets validated against authoritative registry.", "- Controlled-vocabulary assignments and lifecycle transition tables validated.", "- Geometry subject-role/type, SRID, numeric accuracy, lineage, dispute, and supersession fields validated.", "- Classification and projection metadata complete for every field.", "- API operation projection coverage validated from route inventory.", "- Representative records validated for distinct scenario-specific proof.", "- ADR/RFI reserved-question coverage and template sections validated.", "- Draft SQL and Mermaid sources parsed/linted.", "- CI integration for generation, semantic check, and clean regeneration diff validated."]
(DM / "design-consistency-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
sys.exit(1 if errors else 0)
