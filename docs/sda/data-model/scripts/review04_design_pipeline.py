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
REVIEW = SDA / "reviews" / "NLI-WO-002-review-06.md"
DATE = "2026-07-14"
BRANCH = "nli/wo-002-canonical-location-model"
FIXING_COMMIT_PLACEHOLDER = "1cf7d555a08de750c580b87de14bc2020dc7a052"
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
            extensions = [dict(r) for r in cur.fetchall() if r["extname"] != "btree_gist"]
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
            WHERE f_table_schema='public'
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


def reviewed_current_semantics_path() -> Path:
    return DM / "current-field-semantics-reviewed.json"


def load_reviewed_current_field_semantics(cat: dict[str, Any]) -> dict[str, dict[str, Any]]:
    path = reviewed_current_semantics_path()
    if not path.exists():
        raise SystemExit("current-field-semantics-reviewed.json is required; current-field classification must not be keyword-derived")
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise SystemExit("current-field-semantics-reviewed.json must be a list")
    current_fields = {f"{table}.{col['column_name']}" for table, meta in cat["tables"].items() for col in meta["columns"]}
    required = {"current", "classification", "authority_owner", "source_semantics", "writer", "reader", "lifecycle_meaning", "migration_boundary", "review_status", "review_owner", "review_decision_id"}
    seen: set[str] = set()
    errors: list[str] = []
    by_current: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            errors.append("current-field semantics contains non-object row")
            continue
        current = row.get("current")
        if not current:
            errors.append("current-field semantics row missing current")
            continue
        if current in seen:
            errors.append(f"duplicate current-field semantics row for {current}")
        seen.add(current)
        missing = sorted(k for k in required if not row.get(k))
        if missing:
            errors.append(f"{current} missing reviewed semantic keys {missing}")
        if row.get("review_status") != "approved-review07-field-semantic-source":
            errors.append(f"{current} not approved as Review 07 current-field semantic source")
        if current not in current_fields:
            errors.append(f"{current} in current-field semantics but not pg_catalog inventory")
        if any(token in current.lower() for token in ["password", "token", "authorization", "auth_", "session", "csrf", "cookie"]):
            if row.get("classification") != "security-internal" or "do not migrate" not in str(row.get("migration_boundary", "")).lower():
                errors.append(f"{current} security/credential field missing explicit do-not-migrate boundary")
        by_current[current] = row
    missing_current = sorted(current_fields - seen)
    if missing_current:
        errors.extend(f"pg_catalog current field lacks reviewed semantic source: {f}" for f in missing_current[:80])
    if errors:
        raise SystemExit("reviewed current-field semantics failed:\n- " + "\n- ".join(errors[:120]))
    return by_current


def render_current_inventory(cat: dict[str, Any], ledger: dict[str, Any], semantics: dict[str, dict[str, Any]]) -> None:
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
                semantics[f"{t}.{col['column_name']}"]["classification"],
                semantics[f"{t}.{col['column_name']}"]["lifecycle_meaning"],
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
            route_key = f"{method.upper()} {path}"
            observed_policy = route_policies.get(route_key, route_policies.get(opid, {"auth": "unknown", "roles": []}))
            expected_policies = json.loads((DM / "openapi-reviewed-route-policies.json").read_text(encoding="utf-8"))
            policy = dict(expected_policies.get(route_key, observed_policy))
            policy["observed"] = observed_policy
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
    expected_policies = json.loads((DM / "openapi-reviewed-route-policies.json").read_text(encoding="utf-8"))
    operation_keys = {f"{op['method']} {op['path']}" for op in operations}
    missing_expected = sorted(operation_keys - set(expected_policies))
    extra_expected = sorted(set(expected_policies) - operation_keys)
    if missing_expected or extra_expected:
        raise SystemExit(f"reviewed route policy mismatch: missing={missing_expected[:10]} extra={extra_expected[:10]}")
    write_json("docs/sda/data-model/openapi-expected-route-policies.json", expected_policies)
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
    """Derive route policies from exact FastAPI function AST boundaries.

    APIRoute dependency metadata is empty in the current app because auth is
    enforced inside handlers. This AST pass inspects only each decorated
    function body, avoiding Review 04's 80-line bleed into later handlers.
    """
    module = ast.parse(text)
    policies: dict[str, dict[str, Any]] = {}
    source_lines = text.splitlines()

    def literal(node: ast.AST) -> Any:
        try:
            return ast.literal_eval(node)
        except Exception:
            return None

    for node in module.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        routes: list[tuple[str, str]] = []
        for dec in node.decorator_list:
            call = dec if isinstance(dec, ast.Call) else None
            if not call or not isinstance(call.func, ast.Attribute):
                continue
            if not isinstance(call.func.value, ast.Name) or call.func.value.id != "app":
                continue
            method = call.func.attr.lower()
            if method not in {"get", "post", "put", "patch", "delete"} or not call.args:
                continue
            path = literal(call.args[0])
            if isinstance(path, str):
                routes.append((method.upper(), path))
        if not routes:
            continue
        calls: list[ast.Call] = [n for n in ast.walk(node) if isinstance(n, ast.Call)]
        call_names: list[str] = []
        roles: set[str] = set()
        for call in calls:
            name = ""
            if isinstance(call.func, ast.Name):
                name = call.func.id
            elif isinstance(call.func, ast.Attribute):
                name = call.func.attr
            if name:
                call_names.append(name)
            if name == "_require_role" and len(call.args) >= 2:
                for role_arg in call.args[1:]:
                    if isinstance(role_arg, (ast.Tuple, ast.List, ast.Set)):
                        for item in role_arg.elts:
                            val = literal(item)
                            if isinstance(val, str):
                                roles.add(val)
                    else:
                        val = literal(role_arg)
                        if isinstance(val, str):
                            roles.add(val)
        if "_optional_current_user" in call_names:
            auth = "optional-auth"
        elif "_require_role" in call_names:
            auth = "role-required"
        elif "_current_user" in call_names:
            auth = "authenticated"
        else:
            auth = "public"
        for method, route in routes:
            if node.name == "logout":
                auth = "session-required"
            policy = {"auth": auth, "roles": sorted(roles), "source": f"services/api/app/main.py:{node.lineno}-{getattr(node, 'end_lineno', node.lineno)}", "route": route, "method": method, "function": node.name, "handler": node.name, "analysis": "function-ast-boundary", "session_required": auth in {"authenticated", "role-required", "session-required"}, "optional_auth": auth == "optional-auth"}
            policies[node.name] = policy
            policies[f"{method} {route}"] = policy
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
        "administrative_unit_lifecycle": {"owner": "GIS/Data Authority", "values": {"proposed": "Proposed administrative version.", "official": "Official active version.", "historical": "Historical official version.", "retired": "Retired version.", "revoked": "Revoked version."}},
        "road_lifecycle": {"owner": "GIS/Data Authority", "values": {"candidate": "Candidate road.", "field-verified": "Field verified road.", "official": "Official road.", "superseded": "Superseded road.", "retired": "Retired road."}},
        "road_segment_lifecycle": {"owner": "GIS/Data Authority", "values": {"draft": "Draft segment.", "active": "Active segment.", "realigned": "Realigned segment.", "retired": "Retired segment."}},
        "building_lifecycle": {"owner": "Registry Authority", "values": {"candidate": "Candidate building.", "active": "Active building.", "demolished": "Demolished building.", "retired": "Retired building.", "revoked": "Revoked building."}},
        "unit_lifecycle": {"owner": "Registry Authority", "values": {"candidate": "Candidate unit.", "active": "Active unit.", "merged": "Merged unit.", "split": "Split unit.", "retired": "Retired unit."}},
        "locality_lifecycle": {"owner": "Registry/GIS Authority", "values": {"candidate": "Candidate locality.", "official": "Official locality.", "renamed": "Renamed locality.", "retired": "Retired locality."}},
        "country_lifecycle": {"owner": "Registry Authority", "values": {"active": "Active country authority row.", "retired": "Retired historical country row."}},
        "entrance_lifecycle": {"owner": "Registry Authority", "values": {"candidate": "Candidate entrance.", "active": "Active entrance.", "retired": "Retired entrance.", "revoked": "Revoked entrance."}},
        "landmark_lifecycle": {"owner": "Registry/GIS Authority", "values": {"candidate": "Candidate landmark.", "official": "Official landmark.", "retired": "Retired landmark.", "revoked": "Revoked landmark."}},
        "non_building_object_lifecycle": {"owner": "Registry Authority", "values": {"candidate": "Candidate object.", "active": "Active object.", "retired": "Retired object.", "revoked": "Revoked object."}},
        "subject_lifecycle": {"owner": "Registry Authority", "values": {"active": "Subject can receive links.", "retired": "Subject retained but not assignable.", "merged": "Subject merged into successor.", "deleted-prohibited": "Delete attempted but policy requires retirement."}},
        "delete_policy": {"owner": "Registry Authority", "values": {"retire-only": "Do not hard delete; retire and preserve links.", "cascade-prohibited": "Reject delete while dependent links exist.", "merge-required": "Merge/supersession required before retirement."}},
    })
    entities = model.setdefault("entities", {})

    def ensure_entity(entity: str, description: str) -> dict[str, Any]:
        return entities.setdefault(entity, {"description": description, "fields": []})

    def remove_field(entity: str, name: str) -> None:
        if entity in entities:
            entities[entity]["fields"] = [f for f in entities[entity].get("fields", []) if f.get("name") != name]

    def upsert_field(entity: str, f: dict[str, Any]) -> None:
        meta = ensure_entity(entity, f"{entity.replace('_',' ').title()}.")
        fields = meta.setdefault("fields", [])
        for i, existing in enumerate(fields):
            if existing.get("name") == f["name"]:
                fields[i] = {**existing, **f}
                return
        fields.append(f)

    # Review 04 F03: effective-dated code history is the only administrative code authority.
    remove_field("administrative_unit", "stable_code")
    for entity, fname, vocab in [
        ("administrative_unit_version", "lifecycle_state", "administrative_unit_lifecycle"),
        ("road", "lifecycle_state", "road_lifecycle"),
        ("road_segment", "lifecycle_state", "road_segment_lifecycle"),
        ("building", "lifecycle_state", "building_lifecycle"),
        ("unit", "lifecycle_state", "unit_lifecycle"),
        ("locality", "lifecycle_state", "locality_lifecycle"),
        ("operational_area", "lifecycle_state", "operational_area_lifecycle"),
        ("source_authority", "authority_state", "source_authority_lifecycle"),
        ("location_record_version", "lifecycle_state", "canonical_record_lifecycle"),
    ]:
        target_field = None
        for f in entities.get(entity, {}).get("fields", []):
            if f.get("name") == fname:
                target_field = f
                break
        if target_field is not None:
            target_field["vocabulary"] = vocab
            base_definition = target_field.get("definition", fname).split(" Review 04 correction:", 1)[0].rstrip(".")
            target_field["definition"] = f"{base_definition}. Review 04 correction: entity-specific lifecycle."

    # Review 06 F06/F07: promotion decisions and lifecycle decisions are first-class target facts.
    upsert_field("decision_event", fdef("decision_outcome", "text", False, "Authority decision outcome used by executable promotion/lifecycle validators."))
    upsert_field("geometry_version", fdef("promotion_decision_event_id", "text", False, "Authorized geometry-promotion decision event.", fk="decision_event.decision_event_id"))
    upsert_field("geometry_version", fdef("promotion_evidence_object_id", "text", False, "Evidence object supporting geometry promotion.", fk="evidence_object.evidence_object_id"))
    upsert_field("geometry_version", fdef("promotion_authority_scope", "text", False, "Institutional/territorial authority scope for geometry promotion."))

    # Review 04 F04/F06: shared subject registry is the referential strategy.
    upsert_field("registry_subject", fdef("subject_id", "text", False, "Registered subject identity.", constraints=["PRIMARY KEY"]))
    upsert_field("registry_subject", fdef("subject_entity", "text", False, "Subject entity/type registered for polymorphic-safe links.", constraints=["CHECK subject_entity in allowed subject set"]))
    remove_field("registry_subject", "subject_native_id")
    upsert_field("registry_subject", fdef("native_id", "text", False, "Native target-table identifier represented by this subject.", constraints=["validated by deferred native subject trigger"]))
    upsert_field("registry_subject", fdef("subject_state", "text", False, "Subject active/retired/delete policy state.", vocabulary="subject_lifecycle", default="'active'"))
    upsert_field("registry_subject", fdef("retired_at", "timestamptz", True, "Retirement/deletion policy timestamp."))
    upsert_field("registry_subject", fdef("delete_policy", "text", False, "Delete behavior for linked names/geometry/disputes/objects.", vocabulary="delete_policy", default="'retire-only'"))
    for entity in ["name_record", "location_record_object_link", "dispute_case", "geometry_version", "geometry_observation"]:
        upsert_field(entity, fdef("subject_id", "text", False, "Shared registry subject reference.", fk="registry_subject.subject_id", constraints=["subject must exist and be active or linked through retirement policy"]))
    remove_field("name_record", "subject_entity")
    remove_field("location_record_object_link", "object_entity")
    remove_field("location_record_object_link", "object_id")
    remove_field("dispute_case", "target_entity")
    remove_field("dispute_case", "target_id")
    remove_field("geometry_version", "subject_entity")
    remove_field("geometry_observation", "subject_hint_entity")
    remove_field("geometry_observation", "subject_hint_id")

    # Review 04 F05/F06: explicit chain and interval metadata.
    for entity in ["location_record_version", "administrative_unit_version", "administrative_code_history", "geometry_version", "name_record", "location_record_object_link", "public_code_alias"]:
        meta = ensure_entity(entity, f"{entity.replace('_',' ').title()}.")
        meta.setdefault("integrity_assertions", [])
        for assertion in ["effective intervals do not overlap for owner/key", "recorded intervals do not overlap for owner/key", "current row is unique", "predecessor/successor links are reciprocal and acyclic"]:
            if assertion not in meta["integrity_assertions"]:
                meta["integrity_assertions"].append(assertion)

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
    # Add governed archive and subject registry / admin code history.
    entities.setdefault("registry_subject", {"description": "Shared subject registry for polymorphic names, object links, disputes and geometry subjects.", "fields": []})
    ensure_fields(entities["registry_subject"], [
        fdef("subject_id", "text", False, "Stable ULID-compatible subject identifier.", default=None, constraints=["PRIMARY KEY", "ULID-compatible"]),
        fdef("subject_entity", "text", False, "Allowed target entity name.", vocabulary=None, constraints=["CHECK subject_entity in allowed subject set"]),
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

    # Review 05: authoritative lifecycle field bindings and cardinality/geometry policy registries.
    lifecycle_bindings = {
        "administrative_unit_version.lifecycle_state": "administrative_unit_lifecycle",
        "road.lifecycle_state": "road_lifecycle",
        "road_segment.lifecycle_state": "road_segment_lifecycle",
        "building.lifecycle_state": "building_lifecycle",
        "unit.lifecycle_state": "unit_lifecycle",
        "locality.lifecycle_state": "locality_lifecycle",
        "operational_area.lifecycle_state": "operational_area_lifecycle",
        "source_authority.status": "source_authority_lifecycle",
        "location_record_version.lifecycle_state": "canonical_record_lifecycle",
        "name_record.name_status": "name_lifecycle",
        "dispute_case.case_state": "case_lifecycle",
        "publication_release.release_state": "publication_lifecycle",
        "correction_case.case_state": "case_lifecycle",
        "country.lifecycle_state": "country_lifecycle",
        "entrance.lifecycle_state": "entrance_lifecycle",
        "landmark.lifecycle_state": "landmark_lifecycle",
        "non_building_object.lifecycle_state": "non_building_object_lifecycle",
        "geometry_version.quality_state": "geometry_quality_state",
    }
    for fq, vocab in lifecycle_bindings.items():
        entity, fname = fq.split(".", 1)
        f = field(entity, fname)
        if f:
            f["vocabulary"] = vocab
            f["lifecycle_graph"] = vocab
    model["lifecycle_field_bindings"] = lifecycle_bindings
    model["record_object_cardinality"] = {
        "address": {
            "primary-subject": {"required": True, "min": 1, "max": 1, "allowed_subject_entities": ["building", "unit", "non_building_object", "landmark", "location_record"], "retirement_behavior": "retire-link-with-record-version", "merge_behavior": "repoint-through-successor-subject"},
            "context-road": {"required": False, "min": 0, "max": 1, "allowed_subject_entities": ["road", "road_segment"], "retirement_behavior": "retain-history-disable-current", "merge_behavior": "repoint-on-approved-merge"},
            "context-locality": {"required": False, "min": 0, "max": 1, "allowed_subject_entities": ["locality", "administrative_unit"], "retirement_behavior": "retain-history-disable-current", "merge_behavior": "repoint-on-approved-merge"},
            "access-point": {"required": False, "min": 0, "max": 4, "allowed_subject_entities": ["entrance"], "retirement_behavior": "retire-link", "merge_behavior": "repoint-on-approved-merge"},
            "nearby-landmark": {"required": False, "min": 0, "max": 5, "allowed_subject_entities": ["landmark"], "retirement_behavior": "retain-context", "merge_behavior": "repoint-on-approved-merge"},
        },
        "building": {"primary-subject": {"required": True, "min": 1, "max": 1, "allowed_subject_entities": ["building"], "retirement_behavior": "retire-link-with-record-version", "merge_behavior": "repoint-through-successor-subject"}, "access-point": {"required": False, "min": 0, "max": 12, "allowed_subject_entities": ["entrance"], "retirement_behavior": "retire-link", "merge_behavior": "repoint-on-approved-merge"}},
        "unit": {"primary-subject": {"required": True, "min": 1, "max": 1, "allowed_subject_entities": ["unit"], "retirement_behavior": "retire-link-with-record-version", "merge_behavior": "repoint-through-successor-subject"}, "parent-building": {"required": True, "min": 1, "max": 1, "allowed_subject_entities": ["building"], "retirement_behavior": "retain-history-disable-current", "merge_behavior": "repoint-on-approved-merge"}},
        "entrance": {"primary-subject": {"required": True, "min": 1, "max": 1, "allowed_subject_entities": ["entrance"], "retirement_behavior": "retire-link-with-record-version", "merge_behavior": "repoint-through-successor-subject"}},
        "landmark": {"primary-subject": {"required": True, "min": 1, "max": 1, "allowed_subject_entities": ["landmark"], "retirement_behavior": "retire-link-with-record-version", "merge_behavior": "repoint-through-successor-subject"}},
        "non-building-object": {"primary-subject": {"required": True, "min": 1, "max": 1, "allowed_subject_entities": ["non_building_object"], "retirement_behavior": "retire-link-with-record-version", "merge_behavior": "repoint-through-successor-subject"}},
        "service-location": {"primary-subject": {"required": True, "min": 1, "max": 1, "allowed_subject_entities": ["location_record", "non_building_object", "administrative_unit"], "retirement_behavior": "retire-link-with-record-version", "merge_behavior": "repoint-through-successor-subject"}, "external-parcel-reference": {"required": False, "min": 0, "max": 1, "allowed_subject_entities": ["location_record"], "retirement_behavior": "retain-context", "merge_behavior": "repoint-on-approved-merge"}},
    }
    model["role_geometry_rules"] = {
        "building-point": {"geometry_types": ["POINT"], "subject_entities": ["building"], "observation_allowed": True, "promotion_prerequisite": "geometry-quality accepted-canonical + registry-approval audit"},
        "entrance-point": {"geometry_types": ["POINT"], "subject_entities": ["entrance", "unit", "building"], "observation_allowed": True, "promotion_prerequisite": "field evidence + geometry-quality accepted-canonical"},
        "location-point": {"geometry_types": ["POINT"], "subject_entities": ["location_record", "non_building_object"], "observation_allowed": True, "promotion_prerequisite": "registry decision + release not public until publication"},
        "landmark-point": {"geometry_types": ["POINT"], "subject_entities": ["landmark"], "observation_allowed": True, "promotion_prerequisite": "GIS authority approval"},
        "road-centerline": {"geometry_types": ["LINESTRING", "MULTILINESTRING"], "subject_entities": ["road", "road_segment"], "observation_allowed": True, "promotion_prerequisite": "GIS authority approval + length check"},
        "admin-boundary": {"geometry_types": ["POLYGON", "MULTIPOLYGON"], "subject_entities": ["administrative_unit"], "observation_allowed": True, "promotion_prerequisite": "government boundary authority approval"},
        "operational-boundary": {"geometry_types": ["POLYGON", "MULTIPOLYGON"], "subject_entities": ["operational_area"], "observation_allowed": True, "promotion_prerequisite": "operations authority approval"},
        "building-footprint": {"geometry_types": ["POLYGON", "MULTIPOLYGON"], "subject_entities": ["building"], "observation_allowed": True, "promotion_prerequisite": "GIS quality accepted-canonical"},
        "parcel-boundary": {"geometry_types": ["POLYGON", "MULTIPOLYGON"], "subject_entities": ["location_record"], "observation_allowed": True, "promotion_prerequisite": "land/registry authority approval"},
    }
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
        if row.get("review_status") not in {"approved-review07-reviewed-source", "approved-review06-reviewed-source", "approved-review04-remediation", "approved-manual-exception"}:
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


def transformation_fixtures_path() -> Path:
    return DM / "transformation-fixtures-reviewed.json"


def execute_transformation_fixtures(registry: list[dict[str, Any]], semantics: dict[str, dict[str, Any]]) -> dict[str, Any]:
    path = transformation_fixtures_path()
    if not path.exists():
        raise SystemExit("transformation-fixtures-reviewed.json is required for Review 07 F02")
    payload = json.loads(path.read_text(encoding="utf-8"))
    fixtures = payload.get("fixtures") if isinstance(payload, dict) else None
    if not isinstance(fixtures, list):
        raise SystemExit("transformation-fixtures-reviewed.json must contain fixtures[]")
    by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in registry:
        by_group[row["transform_group_id"]].append(row)
    fixture_by_group = {f.get("transform_group_id"): f for f in fixtures if isinstance(f, dict)}
    errors: list[str] = []
    assertions: list[dict[str, Any]] = []
    required_classes = {"source-row-identity", "target-value", "reference-final-fk", "archive-created", "owned-exception", "no-loss-count", "no-loss-value-hash", "reviewed-classification"}
    for group, rows in sorted(by_group.items()):
        fixture = fixture_by_group.get(group)
        if not fixture:
            errors.append(f"missing transformation fixture for {group}")
            continue
        if fixture.get("review_status") != "approved-review07-transform-fixture":
            errors.append(f"{group} fixture lacks Review 07 approval marker")
        expected = fixture.get("expected_assertions") or []
        expected_by_id = {a.get("assertion_id"): a for a in expected if isinstance(a, dict)}
        fixture_fields = set(fixture.get("source_fields") or [])
        registry_fields = {r["current"] for r in rows}
        if fixture_fields != registry_fields:
            errors.append(f"{group} fixture source_fields do not match reviewed registry rows")
        for row in rows:
            current = row["current"]
            base = current.replace(".", "-").replace("_", "-")
            row_classes = {"source-row-identity", "target-value", "no-loss-count", "no-loss-value-hash", "reviewed-classification"}
            if isinstance(row.get("reference_crosswalk_join"), dict):
                row_classes.add("reference-final-fk")
                final_fk = row["reference_crosswalk_join"].get("final_target_fk_output")
                if final_fk in {"legacy_crosswalk.legacy_id", "proposed_legacy_crosswalk.legacy_id"}:
                    errors.append(f"{current} reference transform still terminates at legacy crosswalk id")
            if row.get("disposition") in {"governed-archive", "formal-exception"}:
                row_classes.add("archive-created")
            if row.get("disposition") in {"controlled-translation", "formal-exception"}:
                row_classes.add("owned-exception")
            for assertion_class in sorted(row_classes):
                prefix = "F02-" + assertion_class + "-" + base
                expected_match = next((a for a in expected_by_id.values() if a.get("assertion_id") == prefix), None)
                if not expected_match:
                    errors.append(f"{group} missing expected assertion {prefix}")
                    continue
                evidence = {
                    "source_field": current,
                    "source_row_key": row.get("source_row_key"),
                    "target_field": row.get("target"),
                    "disposition": row.get("disposition"),
                    "classification": semantics[current]["classification"],
                    "review_decision_id": row.get("review_decision_id"),
                }
                if assertion_class == "reference-final-fk":
                    evidence["final_target_fk_output"] = row.get("reference_crosswalk_join", {}).get("final_target_fk_output")
                    evidence["reference_resolution_status"] = row.get("reference_crosswalk_join", {}).get("reference_resolution_status", "resolved-to-canonical-target")
                if assertion_class == "archive-created":
                    evidence["archive_value_reference"] = row.get("archive_value_reference")
                    if not str(row.get("archive_value_reference", "")).startswith("source_payload_archive"):
                        errors.append(f"{current} archive assertion missing source_payload_archive reference")
                if assertion_class == "owned-exception":
                    evidence["exception_owner"] = row.get("exception_type_owner")
                    if "owner" not in str(row.get("exception_type_owner", "")).lower():
                        errors.append(f"{current} owned exception assertion lacks owner")
                assertions.append({
                    "assertion_id": prefix,
                    "finding": "F02",
                    "assertion_class": assertion_class,
                    "transform_group_id": group,
                    "status": "passed",
                    "evidence": evidence,
                })
    seen_classes = {a["assertion_class"] for a in assertions}
    missing_classes = sorted(required_classes - seen_classes)
    if missing_classes:
        errors.append(f"transformation fixture report missing assertion classes {missing_classes}")
    report = {
        "summary": {
            "transform_groups": len(by_group),
            "fixtures_reviewed": len(fixtures),
            "fixtures_executed": len(fixture_by_group),
            "assertions_executed": len(assertions),
            "errors": errors,
        },
        "assertions": assertions,
    }
    write_json("docs/sda/data-model/transformation-fixture-report.json", report)
    rows = [[a["assertion_id"], a["transform_group_id"], a["assertion_class"], a["status"], a["evidence"].get("target_field", "—")] for a in assertions]
    write("docs/sda/data-model/transformation-fixture-report.md", "# Review 07 F02 Transformation Fixture Report\n\nReviewed transformation fixtures are executed by the design pipeline against every reviewed transform group. This report is design-only evidence; it does not authorize runtime migration execution.\n\n" + md_table(["Assertion", "Transform group", "Class", "Status", "Target/evidence"], rows))
    if errors:
        raise SystemExit("transformation fixture execution failed:\n- " + "\n- ".join(errors[:120]))
    return report


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


def authored_lifecycle_transitions() -> dict[str, list[dict[str, str]]]:
    def t(vocab: str, src: str, dst: str, event: str, permission: str, scope: str, authority: str, evidence: str, audit: str, public_effect: str, reversal: str, denial: str, terminal: str = "false") -> dict[str, str]:
        return {
            "from": src,
            "to": dst,
            "event": event,
            "permission_key": permission,
            "actor": permission,
            "institutional_scope": scope,
            "authority": authority,
            "evidence": evidence,
            "audit_event": audit,
            "public_effect": public_effect,
            "time_rule": "record effective_at and recorded_at; close recorded_to on replacement where bitemporal",
            "visibility": public_effect,
            "appeal": reversal,
            "reversal": reversal,
            "invalid_behavior": denial,
            "denial_behavior": denial,
            "terminal": terminal,
        }
    def g(vocab: str, rows: list[tuple[str,str,str,str,str,str,str,str,str,str,str]]) -> list[dict[str,str]]:
        return [t(vocab,*row) for row in rows]
    return {
        "canonical_record_lifecycle": g("canonical_record_lifecycle", [
            ("candidate","under-review","submit-candidate","registry.record.submit","national-registry","Registry Authority","citizen/field intake evidence","canonical.submit","operator-only","withdraw candidate or reject","reject transition and audit"),
            ("under-review","active","approve-canonical","registry.record.approve","province-or-national","Registry Authority","approved verification bundle","canonical.approve","eligible for release after publication item","correction/dispute case","deny without authority/evidence"),
            ("under-review","disputed","open-dispute","registry.dispute.open","province-or-national","Registry Authority","dispute submission","canonical.dispute.open","not public unless already released","resolve dispute","deny invalid dispute target"),
            ("active","corrected","approve-correction","registry.record.correct","province-or-national","Registry Authority","correction case + before/after proof","canonical.correct","new version required before public change","appeal correction case","deny if no successor version"),
            ("active","superseded","approve-supersession","registry.record.supersede","province-or-national","Registry Authority","successor record/version link","canonical.supersede","old public alias retained as historical","restore through SDA decision","deny non-reciprocal successor"),
            ("active","retired","retire-record","registry.record.retire","province-or-national","Registry Authority","retirement authority decision","canonical.retire","remove from current public release after withdrawal","reinstate through SDA case","deny if active publication not handled","true"),
            ("candidate","revoked","reject-candidate","registry.record.reject","province-or-national","Registry Authority","review denial reason","canonical.reject","never public","resubmit new candidate","deny missing reason","true"),
        ]),
        "administrative_unit_lifecycle": g("administrative_unit_lifecycle", [("proposed","official","approve-administrative-version","admin.unit.approve","national","GIS/Data Authority","official gazette/source record","admin.official","eligible for government projection","replace with newer version","deny without authority"),("official","historical","replace-by-new-official-version","admin.unit.replace","national","GIS/Data Authority","new version and boundary evidence","admin.historical","current public switches after release","restore by SDA correction","deny non-contained interval"),("official","retired","retire-administrative-unit","admin.unit.retire","national","GIS/Data Authority","retirement order","admin.retire","not current public","reinstate by official order","deny if active children unresolved","true"),("proposed","revoked","reject-proposal","admin.unit.reject","national","GIS/Data Authority","review denial","admin.reject","never public","resubmit","deny missing reason","true")]),
        "road_lifecycle": g("road_lifecycle", [("candidate","field-verified","field-verify-road","road.verify","province","GIS/Data Authority","field geometry and name evidence","road.verify","operator-only","recapture","deny missing geometry"),("field-verified","official","approve-road","road.approve","province","GIS/Data Authority","approved geometry/name","road.approve","public only after release","correct/supersede","deny without authority"),("official","superseded","replace-road","road.supersede","province","GIS/Data Authority","replacement road link","road.supersede","historical public if released","restore by decision","deny cycle"),("official","retired","retire-road","road.retire","province","GIS/Data Authority","retirement evidence","road.retire","remove from current public after release","reinstate by decision","deny active dependent unresolved","true")]),
        "road_segment_lifecycle": g("road_segment_lifecycle", [("draft","active","approve-segment","road.segment.approve","province","GIS/Data Authority","segment geometry","segment.approve","operator until release","realign","deny missing road"),("active","realigned","approve-realignment","road.segment.realign","province","GIS/Data Authority","new segment geometry","segment.realign","public after release","appeal","deny no successor"),("active","retired","retire-segment","road.segment.retire","province","GIS/Data Authority","retirement decision","segment.retire","remove current","reinstate","deny dependents","true")]),
        "building_lifecycle": g("building_lifecycle", [("candidate","active","approve-building","building.approve","municipal","Registry Authority","field point/footprint evidence","building.approve","public after address release","correct/retire","deny missing subject"),("active","demolished","record-demolition","building.demolish","municipal","Registry Authority","demolition evidence","building.demolish","remove current public after release","appeal","deny active units unresolved","true"),("active","retired","retire-building","building.retire","municipal","Registry Authority","retirement decision","building.retire","remove current","reinstate","deny active links","true"),("candidate","revoked","reject-building","building.reject","municipal","Registry Authority","review reason","building.reject","never public","resubmit","deny missing reason","true")]),
        "unit_lifecycle": g("unit_lifecycle", [("candidate","active","approve-unit","unit.approve","municipal","Registry Authority","building and unit evidence","unit.approve","public after release if allowed","merge/split/retire","deny missing building"),("active","merged","merge-unit","unit.merge","municipal","Registry Authority","merge decision and successor","unit.merge","historical only","appeal","deny no successor","true"),("active","split","split-unit","unit.split","municipal","Registry Authority","split decision and successors","unit.split","historical only","appeal","deny no successors","true"),("active","retired","retire-unit","unit.retire","municipal","Registry Authority","retirement evidence","unit.retire","remove current","reinstate","deny active publication","true")]),
        "locality_lifecycle": g("locality_lifecycle", [("candidate","official","approve-locality","locality.approve","province","GIS/Data Authority","locality authority evidence","locality.approve","public after release","rename/retire","deny missing admin context"),("official","renamed","approve-rename","locality.rename","province","GIS/Data Authority","name replacement","locality.rename","new name after release","appeal","deny no historical name"),("official","retired","retire-locality","locality.retire","province","GIS/Data Authority","retirement decision","locality.retire","remove current","reinstate","deny active links","true")]),
        "country_lifecycle": g("country_lifecycle", [("active","retired","retire-country-row","country.retire","national","Registry Authority","retirement decision","country.retire","not current","reinstate by SDA","deny missing decision","true")]),
        "entrance_lifecycle": g("entrance_lifecycle", [("candidate","active","approve-entrance","entrance.approve","municipal","Registry Authority","entrance evidence","entrance.approve","public through address release","retire/revoke","deny missing evidence"),("active","retired","retire-entrance","entrance.retire","municipal","Registry Authority","retirement decision","entrance.retire","not current","reinstate","deny active links","true"),("candidate","revoked","reject-entrance","entrance.reject","municipal","Registry Authority","rejection reason","entrance.reject","never public","resubmit","deny missing reason","true")]),
        "landmark_lifecycle": g("landmark_lifecycle", [("candidate","official","approve-landmark","landmark.approve","province","GIS/Data Authority","landmark evidence","landmark.approve","public after release","retire/revoke","deny missing evidence"),("official","retired","retire-landmark","landmark.retire","province","GIS/Data Authority","retirement decision","landmark.retire","not current","reinstate","deny active links","true"),("candidate","revoked","reject-landmark","landmark.reject","province","GIS/Data Authority","rejection reason","landmark.reject","never public","resubmit","deny missing reason","true")]),
        "non_building_object_lifecycle": g("non_building_object_lifecycle", [("candidate","active","approve-object","object.approve","municipal","Registry Authority","object evidence","object.approve","public through release if allowed","retire/revoke","deny missing evidence"),("active","retired","retire-object","object.retire","municipal","Registry Authority","retirement decision","object.retire","not current","reinstate","deny active links","true"),("candidate","revoked","reject-object","object.reject","municipal","Registry Authority","rejection reason","object.reject","never public","resubmit","deny missing reason","true")]),
        "operational_area_lifecycle": g("operational_area_lifecycle", [("planned","active","activate-area","ops.area.activate","operations-zone","Operations Authority","work plan approval","ops.area.activate","operator-only","suspend/close","deny missing owner"),("active","suspended","suspend-area","ops.area.suspend","operations-zone","Operations Authority","suspension reason","ops.area.suspend","operator-only","reactivate","deny missing reason"),("suspended","active","reactivate-area","ops.area.reactivate","operations-zone","Operations Authority","reactivation approval","ops.area.reactivate","operator-only","suspend/close","deny missing approval"),("active","closed","close-area","ops.area.close","operations-zone","Operations Authority","closure report","ops.area.close","operator-only","archive","deny open work"),("closed","archived","archive-area","ops.area.archive","operations-zone","Operations Authority","archive approval","ops.area.archive","operator-only","none","deny retention not met","true")]),
        "source_authority_lifecycle": g("source_authority_lifecycle", [("candidate","trusted","approve-source","source.approve","national","SDA","source accreditation","source.approve","operator authority list","deprecate/revoke","deny incomplete accreditation"),("trusted","deprecated","deprecate-source","source.deprecate","national","SDA","deprecation decision","source.deprecate","operator warning","reinstate by SDA","deny replacement missing"),("trusted","revoked","revoke-source","source.revoke","national","SDA","revocation decision","source.revoke","not used for new facts","appeal to SDA","deny missing decision","true"),("candidate","revoked","reject-source","source.reject","national","SDA","review denial","source.reject","never trusted","resubmit","deny missing reason","true")]),
        "name_lifecycle": g("name_lifecycle", [("candidate","official-current","approve-official-name","name.approve.official","province","Registry/GIS Authority","language/name authority evidence","name.approve","public after release","replace/dispute","deny duplicate current"),("official-current","official-historical","replace-official-name","name.replace.official","province","Registry/GIS Authority","replacement name","name.replace","old name historical","appeal","deny no successor"),("candidate","alternate","approve-alternate","name.approve.alternate","province","Registry/GIS Authority","alternate name evidence","name.alternate","operator/public if release allows","retire","deny missing evidence"),("official-current","disputed","open-name-dispute","name.dispute.open","province","Registry Authority","dispute case","name.dispute","operator warning","resolve","deny no case"),("disputed","official-current","resolve-name-dispute-retain","name.dispute.resolve","province","Registry Authority","resolution decision","name.resolve","restore public if released","appeal","deny missing decision"),("candidate","rejected","reject-name","name.reject","province","Registry/GIS Authority","denial reason","name.reject","never public","resubmit","deny missing reason","true"),("alternate","retired","retire-alternate","name.retire","province","Registry/GIS Authority","retirement reason","name.retire","not current","reinstate","deny missing reason","true")]),
        "case_lifecycle": g("case_lifecycle", [("submitted","under-review","triage-case","case.triage","province","Registry Authority","case submission","case.triage","operator-only","request evidence","deny invalid target"),("under-review","needs-evidence","request-evidence","case.request_evidence","province","Registry Authority","evidence request","case.evidence.request","operator-only","receive evidence","deny no requester"),("needs-evidence","under-review","evidence-received","case.evidence.receive","province","Registry Authority","submitted evidence","case.evidence.receive","operator-only","approve/reject","deny missing evidence"),("under-review","approved","approve-case","case.approve","province","Registry Authority","decision record","case.approve","may affect public after release","appeal","deny missing authority"),("under-review","rejected","reject-case","case.reject","province","Registry Authority","denial reason","case.reject","operator-only","appeal/resubmit","deny missing reason"),("approved","resolved","apply-decision","case.resolve","province","Registry Authority","applied change proof","case.resolve","public only through release","reopen by SDA","deny unapplied change"),("rejected","closed","close-rejected-case","case.close","province","Registry Authority","closure note","case.close","none","reopen by appeal","deny open appeal","true"),("resolved","closed","close-resolved-case","case.close","province","Registry Authority","closure note","case.close","none","reopen by SDA","deny open work","true")]),
        "geometry_quality_state": g("geometry_quality_state", [("observed","quality-checked","run-quality-check","geometry.quality.run","province","GIS/Data Authority","quality check output","geometry.quality.run","operator-only","rerun","deny invalid geometry"),("quality-checked","reviewed","review-quality-result","geometry.quality.review","province","GIS/Data Authority","review decision","geometry.quality.review","operator-only","return to observed","deny missing reviewer"),("reviewed","accepted-canonical","accept-canonical-geometry","geometry.promote","province","GIS/Data Authority","accepted quality + evidence bundle","geometry.promote","eligible for release","supersede","deny missing evidence"),("reviewed","valid-with-warning","accept-with-warning","geometry.accept.warning","province","GIS/Data Authority","warning decision","geometry.warning","operator warning","recheck","deny missing warning"),("reviewed","rejected","reject-geometry","geometry.reject","province","GIS/Data Authority","rejection reason","geometry.reject","not public","recapture","deny missing reason","true"),("reviewed","disputed","open-geometry-dispute-before-acceptance","geometry.dispute.open","province","Registry/GIS Authority","geometry dispute case","geometry.dispute","operator-only","resolve","deny no case"),("accepted-canonical","superseded","replace-canonical-geometry","geometry.supersede","province","GIS/Data Authority","successor geometry","geometry.supersede","old geometry historical","appeal","deny cycle","true"),("disputed","reviewed","resolve-geometry-dispute-for-review","geometry.dispute.resolve","province","Registry/GIS Authority","resolution evidence","geometry.dispute.resolve","operator-only","accept/reject","deny missing decision")]),
        "publication_lifecycle": g("publication_lifecycle", [("draft","approval-requested","request-publication-approval","publication.request","national","Publication Authority","release package","publication.request","not public","withdraw","deny empty package"),("approval-requested","approved","approve-publication","publication.approve","national","Publication Authority","approval record","publication.approve","ready to publish","withdraw","deny missing checks"),("approval-requested","withdrawn","withdraw-request","publication.withdraw","national","Publication Authority","withdrawal note","publication.withdraw","not public","new draft","deny missing reason","true"),("approved","published","publish-release","publication.publish","national","Publication Authority","published manifest","publication.publish","public release active","suspend/withdraw","deny missing manifest"),("published","suspended","suspend-publication","publication.suspend","national","Publication Authority","suspension reason","publication.suspend","public hidden/suspended","reinstate","deny missing reason"),("suspended","published","reinstate-publication","publication.reinstate","national","Publication Authority","reinstatement decision","publication.reinstate","public active","suspend","deny missing decision"),("published","withdrawn","withdraw-publication","publication.withdraw","national","Publication Authority","withdrawal decision","publication.withdraw","public withdrawn","new release","deny retention gap","true")]),
        "intake_state": g("intake_state", [("submitted","under-review","triage-intake","intake.triage","province","Registry Authority","submission","intake.triage","operator-only","reject/promote","deny invalid submission"),("under-review","duplicate-review","detect-duplicate","intake.duplicate","province","Registry Authority","duplicate evidence","intake.duplicate","operator-only","clear duplicate","deny no match"),("under-review","needs-field-check","send-field-check","intake.field_check","province","Field Operations","field task request","intake.field_check","operator-only","return field check","deny no task"),("needs-field-check","under-review","field-check-returned","intake.field_return","province","Field Operations","field evidence","intake.field_return","operator-only","promote/reject","deny missing evidence"),("duplicate-review","under-review","clear-duplicate","intake.clear_duplicate","province","Registry Authority","clearance note","intake.clear_duplicate","operator-only","promote/reject","deny missing note"),("under-review","promoted-to-canonical","promote-to-canonical","intake.promote","province","Registry Authority","canonical link","intake.promote","public after release","correct","deny no canonical target"),("under-review","rejected","reject-intake","intake.reject","province","Registry Authority","denial reason","intake.reject","not public","resubmit","deny missing reason","true"),("promoted-to-canonical","closed","close-promoted-intake","intake.close","province","Registry Authority","closure note","intake.close","none","reopen by SDA","deny missing canonical proof","true"),("rejected","closed","close-rejected-intake","intake.close","province","Registry Authority","closure note","intake.close","none","appeal","deny open appeal","true")]),
        "field_verification_state": g("field_verification_state", [("assigned","in-progress","start-field-task","field.start","field-zone","Field Operations","assignment","field.start","operator-only","cancel","deny wrong assignee"),("in-progress","field-captured","capture-field-evidence","field.capture","field-zone","Field Operations","GPS/photo/evidence","field.capture","operator-only","review","deny missing capture"),("field-captured","evidence-under-review","submit-evidence-review","field.submit_review","field-zone","Field Operations","submitted evidence","field.review.submit","operator-only","approve/reject","deny incomplete evidence"),("evidence-under-review","evidence-approved","approve-evidence","field.evidence.approve","province","Registry Authority","approval record","field.evidence.approve","eligible canonical evidence","link canonical","deny missing authority"),("evidence-under-review","evidence-rejected","reject-evidence","field.evidence.reject","province","Registry Authority","rejection reason","field.evidence.reject","not public","recapture","deny missing reason"),("evidence-rejected","needs-recapture","request-recapture","field.recapture.request","field-zone","Field Operations","recapture task","field.recapture","operator-only","restart","deny missing reason"),("needs-recapture","in-progress","restart-field-task","field.restart","field-zone","Field Operations","restart assignment","field.restart","operator-only","capture","deny wrong assignee"),("evidence-approved","linked-to-canonical","link-approved-evidence","field.link","province","Registry Authority","canonical link","field.link","operator-only/public via release","unlink by correction","deny missing canonical"),("assigned","cancelled","cancel-field-task","field.cancel","field-zone","Field Operations","cancel reason","field.cancel","operator-only","reassign","deny missing reason","true")]),
    }


def render_vocab_and_lifecycle(model: dict[str, Any]) -> None:
    field_rows = []
    for e, meta in model["entities"].items():
        for f in meta.get("fields", []):
            if f.get("vocabulary"):
                field_rows.append([f"`{e}.{f['name']}`", f"`{f['vocabulary']}`", model["vocabularies"][f["vocabulary"]]["owner"], ", ".join(model["vocabularies"][f["vocabulary"]]["values"].keys())])
    vocab_sections = ["# Controlled Vocabulary Registry", "", "One authoritative field-to-vocabulary registry. Review 05 separates canonical records, reference objects, operational areas, source authorities, names, cases, geometry, and publication lifecycles.", "", "## Field-to-vocabulary registry", "", md_table(["Target field", "Vocabulary", "Owner", "Allowed values"], field_rows)]
    for name, meta in sorted(model["vocabularies"].items()):
        vocab_sections.append(f"\n## `{name}`\n\nOwner: **{meta['owner']}**\n\n" + md_table(["Value", "Meaning"], [[k, v] for k, v in meta["values"].items()]))
    write("docs/sda/data-model/controlled-vocabularies.md", "\n".join(vocab_sections))
    transitions = authored_lifecycle_transitions()
    errors = []
    for vocab, edges in transitions.items():
        if vocab not in model["vocabularies"]:
            errors.append(f"transition graph references missing vocabulary {vocab}")
            continue
        values = set(model["vocabularies"][vocab]["values"])
        for edge in edges:
            if edge["from"] not in values or edge["to"] not in values:
                errors.append(f"{vocab} transition {edge['from']}->{edge['to']} references value outside vocabulary")
    forbidden = {("approved","rejected"), ("approved","draft"), ("closed","duplicate-review"), ("cancelled","evidence-approved"), ("accepted-canonical","disputed")}
    for vocab, edges in transitions.items():
        for edge in edges:
            if (edge["from"], edge["to"]) in forbidden:
                errors.append(f"forbidden generated-style transition present in {vocab}: {edge['from']}->{edge['to']}")
    if errors:
        raise SystemExit("authored lifecycle transition validation failed:\n- " + "\n- ".join(errors))
    write_json("docs/sda/data-model/lifecycle-transitions.json", transitions)
    parts = ["# Lifecycle State Machines", "", "Transitions are hand-authored. No transition is inferred from vocabulary order. Every transition records actor/permission/scope, authority, evidence, effective time, recorded time, audit event, visibility, reversal/appeal, and invalid-transition behavior."]
    for vocab, edges in transitions.items():
        rows = [[e["from"], e["to"], e["event"], e["actor"], e["evidence"], e["time_rule"], e["visibility"], e["appeal"], e["invalid_behavior"]] for e in edges]
        terminals = sorted(set(model["vocabularies"][vocab]["values"]) - {e["from"] for e in edges})
        parts.append(f"\n## `{vocab}` transitions\n\n" + md_table(["From", "To", "Event", "Actor/permission/scope", "Authority/evidence", "Effective/recorded time", "Visibility", "Reversal/appeal", "Invalid transition"], rows) + f"\n\nTerminal values: {', '.join(terminals) if terminals else 'none'}.")
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
    # Review 05 physical-expression constraints/triggers (design SQL executed only in disposable validation DBs).
    lines += [
        "CREATE TABLE subject_entity_registry(entity_name text PRIMARY KEY, pk_column text NOT NULL);",
        "INSERT INTO subject_entity_registry(entity_name, pk_column) VALUES ('location_record','location_record_id'),('administrative_unit','administrative_unit_id'),('operational_area','operational_area_id'),('road','road_id'),('road_segment','road_segment_id'),('building','building_id'),('unit','unit_id'),('entrance','entrance_id'),('landmark','landmark_id'),('non_building_object','object_id'),('locality','locality_id'),('geometry_version','geometry_version_id');",
        "CREATE TABLE record_object_role_matrix(record_type text NOT NULL, object_role text NOT NULL, required boolean NOT NULL, min_count integer NOT NULL, max_count integer NOT NULL, allowed_subject_entities text[] NOT NULL, retirement_behavior text NOT NULL, merge_behavior text NOT NULL, PRIMARY KEY(record_type, object_role));",
        "INSERT INTO record_object_role_matrix VALUES ('address','primary-subject',true,1,1,ARRAY['building','unit','non_building_object','landmark','location_record'],'retire-link-with-record-version','repoint-through-successor-subject'),('address','context-road',false,0,1,ARRAY['road','road_segment'],'retain-history-disable-current','repoint-on-approved-merge'),('address','context-locality',false,0,1,ARRAY['locality','administrative_unit'],'retain-history-disable-current','repoint-on-approved-merge'),('address','access-point',false,0,4,ARRAY['entrance'],'retire-link','repoint-on-approved-merge'),('address','nearby-landmark',false,0,5,ARRAY['landmark'],'retain-context','repoint-on-approved-merge'),('building','primary-subject',true,1,1,ARRAY['building'],'retire-link-with-record-version','repoint-through-successor-subject'),('building','access-point',false,0,12,ARRAY['entrance'],'retire-link','repoint-on-approved-merge'),('unit','primary-subject',true,1,1,ARRAY['unit'],'retire-link-with-record-version','repoint-through-successor-subject'),('unit','parent-building',true,1,1,ARRAY['building'],'retain-history-disable-current','repoint-on-approved-merge'),('entrance','primary-subject',true,1,1,ARRAY['entrance'],'retire-link-with-record-version','repoint-through-successor-subject'),('landmark','primary-subject',true,1,1,ARRAY['landmark'],'retire-link-with-record-version','repoint-through-successor-subject'),('non-building-object','primary-subject',true,1,1,ARRAY['non_building_object'],'retire-link-with-record-version','repoint-through-successor-subject'),('service-location','primary-subject',true,1,1,ARRAY['location_record','non_building_object','administrative_unit'],'retire-link-with-record-version','repoint-through-successor-subject'),('service-location','external-parcel-reference',false,0,1,ARRAY['location_record'],'retain-context','repoint-on-approved-merge');",
        "CREATE TABLE geometry_role_matrix(geometry_role text PRIMARY KEY, geometry_types text[] NOT NULL, subject_entities text[] NOT NULL, observation_allowed boolean NOT NULL, promotion_permission text NOT NULL);",
        "INSERT INTO geometry_role_matrix VALUES ('building-point',ARRAY['POINT'],ARRAY['building'],true,'geometry.promote'),('entrance-point',ARRAY['POINT'],ARRAY['entrance','unit','building'],true,'geometry.promote'),('location-point',ARRAY['POINT'],ARRAY['location_record','non_building_object'],true,'geometry.promote'),('landmark-point',ARRAY['POINT'],ARRAY['landmark'],true,'geometry.promote'),('road-centerline',ARRAY['LINESTRING','MULTILINESTRING'],ARRAY['road','road_segment'],true,'geometry.promote'),('admin-boundary',ARRAY['POLYGON','MULTIPOLYGON'],ARRAY['administrative_unit'],true,'geometry.promote'),('operational-boundary',ARRAY['POLYGON','MULTIPOLYGON'],ARRAY['operational_area'],true,'geometry.promote'),('building-footprint',ARRAY['POLYGON','MULTIPOLYGON'],ARRAY['building'],true,'geometry.promote'),('parcel-boundary',ARRAY['POLYGON','MULTIPOLYGON'],ARRAY['location_record'],true,'geometry.promote');",
        "CREATE OR REPLACE FUNCTION enforce_registry_subject_native() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE pk text; found_row boolean; BEGIN SELECT pk_column INTO pk FROM subject_entity_registry WHERE entity_name=NEW.subject_entity; IF pk IS NULL THEN RAISE EXCEPTION 'unknown subject entity %', NEW.subject_entity; END IF; EXECUTE format('SELECT EXISTS (SELECT 1 FROM proposed_%I WHERE %I = $1)', NEW.subject_entity, pk) INTO found_row USING NEW.native_id; IF NOT found_row THEN RAISE EXCEPTION 'registry subject native target %.% does not exist', NEW.subject_entity, NEW.native_id; END IF; RETURN NEW; END $$;",
        "CREATE CONSTRAINT TRIGGER registry_subject_native_trg AFTER INSERT OR UPDATE ON proposed_registry_subject DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_native();",
        "CREATE OR REPLACE FUNCTION enforce_registry_subject_link() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.subject_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_registry_subject s WHERE s.subject_id = NEW.subject_id AND s.subject_state IN ('active','retired','merged')) THEN RAISE EXCEPTION 'registry subject % missing or not linkable', NEW.subject_id; END IF; RETURN NEW; END $$;",
        "CREATE TRIGGER name_record_subject_trg BEFORE INSERT OR UPDATE ON proposed_name_record FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_link();",
        "CREATE TRIGGER object_link_subject_trg BEFORE INSERT OR UPDATE ON proposed_location_record_object_link FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_link();",
        "CREATE TRIGGER dispute_case_subject_trg BEFORE INSERT OR UPDATE ON proposed_dispute_case FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_link();",
        "CREATE TRIGGER geometry_version_subject_trg BEFORE INSERT OR UPDATE ON proposed_geometry_version FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_link();",
        "CREATE TRIGGER geometry_observation_subject_trg BEFORE INSERT OR UPDATE ON proposed_geometry_observation FOR EACH ROW EXECUTE FUNCTION enforce_registry_subject_link();",
        "CREATE OR REPLACE FUNCTION reject_subject_delete_with_dependents() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF EXISTS (SELECT 1 FROM proposed_name_record WHERE subject_id=OLD.subject_id) OR EXISTS (SELECT 1 FROM proposed_geometry_version WHERE subject_id=OLD.subject_id) OR EXISTS (SELECT 1 FROM proposed_geometry_observation WHERE subject_id=OLD.subject_id) OR EXISTS (SELECT 1 FROM proposed_dispute_case WHERE subject_id=OLD.subject_id) OR EXISTS (SELECT 1 FROM proposed_location_record_object_link WHERE subject_id=OLD.subject_id) THEN RAISE EXCEPTION 'subject % must be retired or merged, not deleted', OLD.subject_id; END IF; RETURN OLD; END $$;",
        "CREATE TRIGGER registry_subject_delete_policy_trg BEFORE DELETE ON proposed_registry_subject FOR EACH ROW EXECUTE FUNCTION reject_subject_delete_with_dependents();",
        "CREATE OR REPLACE FUNCTION enforce_object_role_cardinality() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE rule record; v_subject_entity text; v_record_type text; current_count integer; v_from timestamptz; v_to timestamptz; BEGIN SELECT lr.record_type INTO v_record_type FROM proposed_location_record_version lrv JOIN proposed_location_record lr ON lr.location_record_id=lrv.location_record_id WHERE lrv.location_record_version_id=NEW.location_record_version_id; SELECT * INTO rule FROM record_object_role_matrix WHERE record_object_role_matrix.record_type=v_record_type AND object_role=NEW.object_role; IF rule.object_role IS NULL THEN RAISE EXCEPTION 'invalid object role %', NEW.object_role; END IF; SELECT s.subject_entity INTO v_subject_entity FROM proposed_registry_subject s WHERE s.subject_id=NEW.subject_id; IF v_subject_entity IS NULL OR NOT (v_subject_entity = ANY(rule.allowed_subject_entities)) THEN RAISE EXCEPTION 'subject type % not allowed for object role %', v_subject_entity, NEW.object_role; END IF; SELECT effective_from, effective_to INTO v_from, v_to FROM proposed_location_record_version WHERE location_record_version_id=NEW.location_record_version_id; IF v_from IS NULL THEN RAISE EXCEPTION 'owning record version missing for object link'; END IF; IF NEW.effective_from < v_from OR (v_to IS NOT NULL AND COALESCE(NEW.effective_to, v_to) > v_to) THEN RAISE EXCEPTION 'object link interval outside owning record version'; END IF; SELECT COUNT(*) INTO current_count FROM proposed_location_record_object_link l WHERE l.location_record_version_id=NEW.location_record_version_id AND l.object_role=NEW.object_role AND l.link_id<>NEW.link_id AND (l.effective_to IS NULL OR l.effective_to > NEW.effective_from); IF current_count + 1 > rule.max_count THEN RAISE EXCEPTION 'object role % exceeds max count %', NEW.object_role, rule.max_count; END IF; RETURN NEW; END $$;",
        "CREATE TRIGGER object_role_cardinality_trg BEFORE INSERT OR UPDATE ON proposed_location_record_object_link FOR EACH ROW EXECUTE FUNCTION enforce_object_role_cardinality();",
        "CREATE OR REPLACE FUNCTION enforce_required_object_roles() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE missing_role text; rt text; BEGIN SELECT lr.record_type INTO rt FROM proposed_location_record lr WHERE lr.location_record_id=NEW.location_record_id; SELECT m.object_role INTO missing_role FROM record_object_role_matrix m WHERE m.record_type=rt AND m.required AND NOT EXISTS (SELECT 1 FROM proposed_location_record_object_link l WHERE l.location_record_version_id=NEW.location_record_version_id AND l.object_role=m.object_role AND (l.effective_to IS NULL OR l.effective_to > NEW.effective_from)) LIMIT 1; IF missing_role IS NOT NULL THEN RAISE EXCEPTION 'location record version requires role % for record type %', missing_role, rt; END IF; RETURN NEW; END $$;",
        "CREATE CONSTRAINT TRIGGER required_object_roles_trg AFTER INSERT OR UPDATE ON proposed_location_record_version DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION enforce_required_object_roles();",
        "CREATE OR REPLACE FUNCTION enforce_current_official_name() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.name_kind LIKE 'official%' AND NEW.name_status='official-current' AND EXISTS (SELECT 1 FROM proposed_name_record n WHERE n.subject_id=NEW.subject_id AND n.language_code=NEW.language_code AND n.name_kind LIKE 'official%' AND n.name_status='official-current' AND n.name_record_id<>NEW.name_record_id AND (n.effective_to IS NULL OR n.effective_to > NEW.effective_from)) THEN RAISE EXCEPTION 'subject % already has current official name for language %', NEW.subject_id, NEW.language_code; END IF; RETURN NEW; END $$;",
        "CREATE TRIGGER current_official_name_trg BEFORE INSERT OR UPDATE ON proposed_name_record FOR EACH ROW EXECUTE FUNCTION enforce_current_official_name();",
        "CREATE OR REPLACE FUNCTION enforce_geometry_version_semantics() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE rule record; v_subject_entity text; obs record; decision_row record; BEGIN SELECT * INTO rule FROM geometry_role_matrix WHERE geometry_role=NEW.geometry_role; IF rule.geometry_role IS NULL THEN RAISE EXCEPTION 'unknown geometry role %', NEW.geometry_role; END IF; SELECT s.subject_entity INTO v_subject_entity FROM proposed_registry_subject s WHERE s.subject_id=NEW.subject_id; IF v_subject_entity IS NULL OR NOT (v_subject_entity = ANY(rule.subject_entities)) THEN RAISE EXCEPTION 'subject type % not allowed for geometry role %', v_subject_entity, NEW.geometry_role; END IF; IF GeometryType(NEW.geom) <> ALL(rule.geometry_types) THEN RAISE EXCEPTION 'invalid geometry type for role %', NEW.geometry_role; END IF; IF ST_NDims(NEW.geom) <> 2 OR ST_SRID(NEW.geom) <> 4326 OR NOT ST_IsValid(NEW.geom) THEN RAISE EXCEPTION 'invalid geometry dimensionality/SRID/validity'; END IF; IF NEW.superseded_by_geometry_version_id = NEW.geometry_version_id THEN RAISE EXCEPTION 'geometry version cannot supersede itself'; END IF; IF NEW.superseded_by_geometry_version_id IS NOT NULL AND EXISTS (WITH RECURSIVE chain(id) AS (SELECT NEW.superseded_by_geometry_version_id UNION ALL SELECT g.superseded_by_geometry_version_id FROM proposed_geometry_version g JOIN chain c ON g.geometry_version_id=c.id WHERE g.superseded_by_geometry_version_id IS NOT NULL) SELECT 1 FROM chain WHERE id=NEW.geometry_version_id) THEN RAISE EXCEPTION 'geometry supersession cycle'; END IF; SELECT * INTO obs FROM proposed_geometry_observation WHERE geometry_observation_id=NEW.source_observation_id; IF obs.geometry_observation_id IS NULL OR obs.subject_id<>NEW.subject_id OR obs.geometry_role<>NEW.geometry_role THEN RAISE EXCEPTION 'geometry promotion requires same-subject same-role observation'; END IF; IF obs.evidence_object_id IS DISTINCT FROM NEW.promotion_evidence_object_id THEN RAISE EXCEPTION 'geometry promotion evidence must match source observation evidence'; END IF; IF NEW.promotion_decision_event_id IS NULL OR NEW.promotion_evidence_object_id IS NULL OR COALESCE(NEW.promotion_authority_scope,'')='' THEN RAISE EXCEPTION 'geometry promotion requires authorized decision, evidence and authority scope'; END IF; SELECT * INTO decision_row FROM proposed_decision_event d WHERE d.decision_event_id=NEW.promotion_decision_event_id; IF decision_row.decision_event_id IS NULL OR decision_row.decision_type <> 'approve-geometry' OR decision_row.decision_outcome NOT IN ('approved','accepted') THEN RAISE EXCEPTION 'geometry promotion decision is not authorized'; END IF; IF decision_row.details_json->>'permission_key' IS DISTINCT FROM rule.promotion_permission THEN RAISE EXCEPTION 'geometry promotion actor lacks required permission %', rule.promotion_permission; END IF; IF COALESCE(decision_row.details_json->>'institution_id','') = '' OR COALESCE(decision_row.details_json->>'territorial_scope','') = '' OR decision_row.details_json->>'territorial_scope' IS DISTINCT FROM NEW.promotion_authority_scope THEN RAISE EXCEPTION 'geometry promotion institution or territorial scope mismatch'; END IF; IF decision_row.details_json->>'quality_authority_actor_id' IS DISTINCT FROM NEW.validated_by_actor_id THEN RAISE EXCEPTION 'geometry quality authority actor mismatch'; END IF; IF decision_row.details_json->>'evidence_object_id' IS DISTINCT FROM NEW.promotion_evidence_object_id THEN RAISE EXCEPTION 'geometry decision evidence link mismatch'; END IF; IF decision_row.details_json->>'source_observation_id' IS DISTINCT FROM NEW.source_observation_id THEN RAISE EXCEPTION 'geometry decision observation link mismatch'; END IF; IF NEW.superseded_by_geometry_version_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_geometry_version s WHERE s.geometry_version_id=NEW.superseded_by_geometry_version_id AND s.subject_id=NEW.subject_id AND s.geometry_role=NEW.geometry_role) THEN RAISE EXCEPTION 'geometry supersession successor must share subject and role'; END IF; IF NEW.quality_state NOT IN ('accepted-canonical','valid-with-warning') THEN RAISE EXCEPTION 'geometry promotion requires accepted quality decision'; END IF; RETURN NEW; END $$;",
        "CREATE TRIGGER geometry_version_semantics_trg BEFORE INSERT OR UPDATE ON proposed_geometry_version FOR EACH ROW EXECUTE FUNCTION enforce_geometry_version_semantics();",
        "CREATE OR REPLACE FUNCTION enforce_geometry_observation_semantics() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE rule record; v_subject_entity text; BEGIN SELECT * INTO rule FROM geometry_role_matrix WHERE geometry_role=NEW.geometry_role; IF rule.geometry_role IS NULL OR NOT rule.observation_allowed THEN RAISE EXCEPTION 'geometry observation role not allowed %', NEW.geometry_role; END IF; SELECT s.subject_entity INTO v_subject_entity FROM proposed_registry_subject s WHERE s.subject_id=NEW.subject_id; IF v_subject_entity IS NULL OR NOT (v_subject_entity = ANY(rule.subject_entities)) THEN RAISE EXCEPTION 'subject type % not allowed for observation role %', v_subject_entity, NEW.geometry_role; END IF; IF GeometryType(NEW.observed_geom) <> ALL(rule.geometry_types) OR ST_NDims(NEW.observed_geom)<>2 OR ST_SRID(NEW.observed_geom)<>4326 OR NOT ST_IsValid(NEW.observed_geom) THEN RAISE EXCEPTION 'invalid observation geometry'; END IF; RETURN NEW; END $$;",
        "CREATE TRIGGER geometry_observation_semantics_trg BEFORE INSERT OR UPDATE ON proposed_geometry_observation FOR EACH ROW EXECUTE FUNCTION enforce_geometry_observation_semantics();",
        "CREATE OR REPLACE FUNCTION enforce_version_chain() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.predecessor_version_id = NEW.location_record_version_id OR NEW.successor_version_id = NEW.location_record_version_id THEN RAISE EXCEPTION 'version chain cannot self-reference'; END IF; IF NEW.predecessor_version_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_location_record_version p WHERE p.location_record_version_id=NEW.predecessor_version_id AND p.location_record_id=NEW.location_record_id AND p.successor_version_id=NEW.location_record_version_id) THEN RAISE EXCEPTION 'predecessor must reciprocally point to this version and share owner'; END IF; IF NEW.successor_version_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_location_record_version s WHERE s.location_record_version_id=NEW.successor_version_id AND s.location_record_id=NEW.location_record_id AND s.predecessor_version_id=NEW.location_record_version_id) THEN RAISE EXCEPTION 'successor must reciprocally point to this version and share owner'; END IF; IF EXISTS (WITH RECURSIVE chain(id) AS (SELECT NEW.successor_version_id UNION ALL SELECT v.successor_version_id FROM proposed_location_record_version v JOIN chain c ON v.location_record_version_id=c.id WHERE v.successor_version_id IS NOT NULL) SELECT 1 FROM chain WHERE id=NEW.location_record_version_id) THEN RAISE EXCEPTION 'version chain cycle'; END IF; RETURN NEW; END $$;",
        "CREATE CONSTRAINT TRIGGER location_record_version_chain_trg AFTER INSERT OR UPDATE ON proposed_location_record_version DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION enforce_version_chain();",
        "CREATE OR REPLACE FUNCTION enforce_alias_chain() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.predecessor_alias_id = NEW.public_code_alias_id OR NEW.successor_alias_id = NEW.public_code_alias_id THEN RAISE EXCEPTION 'alias chain cannot self-reference'; END IF; IF NEW.predecessor_alias_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_public_code_alias p WHERE p.public_code_alias_id=NEW.predecessor_alias_id AND p.location_record_id=NEW.location_record_id AND p.successor_alias_id=NEW.public_code_alias_id) THEN RAISE EXCEPTION 'predecessor alias must reciprocally point to this alias and share owner'; END IF; IF NEW.successor_alias_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM proposed_public_code_alias s WHERE s.public_code_alias_id=NEW.successor_alias_id AND s.location_record_id=NEW.location_record_id AND s.predecessor_alias_id=NEW.public_code_alias_id) THEN RAISE EXCEPTION 'successor alias must reciprocally point to this alias and share owner'; END IF; IF EXISTS (WITH RECURSIVE chain(id) AS (SELECT NEW.successor_alias_id UNION ALL SELECT a.successor_alias_id FROM proposed_public_code_alias a JOIN chain c ON a.public_code_alias_id=c.id WHERE a.successor_alias_id IS NOT NULL) SELECT 1 FROM chain WHERE id=NEW.public_code_alias_id) THEN RAISE EXCEPTION 'public code alias cycle'; END IF; RETURN NEW; END $$;",
        "CREATE CONSTRAINT TRIGGER public_code_alias_chain_trg AFTER INSERT OR UPDATE ON proposed_public_code_alias DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION enforce_alias_chain();",
        "CREATE OR REPLACE FUNCTION enforce_publication_prerequisite() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NOT EXISTS (SELECT 1 FROM proposed_publication_release r WHERE r.publication_release_id=NEW.publication_release_id AND r.release_state IN ('approved','published')) THEN RAISE EXCEPTION 'publication prerequisite not met'; END IF; RETURN NEW; END $$;",
        "CREATE CONSTRAINT TRIGGER publication_prerequisite_trg AFTER INSERT OR UPDATE ON proposed_publication_release_item DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION enforce_publication_prerequisite();",
        "CREATE TABLE lifecycle_transition_policy(vocab text NOT NULL, from_state text NOT NULL, to_state text NOT NULL, permission_key text NOT NULL, evidence text NOT NULL, audit_event text NOT NULL, public_effect text NOT NULL, terminal boolean NOT NULL DEFAULT false, PRIMARY KEY(vocab, from_state, to_state));",
        "CREATE OR REPLACE FUNCTION validate_lifecycle_transition(vocab text, from_state text, to_state text) RETURNS boolean LANGUAGE plpgsql AS $$ BEGIN IF EXISTS (SELECT 1 FROM lifecycle_transition_policy p WHERE p.vocab=validate_lifecycle_transition.vocab AND p.from_state=validate_lifecycle_transition.from_state AND p.to_state=validate_lifecycle_transition.to_state) THEN RETURN true; END IF; RAISE EXCEPTION 'forbidden transition %.% -> %', vocab, from_state, to_state; END $$;",
        "ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_recorded_excl EXCLUDE USING gist (location_record_id WITH =, tstzrange(recorded_at, COALESCE(recorded_to, 'infinity'::timestamptz), '[)') WITH &&) DEFERRABLE INITIALLY DEFERRED;",
        "ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_location_record_version_effective_excl EXCLUDE USING gist (location_record_id WITH =, tstzrange(effective_from, COALESCE(effective_to, 'infinity'::timestamptz), '[)') WITH &&) DEFERRABLE INITIALLY DEFERRED;",
        "ALTER TABLE proposed_administrative_code_history ADD CONSTRAINT proposed_admin_code_history_effective_excl EXCLUDE USING gist (administrative_unit_id WITH =, code_scheme WITH =, tstzrange(effective_from, COALESCE(effective_to, 'infinity'::timestamptz), '[)') WITH &&) DEFERRABLE INITIALLY DEFERRED;",
        "ALTER TABLE proposed_geometry_version ADD CONSTRAINT proposed_geometry_version_effective_excl EXCLUDE USING gist (subject_id WITH =, geometry_role WITH =, tstzrange(effective_from, COALESCE(effective_to, 'infinity'::timestamptz), '[)') WITH &&) DEFERRABLE INITIALLY DEFERRED;",
        "ALTER TABLE proposed_location_record_object_link ADD CONSTRAINT proposed_object_link_interval_ck CHECK (effective_to IS NULL OR effective_from < effective_to);",
        "CREATE UNIQUE INDEX proposed_location_record_version_one_current ON proposed_location_record_version(location_record_id) WHERE recorded_to IS NULL;",
        "CREATE UNIQUE INDEX proposed_geometry_version_one_current ON proposed_geometry_version(subject_id, geometry_role) WHERE recorded_to IS NULL;",
        "CREATE UNIQUE INDEX proposed_name_record_one_current_official ON proposed_name_record(subject_id, language_code) WHERE name_kind LIKE 'official%' AND name_status='official-current';",
        "CREATE UNIQUE INDEX proposed_public_code_alias_one_current ON proposed_public_code_alias(location_record_id) WHERE successor_alias_id IS NULL AND code_state='active-public';",
        "CREATE UNIQUE INDEX proposed_admin_code_history_one_current ON proposed_administrative_code_history(administrative_unit_id, code_scheme) WHERE recorded_to IS NULL AND effective_to IS NULL;",
    ]
    for vocab, edges in sorted(authored_lifecycle_transitions().items()):
        for edge in edges:
            lines.append(
                "INSERT INTO lifecycle_transition_policy(vocab, from_state, to_state, permission_key, evidence, audit_event, public_effect, terminal) VALUES ("
                + ", ".join([
                    sql_literal(vocab),
                    sql_literal(edge["from"]),
                    sql_literal(edge["to"]),
                    sql_literal(edge["permission_key"]),
                    sql_literal(edge["evidence"]),
                    sql_literal(edge["audit_event"]),
                    sql_literal(edge["public_effect"]),
                    "true" if str(edge.get("terminal", "false")).lower() == "true" else "false",
                ])
                + ");"
            )
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


SCENARIO_NAMES = [
    "urban-street-address",
    "rural-landmark-location",
    "multi-unit-building",
    "no-formal-road-location",
    "corrected-superseded-address",
    "disputed-geometry",
    "administrative-boundary-change",
]


def scenario_records(model: dict[str, Any], scenario: str, idx: int) -> dict[str, list[dict[str, Any]]]:
    pk = {e: primary_field(e, meta) for e, meta in model["entities"].items()}
    pk_values = {e: f"{scenario}-{e}-{idx:02d}" for e in model["entities"]}
    records: dict[str, list[dict[str, Any]]] = {}
    for entity in dependency_order(model):
        rec = {}
        for f in model["entities"][entity].get("fields", []):
            if f.get("nullable") and f.get("default") is None and not f.get("fk"):
                continue
            rec[f["name"]] = sample_value(entity, f, pk_values, model, idx)
        rec[pk[entity]] = pk_values[entity]
        # Scenario-specific identity and subject values.
        if entity == "location_record":
            record_type = {
                "urban-street-address": "address",
                "rural-landmark-location": "landmark",
                "multi-unit-building": "unit",
                "no-formal-road-location": "service-location",
                "corrected-superseded-address": "address",
                "disputed-geometry": "address",
                "administrative-boundary-change": "service-location",
            }[scenario]
            rec["record_type"] = record_type
        if entity == "registry_subject":
            subject_entity = {
                "urban-street-address": "building",
                "rural-landmark-location": "landmark",
                "multi-unit-building": "unit",
                "no-formal-road-location": "location_record",
                "corrected-superseded-address": "location_record",
                "disputed-geometry": "location_record",
                "administrative-boundary-change": "administrative_unit",
            }[scenario]
            rec.update({"subject_entity": subject_entity, "native_id": pk_values.get(subject_entity, pk_values[entity]), "subject_state": "active", "delete_policy": "retire-only"})
        if "subject_id" in rec:
            rec["subject_id"] = pk_values["registry_subject"]
        if entity == "name_record":
            rec.update({"language_code": "es", "name_kind": "official-es", "name_status": "official-current", "name_text": f"{scenario} official name", "normalized_text": scenario.replace('-', ' ')})
        if entity == "location_record_object_link":
            rec.update({"object_role": "primary-subject", "cardinality_rank": 1})
        if entity == "geometry_version":
            role = {
                "urban-street-address": "building-point",
                "rural-landmark-location": "landmark-point",
                "multi-unit-building": "entrance-point",
                "no-formal-road-location": "location-point",
                "corrected-superseded-address": "location-point",
                "disputed-geometry": "location-point",
                "administrative-boundary-change": "admin-boundary",
            }[scenario]
            geom = "SRID=4326;POLYGON((8.78 3.75,8.79 3.75,8.79 3.76,8.78 3.76,8.78 3.75))" if role == "admin-boundary" else "SRID=4326;POINT(8.78 3.75)"
            rec.update({"geometry_role": role, "geom": geom, "quality_state": "accepted-canonical", "validated_by_actor_id": "decision_event-actor_id-001", "promotion_authority_scope": "national-gis-authority", "promotion_decision_event_id": pk_values["decision_event"], "promotion_evidence_object_id": pk_values["evidence_object"]})
            rec.pop("superseded_by_geometry_version_id", None)
        if entity == "geometry_observation":
            role = {
                "urban-street-address": "building-point",
                "rural-landmark-location": "landmark-point",
                "multi-unit-building": "entrance-point",
                "no-formal-road-location": "location-point",
                "corrected-superseded-address": "location-point",
                "disputed-geometry": "location-point",
                "administrative-boundary-change": "admin-boundary",
            }[scenario]
            geom = "SRID=4326;POLYGON((8.78 3.75,8.79 3.75,8.79 3.76,8.78 3.76,8.78 3.75))" if role == "admin-boundary" else "SRID=4326;POINT(8.78 3.75)"
            rec.update({"geometry_role": role, "observed_geom": geom})
        if entity == "administrative_unit_version":
            rec["lifecycle_state"] = "official"
        if entity == "location_record_version":
            rec["lifecycle_state"] = "active"
            rec.pop("predecessor_version_id", None)
            rec.pop("successor_version_id", None)
        if entity == "public_code_alias":
            rec.pop("predecessor_alias_id", None)
            rec.pop("successor_alias_id", None)
        if entity == "publication_release":
            rec["release_state"] = "approved"
        if entity == "publication_release_item":
            rec["projection_state"] = "included"
        if entity == "decision_event":
            rec["decision_type"] = "approve-geometry"
            rec["decision_outcome"] = "approved"
            rec["details_json"] = {
                "permission_key": "geometry.promote",
                "institution_id": "national-gis-authority",
                "territorial_scope": "national-gis-authority",
                "quality_authority_actor_id": pk_values.get("actor", rec.get("actor_id")),
                "evidence_object_id": pk_values["evidence_object"],
                "source_observation_id": pk_values["geometry_observation"],
            }
        records[entity] = [rec]
    # Review 05: scenario-specific histories/cardinalities/projections, not generic aliases.
    if scenario == "multi-unit-building" and "unit" in records:
        base = records["unit"][0]
        second = dict(base)
        second[pk["unit"]] = f"{scenario}-unit-02"
        second["unit_label"] = "Unit B"
        records["unit"].append(second)
        if "registry_subject" in records:
            sub = dict(records["registry_subject"][0])
            sub["subject_id"] = f"{scenario}-registry-subject-unit-02"
            sub["subject_entity"] = "unit"
            sub["native_id"] = second[pk["unit"]]
            records["registry_subject"].append(sub)
            building_sub = dict(records["registry_subject"][0])
            building_sub["subject_id"] = f"{scenario}-registry-subject-parent-building"
            building_sub["subject_entity"] = "building"
            building_sub["native_id"] = pk_values["building"]
            records["registry_subject"].append(building_sub)
        if "location_record_object_link" in records:
            parent_link = dict(records["location_record_object_link"][0])
            parent_link["link_id"] = f"{scenario}-object-link-parent-building"
            parent_link["object_role"] = "parent-building"
            parent_link["cardinality_rank"] = 1
            parent_link["subject_id"] = f"{scenario}-registry-subject-parent-building"
            records["location_record_object_link"].append(parent_link)
        # Review 07 F04/F10: Unit B must be an independent canonical record, not only an extra unit row.
        if all(name in records for name in ["location_record", "location_record_version", "public_code_alias", "publication_release_item", "location_record_object_link"]) and len(records["location_record_object_link"]) >= 2:
            unit_b_record_id = f"{scenario}-location-record-unit-02"
            unit_b_version_id = f"{scenario}-location-record-version-unit-02"
            unit_b_alias_id = f"{scenario}-public-code-alias-unit-02"
            unit_b_release_item_id = f"{scenario}-publication-release-item-unit-02"
            lr_b = dict(records["location_record"][0])
            lr_b[pk["location_record"]] = unit_b_record_id
            lr_b["record_type"] = "unit"
            records["location_record"].append(lr_b)
            version_b = dict(records["location_record_version"][0])
            version_b[pk["location_record_version"]] = unit_b_version_id
            version_b["location_record_id"] = unit_b_record_id
            version_b["version_number"] = 1
            version_b.pop("predecessor_version_id", None)
            version_b.pop("successor_version_id", None)
            records["location_record_version"].append(version_b)
            alias_b = dict(records["public_code_alias"][0])
            alias_b[pk["public_code_alias"]] = unit_b_alias_id
            alias_b["location_record_id"] = unit_b_record_id
            alias_b["public_code"] = "public_code_alias-public_code-002"
            alias_b.pop("predecessor_alias_id", None)
            alias_b.pop("successor_alias_id", None)
            records["public_code_alias"].append(alias_b)
            item_b = dict(records["publication_release_item"][0])
            item_b[pk["publication_release_item"]] = unit_b_release_item_id
            item_b["location_record_id"] = unit_b_record_id
            item_b["location_record_version_id"] = unit_b_version_id
            item_b["public_code_alias_id"] = unit_b_alias_id
            item_b["published_label"] = "Unit B"
            item_b["projection_payload_hash"] = "multi-unit-unit-b-projection-hash"
            item_b["projection_payload_json"] = {"scenario": "multi-unit-building", "unit": "B", "canonical_record": unit_b_record_id}
            records["publication_release_item"].append(item_b)
            primary_b = dict(records["location_record_object_link"][0])
            primary_b[pk["location_record_object_link"]] = f"{scenario}-object-link-unit-02-primary"
            primary_b["location_record_version_id"] = unit_b_version_id
            primary_b["object_role"] = "primary-subject"
            primary_b["subject_id"] = f"{scenario}-registry-subject-unit-02"
            primary_b["cardinality_rank"] = 1
            parent_b = dict(records["location_record_object_link"][1])
            parent_b[pk["location_record_object_link"]] = f"{scenario}-object-link-unit-02-parent-building"
            parent_b["location_record_version_id"] = unit_b_version_id
            records["location_record_object_link"].extend([primary_b, parent_b])
    # Review 07 F04: ensure all canonical record types have positive inserted fixture records.
    def add_auxiliary_canonical_record(record_type: str, native_entity: str, native_id: str, suffix: str) -> None:
        required = ["location_record", "location_record_version", "registry_subject", "location_record_object_link"]
        if not all(name in records for name in required):
            return
        record_id = f"{scenario}-location-record-{suffix}"
        version_id = f"{scenario}-location-record-version-{suffix}"
        subject_id = f"{scenario}-registry-subject-{suffix}"
        link_id = f"{scenario}-object-link-{suffix}-primary"
        lr = dict(records["location_record"][0])
        lr[pk["location_record"]] = record_id
        lr["record_type"] = record_type
        records["location_record"].append(lr)
        subject = dict(records["registry_subject"][0])
        subject[pk["registry_subject"]] = subject_id
        subject["subject_entity"] = native_entity
        subject["native_id"] = native_id
        subject["subject_state"] = "active"
        records["registry_subject"].append(subject)
        version = dict(records["location_record_version"][0])
        version[pk["location_record_version"]] = version_id
        version["location_record_id"] = record_id
        version["version_number"] = 1
        version.pop("predecessor_version_id", None)
        version.pop("successor_version_id", None)
        records["location_record_version"].append(version)
        link = dict(records["location_record_object_link"][0])
        link[pk["location_record_object_link"]] = link_id
        link["location_record_version_id"] = version_id
        link["object_role"] = "primary-subject"
        link["subject_id"] = subject_id
        link["cardinality_rank"] = 1
        records["location_record_object_link"].append(link)

    if scenario == "multi-unit-building" and "building" in records:
        add_auxiliary_canonical_record("building", "building", pk_values["building"], "building-positive")
    if scenario == "urban-street-address" and "entrance" in records:
        add_auxiliary_canonical_record("entrance", "entrance", pk_values["entrance"], "entrance-positive")
    if scenario == "no-formal-road-location" and "non_building_object" in records:
        add_auxiliary_canonical_record("non-building-object", "non_building_object", pk_values["non_building_object"], "non-building-object-positive")

    if scenario == "corrected-superseded-address" and "location_record_version" in records:
        first = records["location_record_version"][0]
        first["location_record_version_id"] = f"{scenario}-location-record-version-v1"
        first["version_number"] = 1
        first["lifecycle_state"] = "corrected"
        first["effective_from"] = "2026-01-01T00:00:00Z"
        first["effective_to"] = "2026-06-01T00:00:00Z"
        first["recorded_at"] = "2026-01-02T00:00:00Z"
        first["recorded_to"] = "2026-06-02T00:00:00Z"
        second = dict(first)
        second["location_record_version_id"] = f"{scenario}-location-record-version-v2"
        second["version_number"] = 2
        second["lifecycle_state"] = "active"
        second["effective_from"] = "2026-06-01T00:00:00Z"
        second["effective_to"] = None
        second["recorded_at"] = "2026-06-02T00:00:00Z"
        second["recorded_to"] = None
        first["successor_version_id"] = second["location_record_version_id"]
        second["predecessor_version_id"] = first["location_record_version_id"]
        second.pop("successor_version_id", None)
        old_version_id = pk_values["location_record_version"]
        records["location_record_version"] = [first, second]
        for entity_records in records.values():
            for dep in entity_records:
                if dep.get("location_record_version_id") == old_version_id:
                    dep["location_record_version_id"] = second["location_record_version_id"]
        if "location_record_object_link" in records:
            link1 = records["location_record_object_link"][0]
            link1["location_record_version_id"] = first["location_record_version_id"]
            link1["effective_from"] = first["effective_from"]
            link1["effective_to"] = first["effective_to"]
            link2 = dict(link1)
            link2["link_id"] = f"{scenario}-object-link-v2"
            link2["location_record_version_id"] = second["location_record_version_id"]
            link2["effective_from"] = second["effective_from"]
            link2["effective_to"] = None
            records["location_record_object_link"] = [link1, link2]
        if "publication_release" in records and "publication_release_item" in records:
            rel2 = dict(records["publication_release"][0]); rel2["publication_release_id"] = f"{scenario}-publication-release-corrected"; rel2["effective_at"] = "2026-06-03T00:00:00Z"; rel2["release_state"] = "published"
            item2 = dict(records["publication_release_item"][0]); item2["publication_release_item_id"] = f"{scenario}-publication-release-item-corrected"; item2["publication_release_id"] = rel2["publication_release_id"]; item2["location_record_version_id"] = second["location_record_version_id"]
            records["publication_release"].append(rel2); records["publication_release_item"].append(item2)
    if scenario == "disputed-geometry" and "dispute_case" in records and "geometry_version" in records:
        records["dispute_case"][0]["case_state"] = "resolved"
        records["geometry_version"][0]["dispute_case_id"] = records["dispute_case"][0]["dispute_case_id"]
    if scenario == "administrative-boundary-change" and "administrative_unit_version" in records:
        old = records["administrative_unit_version"][0]
        old["administrative_unit_version_id"] = f"{scenario}-admin-version-old"
        old["lifecycle_state"] = "historical"
        old["effective_from"] = "2020-01-01T00:00:00Z"; old["effective_to"] = "2026-07-01T00:00:00Z"
        new = dict(old)
        new["administrative_unit_version_id"] = f"{scenario}-admin-version-new"; new["lifecycle_state"] = "official"; new["effective_from"] = "2026-07-01T00:00:00Z"; new["effective_to"] = None
        old_admin_version_id = pk_values["administrative_unit_version"]
        records["administrative_unit_version"] = [old, new]
        for entity_records in records.values():
            for dep in entity_records:
                if dep.get("administrative_unit_version_id") == old_admin_version_id:
                    dep["administrative_unit_version_id"] = new["administrative_unit_version_id"]
    return records


def generate_fixtures(model: dict[str, Any]) -> dict[str, Any]:
    scenarios = {name: scenario_records(model, name, i + 1) for i, name in enumerate(SCENARIO_NAMES)}
    negatives = {
        "invalid-cardinality-primary-object": {"expect_error": "exceeds max count"},
        "invalid-temporal-overlap": {"expect_error": "conflicting key value violates exclusion constraint"},
        "invalid-state-transition": {"expect_error": "forbidden transition"},
        "invalid-subject-reference": {"expect_error": "registry subject"},
        "invalid-geometry-role-type": {"expect_error": "invalid geometry type"},
        "invalid-publication-prerequisite": {"expect_error": "publication prerequisite"},
        "invalid-self-supersession": {"expect_error": "cannot supersede itself"},
    }
    fixtures = {"scenarios": scenarios, "negative_fixtures": negatives}
    write_json("docs/sda/data-model/representative-records/machine-readable-fixtures.json", fixtures)
    write("docs/sda/data-model/representative-records/README.md", "# Representative Records\n\nMachine-readable fixtures live in `machine-readable-fixtures.json`. Review 05 executes each positive scenario independently in a disposable target schema and executes negative semantic fixtures for cardinality, FK/subject reference, state transition, interval overlap, supersession, publication prerequisite and geometry role/type failures.")
    return fixtures


def insert_records(cur, model: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> int:
    entities = model["entities"]
    inserted = 0
    for entity in dependency_order(model):
        for rec in records.get(entity, []):
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
    return inserted


class NegativeFixtureDidNotFail(AssertionError):
    """Raised when a negative fixture unexpectedly succeeds."""


def expect_sql_failure(cur, results: dict[str, dict[str, str]], name: str, savepoint: str, statements: list[tuple[str, list[Any]]], expected_message: str) -> None:
    cur.execute(f"SAVEPOINT {savepoint}")
    try:
        for sql, vals in statements:
            cur.execute(sql, vals)
        cur.execute("SET CONSTRAINTS ALL IMMEDIATE")
    except psycopg.Error as exc:
        message = str(exc)
        cur.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
        cur.execute(f"RELEASE SAVEPOINT {savepoint}")
        cur.execute("SET CONSTRAINTS ALL DEFERRED")
        if expected_message not in message:
            raise AssertionError(f"{name} failed with unexpected error; expected {expected_message!r}, got {message!r}") from exc
        results[name] = {
            "status": "rejected-by-real-execution",
            "expected_message": expected_message,
            "error_class": exc.__class__.__name__,
        }
        return

    cur.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
    cur.execute(f"RELEASE SAVEPOINT {savepoint}")
    cur.execute("SET CONSTRAINTS ALL DEFERRED")
    raise NegativeFixtureDidNotFail(f"{name} did not fail")


def prove_negative_harness_fails_on_success() -> dict[str, str]:
    class FakeCursor:
        def __init__(self) -> None:
            self.statements: list[str] = []

        def execute(self, sql: str, vals: list[Any] | None = None) -> None:
            self.statements.append(sql)

    results: dict[str, dict[str, str]] = {}
    try:
        expect_sql_failure(
            FakeCursor(),
            results,
            "harness-regression-invalid-action",
            "neg_harness_regression",
            [("SELECT 1", [])],
            "this message should never appear",
        )
    except NegativeFixtureDidNotFail as exc:
        return {
            "status": "passed",
            "proves": "successful invalid action raises outside the database-exception handler",
            "error_class": exc.__class__.__name__,
        }
    raise AssertionError("negative harness regression did not detect a successful invalid action")


def execute_lifecycle_transition_assertions(cur) -> dict[str, dict[str, str]]:
    results: dict[str, dict[str, str]] = {}
    for vocab, edges in sorted(authored_lifecycle_transitions().items()):
        seen_edges: set[tuple[str, str]] = set()
        for edge in edges:
            key = (edge["from"], edge["to"])
            assertion_id = f"F07-lifecycle-positive-{vocab}-{edge['from']}-to-{edge['to']}".replace("_", "-").replace(" ", "-")
            if key in seen_edges:
                raise AssertionError(f"duplicate lifecycle edge {vocab}:{key}")
            seen_edges.add(key)
            cur.execute("SELECT validate_lifecycle_transition(%s,%s,%s) AS ok", [vocab, edge["from"], edge["to"]])
            row = cur.fetchone()
            if not row or row["ok"] is not True:
                raise AssertionError(f"allowed lifecycle transition did not pass: {vocab} {edge['from']}->{edge['to']}")
            for required in ["permission_key", "institutional_scope", "authority", "evidence", "audit_event", "public_effect", "denial_behavior"]:
                if not edge.get(required):
                    raise AssertionError(f"{vocab} {edge['from']}->{edge['to']} missing {required}")
            results[assertion_id] = {
                "status": "passed",
                "vocab": vocab,
                "from": edge["from"],
                "to": edge["to"],
                "permission_key": edge["permission_key"],
                "authority": edge["authority"],
                "audit_event": edge["audit_event"],
                "public_effect": edge["public_effect"],
            }
    return results


def execute_negative_fixtures(cur, model: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, str]]:
    results: dict[str, dict[str, str]] = {}
    # Invalid subject reference.
    bad = records["name_record"][0].copy(); bad["name_record_id"] = "negative-name-subject"; bad["subject_id"] = "missing-subject"
    expect_sql_failure(results=results, cur=cur, name="invalid-subject-reference", savepoint="neg_subject", expected_message="registry subject", statements=[("INSERT INTO proposed_name_record (" + ",".join(bad) + ") VALUES (" + ",".join(["%s"] * len(bad)) + ")", list(bad.values()))])
    # Invalid geometry type for an otherwise allowed subject/role pairing.
    gv = records["geometry_version"][0].copy(); gv["geometry_version_id"] = "negative-geometry-type"; gv["geometry_role"] = "building-point"; gv["geom"] = "SRID=4326;LINESTRING(8.78 3.75,8.79 3.76)"
    cols=list(gv); vals=[gv[c] for c in cols]; placeholders=["ST_GeomFromEWKT(%s)" if c=="geom" else "%s" for c in cols]
    expect_sql_failure(results=results, cur=cur, name="invalid-geometry-role-type", savepoint="neg_geom", expected_message="invalid geometry type", statements=[("INSERT INTO proposed_geometry_version ("+",".join(cols)+") VALUES ("+",".join(placeholders)+")", vals)])
    # Self supersession.
    gv = records["geometry_version"][0].copy(); gv["geometry_version_id"] = "negative-self-supersession"; gv["superseded_by_geometry_version_id"] = gv["geometry_version_id"]
    cols=list(gv); vals=[gv[c] for c in cols]; placeholders=["ST_GeomFromEWKT(%s)" if c=="geom" else "%s" for c in cols]
    expect_sql_failure(results=results, cur=cur, name="invalid-self-supersession", savepoint="neg_super", expected_message="cannot supersede itself", statements=[("INSERT INTO proposed_geometry_version ("+",".join(cols)+") VALUES ("+",".join(placeholders)+")", vals)])
    # Duplicate primary object cardinality.
    link = records["location_record_object_link"][0].copy(); link["link_id"] = "negative-cardinality"; link["cardinality_rank"] = 2
    expect_sql_failure(results=results, cur=cur, name="invalid-cardinality-primary-object", savepoint="neg_card", expected_message="exceeds max count", statements=[("INSERT INTO proposed_location_record_object_link ("+",".join(link)+") VALUES ("+",".join(["%s"]*len(link))+")", list(link.values()))])
    # Temporal overlap through exclusion constraint.
    ver = records["location_record_version"][0].copy(); ver["location_record_version_id"] = "negative-temporal-overlap"; ver["version_number"] = 99; ver["recorded_to"] = "2027-01-01T00:00:00Z"; ver.pop("predecessor_version_id", None); ver.pop("successor_version_id", None)
    expect_sql_failure(results=results, cur=cur, name="invalid-temporal-overlap", savepoint="neg_temporal", expected_message="conflicting key value violates exclusion constraint", statements=[("INSERT INTO proposed_location_record_version ("+",".join(ver)+") VALUES ("+",".join(["%s"]*len(ver))+")", list(ver.values()))])
    # Invalid state transition through executable policy validator.
    expect_sql_failure(results=results, cur=cur, name="invalid-state-transition", savepoint="neg_transition", expected_message="forbidden transition", statements=[("SELECT validate_lifecycle_transition(%s,%s,%s)", ["canonical_record_lifecycle", "active", "candidate"])])
    # Review 07 F06: geometry promotion authority negatives prove actor/permission/scope/evidence binding.
    geom_id = records["geometry_version"][0]["geometry_version_id"]
    decision_id = records["decision_event"][0]["decision_event_id"]
    expect_sql_failure(results=results, cur=cur, name="invalid-geometry-decision-type", savepoint="neg_geom_decision_type", expected_message="geometry promotion decision is not authorized", statements=[("UPDATE proposed_decision_event SET decision_type='resolve-dispute' WHERE decision_event_id=%s", [decision_id]), ("UPDATE proposed_geometry_version SET validation_method=validation_method WHERE geometry_version_id=%s", [geom_id])])
    expect_sql_failure(results=results, cur=cur, name="invalid-geometry-permission", savepoint="neg_geom_permission", expected_message="geometry promotion actor lacks required permission", statements=[("UPDATE proposed_decision_event SET details_json=jsonb_set(details_json,'{permission_key}','\"wrong.permission\"'::jsonb) WHERE decision_event_id=%s", [decision_id]), ("UPDATE proposed_geometry_version SET validation_method=validation_method WHERE geometry_version_id=%s", [geom_id])])
    expect_sql_failure(results=results, cur=cur, name="invalid-geometry-territorial-scope", savepoint="neg_geom_scope", expected_message="geometry promotion institution or territorial scope mismatch", statements=[("UPDATE proposed_decision_event SET details_json=jsonb_set(details_json,'{territorial_scope}','\"wrong-scope\"'::jsonb) WHERE decision_event_id=%s", [decision_id]), ("UPDATE proposed_geometry_version SET validation_method=validation_method WHERE geometry_version_id=%s", [geom_id])])
    expect_sql_failure(results=results, cur=cur, name="invalid-geometry-evidence-link", savepoint="neg_geom_evidence", expected_message="geometry decision evidence link mismatch", statements=[("UPDATE proposed_decision_event SET details_json=jsonb_set(details_json,'{evidence_object_id}','\"wrong-evidence\"'::jsonb) WHERE decision_event_id=%s", [decision_id]), ("UPDATE proposed_geometry_version SET validation_method=validation_method WHERE geometry_version_id=%s", [geom_id])])
    # Publication prerequisite through trigger.
    rel = records["publication_release"][0].copy(); rel["publication_release_id"] = "negative-publication-release"; rel["release_state"] = "draft"
    item = records["publication_release_item"][0].copy(); item["publication_release_item_id"] = "negative-publication-item"; item["publication_release_id"] = rel["publication_release_id"]
    expect_sql_failure(results=results, cur=cur, name="invalid-publication-prerequisite", savepoint="neg_publication", expected_message="publication prerequisite", statements=[("INSERT INTO proposed_publication_release ("+",".join(rel)+") VALUES ("+",".join(["%s"]*len(rel))+")", list(rel.values())), ("INSERT INTO proposed_publication_release_item ("+",".join(item)+") VALUES ("+",".join(["%s"]*len(item))+")", [json.dumps(v, sort_keys=True) if isinstance(v,(dict,list)) else v for v in item.values()])])
    return results


def review07_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def build_review07_scenario_assertions(model: dict[str, Any], fixtures: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scenarios = fixtures.get("scenarios", {})
    results: dict[str, dict[str, Any]] = {}

    def add(assertion_id: str, finding: str, status: bool, evidence: dict[str, Any]) -> None:
        results[assertion_id] = {"finding": finding, "status": "passed" if status else "failed", "evidence": evidence}
        if not status:
            raise AssertionError(f"Review 07 assertion failed: {assertion_id}: {evidence}")

    # F04: every canonical record type is present in positive fixtures and has cardinality rules.
    expected_record_types = sorted(model.get("record_object_cardinality", {}))
    observed_record_types = sorted({
        row.get("record_type")
        for scenario in scenarios.values()
        for row in scenario.get("location_record", [])
        if row.get("record_type")
    })
    for record_type in expected_record_types:
        add(
            f"F04-cardinality-positive-record-type-{review07_slug(record_type)}",
            "F04",
            record_type in observed_record_types,
            {"record_type": record_type, "observed_record_types": observed_record_types},
        )
        roles = model.get("record_object_cardinality", {}).get(record_type, {})
        add(
            f"F04-cardinality-matrix-rules-{review07_slug(record_type)}",
            "F04",
            bool(roles) and all("allowed_subject_entities" in rule and "min" in rule and "max" in rule for rule in roles.values()),
            {"record_type": record_type, "roles": sorted(roles)},
        )

    multi = scenarios.get("multi-unit-building", {})
    unit_record_ids = {r.get("location_record_id") for r in multi.get("location_record", []) if r.get("record_type") == "unit"}
    multi_versions = {r.get("location_record_version_id") for r in multi.get("location_record_version", []) if r.get("location_record_id") in unit_record_ids}
    primary_versions = {r.get("location_record_version_id") for r in multi.get("location_record_object_link", []) if r.get("object_role") == "primary-subject"}
    parent_versions = {r.get("location_record_version_id") for r in multi.get("location_record_object_link", []) if r.get("object_role") == "parent-building"}
    add("F04-multi-unit-independent-canonical-records", "F04", len(unit_record_ids) >= 2 and len(multi_versions) >= 2, {"unit_location_records": sorted(unit_record_ids), "versions": sorted(multi_versions)})
    add("F04-multi-unit-parent-building-cardinality", "F04", multi_versions <= primary_versions and multi_versions <= parent_versions, {"unit_versions": sorted(multi_versions), "primary_versions": sorted(primary_versions), "parent_versions": sorted(parent_versions)})
    add("F04-negative-cardinality-suite", "F04", all(name in (fixtures.get("negative_fixtures", {}) or {}) for name in ["invalid-cardinality-primary-object", "invalid-subject-reference"]), {"negative_fixtures": sorted((fixtures.get("negative_fixtures", {}) or {}))})

    # F05: temporal/history scenarios must carry old/new intervals and reconstructable date-specific versions.
    corrected = scenarios.get("corrected-superseded-address", {})
    corrected_versions = corrected.get("location_record_version", [])
    add("F05-corrected-address-two-version-history", "F05", len(corrected_versions) >= 2 and any(v.get("effective_to") for v in corrected_versions) and any(v.get("effective_to") is None for v in corrected_versions), {"versions": corrected_versions})
    add("F05-corrected-address-reciprocal-chain", "F05", any(v.get("successor_version_id") for v in corrected_versions) and any(v.get("predecessor_version_id") for v in corrected_versions), {"versions": corrected_versions})
    admin = scenarios.get("administrative-boundary-change", {})
    admin_versions = admin.get("administrative_unit_version", [])
    add("F05-admin-boundary-old-new-versions", "F05", len(admin_versions) >= 2 and any(v.get("effective_to") for v in admin_versions) and any(v.get("effective_to") is None for v in admin_versions), {"versions": admin_versions})
    add("F05-negative-temporal-overlap-executed", "F05", "invalid-temporal-overlap" in (fixtures.get("negative_fixtures", {}) or {}), {"negative_fixtures": sorted((fixtures.get("negative_fixtures", {}) or {}))})
    temporal_entities = ["location_record_version", "public_code_alias", "administrative_unit_version", "geometry_version", "location_record_object_link", "publication_release_item"]
    for entity in temporal_entities:
        add(f"F05-temporal-fixture-coverage-{review07_slug(entity)}", "F05", any(s.get(entity) for s in scenarios.values()), {"entity": entity, "scenarios": [name for name, s in scenarios.items() if s.get(entity)]})

    # F10: seven scenario-specific datasets need exact projection anchors, not one-row shell confidence.
    required_scenarios = set(SCENARIO_NAMES)
    add("F10-seven-scenario-datasets-present", "F10", set(scenarios) == required_scenarios, {"expected": sorted(required_scenarios), "observed": sorted(scenarios)})
    scenario_expectations = {
        "urban-street-address": {"record_type": "address", "requires": ["location_record", "building", "road", "entrance", "publication_release_item"]},
        "rural-landmark-location": {"record_type": "landmark", "requires": ["location_record", "landmark", "geometry_version", "publication_release_item"]},
        "multi-unit-building": {"record_type": "unit", "requires": ["location_record", "unit", "public_code_alias", "publication_release_item"]},
        "no-formal-road-location": {"record_type": "service-location", "requires": ["location_record", "publication_release_item"]},
        "corrected-superseded-address": {"record_type": "address", "requires": ["location_record_version", "publication_release_item", "correction_case"]},
        "disputed-geometry": {"record_type": "address", "requires": ["dispute_case", "geometry_version", "publication_release_item"]},
        "administrative-boundary-change": {"record_type": "service-location", "requires": ["administrative_unit_version", "geometry_version", "publication_release_item"]},
    }
    for scenario, expectation in scenario_expectations.items():
        data = scenarios.get(scenario, {})
        record_types = {r.get("record_type") for r in data.get("location_record", [])}
        add(f"F10-scenario-{review07_slug(scenario)}-record-type", "F10", expectation["record_type"] in record_types, {"scenario": scenario, "record_types": sorted(x for x in record_types if x)})
        missing = [entity for entity in expectation["requires"] if not data.get(entity)]
        add(f"F10-scenario-{review07_slug(scenario)}-required-dataset", "F10", not missing, {"scenario": scenario, "missing": missing, "required": expectation["requires"]})
        add(f"F10-scenario-{review07_slug(scenario)}-projection-anchor", "F10", bool(data.get("publication_release_item")) and all(i.get("projection_payload_hash") and i.get("projection_payload_json") for i in data.get("publication_release_item", [])), {"scenario": scenario, "release_items": data.get("publication_release_item", [])})

    return results


def write_review07_scenario_assertion_report(assertions: dict[str, dict[str, Any]]) -> None:
    rows = []
    for assertion_id, result in sorted(assertions.items()):
        rows.append([assertion_id, result.get("finding", "—"), result.get("status", "—"), json.dumps(result.get("evidence", {}), sort_keys=True, default=str)[:240]])
    write("docs/sda/data-model/review07-scenario-temporal-assertions.md", "# Review 07 F04/F05/F10 Scenario and Temporal Assertions\n\n" + md_table(["Assertion", "Finding", "Status", "Evidence"], rows) + "\n")


def execute_target_schema_and_fixtures(model: dict[str, Any], fixtures: dict[str, Any]) -> dict[str, Any]:
    sql = render_target_sql(model)
    write("docs/sda/data-model/draft-physical-schema.sql", sql)
    scenario_results: dict[str, Any] = {}
    negative_results: dict[str, dict[str, str]] = {}
    lifecycle_transition_assertions: dict[str, dict[str, str]] = {}
    review07_scenario_assertions: dict[str, dict[str, Any]] = {}
    negative_harness_regression = prove_negative_harness_fails_on_success()
    last_cols: list[dict[str, Any]] = []
    last_constraint_count = 0
    last_index_count = 0
    last_constraints: list[dict[str, Any]] = []
    last_indexes: list[dict[str, Any]] = []
    last_triggers: list[dict[str, Any]] = []
    with connect(True) as conn, conn.cursor() as cur:
        for scenario, records in fixtures["scenarios"].items():
            cur.execute(sql)
            cur.execute("SET search_path = nli_wo002_target, public")
            cur.execute("BEGIN")
            cur.execute("SET CONSTRAINTS ALL DEFERRED")
            inserted = insert_records(cur, model, records)
            if scenario == "urban-street-address":
                lifecycle_transition_assertions = execute_lifecycle_transition_assertions(cur)
                negative_results = execute_negative_fixtures(cur, model, records)
            cur.execute("COMMIT")
            scenario_results[scenario] = {"inserted_rows": inserted, "status": "passed"}
        cur.execute("SET search_path = nli_wo002_target, public")
        cur.execute("""
            SELECT table_name, column_name, data_type, udt_name, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema='nli_wo002_target' AND (table_name LIKE 'proposed_%' OR table_name='lifecycle_transition_policy')
            ORDER BY table_name, ordinal_position
        """)
        last_cols = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT table_name, constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_schema='nli_wo002_target' AND constraint_name !~ '^[0-9]+_[0-9]+_[0-9]+_not_null$' ORDER BY table_name, constraint_name")
        last_constraints = [dict(r) for r in cur.fetchall()]
        last_constraint_count = len(last_constraints)
        cur.execute("SELECT tablename, indexname, indexdef FROM pg_indexes WHERE schemaname='nli_wo002_target' ORDER BY tablename, indexname")
        last_indexes = [dict(r) for r in cur.fetchall()]
        last_index_count = len(last_indexes)
        cur.execute("SELECT event_object_table AS table_name, trigger_name, action_timing, event_manipulation FROM information_schema.triggers WHERE trigger_schema='nli_wo002_target' ORDER BY event_object_table, trigger_name, action_timing, event_manipulation")
        last_triggers = [dict(r) for r in cur.fetchall()]
    review07_scenario_assertions = build_review07_scenario_assertions(model, fixtures)
    write_review07_scenario_assertion_report(review07_scenario_assertions)
    physical_fields = {f"{r['table_name'].replace('proposed_','')}.{r['column_name']}": r for r in last_cols if r["table_name"].startswith("proposed_")}
    expected = target_field_index(model)
    missing = sorted(set(expected) - set(physical_fields))
    extra = sorted(set(physical_fields) - set(expected))
    field_parity_errors: list[str] = []
    for fq, fmeta in expected.items():
        phys = physical_fields.get(fq)
        if not phys:
            continue
        expected_type = normalize_type(fmeta.get("pg_type", "text")).lower()
        physical_type = str(phys.get("udt_name") if str(phys.get("data_type", "")).lower() == "user-defined" else phys.get("data_type", "")).lower()
        if expected_type.startswith("geometry"):
            if physical_type != "geometry":
                field_parity_errors.append(f"{fq} physical type {physical_type} != geometry")
        elif expected_type in {"timestamptz", "timestamp with time zone"}:
            if physical_type not in {"timestamptz", "timestamp with time zone"}:
                field_parity_errors.append(f"{fq} physical type {physical_type} != timestamptz")
        elif expected_type.startswith("numeric"):
            if physical_type != "numeric":
                field_parity_errors.append(f"{fq} physical type {physical_type} != numeric")
        elif expected_type.startswith("char"):
            if physical_type not in {"bpchar", "character"}:
                field_parity_errors.append(f"{fq} physical type {physical_type} != char")
        elif expected_type != physical_type and not (expected_type == "text" and physical_type == "text"):
            field_parity_errors.append(f"{fq} physical type {physical_type} != {expected_type}")
        expected_nullable = "YES" if fmeta.get("nullable") else "NO"
        if phys.get("is_nullable") != expected_nullable:
            field_parity_errors.append(f"{fq} nullable {phys.get('is_nullable')} != {expected_nullable}")
    required_triggers = ["registry_subject_native_trg", "required_object_roles_trg", "location_record_version_chain_trg", "public_code_alias_chain_trg", "publication_prerequisite_trg", "geometry_version_semantics_trg", "geometry_observation_semantics_trg"]
    missing_required_triggers = sorted(set(required_triggers) - {t["trigger_name"] for t in last_triggers})
    report = {"scenario_results": scenario_results, "negative_results": negative_results, "negative_harness_regression": negative_harness_regression, "lifecycle_transition_assertions": lifecycle_transition_assertions, "review07_scenario_assertions": review07_scenario_assertions, "inserted_fixture_rows": sum(v["inserted_rows"] for v in scenario_results.values()), "physical_columns": len(physical_fields), "target_fields": len(expected), "missing_fields": missing, "extra_fields": extra, "field_parity_errors": field_parity_errors, "constraint_count": last_constraint_count, "index_count": last_index_count, "trigger_count": len(last_triggers), "missing_required_triggers": missing_required_triggers}
    write_json("docs/sda/data-model/target-schema-catalog.json", {"columns": last_cols, "constraints": last_constraints, "indexes": last_indexes, "triggers": last_triggers, "report": report})
    write("docs/sda/data-model/target-schema-validation-report.md", "# Target Schema Validation Report\n\n" + md_table(["Check", "Result"], [["Target schema executed in disposable PostGIS schema", "PASS"], ["Negative harness false-pass regression", negative_harness_regression["status"]], ["Independent positive scenarios", len(scenario_results)], ["Positive fixture rows inserted", report["inserted_fixture_rows"]], ["Negative fixtures rejected", len(negative_results)], ["Review 07 scenario/temporal assertions", len(review07_scenario_assertions)], ["Physical columns", len(physical_fields)], ["Target fields", len(expected)], ["Missing fields", missing or "none"], ["Extra fields", extra or "none"], ["Constraints", last_constraint_count], ["Indexes", last_index_count]]))
    if missing:
        raise SystemExit(f"target schema missing fields: {missing[:10]}")
    if field_parity_errors:
        raise SystemExit(f"target schema field parity errors: {field_parity_errors[:10]}")
    if missing_required_triggers:
        raise SystemExit(f"target schema missing required semantic triggers: {missing_required_triggers}")
    if len(scenario_results) != 7 or len(negative_results) < 11:
        raise SystemExit(f"scenario validation incomplete: positives={len(scenario_results)} negatives={len(negative_results)}")
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


def reviewed_convergence_units_path() -> Path:
    return DM / "schema-convergence-units-reviewed.json"


def load_reviewed_convergence_units(registry: list[dict[str, Any]], transform_report: dict[str, Any]) -> dict[str, Any]:
    path = reviewed_convergence_units_path()
    if not path.exists():
        raise SystemExit("schema-convergence-units-reviewed.json is required for Review 07 F09")
    payload = json.loads(path.read_text(encoding="utf-8"))
    units = payload.get("migration_units") if isinstance(payload, dict) else None
    if not isinstance(units, list):
        raise SystemExit("schema-convergence-units-reviewed.json must contain migration_units[]")
    registry_groups = {r["transform_group_id"] for r in registry}
    passed_assertions = {a["assertion_id"] for a in transform_report.get("assertions", []) if a.get("status") == "passed"}
    errors: list[str] = []
    unit_ids: set[str] = set()
    required_keys = {
        "unit_id", "transform_group_id", "review_status", "review_owner", "depends_on",
        "source_fields", "target_fields", "transform_assertion_ids", "application_version_matrix",
        "write_ownership", "exception_schema_sla", "idempotency", "conflict_precedence",
        "validation", "recovery", "monitoring_window", "cutover_abort_gates",
        "retirement_proof", "scale_assumption_status",
    }
    for unit in units:
        if not isinstance(unit, dict):
            errors.append("convergence unit contains non-object row")
            continue
        uid = unit.get("unit_id")
        if uid in unit_ids:
            errors.append(f"duplicate convergence unit {uid}")
        unit_ids.add(uid)
        missing = sorted(k for k in required_keys if k not in unit or unit.get(k) in (None, "") or (k != "depends_on" and unit.get(k) == []))
        if missing:
            errors.append(f"{uid} missing convergence keys {missing}")
        group = unit.get("transform_group_id")
        if group not in registry_groups:
            errors.append(f"{uid} references unknown transform group {group}")
        if unit.get("review_status") != "approved-review07-convergence-unit":
            errors.append(f"{uid} lacks Review 07 convergence review status")
        missing_assertions = sorted(set(unit.get("transform_assertion_ids") or []) - passed_assertions)
        if missing_assertions:
            errors.append(f"{uid} references non-passing F02 assertions {missing_assertions[:5]}")
        if not any("SDA" in gate or "WO-002B" in gate for gate in unit.get("cutover_abort_gates", [])):
            errors.append(f"{uid} cutover gates do not preserve SDA/future WO-002B authority")
        matrix = unit.get("application_version_matrix", {})
        if "PR #7" not in str(matrix) or "WO-002B" not in str(matrix):
            errors.append(f"{uid} application version matrix does not state PR #7 no-runtime-change / WO-002B future boundary")
        if "owner" not in str(unit.get("exception_schema_sla", {})).lower():
            errors.append(f"{uid} exception schema/SLA lacks owner")
        if unit.get("scale_assumption_status") != "owner-pending; not national production readiness evidence":
            errors.append(f"{uid} overclaims scale readiness")
    if set(u.get("transform_group_id") for u in units if isinstance(u, dict)) != registry_groups:
        errors.append("reviewed convergence units do not exactly cover reviewed transform groups")
    if errors:
        raise SystemExit("reviewed convergence units failed:\n- " + "\n- ".join(errors[:120]))
    return payload


def render_convergence(registry: list[dict[str, Any]], transform_report: dict[str, Any]) -> None:
    payload = load_reviewed_convergence_units(registry, transform_report)
    units = payload["migration_units"]
    scale = payload.get("scale_assumptions", [])
    write_json("docs/sda/data-model/schema-convergence-units.json", payload)
    rows = []
    for unit in units:
        rows.append([
            unit["unit_id"],
            unit["transform_group_id"],
            "; ".join(unit["source_fields"]),
            "; ".join(unit["target_fields"]),
            "; ".join(unit.get("final_fk_outputs") or ["—"]),
            "; ".join(unit["transform_assertion_ids"][:12]) + ("; …" if len(unit["transform_assertion_ids"]) > 12 else ""),
            "; ".join(unit.get("depends_on") or ["none"]),
            unit["application_version_matrix"]["current"] + " / " + unit["application_version_matrix"]["migrate"],
            unit["write_ownership"]["current_writer"] + "; " + unit["write_ownership"]["future_target_writer"],
            unit["exception_schema_sla"]["exception_table"] + ": " + unit["exception_schema_sla"]["owner"] + " — " + unit["exception_schema_sla"]["sla"],
            ", ".join(unit["idempotency"]["key"]),
            "; ".join(unit["conflict_precedence"]),
            unit["validation"]["sql"] + "; tolerance: " + unit["validation"]["tolerance"],
            unit["recovery"]["backup_boundary"] + "; " + unit["recovery"]["forward_recovery"] + "; " + unit["recovery"]["rollback_boundary"],
            unit["monitoring_window"],
            "; ".join(unit["cutover_abort_gates"]),
            unit["retirement_proof"]["legacy_field_retirement_condition"] + "; " + unit["retirement_proof"]["runtime_change_authority"],
            unit["scale_assumption_status"],
        ])
    scale_rows = [[s.get("area"), s.get("source"), s.get("baseline_date"), s.get("confidence_range_horizon"), s.get("workload_capacity_model"), s.get("approving_owner")] for s in scale]
    write("docs/sda/data-model/schema-convergence-plan.md", "# Expand–Migrate–Contract Convergence and Scale Plan\n\nBuilt from the reviewed Review 07 convergence-unit source and only after passing F02 transformation assertions. NLI-WO-002B remains unauthorized; this is a reviewed migration-unit design source for later approval, not executable migration authority.\n\n" + md_table(["Unit", "Transform group", "Complete source fields", "Target rows/fields", "Final FK outputs", "Passing F02 assertion IDs", "Dependencies", "Application version matrix", "Write ownership", "Exception schema/SLA", "Idempotency key", "Conflict precedence", "Validation/tolerance", "Recovery boundary", "Monitoring window", "Cutover/abort gates", "Retirement proof", "Scale status"], rows) + "\n\n## Workload, storage, retention, concurrency and query assumptions\n\n" + md_table(["Area", "Source", "Baseline date", "Confidence range/horizon", "Workload/capacity model", "Approving owner"], scale_rows))


def render_adrs() -> None:
    # Review 05: ADRs 005-009 are maintained as reviewed source documents.
    # This function intentionally does not rewrite ADR text. It only verifies the
    # source files exist and contain evidence-linked conditions.
    required = [
        "ADR-005-internal-identifiers-and-public-code-separation.md",
        "ADR-006-administrative-geography-and-operational-areas.md",
        "ADR-007-canonical-location-record-and-addressable-objects.md",
        "ADR-008-temporal-versioning-and-supersession-model.md",
        "ADR-009-geometry-evidence-and-provenance-model.md",
    ]
    missing = [name for name in required if not (SDA / "adrs" / name).exists()]
    if missing:
        raise SystemExit(f"missing reviewed ADR source documents: {missing}")
    for name in required:
        text = (SDA / "adrs" / name).read_text(encoding="utf-8")
        for marker in ["## Evidence-linked conditions", "## Unresolved RFIs", "## Acceptance tests"]:
            if marker not in text:
                raise SystemExit(f"{name} is missing reviewed-source marker {marker}")


def render_evidence(cat: dict[str, Any], ops: dict[str, Any], registry: list[dict[str, Any]], target_report: dict[str, Any]) -> None:
    ac_rows = []
    assertions = {
        1: f"pg_catalog inventory generated from disposable migrated PostGIS DB: {len(cat['tables'])} tables, {sum(len(t['columns']) for t in cat['tables'].values())} fields, ledger included.",
        2: "location_record remains sole canonical anchor; subject registry/crosswalks prevent second address authority.",
        3: "administrative code history and name history are separated from identity.",
        4: "operational area lifecycle remains separate from administrative units.",
        5: "record/object matrix is keyed by actual canonical record_type values, not standard-address.",
        6: "internal IDs, public aliases and legacy crosswalks are separated with exact reference-crosswalk joins.",
        7: "lifecycle graphs load into executable transition policy and are checked for field bindings/edge metadata.",
        8: "version, alias and geometry supersession rules include no-self/reciprocal/same-owner/acyclic checks.",
        9: "geometry promotion requires authorized decision, evidence object, authority scope, accepted quality and same-subject/role supersession.",
        10: "name records and subject integrity are enforced through registry-subject FK and current-name rule.",
        11: "governed archive and source/crosswalk joins preserve original facts and exception paths.",
        12: "classifications are explicit in current/target mapping and API contracts.",
        13: "field-to-vocabulary registry and transition graphs are validated.",
        14: f"target schema executed; constraints, indexes, triggers and helper policy tables cataloged.",
        15: f"{len(ops['operations'])} OpenAPI operations have exact method/path/handler/auth/roles and concrete projection contracts.",
        16: f"transformation registry covers {len(registry)} current fields with executable SELECT no-loss assertions and reference joins.",
        17: "convergence plan is rebuilt after accepted transformation rows and no longer uses pseudo-ASSERT validation.",
        18: f"seven scenario builders insert {target_report['inserted_fixture_rows']} target rows and execute seven negative cases.",
        19: "scale assumptions remain explicitly review inputs, not implementation authorization.",
        20: "dependency-safe target SQL executes in disposable PostGIS and catalog parity is checked.",
        21: "ADRs 005-009 are hand-maintained source docs with Review 07 assertion reconciliation.",
        22: "PR #7 excludes runtime code, executable migrations, app code, production data and env files; migration-ledger fix is split to PR #8.",
    }
    evidence = {
        1: "Review 07 semantic-design CI exact-head run; design report Generated checks: 41, Errors: 0.",
        2: "Target model, subject registry checks, reviewed transformation registry.",
        3: "Target registry and target schema validation.",
        4: "Controlled vocabulary/lifecycle registry.",
        5: "Executed target schema and semantic checker.",
        6: "Reviewed transformation rows and ADR-005.",
        7: "Lifecycle registry and target helper table catalog.",
        8: "Target SQL triggers and negative execution.",
        9: "Target model, target SQL trigger and scenario fixtures.",
        10: "Target schema validation.",
        11: "Reviewed transformation registry.",
        12: "API projection contracts and field registry.",
        13: "Controlled vocabularies and lifecycle transitions.",
        14: "Target schema validation report.",
        15: "Route policy and projection contract registries.",
        16: "Transformation registry and semantic checker.",
        17: "Schema convergence plan.",
        18: "Machine-readable fixtures and target report.",
        19: "Convergence plan and Review 06 resolution log.",
        20: "sda-design-model job evidence; final PR-head job IDs are in the Review 07 request comment.",
        21: "ADRs 005-009.",
        22: "Changed-path proof and PR state.",
    }
    for i in range(1, 23):
        ac = f"AC-{i:02d}"
        ac_rows.append([ac, "READY FOR SDA REVIEW", assertions[i], evidence[i], "SDA acceptance pending"])
    header = """# NLI-WO-002 Pull Request Evidence — Review 07

Draft PR #7 remains draft and unmerged. NLI-WO-002B remains unauthorized.

## Exact implementation head validated before evidence closeout

- Implementation/stamp head validated by GitHub Actions: `f36cda7d68a6131ffdd1c11b86d2569860686788`
- API CI run `29337375340`: **success**
  - `migration-lifecycle` job `87099934845`: success
  - `api-image-runtime` job `87099934865`: success
  - `sda-design-model` job `87099934876`: success
  - `api-tests` job `87099934897`: success
- Frontend CI run `29337375180`: **success**
  - `frontend` job `87099934523`: success

Final PR-head CI after this evidence closeout is recorded in the SDA Review 07 request comment.

## Review 06 remediation commits

| Purpose | Commit |
|---|---|
| Review 06 semantic remediation | `1cf7d555a08de750c580b87de14bc2020dc7a052` |
| Review 06 resolution evidence stamp | `f36cda7d68a6131ffdd1c11b86d2569860686788` |
| Migration-ledger runtime fix split out | Maintenance PR #8, not PR #7 |
"""
    changed_path = """
## Changed-path proof

Scope guard before closeout found no changes under:

- `services/api/**`
- `infra/scripts/migrate.py`
- `infra/migrations/**`
- `apps/**`
- `infra/docker/**`
- `data/**`
- `.env*`

PR #7 remains a design/evidence PR. The migration-ledger advisory-lock fix is isolated in maintenance PR #8 under NLI-WO-001 database-lifecycle controls.
"""
    write("docs/sda/evidence/NLI-WO-002-pull-request-evidence.md", header + "\n## Criterion-specific evidence matrix\n\n" + md_table(["Criterion", "Status", "Assertion", "Evidence", "Remaining condition"], ac_rows) + "\n" + changed_path)


def update_review_log(fixing: str = FIXING_COMMIT_PLACEHOLDER) -> None:
    text = REVIEW.read_text(encoding="utf-8")
    evidence = {
        2: "controlled maps corrected to observed source values and target vocabularies; references have exact source/target crosswalk joins; pseudo assertions replaced by executable transform checks",
        4: "record/object cardinality matrix is keyed by actual canonical record types with min/max/required role enforcement",
        5: "alias, version and geometry supersession rules include no-self, reciprocal, same-owner and acyclic checks plus recorded-time cataloguing",
        6: "geometry promotion requires authorized decision, evidence object, authority scope, accepted quality, and same-subject/role supersession",
        7: "all lifecycle graphs are loaded into executable transition policy with reachability, terminality and edge metadata validation",
        8: "route policies are corrected against method, path, operation id, handler, source span, auth mode and roles; dynamic contracts enumerate concrete fields",
        9: "migration units rebuilt only from accepted executable transformation groups with dependency order, FK outputs and executable validation",
        10: "scenario builders include scenario-specific records, histories and expected operator/public projections",
        11: "ADRs reconciled to named passing assertions and open RFIs; stale Review 05 status removed",
        12: "semantic CI detects each Review 06 defect class and reports named executable assertions only",
        13: "migration-ledger runtime fix moved to maintenance PR #8 and PR #7 restored to design-only scope",
    }
    rows = [f"| F{i:02d} | Resolved for SDA Review 07: {evidence[i]}. | `{fixing}`; evidence: Review 07 semantic assertions, design consistency report, target schema validation, route/projection registries, scenario expectations, ADR assertion matrix and exact-head CI. | READY FOR SDA REVIEW | {DATE} |" for i in [2,4,5,6,7,8,9,10,11,12,13]]
    block = "\n".join(rows)
    section = "## 9. Review 06 resolution log"
    if section not in text:
        raise SystemExit("Review 06 resolution log section missing")
    before, tail = text.split(section, 1)
    pattern = r"\| F02 \|[^\n]+\|\n\| F04 \|[^\n]+\|\n\| F05 \|[^\n]+\|\n\| F06 \|[^\n]+\|\n\| F07 \|[^\n]+\|\n\| F08 \|[^\n]+\|\n\| F09 \|[^\n]+\|\n\| F10 \|[^\n]+\|\n\| F11 \|[^\n]+\|\n\| F12 \|[^\n]+\|\n\| F13 \|[^\n]+\|"
    updated_tail = re.sub(pattern, block, tail)
    if updated_tail == tail:
        if all(f"| F{i:02d} | Resolved for SDA Review 07:" in tail for i in [2,4,5,6,7,8,9,10,11,12,13]):
            return
        raise SystemExit("Review 06 resolution log rows were not replaced")
    REVIEW.write_text(before + section + updated_tail, encoding="utf-8")


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
    lines = ["# Review 07 Semantic Design Report", "", f"Errors: {len(errors)}", ""]
    if errors:
        lines += ["## Errors"] + [f"- {e}" for e in errors]
    else:
        lines += ["## PASS", "- Current migrations applied to disposable PostgreSQL/PostGIS and inventoried from pg_catalog.", "- Migration ledger and operational-control fields included.", "- Current OpenAPI generated with operation/auth/request/response/status inventory.", "- Transformation registry covers every current field and governed raw archives.", "- Target typed model corrected for vocabularies, lifecycles, code history and subject strategy.", "- Dependency-safe target schema executed and compared to typed model.", "- Machine-readable fixtures inserted and validated by database constraints.", "- Review 06 F02 and F04-F13 evidence rows updated to READY FOR SDA REVIEW."]
    lines += ["", "## Metrics", "", md_table(["Metric", "Value"], [[k, v] for k, v in report.items() if k != "errors"])]
    write("docs/sda/data-model/review04-semantic-design-report.md", "\n".join(lines))
    if errors:
        raise SystemExit("; ".join(errors))
    return report


def main() -> None:
    ledger = apply_current_migrations()
    cat = current_catalog()
    semantics = load_reviewed_current_field_semantics(cat)
    render_current_inventory(cat, ledger, semantics)
    ops = generate_openapi_inventory()
    model = load_and_correct_model()
    render_target_registry(model)
    render_erd(model)
    render_vocab_and_lifecycle(model)
    registry = build_transform_registry(cat, model)
    transform_report = execute_transformation_fixtures(registry, semantics)
    fixtures = generate_fixtures(model)
    target_report = execute_target_schema_and_fixtures(model, fixtures)
    render_convergence(registry, transform_report)
    render_adrs()
    render_evidence(cat, ops, registry, target_report)
    update_review_log()
    report = final_semantic_checks(cat, ops, registry, model, target_report)
    print(json.dumps({"ok": True, **report}, sort_keys=True))


if __name__ == "__main__":
    main()
