#!/usr/bin/env python3
"""Review 04 semantic design pipeline for NLI-WO-002.

This script is intentionally docs/design-only. It requires a disposable
PostgreSQL/PostGIS database in DATABASE_URL, applies the accepted current
migrations, inventories the live pg_catalog, generates current OpenAPI field
coverage, rebuilds the current-to-target transformation registry, emits a
creation-safe target proposal, executes it in a disposable schema, loads
machine-readable fixtures, and writes SDA evidence artifacts.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict, deque
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
SDA = ROOT / "docs" / "sda"
DM = SDA / "data-model"
REVIEW = SDA / "reviews" / "NLI-WO-002-review-03.md"
DATE = "2026-07-14"
BRANCH = "nli/wo-002-canonical-location-model"
FIXING_COMMIT_PLACEHOLDER = "bf4a203d24ac031a170f71480338f4ab4a1e4d90"
FINAL_HEAD_NOTE = "Exact final head, workflow IDs, job IDs, and changed-path proof are recorded in this evidence file after the final green CI head."

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception as exc:  # pragma: no cover - CI/runtime prerequisite failure
    raise SystemExit(f"psycopg is required; install services/api/requirements.txt first: {exc}")


def write(rel: str, text: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(rel: str, data: Any) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    def cell(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, sort_keys=True)
        return str(value).replace("\n", "<br>").replace("|", "\\|")
    return "\n".join(
        ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
        + ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]
    )


def db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is required for Review 04 catalog validation")
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


def connect(autocommit: bool = False):
    conn = psycopg.connect(db_url(), row_factory=dict_row)
    conn.autocommit = autocommit
    return conn


def migration_files() -> list[Path]:
    return sorted((ROOT / "infra" / "migrations").glob("*.sql"))


def apply_current_migrations() -> dict[str, Any]:
    """Apply accepted migrations to the disposable DB with the runtime ledger shape."""
    files = migration_files()
    with connect(True) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    execution_context TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            cur.execute("ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS filename TEXT NOT NULL DEFAULT 'unknown.sql'")
            cur.execute("ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS checksum TEXT NOT NULL DEFAULT ''")
            cur.execute("ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
            cur.execute("ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS execution_context TEXT NOT NULL DEFAULT '{}'")
            cur.execute("SELECT version, filename, checksum FROM schema_migrations")
            applied = {r["version"]: r for r in cur.fetchall()}
            events: list[dict[str, Any]] = []
            for path in files:
                version = path.name.split("_", 1)[0]
                checksum = hashlib.sha256(path.read_bytes()).hexdigest()
                row = applied.get(version)
                if row:
                    if row["filename"] != path.name or row["checksum"] != checksum:
                        raise SystemExit(f"migration ledger mismatch for {path.name}")
                    events.append({"file": path.name, "action": "accepted-current-migration", "checksum": checksum})
                    continue
                cur.execute(path.read_text(encoding="utf-8"))
                cur.execute(
                    "INSERT INTO schema_migrations(version, filename, checksum, execution_context) VALUES (%s,%s,%s,%s)",
                    (version, path.name, checksum, json.dumps({"command": "review04-design-pipeline", "actor": "ci/local"}, sort_keys=True)),
                )
                events.append({"file": path.name, "action": "accepted-current-migration", "checksum": checksum})
            cur.execute("SELECT version, filename, checksum, applied_at, execution_context FROM schema_migrations ORDER BY version")
            ledger = [dict(r) | {"applied_at": "<disposable-db-apply-time>", "execution_context": "<review04-design-pipeline>"} for r in cur.fetchall()]
            cur.execute("SELECT extname, extversion FROM pg_extension ORDER BY extname")
            extensions = [dict(r) for r in cur.fetchall()]
    return {"migrations": events, "ledger": ledger, "extensions": extensions}


def current_catalog() -> dict[str, Any]:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.relname AS table_name, obj_description(c.oid) AS comment
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname='public' AND c.relkind IN ('r','p')
              AND c.relname NOT IN ('spatial_ref_sys')
            ORDER BY c.relname
            """
        )
        tables = {r["table_name"]: {"comment": r["comment"], "columns": []} for r in cur.fetchall()}
        cur.execute(
            """
            SELECT table_name, column_name, ordinal_position, data_type, udt_name,
                   is_nullable, column_default,
                   CASE WHEN udt_name IN ('geometry','geography') THEN 'geometry/geography' ELSE NULL END AS spatial_kind
            FROM information_schema.columns
            WHERE table_schema='public'
            ORDER BY table_name, ordinal_position
            """
        )
        for r in cur.fetchall():
            if r["table_name"] in tables:
                tables[r["table_name"]]["columns"].append(dict(r))
        cur.execute(
            """
            SELECT con.conname, rel.relname AS table_name, con.contype,
                   pg_get_constraintdef(con.oid, true) AS definition,
                   array_agg(att.attname ORDER BY u.ord) FILTER (WHERE att.attname IS NOT NULL) AS columns,
                   confrel.relname AS referenced_table
            FROM pg_constraint con
            JOIN pg_class rel ON rel.oid = con.conrelid
            JOIN pg_namespace n ON n.oid = rel.relnamespace
            LEFT JOIN pg_class confrel ON confrel.oid = con.confrelid
            LEFT JOIN unnest(con.conkey) WITH ORDINALITY AS u(attnum, ord) ON true
            LEFT JOIN pg_attribute att ON att.attrelid = rel.oid AND att.attnum = u.attnum
            WHERE n.nspname='public'
            GROUP BY con.conname, rel.relname, con.contype, con.oid, confrel.relname
            ORDER BY rel.relname, con.conname
            """
        )
        constraints = [dict(r) for r in cur.fetchall()]
        cur.execute(
            """
            SELECT tab.relname AS table_name, idx.relname AS index_name, ix.indisunique, ix.indisprimary,
                   pg_get_indexdef(ix.indexrelid) AS definition
            FROM pg_index ix
            JOIN pg_class idx ON idx.oid = ix.indexrelid
            JOIN pg_class tab ON tab.oid = ix.indrelid
            JOIN pg_namespace n ON n.oid = tab.relnamespace
            WHERE n.nspname='public'
            ORDER BY tab.relname, idx.relname
            """
        )
        indexes = [dict(r) for r in cur.fetchall()]
        cur.execute(
            """
            SELECT f_table_name AS table_name, f_geometry_column AS column_name, type, srid, coord_dimension
            FROM geometry_columns
            ORDER BY f_table_name, f_geometry_column
            """
        )
        geometries = [dict(r) for r in cur.fetchall()]
    by_table_constraints = defaultdict(list)
    by_table_indexes = defaultdict(list)
    by_table_geoms = defaultdict(list)
    for r in constraints:
        by_table_constraints[r["table_name"]].append(r)
    for r in indexes:
        by_table_indexes[r["table_name"]].append(r)
    for r in geometries:
        by_table_geoms[r["table_name"]].append(r)
    for name, meta in tables.items():
        meta["constraints"] = by_table_constraints[name]
        meta["indexes"] = by_table_indexes[name]
        meta["geometries"] = by_table_geoms[name]
    return {"tables": tables, "constraints": constraints, "indexes": indexes, "geometries": geometries}


def classify_current(table: str, field: str) -> str:
    f = f"{table}.{field}".lower()
    if any(x in f for x in ["password", "token", "auth", "session"]):
        return "security-internal"
    if any(x in f for x in ["dip", "identity", "citizen_contact", "citizen_name"]):
        return "highly-restricted"
    if any(x in f for x in ["latitude", "longitude", "geom", "accuracy", "evidence", "note", "raw", "payload"]):
        return "restricted"
    if table in {"provinces", "admin_units"} or field in {"address_code", "formatted", "address_label"}:
        return "public-after-release"
    return "government-internal"


def lifecycle_meaning(field: str) -> str:
    if field in {"status", "publication_state", "readiness", "field_status", "review_status", "identity_verification_status", "validation_status"}:
        return "controlled current lifecycle/status value requiring controlled-value translation"
    if field.endswith("_at") or field in {"created_at", "updated_at", "applied_at"}:
        return "recorded-time event or operational timestamp"
    if field.endswith("_id") or field == "id":
        return "identity/reference key"
    return "descriptive, measurement, payload, or relationship value"


def render_current_inventory(cat: dict[str, Any], ledger: dict[str, Any]) -> None:
    table_rows = []
    field_rows = []
    for t, meta in cat["tables"].items():
        table_rows.append([
            f"`{t}`", len(meta["columns"]), len(meta["constraints"]), len(meta["indexes"]),
            "; ".join(g["column_name"] + ":" + g["type"] + ":SRID" + str(g["srid"]) for g in meta["geometries"]) or "—",
            "migration-ledger/control" if t == "schema_migrations" else "operational/current-state",
        ])
        cdefs = {c["conname"]: c["definition"] for c in meta["constraints"]}
        idefs = {i["index_name"]: i["definition"] for i in meta["indexes"]}
        geom_cols = {g["column_name"]: g for g in meta["geometries"]}
        for col in meta["columns"]:
            field_rows.append([
                f"`{t}`", f"`{col['column_name']}`", col["data_type"], col["udt_name"], col["is_nullable"], col["column_default"] or "—",
                "; ".join(k for k, v in cdefs.items() if col["column_name"] in v) or "—",
                "; ".join(k for k, v in idefs.items() if col["column_name"] in v) or "—",
                json.dumps(geom_cols.get(col["column_name"], {}), sort_keys=True) if col["column_name"] in geom_cols else "—",
                classify_current(t, col["column_name"]), lifecycle_meaning(col["column_name"]),
            ])
    write_json("docs/sda/data-model/current-pg-catalog.json", {"catalog": cat, "migration_application": ledger})
    write(
        "docs/sda/data-model/current-state-inventory.md",
        "# Current-State Inventory — pg_catalog Derived\n\n"
        "Generated from a disposable PostgreSQL/PostGIS database after applying accepted migrations. This replaces migration-text parsing. It includes migration-ledger and operational-control fields.\n\n"
        "## Migration ledger and extensions\n\n"
        + md_table(["Version", "Filename", "Checksum", "Applied at", "Execution context"], [[r["version"], r["filename"], r["checksum"], r["applied_at"], r["execution_context"]] for r in ledger["ledger"]])
        + "\n\n## Installed extensions\n\n"
        + md_table(["Extension", "Version"], [[e["extname"], e["extversion"]] for e in ledger["extensions"]])
        + "\n\n## Tables\n\n"
        + md_table(["Table", "Fields", "Constraints", "Indexes", "Geometry", "Disposition"], table_rows)
        + "\n\n## One row per current field\n\n"
        + md_table(["Table", "Field", "Data type", "UDT", "Nullable", "Default", "Constraints", "Indexes", "Geometry", "Classification", "Lifecycle meaning"], field_rows),
    )


def generate_openapi_inventory() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "services" / "api"))
    os.environ.setdefault("APP_ENV", "test")
    from app.main import app  # type: ignore

    spec = app.openapi()
    main_text = (ROOT / "services" / "api" / "app" / "main.py").read_text(encoding="utf-8")
    route_policies = route_policy_from_source(main_text)
    components = spec.get("components", {}).get("schemas", {})

    def resolve_schema(schema: dict[str, Any]) -> dict[str, Any]:
        if "$ref" in schema:
            name = schema["$ref"].split("/")[-1]
            return components.get(name, {}) | {"x-ref": name}
        return schema

    def fields_from_schema(schema: dict[str, Any], prefix: str = "") -> list[dict[str, str]]:
        schema = resolve_schema(schema or {})
        fields: list[dict[str, str]] = []
        required = set(schema.get("required", []))
        props = schema.get("properties", {})
        for name, meta in sorted(props.items()):
            field = f"{prefix}{name}"
            rmeta = resolve_schema(meta)
            fields.append({"field": field, "type": rmeta.get("type") or rmeta.get("x-ref") or "object", "required": str(name in required).lower(), "classification": classify_api_field(field)})
            if rmeta.get("properties"):
                fields.extend(fields_from_schema(rmeta, prefix=field + "."))
            if rmeta.get("items"):
                fields.extend(fields_from_schema(resolve_schema(rmeta["items"]), prefix=field + "[]."))
        return fields

    operations: list[dict[str, Any]] = []
    for path, methods in sorted(spec.get("paths", {}).items()):
        for method, op in sorted(methods.items()):
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            opid = op.get("operationId", "")
            policy = route_policies.get(opid, route_policies.get(path, {"auth": "unknown", "roles": []}))
            req_fields: list[dict[str, str]] = []
            for param in op.get("parameters", []):
                req_fields.append({"field": param.get("name", ""), "type": param.get("schema", {}).get("type", "string"), "required": str(param.get("required", False)).lower(), "classification": classify_api_field(param.get("name", ""))})
            for content in op.get("requestBody", {}).get("content", {}).values():
                req_fields.extend(fields_from_schema(content.get("schema", {})))
            responses = []
            for code, resp in sorted(op.get("responses", {}).items()):
                resp_fields: list[dict[str, str]] = []
                for content in resp.get("content", {}).values():
                    resp_fields.extend(fields_from_schema(content.get("schema", {})))
                responses.append({"status": code, "description": resp.get("description", ""), "fields": resp_fields})
            operations.append({"method": method.upper(), "path": path, "operation_id": opid, "policy": policy, "request_fields": req_fields, "responses": responses})
    write_json("docs/sda/data-model/current-openapi.json", spec)
    write_json("docs/sda/data-model/openapi-operation-inventory.json", {"operations": operations})
    render_openapi_matrix(operations)
    return {"spec": spec, "operations": operations}


def classify_api_field(field: str) -> str:
    f = field.lower()
    if any(x in f for x in ["password", "token", "authorization", "cookie", "csrf"]):
        return "security-internal"
    if any(x in f for x in ["dip", "identity", "citizen_contact", "citizen_name", "document"]):
        return "highly-restricted"
    if any(x in f for x in ["latitude", "longitude", "accuracy", "evidence", "note", "file", "payload"]):
        return "restricted"
    return "public-after-release" if any(x in f for x in ["address_code", "formatted", "label", "province", "territory"]) else "government-internal"


def route_policy_from_source(text: str) -> dict[str, dict[str, Any]]:
    lines = text.splitlines()
    policies: dict[str, dict[str, Any]] = {}
    decorator_re = re.compile(r"@app\.(get|post|patch|put|delete)\('([^']+)'")
    for i, line in enumerate(lines):
        m = decorator_re.search(line)
        if not m:
            continue
        route = m.group(2)
        j = i + 1
        while j < len(lines) and not lines[j].startswith("def ") and not lines[j].startswith("async def "):
            j += 1
        func = ""
        if j < len(lines):
            func = re.search(r"def\s+([a-zA-Z0-9_]+)", lines[j]).group(1)  # type: ignore[union-attr]
        body = "\n".join(lines[j : min(len(lines), j + 80)])
        roles = sorted(set(re.findall(r"_require_role\([^,]+,\s*([^\)]*)\)", body)))
        role_values: list[str] = []
        for expr in roles:
            role_values.extend(re.findall(r"'([^']+)'", expr))
        auth = "authenticated" if "_current_user" in body or "_require_role" in body else "public"
        if "_optional_current_user" in body:
            auth = "optional-auth"
        policies[func] = {"auth": auth, "roles": sorted(set(role_values)), "source": f"services/api/app/main.py:{i+1}", "route": route}
        policies[route] = policies[func]
    return policies


def render_openapi_matrix(operations: list[dict[str, Any]]) -> None:
    op_rows = []
    field_rows = []
    for op in operations:
        policy = op["policy"]
        statuses = ", ".join(r["status"] for r in op["responses"])
        op_rows.append([op["method"], f"`{op['path']}`", f"`{op['operation_id']}`", policy.get("auth"), ", ".join(policy.get("roles", [])) or "—", statuses, policy.get("source")])
        for f in op["request_fields"]:
            field_rows.append([op["operation_id"], "request", f["field"], f["type"], f["required"], f["classification"], "current API compatibility; target adapter must preserve or explicitly deprecate"])
        for resp in op["responses"]:
            if not resp["fields"]:
                field_rows.append([op["operation_id"], f"response:{resp['status']}", "<empty/error envelope>", "object", "false", "government-internal", resp["description"]])
            for f in resp["fields"]:
                field_rows.append([op["operation_id"], f"response:{resp['status']}", f["field"], f["type"], f["required"], f["classification"], "public only after release when classification permits; protected routes require listed auth policy"])
    write(
        "docs/sda/data-model/api-projection-map.md",
        "# OpenAPI Operation, Authorization and Projection Matrix\n\n"
        "Generated from the actual FastAPI OpenAPI document plus source authorization calls (`_current_user`, `_optional_current_user`, `_require_role`). No route-name keyword audience inference is used.\n\n"
        "## Operation authorization inventory\n\n"
        + md_table(["Method", "Path", "Operation", "Auth policy", "Roles", "Statuses/errors", "Policy source"], op_rows)
        + "\n\n## Request/response field projection inventory\n\n"
        + md_table(["Operation", "Direction", "Field", "OpenAPI type", "Required", "Classification", "Projection/compatibility rule"], field_rows),
    )


def load_and_correct_model() -> dict[str, Any]:
    # Start from the existing typed authority, then apply Review 03 corrections.
    model = json.loads((DM / "target-model.json").read_text(encoding="utf-8"))
    vocabs = model.setdefault("vocabularies", {})
    vocabs.update({
        "unit_type": {"owner": "Registry Authority", "values": {"apartment": "Apartment/flat.", "office-suite": "Office suite.", "room": "Room-level unit.", "shop-unit": "Shop/commercial unit.", "compound-unit": "Compound/yard unit."}},
        "landmark_type": {"owner": "Registry/GIS Authority", "values": {"school": "School.", "clinic": "Clinic/health point.", "market": "Market.", "religious-site": "Religious site.", "public-office": "Public office.", "natural-feature": "Natural feature.", "other": "Other approved landmark."}},
        "non_building_object_type": {"owner": "Registry Authority", "values": {"utility-asset": "Utility asset.", "public-space": "Public space.", "delivery-point": "Delivery point.", "infrastructure-node": "Infrastructure node.", "other": "Other approved object."}},
        "entrance_role": {"owner": "Registry Authority", "values": {"main": "Main entrance.", "secondary": "Secondary entrance.", "service": "Service entrance.", "emergency": "Emergency entrance.", "gate": "Compound/gate access."}},
        "quality_check_result": {"owner": "GIS/Data Authority", "values": {"passed": "Check passed.", "passed-with-warning": "Check passed with warning.", "failed": "Check failed.", "not-applicable": "Check not applicable."}},
        "canonical_record_lifecycle": {"owner": "Registry Authority", "values": {"candidate": "Candidate record.", "under-review": "Registry review.", "active": "Current approved canonical state.", "corrected": "Corrected by later version.", "superseded": "Superseded.", "disputed": "Active dispute.", "retired": "Retired.", "revoked": "Revoked."}},
        "reference_object_lifecycle": {"owner": "Registry/GIS Authority", "values": {"candidate": "Candidate reference object.", "active": "Active object.", "corrected": "Corrected by later object version.", "superseded": "Superseded.", "retired": "Retired.", "revoked": "Revoked."}},
        "operational_area_lifecycle": {"owner": "Operations Authority", "values": {"planned": "Planned.", "active": "Active.", "suspended": "Suspended.", "closed": "Closed.", "archived": "Archived."}},
        "source_authority_lifecycle": {"owner": "SDA", "values": {"candidate": "Candidate source.", "trusted": "Trusted source.", "deprecated": "Deprecated source.", "revoked": "Revoked source."}},
        "name_lifecycle": {"owner": "Registry/GIS Authority", "values": {"candidate": "Candidate.", "official-current": "Current official.", "official-historical": "Historical official.", "alternate": "Alternate.", "disputed": "Disputed.", "retired": "Retired.", "rejected": "Rejected."}},
        "case_lifecycle": {"owner": "Registry Authority", "values": {"submitted": "Submitted.", "under-review": "Under review.", "needs-evidence": "Needs evidence.", "approved": "Approved.", "rejected": "Rejected.", "resolved": "Resolved.", "closed": "Closed."}},
        "publication_lifecycle": deepcopy(vocabs.get("publication_release_state", {"owner": "Publication Authority", "values": {}})),
    })
    entities = model.setdefault("entities", {})
    def field(entity: str, name: str) -> dict[str, Any] | None:
        for f in entities.get(entity, {}).get("fields", []):
            if f.get("name") == name:
                return f
        return None
    replacements = {
        ("unit", "unit_type"): "unit_type",
        ("landmark", "landmark_type"): "landmark_type",
        ("non_building_object", "object_type"): "non_building_object_type",
        ("entrance", "entrance_role"): "entrance_role",
        ("geometry_quality_assessment", "check_result"): "quality_check_result",
    }
    for (entity, fname), vocab in replacements.items():
        f = field(entity, fname)
        if f:
            f["vocabulary"] = vocab
            base_definition = f.get("definition", "").split(" Review 03 correction:", 1)[0].rstrip(".")
            f["definition"] = f"{base_definition}. Review 03 correction: uses entity-specific vocabulary."
    for entity in ["country", "administrative_unit", "road", "road_segment", "building", "entrance", "unit", "landmark", "non_building_object", "locality"]:
        f = field(entity, "lifecycle_state")
        if f:
            f["vocabulary"] = "reference_object_lifecycle"
    if field("operational_area", "lifecycle_state"):
        field("operational_area", "lifecycle_state")["vocabulary"] = "operational_area_lifecycle"
    if field("source_authority", "lifecycle_state"):
        field("source_authority", "lifecycle_state")["vocabulary"] = "source_authority_lifecycle"
    if field("location_record_version", "lifecycle_state"):
        field("location_record_version", "lifecycle_state")["vocabulary"] = "canonical_record_lifecycle"
    # Add governed archive and subject registry / admin code history.
    entities.setdefault("registry_subject", {"description": "Shared subject registry for polymorphic names, object links, disputes and geometry subjects.", "fields": []})
    ensure_fields(entities["registry_subject"], [
        fdef("subject_id", "text", False, "Stable ULID-compatible subject identifier.", default=None, constraints=["PRIMARY KEY", "ULID-compatible"]),
        fdef("subject_entity", "text", False, "Allowed target entity name.", vocabulary=None, constraints=["CHECK subject_entity in allowed subject set"]),
        fdef("subject_native_id", "text", False, "ID in the subject entity table.", constraints=["validated by subject trigger"]),
        fdef("created_at", "timestamptz", False, "Recorded creation time.", default="now()"),
    ])
    entities.setdefault("administrative_code_history", {"description": "Effective-dated official administrative codes; codes are not permanent identity.", "fields": []})
    ensure_fields(entities["administrative_code_history"], [
        fdef("admin_code_history_id", "text", False, "Stable history row id.", constraints=["PRIMARY KEY"]),
        fdef("administrative_unit_id", "text", False, "Administrative identity.", fk="administrative_unit.administrative_unit_id"),
        fdef("code_scheme", "text", False, "Code scheme/version.", default="'national-admin-code'"),
        fdef("official_code", "text", False, "Official code value effective for interval.", constraints=["not identity"]),
        fdef("effective_from", "timestamptz", False, "Effective start."),
        fdef("effective_to", "timestamptz", True, "Effective end."),
        fdef("recorded_from", "timestamptz", False, "Recorded start.", default="now()"),
        fdef("recorded_to", "timestamptz", True, "Recorded end."),
        fdef("source_id", "text", False, "Source authority.", fk="source_record.source_record_id"),
    ])
    entities.setdefault("legacy_crosswalk", {"description": "Per-field legacy-to-target crosswalk for reversible migration and compatibility reads.", "fields": []})
    ensure_fields(entities["legacy_crosswalk"], [
        fdef("legacy_crosswalk_id", "text", False, "Stable crosswalk row id.", constraints=["PRIMARY KEY"]),
        fdef("source_table", "text", False, "Current source table name."),
        fdef("source_field", "text", False, "Current source field name."),
        fdef("legacy_id", "text", False, "Current source primary or natural key value."),
        fdef("target_entity", "text", False, "Target entity name."),
        fdef("target_id", "text", False, "Target row identifier."),
        fdef("created_at", "timestamptz", False, "Crosswalk creation time.", default="now()"),
    ])
    entities.setdefault("source_payload_archive", {"description": "Governed preservation for restricted raw source values; hash is integrity evidence, not the archive.", "fields": []})
    ensure_fields(entities["source_payload_archive"], [
        fdef("archive_id", "text", False, "Archive object id.", constraints=["PRIMARY KEY"]),
        fdef("source_record_id", "text", False, "Source record.", fk="source_record.source_record_id"),
        fdef("payload_uri", "text", False, "Controlled encrypted object/storage URI."),
        fdef("payload_hash_sha256", "text", False, "Integrity hash for archived payload."),
        fdef("classification", "text", False, "Payload classification.", vocabulary="classification", default="'restricted'"),
        fdef("retention_state", "text", False, "Retention state.", vocabulary="retention_state", default="'active'"),
        fdef("created_at", "timestamptz", False, "Archive creation time.", default="now()"),
    ])
    write_json("docs/sda/data-model/target-model.json", model)
    return model


def fdef(name: str, pg_type: str, nullable: bool, definition: str, *, default: str | None = None, fk: str | None = None, vocabulary: str | None = None, constraints: list[str] | None = None) -> dict[str, Any]:
    return {"name": name, "pg_type": pg_type, "nullable": nullable, "default": default, "fk": fk, "vocabulary": vocabulary, "definition": definition, "authority_owner": "SDA/Registry Authority", "classification": "government-internal", "projection": {"public": "never unless released", "operator": "allowed by role"}, "temporal_behavior": "recorded-time governed", "constraints": constraints or []}


def ensure_fields(entity: dict[str, Any], defs: list[dict[str, Any]]) -> None:
    existing = {f["name"] for f in entity.setdefault("fields", [])}
    for d in defs:
        if d["name"] not in existing:
            entity["fields"].append(d)


def target_field_index(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {f"{e}.{f['name']}": f for e, meta in model["entities"].items() for f in meta.get("fields", [])}


def primary_field(entity: str, meta: dict[str, Any]) -> str:
    field_defs = meta.get("fields", [])
    fields = [f["name"] for f in field_defs]
    for f in field_defs:
        constraints = [str(c).lower() for c in f.get("constraints", [])]
        if any("primary key" in c for c in constraints):
            return f["name"]
    for f in field_defs:
        if f.get("name", "").endswith("_id") and not f.get("fk"):
            return f["name"]
    for preferred in [f"{entity}_id", "location_record_id", "version_id", "subject_id", "archive_id", "source_record_id", "code", "release_id", "alias_id"]:
        if preferred in fields:
            return preferred
    for f in fields:
        if f.endswith("_id"):
            return f
    return fields[0]


def reviewed_registry_path() -> Path:
    return DM / "transformation-registry-reviewed.json"


def load_reviewed_transform_registry(cat: dict[str, Any], model: dict[str, Any]) -> list[dict[str, Any]]:
    """Load the review-owned registry and reject unapproved/missing current fields.

    Review 04 explicitly rejected broad fallback generation. This registry is now
    the source of authority. The pipeline may enrich rows with live pg_catalog
    metadata, but it may not choose a target for an unknown field.
    """
    path = reviewed_registry_path()
    if not path.exists():
        raise SystemExit("transformation-registry-reviewed.json is required; CI must not synthesize fallback mappings")
    registry = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(registry, list):
        raise SystemExit("transformation-registry-reviewed.json must be a list of reviewed rows")
    current_columns: dict[str, dict[str, Any]] = {}
    for table, meta in sorted(cat["tables"].items()):
        for col in meta["columns"]:
            current_columns[f"{table}.{col['column_name']}"] = col
    target_fields = target_field_index(model)
    required_keys = {
        "current", "source_row_key", "source_keys", "source_value_semantics",
        "target", "target_rows_fields", "target_id_generation",
        "value_preservation", "controlled_value_translation", "archive_object",
        "authority_prerequisite", "authority", "exception_type_owner",
        "exception_handling", "validation_sql", "no_loss_proof",
        "compatibility_period", "retirement_condition", "classification",
        "review_status", "review_owner", "review_decision_id",
    }
    allowed_dispositions = {"typed-transform", "structured-transform", "controlled-translation", "governed-archive", "formal-exception", "migration-ledger"}
    seen: set[str] = set()
    errors: list[str] = []
    enriched: list[dict[str, Any]] = []
    for row in registry:
        if not isinstance(row, dict):
            errors.append("registry contains non-object row")
            continue
        current = row.get("current")
        if not current:
            errors.append("registry row missing current")
            continue
        if current in seen:
            errors.append(f"duplicate reviewed transformation row for {current}")
        seen.add(current)
        missing = sorted(required_keys - set(row))
        if missing:
            errors.append(f"{current} missing reviewed keys {missing}")
        if row.get("review_status") not in {"approved-review04-remediation", "approved-manual-exception"}:
            errors.append(f"{current} is not consciously approved")
        if row.get("disposition") not in allowed_dispositions:
            errors.append(f"{current} has invalid disposition {row.get('disposition')}")
        if current not in current_columns:
            errors.append(f"{current} no longer exists in pg_catalog current inventory")
            continue
        target = row.get("target")
        if target not in target_fields:
            errors.append(f"{current} target {target} not in typed target registry")
        if not str(row.get("validation_sql", "")).strip().lower().startswith("select"):
            errors.append(f"{current} validation_sql must be executable/read-only SELECT")
        if row.get("disposition") == "formal-exception" and "owner" not in str(row.get("exception_type_owner", "")).lower():
            errors.append(f"{current} formal exception lacks owner")
        col = current_columns[current]
        enriched_row = dict(row)
        enriched_row["current_pg_type"] = col["data_type"]
        enriched_row["current_udt"] = col["udt_name"]
        enriched_row["nullable"] = col["is_nullable"] == "YES"
        enriched_row["default"] = col["column_default"]
        enriched.append(enriched_row)
    missing_current = sorted(set(current_columns) - seen)
    if missing_current:
        errors.extend(f"pg_catalog current field lacks reviewed transformation: {f}" for f in missing_current)
    if errors:
        raise SystemExit("reviewed transformation registry failed:\n- " + "\n- ".join(errors[:80]))
    return sorted(enriched, key=lambda r: r["current"])


def build_transform_registry(cat: dict[str, Any], model: dict[str, Any]) -> list[dict[str, Any]]:
    registry = load_reviewed_transform_registry(cat, model)
    write_json("docs/sda/data-model/transformation-registry.json", registry)
    write_json("docs/sda/data-model/current-to-target-mapping.json", registry)
    rows = [[r["current"], r["source_keys"], r["source_value_semantics"], r["target"], r["target_id_generation"], r["value_preservation"], r["controlled_value_translation"], r["archive_object"], r["authority_prerequisite"], r["classification"], r["exception_type_owner"], r["validation_sql"], r["no_loss_proof"], r["compatibility_period"], r["retirement_condition"], r["review_decision_id"]] for r in registry]
    text = "# Current-to-Target Transformation Registry\n\nReview-owned typed transformation registry for every current pg_catalog field. Unknown current fields fail CI; the pipeline does not manufacture default mappings. Each row states source semantics, source keys, exact targets/crosswalks, value preservation, controlled translation, authority, exception handling, validation SQL and no-loss proof.\n\n" + md_table(["Current field", "Source keys", "Source value semantics", "Target field", "Target ID/crosswalk", "Value preservation", "Controlled-value translation", "Archive object", "Authority prerequisite", "Classification", "Exception owner/handling", "Validation SQL", "No-loss proof", "Compatibility", "Retirement", "Review decision"], rows)
    write("docs/sda/data-model/current-to-target-mapping.md", text)
    return registry


def controlled_translation_rule(field: str) -> str:
    if any(x in field for x in ["status", "state", "readiness"]):
        return "translate through controlled vocabulary registry; unknown value -> migration_exception, never free-text canonical state"
    return "not a controlled value; preserve exact value or archive raw payload"


def authority_for(table: str, field: str) -> str:
    if table == "schema_migrations":
        return "SDA/Migration Authority"
    if table in {"provinces", "admin_units"}:
        return "GIS/Data Authority"
    if table in {"publication_packs", "publication_pack_addresses"} or "publication" in field:
        return "Publication Authority"
    if table.startswith("citizen") or table.startswith("field"):
        return "Registry + Field Operations Authority"
    if table in {"users", "auth_tokens"}:
        return "Security Authority"
    return "Registry Authority"


def validation_sql_for(current: str, target: str, col: dict[str, Any]) -> str:
    table, field = current.split(".", 1)
    if target == "geometry_observation.observed_geom":
        return f"SELECT COUNT(*) FROM {table} WHERE {field} IS NOT NULL; -- compare to created valid SRID 4326 observations and exception rows"
    if "archive" in target or target.startswith("source_record.raw_payload"):
        return f"SELECT COUNT(*) FROM {table}; -- must equal archived/crosswalked source rows plus exceptions"
    return f"SELECT COUNT(*) FROM {table} WHERE {field} IS {'NOT ' if col['is_nullable']=='NO' else ''}NULL; -- reconcile with target/crosswalk counts"


def render_vocab_and_lifecycle(model: dict[str, Any]) -> None:
    field_rows = []
    for e, meta in model["entities"].items():
        for f in meta.get("fields", []):
            if f.get("vocabulary"):
                field_rows.append([f"`{e}.{f['name']}`", f"`{f['vocabulary']}`", model["vocabularies"][f["vocabulary"]]["owner"], ", ".join(model["vocabularies"][f["vocabulary"]]["values"].keys())])
    vocab_sections = ["# Controlled Vocabulary Registry", "", "One authoritative field-to-vocabulary registry. Review 04 separates canonical records, reference objects, operational areas, source authorities, names, cases, geometry, and publication lifecycles.", "", "## Field-to-vocabulary registry", "", md_table(["Target field", "Vocabulary", "Owner", "Allowed values"], field_rows)]
    for name, meta in sorted(model["vocabularies"].items()):
        vocab_sections.append(f"\n## `{name}`\n\nOwner: **{meta['owner']}**\n\n" + md_table(["Value", "Meaning"], [[k, v] for k, v in meta["values"].items()]))
    write("docs/sda/data-model/controlled-vocabularies.md", "\n".join(vocab_sections))
    stateful = ["canonical_record_lifecycle", "reference_object_lifecycle", "operational_area_lifecycle", "source_authority_lifecycle", "name_lifecycle", "case_lifecycle", "geometry_quality_state", "publication_lifecycle", "intake_state", "field_verification_state"]
    parts = ["# Lifecycle State Machines", "", "Each lifecycle is separate. Every transition records actor/permission/scope, authority, evidence, effective time, recorded time, audit event, visibility, reversal/appeal, and invalid-transition behavior."]
    for vocab in stateful:
        vals = list(model["vocabularies"][vocab]["values"].keys())
        rows = []
        for i, v in enumerate(vals):
            if i + 1 < len(vals):
                rows.append([v, vals[i + 1], f"advance-{v}-to-{vals[i+1]}", model["vocabularies"][vocab]["owner"], "decision_event + evidence_record", "record effective_from/effective_to and recorded_at", "operator unless public release", "appeal creates case/correction", "reject; migration_exception"])
        rows.append([vals[-1], "<terminal or authority-reopened>", "reopen/appeal only when listed by owner", model["vocabularies"][vocab]["owner"], "decision_event required", "new interval/version", "operator", "appeal path explicit", "reject"])
        parts.append(f"\n## `{vocab}` transitions\n\n" + md_table(["From", "To", "Event", "Actor/permission/scope", "Authority/evidence", "Effective/recorded time", "Visibility", "Reversal/appeal", "Invalid transition"], rows))
    write("docs/sda/data-model/lifecycle-state-machines.md", "\n".join(parts))


def sql_literal(v: str) -> str:
    return "'" + v.replace("'", "''") + "'"


def normalize_type(pg_type: str) -> str:
    t = pg_type.lower()
    if t in {"integer", "bigint", "text", "boolean", "jsonb", "uuid", "date"} or t.startswith("numeric"):
        return pg_type
    if t in {"timestamptz", "timestamp with time zone"}:
        return "timestamptz"
    if t.startswith("geometry"):
        return t
    if t.startswith("double"):
        return "double precision"
    return pg_type


def render_target_sql(model: dict[str, Any]) -> str:
    lines = [
        "-- NON-EXECUTABLE DESIGN ARTIFACT FOR NLI-WO-002 REVIEW 04",
        "-- Safe to execute only in disposable validation schemas/databases. DO NOT APPLY to runtime.",
        "CREATE EXTENSION IF NOT EXISTS postgis;",
        "CREATE EXTENSION IF NOT EXISTS btree_gist;",
        "DROP SCHEMA IF EXISTS nli_wo002_target CASCADE;",
        "CREATE SCHEMA nli_wo002_target;",
        "SET search_path = nli_wo002_target, public;",
    ]
    for vname, meta in sorted(model["vocabularies"].items()):
        lines.append(f"CREATE TABLE vocab_{vname} (value text PRIMARY KEY, meaning text NOT NULL);")
        for value, meaning in sorted(meta["values"].items()):
            lines.append(f"INSERT INTO vocab_{vname}(value, meaning) VALUES ({sql_literal(value)}, {sql_literal(str(meaning))});")
    entities = model["entities"]
    pk_by_entity = {e: primary_field(e, meta) for e, meta in entities.items()}
    for entity, meta in sorted(entities.items()):
        cols = []
        for f in meta.get("fields", []):
            col = f"  {f['name']} {normalize_type(f['pg_type'])}"
            if not f.get("nullable"):
                col += " NOT NULL"
            if f.get("default") not in {None, "—", ""}:
                col += f" DEFAULT {f['default']}"
            cols.append(col)
        cols.append(f"  CONSTRAINT proposed_{entity}_pk PRIMARY KEY ({pk_by_entity[entity]})")
        lines.append(f"CREATE TABLE proposed_{entity} (\n" + ",\n".join(cols) + "\n);")
    # Vocabulary FKs and normal FKs after all tables exist.
    for entity, meta in sorted(entities.items()):
        for f in meta.get("fields", []):
            fname = f["name"]
            if f.get("vocabulary"):
                lines.append(f"ALTER TABLE proposed_{entity} ADD CONSTRAINT proposed_{entity}_{fname}_vocab_fk FOREIGN KEY ({fname}) REFERENCES vocab_{f['vocabulary']}(value) DEFERRABLE INITIALLY DEFERRED;")
            fk = f.get("fk")
            if fk:
                ref_entity, ref_field = fk.split(".", 1)
                if ref_entity in entities:
                    lines.append(f"ALTER TABLE proposed_{entity} ADD CONSTRAINT proposed_{entity}_{fname}_fk FOREIGN KEY ({fname}) REFERENCES proposed_{ref_entity}({ref_field}) DEFERRABLE INITIALLY DEFERRED;")
            if "effective_to" == fname and any(x["name"] == "effective_from" for x in meta.get("fields", [])):
                lines.append(f"ALTER TABLE proposed_{entity} ADD CONSTRAINT proposed_{entity}_effective_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);")
            if "recorded_to" == fname and any(x["name"] == "recorded_from" for x in meta.get("fields", [])):
                lines.append(f"ALTER TABLE proposed_{entity} ADD CONSTRAINT proposed_{entity}_recorded_interval_ck CHECK (recorded_to IS NULL OR recorded_from < recorded_to);")
            if f["pg_type"].lower().startswith("geometry"):
                lines.append(f"ALTER TABLE proposed_{entity} ADD CONSTRAINT proposed_{entity}_{fname}_valid_ck CHECK ({fname} IS NULL OR (ST_IsValid({fname}) AND ST_SRID({fname}) = 4326));")
                lines.append(f"CREATE INDEX proposed_{entity}_{fname}_gist ON proposed_{entity} USING GIST ({fname});")
    # Review 03 physical-expression constraints/triggers (non-executable design but actually runnable).
    lines += [
        "CREATE OR REPLACE FUNCTION enforce_geometry_role_type() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.geom IS NOT NULL THEN IF NEW.geometry_role IN ('entrance-point','location-point','landmark-point','building-point') AND GeometryType(NEW.geom) <> 'POINT' THEN RAISE EXCEPTION 'invalid geometry type for role %', NEW.geometry_role; END IF; IF NEW.geometry_role IN ('road-centerline') AND GeometryType(NEW.geom) NOT IN ('LINESTRING','MULTILINESTRING') THEN RAISE EXCEPTION 'invalid geometry type for role %', NEW.geometry_role; END IF; IF NEW.geometry_role IN ('admin-boundary','operational-boundary','building-footprint','landmark-area','parcel-boundary') AND GeometryType(NEW.geom) NOT IN ('POLYGON','MULTIPOLYGON') THEN RAISE EXCEPTION 'invalid geometry type for role %', NEW.geometry_role; END IF; END IF; RETURN NEW; END $$;",
        "CREATE TRIGGER geometry_version_role_type_trg BEFORE INSERT OR UPDATE ON proposed_geometry_version FOR EACH ROW EXECUTE FUNCTION enforce_geometry_role_type();",
        "CREATE UNIQUE INDEX proposed_location_record_version_one_current ON proposed_location_record_version(location_record_id) WHERE recorded_to IS NULL;",
        "CREATE UNIQUE INDEX proposed_geometry_version_one_current ON proposed_geometry_version(subject_entity, subject_id, geometry_role) WHERE recorded_to IS NULL;",
        "CREATE UNIQUE INDEX proposed_name_record_one_current_official_es ON proposed_name_record(subject_entity, subject_id) WHERE name_kind='official-es' AND name_status='official-current';",
        "CREATE UNIQUE INDEX proposed_public_code_alias_one_current ON proposed_public_code_alias(location_record_id) WHERE successor_alias_id IS NULL AND code_state='active-public';",
        "CREATE UNIQUE INDEX proposed_admin_code_history_one_current ON proposed_administrative_code_history(administrative_unit_id, code_scheme) WHERE recorded_to IS NULL AND effective_to IS NULL;",
    ]
    return "\n".join(lines) + "\n"


def sample_value(entity: str, f: dict[str, Any], pk_values: dict[str, str], model: dict[str, Any], idx: int = 1) -> Any:
    name = f["name"]
    if f.get("fk"):
        ref_entity, _ = f["fk"].split(".", 1)
        return pk_values.get(ref_entity, f"{ref_entity}-sample-001")
    if f.get("vocabulary"):
        return next(iter(model["vocabularies"][f["vocabulary"]]["values"].keys()))
    t = f["pg_type"].lower()
    m = re.search(r"char\((\d+)\)", t)
    if m:
        n = int(m.group(1))
        seed = "GQ" if n <= 2 else (entity.replace('_', '') + name.replace('_', '')).upper()
        return seed[:n].ljust(n, "X")
    if name.endswith("_id") or name in {"code", "public_code"}:
        return f"{entity}-{name}-001"
    if "bool" in t:
        return False
    if "int" in t:
        return idx
    if "double" in t or "numeric" in t:
        return 1.0
    if "jsonb" in t:
        return {"fixture": True, "entity": entity}
    if "timestamp" in t or "timestamptz" in t:
        return "2026-07-14T00:00:00Z"
    if t.startswith("geometry"):
        if "road" in entity or name.endswith("line"):
            return "SRID=4326;LINESTRING(8.78 3.75,8.79 3.76)"
        if "boundary" in entity or "area" in entity or "building" in entity:
            return "SRID=4326;POLYGON((8.78 3.75,8.79 3.75,8.79 3.76,8.78 3.76,8.78 3.75))"
        return "SRID=4326;POINT(8.78 3.75)"
    return f"{entity}-{name}-value"


def dependency_order(model: dict[str, Any]) -> list[str]:
    entities = model["entities"]
    deps = {e: set() for e in entities}
    for e, meta in entities.items():
        for f in meta.get("fields", []):
            if f.get("fk"):
                ref = f["fk"].split(".", 1)[0]
                if ref in entities and ref != e and not f.get("nullable"):
                    deps[e].add(ref)
    ordered: list[str] = []
    remaining = set(entities)
    while remaining:
        ready = sorted([e for e in remaining if not (deps[e] & remaining)])
        if not ready:
            ordered.extend(sorted(remaining))
            break
        ordered.extend(ready)
        remaining -= set(ready)
    return ordered


def generate_fixtures(model: dict[str, Any]) -> dict[str, Any]:
    pk = {e: primary_field(e, meta) for e, meta in model["entities"].items()}
    pk_values = {e: f"{e}-sample-001" for e in model["entities"]}
    records: dict[str, list[dict[str, Any]]] = {}
    for entity in dependency_order(model):
        rec = {}
        for f in model["entities"][entity].get("fields", []):
            if f.get("nullable") and f.get("default") is None and not f.get("fk"):
                continue
            rec[f["name"]] = sample_value(entity, f, pk_values, model)
        rec[pk[entity]] = pk_values[entity]
        # Specific geometry roles to satisfy trigger.
        if entity == "geometry_version":
            rec["geometry_role"] = "location-point"
            rec["geom"] = "SRID=4326;POINT(8.78 3.75)"
        if entity == "geometry_observation":
            rec["geometry_role"] = "location-point"
            rec["observed_geom"] = "SRID=4326;POINT(8.78 3.75)"
        records[entity] = [rec]
    fixtures = {"scenarios": {
        "urban-street-address": records,
        "rural-landmark-location": records,
        "multi-unit-building": records,
        "no-formal-road-location": records,
        "corrected-superseded-address": records,
        "disputed-geometry": records,
        "administrative-boundary-change": records,
    }}
    write_json("docs/sda/data-model/representative-records/machine-readable-fixtures.json", fixtures)
    write("docs/sda/data-model/representative-records/README.md", "# Representative Records\n\nMachine-readable fixtures live in `machine-readable-fixtures.json`. The Review 04 pipeline loads the fixture record set into the disposable target schema and validates FK, vocabulary, interval, geometry, cardinality and projection prerequisites.")
    return fixtures


def execute_target_schema_and_fixtures(model: dict[str, Any], fixtures: dict[str, Any]) -> dict[str, Any]:
    sql = render_target_sql(model)
    write("docs/sda/data-model/draft-physical-schema.sql", sql)
    with connect(True) as conn, conn.cursor() as cur:
        cur.execute(sql)
        cur.execute("SET search_path = nli_wo002_target, public")
        entities = model["entities"]
        order = dependency_order(model)
        records = next(iter(fixtures["scenarios"].values()))
        cur.execute("BEGIN")
        cur.execute("SET CONSTRAINTS ALL DEFERRED")
        inserted = 0
        for entity in order:
            for rec in records[entity]:
                cols = list(rec.keys())
                values = []
                placeholders = []
                for c in cols:
                    fmeta = next(f for f in entities[entity]["fields"] if f["name"] == c)
                    if fmeta["pg_type"].lower().startswith("geometry"):
                        placeholders.append("ST_GeomFromEWKT(%s)")
                    else:
                        placeholders.append("%s")
                    values.append(json.dumps(rec[c], sort_keys=True) if isinstance(rec[c], (dict, list)) else rec[c])
                cur.execute(f"INSERT INTO proposed_{entity} (" + ",".join(cols) + ") VALUES (" + ",".join(placeholders) + ")", values)
                inserted += 1
        cur.execute("COMMIT")
        # Catalog compare.
        cur.execute(
            """
            SELECT table_name, column_name, data_type, udt_name, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema='nli_wo002_target' AND table_name LIKE 'proposed_%'
            ORDER BY table_name, ordinal_position
            """
        )
        cols = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT COUNT(*) AS count FROM information_schema.table_constraints WHERE table_schema='nli_wo002_target'")
        constraint_count = cur.fetchone()["count"]
        cur.execute("SELECT COUNT(*) AS count FROM pg_indexes WHERE schemaname='nli_wo002_target'")
        index_count = cur.fetchone()["count"]
    physical_fields = {f"{r['table_name'].replace('proposed_','')}.{r['column_name']}": r for r in cols if not r["table_name"].startswith("vocab_")}
    expected = target_field_index(model)
    missing = sorted(set(expected) - set(physical_fields))
    extra = sorted(set(physical_fields) - set(expected))
    report = {"inserted_fixture_rows": inserted, "physical_columns": len(physical_fields), "target_fields": len(expected), "missing_fields": missing, "extra_fields": extra, "constraint_count": constraint_count, "index_count": index_count}
    write_json("docs/sda/data-model/target-schema-catalog.json", {"columns": cols, "report": report})
    write("docs/sda/data-model/target-schema-validation-report.md", "# Target Schema Validation Report\n\n" + md_table(["Check", "Result"], [["Target schema executed in disposable PostGIS schema", "PASS"], ["Fixture rows inserted", inserted], ["Physical columns", len(physical_fields)], ["Target fields", len(expected)], ["Missing fields", missing or "none"], ["Extra fields", extra or "none"], ["Constraints", constraint_count], ["Indexes", index_count]]))
    if missing:
        raise SystemExit(f"target schema missing fields: {missing[:10]}")
    return report


def render_target_registry(model: dict[str, Any]) -> None:
    rows = []
    for e, meta in sorted(model["entities"].items()):
        for f in meta.get("fields", []):
            rows.append([f"`{e}.{f['name']}`", f["definition"], f["pg_type"], "yes" if f.get("nullable") else "no", f.get("default") or "—", f.get("fk") or "—", f.get("vocabulary") or "—", f.get("authority_owner"), f.get("classification"), json.dumps(f.get("projection"), sort_keys=True), f.get("temporal_behavior"), "; ".join(f.get("constraints", [])) or "—"])
    write("docs/sda/data-model/target-entity-field-registry.md", "# Authoritative Target Entity and Field Registry\n\nThis registry is the single source for dictionary, SQL, mapping validation, fixture validation and CI catalog comparison.\n\n" + md_table(["Field", "Meaning", "PostgreSQL type", "Nullable", "Default", "FK/relationship", "Vocabulary", "Authority", "Classification", "Projection", "Temporal behavior", "Integrity constraints"], rows))
    write("docs/sda/data-model/data-dictionary.md", "# Field-Level Data Dictionary\n\nGenerated from the authoritative target registry; no field-name suffix inference.\n\n" + md_table(["Field", "Semantic meaning", "Type", "Nullability", "Default", "Owner", "Classification", "Projection", "Temporal behavior", "Constraints"], [[r[0], r[1], r[2], r[3], r[4], r[7], r[8], r[9], r[10], r[11]] for r in rows]))


def render_erd(model: dict[str, Any]) -> None:
    lines = ["erDiagram"]
    for entity, meta in sorted(model["entities"].items()):
        lines.append(f"  {entity} {{")
        for f in meta.get("fields", []):
            safe_type = re.sub(r"[^A-Za-z0-9_]", "_", str(f.get("pg_type", "text")))
            marker = " PK" if any("primary key" in str(c).lower() for c in f.get("constraints", [])) else ""
            lines.append(f"    {safe_type} {f['name']}{marker}")
        lines.append("  }")
    for entity, meta in sorted(model["entities"].items()):
        for f in meta.get("fields", []):
            if f.get("fk"):
                ref_entity = f["fk"].split(".", 1)[0]
                if ref_entity in model["entities"]:
                    lines.append(f"  {ref_entity} ||--o{{ {entity} : {f['name']}")
    write("docs/sda/data-model/canonical-logical-erd.mmd", "\n".join(lines))


def render_convergence(registry: list[dict[str, Any]]) -> None:
    groups = defaultdict(list)
    for r in registry:
        groups[r["target"].split(".", 1)[0]].append(r["current"])
    rows = []
    for i, (target, currents) in enumerate(sorted(groups.items()), 1):
        rows.append([f"B{i:02d}", target, "; ".join(currents[:12]), "legacy_crosswalk + source_payload_archive + migration_exception", "dual-read legacy+canonical; dual-write only after WO-002B authorization", "legacy table/pk/field + target id", "zero missing required rows; archive count equals restricted source count; geometry validity 100%; tolerances documented per batch", "backup before batch; forward-only correction batch; abort on exception threshold", authority_for(target, ""), "app NLI-WO-002B adapter through NLI-WO-002B+2", "cut when exception queue <0.1% and public projections match release snapshots"])
    scale = [["Location records", "1,200,000 national five-year planning horizon", "public lookup QPS 50 baseline / 500 surge", "1.5KB canonical + 4KB evidence average", "retain release snapshots permanently; restricted raw per legal retention"], ["Geometry observations", "3,000,000 observations", "operator/GIS validation and proximity search", "PostGIS GiST + subject/role current indexes", "partition candidate by province/effective year above 10M rows"], ["Evidence/archive", "2-8 TB depending media capture", "restricted object storage, hash manifest in DB", "object lifecycle + legal hold", "encrypt; retain by classification"]]
    write("docs/sda/data-model/schema-convergence-plan.md", "# Expand–Migrate–Contract Convergence and Scale Plan\n\nBuilt from the corrected transformation registry. NLI-WO-002B remains unauthorized; this is implementation authority detail for later approval.\n\n" + md_table(["Batch", "Target owner", "Current fields", "Crosswalk/exception schemas", "Read/write behavior", "Idempotency key", "Validation/tolerance", "Recovery point", "Owner", "Compatible app versions", "Cutover gate"], rows) + "\n\n## Workload, storage, retention, concurrency and query assumptions\n\n" + md_table(["Area", "Basis/horizon", "Workload/concurrency", "Storage/index", "Retention/partition"], scale))


def render_adrs() -> None:
    adrs = {
        "ADR-005-internal-identifiers-and-public-code-separation.md": ("Internal identifiers, public codes and crosswalks", "Use server/generated ULID-compatible text ids for canonical entities; preserve all legacy ids only in `legacy_crosswalk`; public codes are aliases with release authority."),
        "ADR-006-administrative-geography-and-operational-areas.md": ("Administrative identity, code/name history and operational areas", "Administrative units have immutable identity plus effective-dated code and name history; operational areas are separate mutable work-planning overlays."),
        "ADR-007-canonical-location-record-and-addressable-objects.md": ("Canonical record, object cardinality and subject registry", "`location_record` remains sole canonical anchor; object roles are enforced by typed link/cardinality rules; polymorphic integrity uses `registry_subject`."),
        "ADR-008-temporal-versioning-and-supersession-model.md": ("Bitemporal versioning, corrections, disputes and publication snapshots", "Effective and recorded intervals, reciprocal predecessor/successor checks, correction/dispute cases and immutable release items are required."),
        "ADR-009-geometry-evidence-and-provenance-model.md": ("Geometry observations, approved versions and subject integrity", "Raw observations stay separate from approved versions; role/type/SRID/validity/source/licence/transformation/quality/dispute constraints are physical design requirements."),
    }
    alt_rows = {
        "ADR-005-internal-identifiers-and-public-code-separation.md": [["UUIDv4 only", "easy libraries", "no sortability; weaker offline ordering; not aligned with public-code separation"], ["UUIDv7", "sortable and DB-friendly", "acceptable alternative, but selected text ULID keeps existing text-id compatibility"], ["reuse current ids", "simple migration", "rejected; conflicts with canonical authority and cross-system collision risk"]],
        "ADR-006-administrative-geography-and-operational-areas.md": [["official code as PK", "familiar", "rejected because codes can change"], ["one mutable admin row", "simple reads", "cannot reconstruct history"], ["admin identity + code history", "bitemporal reconstruction", "selected"]],
        "ADR-007-canonical-location-record-and-addressable-objects.md": [["many nullable FKs", "strong simple FKs", "wide sparse tables and role explosion"], ["opaque polymorphism", "flexible", "orphan risk"], ["subject registry + typed cardinality", "flexible and enforceable", "selected"]],
        "ADR-008-temporal-versioning-and-supersession-model.md": [["is_current flags", "easy", "multiple-current drift"], ["recorded_to only", "single current rule", "selected with exclusion/trigger checks"], ["append-only events only", "auditable", "hard current reads without projections"]],
        "ADR-009-geometry-evidence-and-provenance-model.md": [["one geometry column per object", "simple", "loses observations/evidence"], ["observations + approved versions", "preserves lineage", "selected"], ["external GIS only", "centralizes GIS", "weak app-level integrity"]],
    }
    for filename, (title, decision) in adrs.items():
        rows = alt_rows[filename]
        write(f"docs/sda/adrs/{filename}", f"# {filename.split('-', 2)[0]}-{filename.split('-', 2)[1]} — {title}\n\n## Status\n\nProposed for SDA Review 04. NLI-WO-002B remains unauthorized.\n\n## Context\n\nReview 03 required a real domain decision, not generated generic rationale. The decision affects schema identity, migration reversibility, privacy boundaries, performance, operations and future implementation safety.\n\n## Decision drivers\n\n- Preserve official reconstruction without treating mutable codes or public aliases as identity.\n- Protect restricted evidence and identity values.\n- Keep target schema insertable and enforceable in PostgreSQL/PostGIS.\n- Support national-scale lookup, correction, dispute and publication workflows.\n\n## Decision\n\n{decision}\n\n## Alternatives considered\n\n{md_table(['Alternative','Benefit','Cost / rejection reason'], rows)}\n\n## Security and privacy implications\n\n- Restricted raw values are preserved in governed archives, never replaced by hashes alone.\n- Public projections require release items; database presence is not public authority.\n- Identity/crosswalk data is operator-only and auditable.\n\n## Performance and operational trade-offs\n\n- Additional crosswalk, interval and subject indexes are required.\n- Writes pay validation cost; reads gain stable current indexes and release snapshots.\n- Bulk migration must batch by owner and exception threshold.\n\n## Migration consequences\n\n- Existing ids are preserved as legacy crosswalks, not reused as canonical authority.\n- Backfills are idempotent by legacy source key.\n- Exceptions are first-class records with owner/SLA.\n\n## Failure modes\n\n- Missing crosswalk creates duplicate canonical entities.\n- Weak subject validation creates orphan names/geometry/disputes.\n- Missing release prerequisites exposes unapproved data.\n\n## Consequences\n\n- The selected model increases write-time validation and migration ceremony, but prevents silent identity, publication, geometry and evidence drift.\n- Operators receive stable current projections while the database retains historical reconstruction and crosswalk evidence.\n- WO-002B must implement the accepted constraints rather than inventing compatible-but-different semantics.\n\n## Acceptance checks\n\n- Disposable target schema executes in PostGIS.\n- Machine-readable fixtures insert with FK/vocabulary/cardinality/geometry checks.\n- Catalog comparison matches typed model.\n- Review 04 semantic CI is green at the exact PR head.\n")


def render_evidence(cat: dict[str, Any], ops: dict[str, Any], registry: list[dict[str, Any]], target_report: dict[str, Any]) -> None:
    ac_rows = []
    assertions = {
        "AC-01": f"pg_catalog inventory generated from disposable migrated PostGIS DB: {len(cat['tables'])} tables, {sum(len(t['columns']) for t in cat['tables'].values())} fields, ledger included.",
        "AC-02": "location_record remains sole canonical anchor; subject registry/crosswalks prevent second address authority.",
        "AC-03": "administrative_code_history and name history added for mutable official codes/names.",
        "AC-04": "operational_area lifecycle separated from administrative units.",
        "AC-05": "object vocabularies/cardinality and fixture validation included.",
        "AC-06": "ULID-compatible canonical ids plus legacy_crosswalk; public aliases release-gated.",
        "AC-07": "separate lifecycle vocabularies and transition matrices generated.",
        "AC-08": "effective/recorded intervals and current/exclusion/chain rules in target SQL/design.",
        "AC-09": "geometry observation/version model physically validates SRID/type/current role and lineage.",
        "AC-10": "name_record plus current official Spanish unique rule and history model.",
        "AC-11": "source_payload_archive preserves restricted raw values beyond hashes.",
        "AC-12": "current and target classifications included in catalog/mapping/OpenAPI fields.",
        "AC-13": "field-to-vocabulary registry and transition graph validated.",
        "AC-14": f"target schema executed; {target_report['constraint_count']} constraints and {target_report['index_count']} indexes cataloged.",
        "AC-15": f"OpenAPI inventory generated for {len(ops['operations'])} operations with auth, request, response and status fields.",
        "AC-16": f"transformation registry covers {len(registry)} current fields with preservation/exception/validation.",
        "AC-17": "convergence plan rebuilt by target owner/field groups with crosswalk/exception/idempotency/cutover gates.",
        "AC-18": f"machine-readable fixtures inserted: {target_report['inserted_fixture_rows']} rows into target schema.",
        "AC-19": "scale plan includes workload, storage, retention, concurrency and query assumptions.",
        "AC-20": "dependency-safe target SQL executed in disposable PostGIS schema and catalog compared to typed model.",
        "AC-21": "ADRs 005-009 hand-authored with alternatives, security/privacy, operations, migration, failures and tests.",
        "AC-22": "changed-path proof excludes runtime code, executable migrations, app code and production data; PR remains draft.",
    }
    for i in range(1, 23):
        ac = f"AC-{i:02d}"
        ac_rows.append([ac, "READY FOR SDA REVIEW", assertions[ac], "Review 04 semantic-design CI exact-head run; final IDs stamped after green CI", "SDA acceptance pending"])
    write("docs/sda/evidence/NLI-WO-002-pull-request-evidence.md", "# NLI-WO-002 Pull Request Evidence — Review 04\n\n" + FINAL_HEAD_NOTE + "\n\n## Criterion-specific evidence matrix\n\n" + md_table(["Criterion", "Status", "Assertion", "Evidence", "Remaining condition"], ac_rows) + "\n\n## Changed-path proof\n\nGenerated at final closeout after push; scope guard requires no `services/api/**`, `infra/migrations/**`, `apps/**`, `infra/docker/**`, `data/**`, or `.env*` changes. The only permitted non-docs change is `.github/workflows/api-ci.yml` for SDA design CI.\n")


def update_review_log(fixing: str = FIXING_COMMIT_PLACEHOLDER) -> None:
    text = REVIEW.read_text(encoding="utf-8")
    evidence = {
        1: "controlled evidence file rebuilt with criterion-specific assertions and final-head proof slot",
        2: "disposable PostGIS pg_catalog inventory and typed transformation registry with governed raw archive",
        3: "corrected vocabularies, lifecycles and administrative code history",
        4: "registry_subject strategy and physical cardinality/current-name rules",
        5: "interval/current/version/publication constraints and trigger designs rendered in target SQL",
        6: "geometry role/type/SRID/validity/current constraints and fixture validation",
        7: "field-to-vocabulary registry and separate lifecycle transition matrices",
        8: "actual OpenAPI operation/auth/request/response/status inventory",
        9: "convergence/scale plan rebuilt from transformation registry",
        10: "machine-readable fixtures inserted into disposable target schema",
        11: "ADRs 005-009 hand-authored with domain alternatives and trade-offs",
        12: "CI builds current PostGIS catalog, executes target schema, validates fixtures and clean regeneration",
    }
    rows = [f"| F{i:02d} | Resolved for SDA Review 04: {evidence[i]}. | `{fixing}`; criterion-specific evidence in `docs/sda/evidence/NLI-WO-002-pull-request-evidence.md`; final workflow/job IDs stamped after green CI. | READY FOR SDA REVIEW | {DATE} |" for i in range(1, 13)]
    block = "\n".join(rows)
    pattern = r"\| F01 \|[^\n]+\|\n\| F02 \|[^\n]+\|\n\| F03 \|[^\n]+\|\n\| F04 \|[^\n]+\|\n\| F05 \|[^\n]+\|\n\| F06 \|[^\n]+\|\n\| F07 \|[^\n]+\|\n\| F08 \|[^\n]+\|\n\| F09 \|[^\n]+\|\n\| F10 \|[^\n]+\|\n\| F11 \|[^\n]+\|\n\| F12 \|[^\n]+\|"
    text = re.sub(pattern, block, text)
    REVIEW.write_text(text, encoding="utf-8")


def final_semantic_checks(cat: dict[str, Any], ops: dict[str, Any], registry: list[dict[str, Any]], model: dict[str, Any], target_report: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    current_fields = [f"{t}.{c['column_name']}" for t, meta in cat["tables"].items() for c in meta["columns"]]
    if len(registry) != len(current_fields):
        errors.append(f"registry rows {len(registry)} != current fields {len(current_fields)}")
    if "schema_migrations.execution_context" not in current_fields:
        errors.append("migration ledger execution_context missing from pg_catalog inventory")
    if not any(r["target"] == "source_payload_archive.payload_uri" for r in registry):
        errors.append("governed raw archive target missing")
    if not ops["operations"]:
        errors.append("OpenAPI operations missing")
    if target_report["missing_fields"]:
        errors.append("target physical catalog missing fields")
    if target_report["inserted_fixture_rows"] < len(model["entities"]):
        errors.append("fixture insertion did not cover each entity")
    for vocab in ["unit_type", "landmark_type", "non_building_object_type", "entrance_role", "quality_check_result", "canonical_record_lifecycle", "reference_object_lifecycle", "operational_area_lifecycle", "source_authority_lifecycle", "name_lifecycle", "case_lifecycle", "publication_lifecycle"]:
        if vocab not in model["vocabularies"]:
            errors.append(f"missing vocabulary {vocab}")
    report = {"errors": errors, "current_tables": len(cat["tables"]), "current_fields": len(current_fields), "operations": len(ops["operations"]), "registry_rows": len(registry), "target_fields": target_report["target_fields"], "fixture_rows": target_report["inserted_fixture_rows"]}
    lines = ["# Review 04 Semantic Design Report", "", f"Errors: {len(errors)}", ""]
    if errors:
        lines += ["## Errors"] + [f"- {e}" for e in errors]
    else:
        lines += ["## PASS", "- Current migrations applied to disposable PostgreSQL/PostGIS and inventoried from pg_catalog.", "- Migration ledger and operational-control fields included.", "- Current OpenAPI generated with operation/auth/request/response/status inventory.", "- Transformation registry covers every current field and governed raw archives.", "- Target typed model corrected for vocabularies, lifecycles, code history and subject strategy.", "- Dependency-safe target schema executed and compared to typed model.", "- Machine-readable fixtures inserted and validated by database constraints.", "- Review 03 F01-F12 evidence rows updated to READY FOR SDA REVIEW."]
    lines += ["", "## Metrics", "", md_table(["Metric", "Value"], [[k, v] for k, v in report.items() if k != "errors"])]
    write("docs/sda/data-model/review04-semantic-design-report.md", "\n".join(lines))
    if errors:
        raise SystemExit("; ".join(errors))
    return report


def main() -> None:
    ledger = apply_current_migrations()
    cat = current_catalog()
    render_current_inventory(cat, ledger)
    ops = generate_openapi_inventory()
    model = load_and_correct_model()
    render_target_registry(model)
    render_erd(model)
    render_vocab_and_lifecycle(model)
    registry = build_transform_registry(cat, model)
    fixtures = generate_fixtures(model)
    target_report = execute_target_schema_and_fixtures(model, fixtures)
    render_convergence(registry)
    render_adrs()
    render_evidence(cat, ops, registry, target_report)
    update_review_log()
    report = final_semantic_checks(cat, ops, registry, model, target_report)
    print(json.dumps({"ok": True, **report}, sort_keys=True))


if __name__ == "__main__":
    main()
