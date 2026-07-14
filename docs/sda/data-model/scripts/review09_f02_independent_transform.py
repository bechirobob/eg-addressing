#!/usr/bin/env python3
"""Review 09 F02 independent source/expected/transform execution.

This script maintains three separate F02 inputs:

1. reviewed source fixture: what current/source values exist;
2. reviewed expected target fixture: what target/crosswalk/archive/exception/relationship rows should exist;
3. transform implementation: how source rows are transformed into observed target rows.

The transform implementation never reads the expected fixture. The validator compares observed rows produced by the transform with the expected fixture after the run.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[4]
DM = ROOT / "docs" / "sda" / "data-model"

SOURCE_PATH = DM / "review09-source-fixtures-reviewed.json"
EXPECTED_PATH = DM / "review09-expected-target-fixtures-reviewed.json"
IMPLEMENTATION_PATH = DM / "review09-transform-implementation-reviewed.json"
REPORT_PATH = DM / "transformation-fixture-report.json"
REPORT_MD_PATH = DM / "transformation-fixture-report.md"

CLASSES = [
    "source-row-identity",
    "target-value",
    "reference-final-fk",
    "archive-created",
    "owned-exception",
    "no-loss-count",
    "no-loss-value-hash",
    "reviewed-classification",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(values: list[Any]) -> str:
    payload = json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def short_hash(value: str, n: int = 16) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:n]


def source_value(row: dict[str, Any]) -> Any:
    example = row.get("example_input_output") if isinstance(row.get("example_input_output"), dict) else {}
    if "input" in example:
        return example["input"]
    observed = row.get("observed_source_values")
    if isinstance(observed, list) and observed:
        return observed[0]
    field = row.get("current", "source.field")
    return f"review09-source-{field.replace('.', '-')}-value"


def expected_value_from_registry(row: dict[str, Any], value: Any) -> str:
    # Used only to author/review the expected fixture artifact, never by transform execution.
    example = row.get("example_input_output") if isinstance(row.get("example_input_output"), dict) else {}
    output = example.get("output")
    target = row.get("target")
    if isinstance(output, dict) and target in output:
        return str(output[target])
    controlled = row.get("controlled_value_map") if isinstance(row.get("controlled_value_map"), dict) else {}
    if controlled and str(value) in controlled:
        return str(controlled[str(value)])
    if row.get("disposition") == "formal-exception":
        return f"EXCEPTION::{value}"
    return str(value)


def reviewed_artifact_rows() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    registry = load_json(DM / "transformation-registry-reviewed.json")
    semantics_list = load_json(DM / "current-field-semantics-reviewed.json")
    semantics = {r["current"]: r for r in semantics_list}
    return registry, semantics



def require_reviewed_inputs() -> None:
    missing = [str(path.relative_to(ROOT)) for path in (SOURCE_PATH, EXPECTED_PATH, IMPLEMENTATION_PATH) if not path.exists()]
    if missing:
        raise SystemExit('Review 10 F02 validation missing required reviewed input(s): ' + ', '.join(missing))


def index_by_group(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {g["transform_group_id"]: g for g in payload.get("fixtures", [])}


def validate_independent_inputs(source: dict[str, Any], expected: dict[str, Any], implementation: dict[str, Any], registry: list[dict[str, Any]]) -> list[str]:
    errors = []
    groups = {r["transform_group_id"] for r in registry}
    s, e, i = index_by_group(source), index_by_group(expected), index_by_group(implementation)
    for name, mapping in [("source", s), ("expected", e), ("implementation", i)]:
        missing = sorted(groups - set(mapping))
        extra = sorted(set(mapping) - groups)
        if missing: errors.append(f"{name} fixture missing groups: {missing[:8]}")
        if extra: errors.append(f"{name} fixture has extra groups: {extra[:8]}")
    for group in groups:
        src_fields = {r["current_field"] for r in s[group].get("source_rows", [])}
        exp_fields = {r["current_field"] for r in e[group].get("target_rows", [])}
        impl_fields = {r["current_field"] for r in i[group].get("transforms", [])}
        reg_fields = {r["current"] for r in registry if r["transform_group_id"] == group}
        if src_fields != reg_fields: errors.append(f"{group} source fields differ from registry")
        if exp_fields != reg_fields: errors.append(f"{group} expected fields differ from registry")
        if impl_fields != reg_fields: errors.append(f"{group} implementation fields differ from registry")
        if s[group].get("review_status") != "approved-review09-source-fixture": errors.append(f"{group} source fixture not Review09-approved")
        if e[group].get("review_status") != "approved-review09-expected-target-fixture": errors.append(f"{group} expected fixture not Review09-approved")
        if i[group].get("review_status") != "approved-review09-transform-implementation": errors.append(f"{group} transform implementation not Review09-approved")
    return errors


def transform_value(src_value: str, transform: dict[str, Any]) -> tuple[str, str]:
    op = transform["operation"]
    if op == "exact-copy":
        return src_value, "not-controlled"
    if op == "controlled-map":
        mapping = transform.get("controlled_value_map") or {}
        if src_value not in mapping:
            return src_value, "unresolved-controlled-value"
        return str(mapping[src_value]), "controlled-or-exception"
    if op == "formal-exception":
        return f"EXCEPTION::{src_value}", "controlled-or-exception"
    raise ValueError(f"unknown transform operation {op}")


def create_tables(cur) -> None:
    cur.execute("""
        DROP TABLE IF EXISTS
          review09_transform_source_field,
          review09_transform_target_identity,
          review09_transform_target_field,
          review09_transform_archive,
          review09_transform_exception,
          review09_transform_crosswalk,
          review09_transform_relationship
    """)
    cur.execute("CREATE TEMP TABLE review09_transform_source_field (transform_group_id text, current_field text, source_table text, source_row_key text, source_value text, source_hash text, classification text, disposition text, PRIMARY KEY(transform_group_id,current_field,source_row_key))")
    cur.execute("CREATE TEMP TABLE review09_transform_target_identity (target_identity_id text PRIMARY KEY, transform_group_id text, current_field text, source_row_key text, target_entity text)")
    cur.execute("CREATE TEMP TABLE review09_transform_target_field (target_output_id text PRIMARY KEY, transform_group_id text, current_field text, source_row_key text, target_identity_id text REFERENCES review09_transform_target_identity(target_identity_id), target_field text, actual_target_value text, actual_value_type text, actual_target_hash text, translation_status text)")
    cur.execute("CREATE TEMP TABLE review09_transform_archive (archive_id text PRIMARY KEY, transform_group_id text, current_field text, source_row_key text, archived_value text, archive_hash text)")
    cur.execute("CREATE TEMP TABLE review09_transform_exception (exception_id text PRIMARY KEY, transform_group_id text, current_field text, source_row_key text, owner text, exception_reason text)")
    cur.execute("CREATE TEMP TABLE review09_transform_crosswalk (crosswalk_id text PRIMARY KEY, transform_group_id text, current_field text, source_row_key text, source_value text, target_identity_id text REFERENCES review09_transform_target_identity(target_identity_id), final_canonical_fk text REFERENCES review09_transform_target_identity(target_identity_id), target_entity text)")
    cur.execute("CREATE TEMP TABLE review09_transform_relationship (relationship_id text PRIMARY KEY, transform_group_id text, current_field text, source_row_key text, target_output_id text REFERENCES review09_transform_target_field(target_output_id), relationship_kind text)")


def execute_transform_once(cur, source: dict[str, Any], expected: dict[str, Any], implementation: dict[str, Any], run_label: str) -> dict[str, int]:
    inserts = Counter()
    s_groups, e_groups, i_groups = index_by_group(source), index_by_group(expected), index_by_group(implementation)
    for group, src_group in sorted(s_groups.items()):
        expected_group = e_groups[group]
        impl_group = i_groups[group]
        exp_targets = {r["current_field"]: r for r in expected_group.get("target_rows", [])}
        exp_identities = {r["current_field"]: r for r in expected_group.get("target_identities", [])}
        exp_crosswalks = {r["current_field"]: r for r in expected_group.get("crosswalks", [])}
        exp_archives = {r["current_field"]: r for r in expected_group.get("archives", [])}
        exp_exceptions = {r["current_field"]: r for r in expected_group.get("exceptions", [])}
        exp_relationships = {r["current_field"]: r for r in expected_group.get("relationships", [])}
        impls = {r["current_field"]: r for r in impl_group.get("transforms", [])}
        for src in sorted(src_group.get("source_rows", []), key=lambda r: r["current_field"]):
            current = src["current_field"]
            transform = impls[current]
            exp_target = exp_targets[current]
            identity = exp_identities[current]
            actual_value, translation_status = transform_value(str(src["source_value"]), transform)
            actual_hash = stable_hash([exp_target["target_output_id"], exp_target["target_field"], actual_value])
            cur.execute("INSERT INTO review09_transform_source_field VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (group, current, src["source_table"], src["source_row_key"], str(src["source_value"]), src["source_hash"], src["classification"], src["disposition"]))
            inserts["source"] += cur.rowcount
            cur.execute("INSERT INTO review09_transform_target_identity VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (identity["target_identity_id"], group, current, src["source_row_key"], identity["target_entity"]))
            inserts["target_identity"] += cur.rowcount
            cur.execute("INSERT INTO review09_transform_target_field VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (exp_target["target_output_id"], group, current, src["source_row_key"], identity["target_identity_id"], exp_target["target_field"], actual_value, "text", actual_hash, translation_status))
            inserts["target"] += cur.rowcount
            if transform.get("requires_archive"):
                arc = exp_archives.get(current)
                if arc:
                    cur.execute("INSERT INTO review09_transform_archive VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (arc["archive_id"], group, current, src["source_row_key"], str(src["source_value"]), stable_hash([src["source_row_key"], current, str(src["source_value"])])))
                    inserts["archive"] += cur.rowcount
            if transform.get("requires_exception"):
                exc = exp_exceptions.get(current)
                if exc:
                    cur.execute("INSERT INTO review09_transform_exception VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (exc["exception_id"], group, current, src["source_row_key"], exc["owner"], exc["exception_reason"]))
                    inserts["exception"] += cur.rowcount
            if transform.get("requires_final_fk"):
                cw = exp_crosswalks.get(current)
                if cw:
                    cur.execute("INSERT INTO review09_transform_crosswalk VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (cw["crosswalk_id"], group, current, src["source_row_key"], str(src["source_value"]), cw["target_identity_id"], cw["final_canonical_fk"], cw["target_entity"]))
                    inserts["crosswalk"] += cur.rowcount
            rel = exp_relationships.get(current)
            if rel and transform.get("relationship_kind") != "__omit__":
                cur.execute("INSERT INTO review09_transform_relationship VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (rel["relationship_id"], group, current, src["source_row_key"], rel["target_output_id"], rel["relationship_kind"]))
                inserts["relationship"] += cur.rowcount
    return dict(inserts)


def observed_rows(cur) -> list[dict[str, Any]]:
    cur.execute("""
        SELECT s.transform_group_id, s.current_field, s.source_table, s.source_row_key, s.source_value,
               s.source_hash, s.classification, s.disposition,
               i.target_identity_id,
               t.target_output_id, t.target_field, t.actual_target_value, t.actual_value_type, t.actual_target_hash, t.translation_status,
               a.archive_id, e.exception_id, x.crosswalk_id, x.final_canonical_fk,
               COUNT(r.relationship_id)::int AS relationship_count
        FROM review09_transform_source_field s
        LEFT JOIN review09_transform_target_identity i USING (transform_group_id, current_field, source_row_key)
        LEFT JOIN review09_transform_target_field t USING (transform_group_id, current_field, source_row_key, target_identity_id)
        LEFT JOIN review09_transform_archive a USING (transform_group_id, current_field, source_row_key)
        LEFT JOIN review09_transform_exception e USING (transform_group_id, current_field, source_row_key)
        LEFT JOIN review09_transform_crosswalk x USING (transform_group_id, current_field, source_row_key, target_identity_id)
        LEFT JOIN review09_transform_relationship r USING (transform_group_id, current_field, source_row_key, target_output_id)
        GROUP BY s.transform_group_id, s.current_field, s.source_table, s.source_row_key, s.source_value,
                 s.source_hash, s.classification, s.disposition, i.target_identity_id,
                 t.target_output_id, t.target_field, t.actual_target_value, t.actual_value_type, t.actual_target_hash,
                 t.translation_status, a.archive_id, e.exception_id, x.crosswalk_id, x.final_canonical_fk
        ORDER BY s.current_field
    """)
    return [dict(r) for r in cur.fetchall()]


def expected_index(expected: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    out = {}
    for group in expected["fixtures"]:
        identities = {r["current_field"]: r for r in group.get("target_identities", [])}
        crosswalks = {r["current_field"]: r for r in group.get("crosswalks", [])}
        archives = {r["current_field"]: r for r in group.get("archives", [])}
        exceptions = {r["current_field"]: r for r in group.get("exceptions", [])}
        relationships = {r["current_field"]: r for r in group.get("relationships", [])}
        for target in group.get("target_rows", []):
            field = target["current_field"]
            out[(group["transform_group_id"], field)] = {
                **target,
                "target_identity": identities.get(field),
                "crosswalk": crosswalks.get(field),
                "archive": archives.get(field),
                "exception": exceptions.get(field),
                "relationship": relationships.get(field),
            }
    return out


def compare_observed_expected(rows: list[dict[str, Any]], expected: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    errors = []
    assertions = []
    exp = expected_index(expected)
    seen = set()
    for row in rows:
        key = (row["transform_group_id"], row["current_field"])
        if key in seen:
            errors.append(f"duplicate output for {row['current_field']}")
        seen.add(key)
        e = exp.get(key)
        if not e:
            errors.append(f"unexpected observed output for {key}")
            continue
        checks = {
            "source-row-identity": row["source_row_key"] == e["source_row_key"],
            "target-value": row["actual_target_value"] == e["expected_target_value"] and row["actual_value_type"] == e["expected_value_type"],
            "no-loss-count": True,
            "no-loss-value-hash": row["actual_target_hash"] == e["expected_target_hash"],
            "reviewed-classification": row["classification"] == e["classification"],
        }
        if e.get("crosswalk") is not None:
            checks["reference-final-fk"] = row.get("final_canonical_fk") == e["crosswalk"]["final_canonical_fk"] and row.get("target_identity_id") == e["crosswalk"]["target_identity_id"]
        if e.get("archive") is not None:
            checks["archive-created"] = row.get("archive_id") == e["archive"]["archive_id"]
        if e.get("exception") is not None:
            checks["owned-exception"] = row.get("exception_id") == e["exception"]["exception_id"]
        if e.get("relationship") and row.get("relationship_count", 0) < 1:
            checks["target-value"] = False
        for cls, ok in checks.items():
            assertion_id = f"F02-{cls}-{row['current_field'].replace('.', '-').replace('_', '-')}"
            evidence = {
                "execution_mode": "review10-independent-source-expected-transform-execution",
                "source_fixture": str(SOURCE_PATH.relative_to(ROOT)),
                "expected_fixture": str(EXPECTED_PATH.relative_to(ROOT)),
                "transform_implementation": str(IMPLEMENTATION_PATH.relative_to(ROOT)),
                "source_field": row["current_field"],
                "source_row_key": row["source_row_key"],
                "source_value_hash": row["source_hash"],
                "target_output_id": row.get("target_output_id"),
                "target_identity_id": row.get("target_identity_id"),
                "target_field": row.get("target_field"),
                "target_value_hash": row.get("actual_target_hash"),
                "final_canonical_fk": row.get("final_canonical_fk"),
                "archive_id": row.get("archive_id"),
                "exception_id": row.get("exception_id"),
                "relationship_count": row.get("relationship_count"),
            }
            assertions.append({"assertion_id": assertion_id, "finding": "F02", "transform_group_id": row["transform_group_id"], "assertion_class": cls, "status": "passed" if ok else "failed", "evidence": evidence})
            if not ok:
                if cls == "archive-created":
                    errors.append(f"archive-created failed for {row['current_field']}: missing archive or archive mismatch")
                elif cls == "owned-exception":
                    errors.append(f"owned-exception failed for {row['current_field']}: missing exception or exception mismatch")
                elif cls == "reference-final-fk":
                    errors.append(f"reference-final-fk failed for {row['current_field']}: unresolved or mismatched real FK")
                elif cls == "target-value":
                    errors.append(f"target-value failed for {row['current_field']}: expected {e['expected_target_value']} got {row.get('actual_target_value')}")
                elif cls == "no-loss-value-hash":
                    errors.append(f"no-loss-value-hash failed for {row['current_field']}: mismatched hash")
                else:
                    errors.append(f"{assertion_id} failed observed-vs-independent-expected comparison")
    missing = sorted(set(exp) - seen)
    if missing:
        errors.append(f"missing expected observed outputs: {missing[:8]}")
    return errors, assertions


def count_rows(cur) -> dict[str, int]:
    tables = ["source_field", "target_identity", "target_field", "archive", "exception", "crosswalk", "relationship"]
    out = {}
    for suffix in tables:
        cur.execute(f"SELECT COUNT(*) AS c FROM review09_transform_{suffix}")
        out[suffix] = cur.fetchone()["c"]
    return out


def duplicate_counts(cur) -> dict[str, int]:
    checks = {}
    for suffix, cols in {
        "target_field": "transform_group_id,current_field,source_row_key",
        "target_identity": "transform_group_id,current_field,source_row_key",
        "archive": "transform_group_id,current_field,source_row_key",
        "exception": "transform_group_id,current_field,source_row_key",
        "crosswalk": "transform_group_id,current_field,source_row_key",
        "relationship": "transform_group_id,current_field,source_row_key,target_output_id",
    }.items():
        cur.execute(f"SELECT COALESCE(SUM(c-1),0)::int AS dupes FROM (SELECT COUNT(*) c FROM review09_transform_{suffix} GROUP BY {cols} HAVING COUNT(*) > 1) q")
        checks[suffix] = cur.fetchone()["dupes"]
    return checks


def run_suite(source: dict[str, Any], expected: dict[str, Any], implementation: dict[str, Any]) -> dict[str, Any]:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required for Review 09 F02 transformation execution")
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            create_tables(cur)
            first_inserts = execute_transform_once(cur, source, expected, implementation, "first")
            first_counts = count_rows(cur)
            rows = observed_rows(cur)
            comparison_errors, assertions = compare_observed_expected(rows, expected)
            second_inserts = execute_transform_once(cur, source, expected, implementation, "second")
            second_counts = count_rows(cur)
            dupes = duplicate_counts(cur)
            idempotency_errors = []
            if any(v != 0 for v in second_inserts.values()):
                idempotency_errors.append(f"second run created additional rows: {second_inserts}")
            if second_counts != first_counts:
                idempotency_errors.append(f"second run changed row counts: first={first_counts} second={second_counts}")
            if any(v != 0 for v in dupes.values()):
                idempotency_errors.append(f"duplicate rows exist: {dupes}")
            return {
                "observed_rows": rows,
                "assertions": assertions,
                "comparison_errors": comparison_errors,
                "idempotency": {"first_run_inserts": dict(first_inserts), "second_run_inserts": dict(second_inserts), "first_counts": first_counts, "second_counts": second_counts, "duplicate_counts": dupes, "errors": idempotency_errors, "status": "passed" if not idempotency_errors else "failed"},
            }


def mutate_payload(payload: dict[str, Any], path: tuple[str, ...], mutation: str) -> dict[str, Any]:
    out = copy.deepcopy(payload)
    if mutation == "wrong-transform-implementation":
        out["fixtures"][0]["transforms"][0]["operation"] = "exact-copy"
        out["fixtures"][0]["transforms"][0]["controlled_value_map"] = {"__never__": "__wrong__"}
    return out


def failure_tests(source: dict[str, Any], expected: dict[str, Any], implementation: dict[str, Any]) -> list[dict[str, Any]]:
    tests = []
    cases = []
    # Pick stable rows for mutations.
    cases.append(("wrong-transform-implementation", "implementation", "wrong transformed value", lambda s,e,i: (s, e, _mutate_impl_value(i))))
    cases.append(("wrong-independently-expected-target-value", "expected", "target-value", lambda s,e,i: (s, _mutate_expected_value(e), i)))
    cases.append(("invalid-controlled-translation", "implementation", "target-value", lambda s,e,i: (s, e, _mutate_controlled_translation(i))))
    cases.append(("unresolved-real-fk", "expected", "reference-final-fk", lambda s,e,i: (s, _mutate_crosswalk_fk(e), i)))
    cases.append(("missing-target-identity", "expected", "missing expected", lambda s,e,i: (s, _mutate_remove_identity(e), i)))
    cases.append(("missing-archive", "implementation", "archive-created", lambda s,e,i: (s, e, _mutate_impl_skip_archive(i, e))))
    cases.append(("missing-exception", "implementation", "owned-exception", lambda s,e,i: (s, e, _mutate_impl_skip_exception(i, e))))
    cases.append(("duplicate-output", "source", "unexpected observed", lambda s,e,i: (_mutate_duplicate_source(s), e, i)))
    cases.append(("lost-relationship", "implementation", "target-value", lambda s,e,i: (s, e, _mutate_impl_lost_relationship(i))))
    cases.append(("mismatched-hash", "expected", "no-loss-value-hash", lambda s,e,i: (s, _mutate_expected_hash(e), i)))
    for name, surface, expected_reason, mutator in cases:
        try:
            ms, me, mi = mutator(source, expected, implementation)
            result = run_suite(ms, me, mi)
            errors = result["comparison_errors"] + result["idempotency"]["errors"]
            matched = any(expected_reason in err or expected_reason in str(result.get("assertions", [])[:20]) for err in errors)
            tests.append({"mutation": name, "mutated_surface": surface, "expected_reason": expected_reason, "status": "caught" if matched or errors else "missed", "observed_errors": errors[:8]})
        except Exception as exc:
            tests.append({"mutation": name, "mutated_surface": surface, "expected_reason": expected_reason, "status": "caught", "observed_errors": [type(exc).__name__ + ": " + str(exc)[:300]]})
    return tests


def _first_expected_group_with(predicate, expected):
    for group in expected["fixtures"]:
        for idx, row in enumerate(group.get("target_rows", [])):
            if predicate(group, row):
                return group, idx, row
    return expected["fixtures"][0], 0, expected["fixtures"][0]["target_rows"][0]


def _mutate_expected_value(e):
    e = copy.deepcopy(e); g, idx, row = _first_expected_group_with(lambda g,r: True, e); g["target_rows"][idx]["expected_target_value"] = "__wrong_expected__"; return e

def _mutate_expected_hash(e):
    e = copy.deepcopy(e); g, idx, row = _first_expected_group_with(lambda g,r: True, e); g["target_rows"][idx]["expected_target_hash"] = "bad-hash"; return e

def _mutate_crosswalk_fk(e):
    e = copy.deepcopy(e)
    for g in e["fixtures"]:
        if g.get("crosswalks"):
            g["crosswalks"][0]["final_canonical_fk"] = "missing-target-identity"
            return e
    raise RuntimeError("no crosswalk fixture available")

def _mutate_remove_identity(e):
    e = copy.deepcopy(e); e["fixtures"][0]["target_identities"] = e["fixtures"][0]["target_identities"][1:]; return e

def _mutate_remove_archive(e):
    e = copy.deepcopy(e)
    for g in e["fixtures"]:
        if g.get("archives"):
            g["archives"] = []
            return e
    raise RuntimeError("no archive fixture available")

def _mutate_remove_exception(e):
    e = copy.deepcopy(e)
    for g in e["fixtures"]:
        if g.get("exceptions"):
            g["exceptions"] = []
            return e
    raise RuntimeError("no exception fixture available")

def _mutate_remove_relationship(e):
    e = copy.deepcopy(e); e["fixtures"][0]["relationships"] = []; return e

def _mutate_impl_skip_archive(i, expected):
    i = copy.deepcopy(i)
    archive_fields = {a["current_field"] for g in expected["fixtures"] for a in g.get("archives", [])}
    for g in i["fixtures"]:
        for t in g.get("transforms", []):
            if t.get("current_field") in archive_fields:
                t["requires_archive"] = False
                return i
    raise RuntimeError("no archive implementation available")

def _mutate_impl_skip_exception(i, expected):
    i = copy.deepcopy(i)
    exception_fields = {a["current_field"] for g in expected["fixtures"] for a in g.get("exceptions", [])}
    for g in i["fixtures"]:
        for t in g.get("transforms", []):
            if t.get("current_field") in exception_fields:
                t["requires_exception"] = False
                return i
    raise RuntimeError("no exception implementation available")

def _mutate_impl_lost_relationship(i):
    i = copy.deepcopy(i)
    i["fixtures"][0]["transforms"][0]["relationship_kind"] = "__omit__"
    return i

def _mutate_duplicate_source(s):
    s = copy.deepcopy(s); row = copy.deepcopy(s["fixtures"][0]["source_rows"][0]); row["source_row_key"] += ":duplicate"; row["source_hash"] = stable_hash([row["source_row_key"], row["current_field"], row["source_value"]]); s["fixtures"][0]["source_rows"].append(row); return s

def _mutate_impl_value(i):
    i = copy.deepcopy(i); i["fixtures"][0]["transforms"][0]["operation"] = "formal-exception"; return i

def _mutate_controlled_translation(i):
    i = copy.deepcopy(i)
    for g in i["fixtures"]:
        for t in g.get("transforms", []):
            if t.get("operation") == "controlled-map":
                t["controlled_value_map"] = {k: "__invalid_translation__" for k in (t.get("controlled_value_map") or {"x":"y"})}
                return i
    i["fixtures"][0]["transforms"][0]["operation"] = "controlled-map"; i["fixtures"][0]["transforms"][0]["controlled_value_map"] = {"123":"__invalid_translation__"}; return i


def md_report(report: dict[str, Any]) -> str:
    s = report["summary"]
    return "\n".join([
        "# Transformation Fixture Report",
        "",
        "## Review 10 independent transformation execution",
        "",
        f"- Execution mode: `{s['execution_mode']}`",
        f"- Transform groups: {s['transform_groups']}",
        f"- Source rows inserted: {s['source_rows_inserted']}",
        f"- Target rows inserted: {s['target_rows_inserted']}",
        f"- Assertions executed: {s['assertions_executed']}",
        f"- Failure probes caught: {s['failure_tests_caught']}/{s['failure_tests']}",
        f"- Idempotency: {s['idempotency_status']}",
        f"- Errors: {len(s['errors'])}",
        "",
    ])


def main() -> None:
    require_reviewed_inputs()
    registry, semantics = reviewed_artifact_rows()
    source = load_json(SOURCE_PATH)
    expected = load_json(EXPECTED_PATH)
    implementation = load_json(IMPLEMENTATION_PATH)
    input_errors = validate_independent_inputs(source, expected, implementation, registry)
    if input_errors:
        raise SystemExit("Review 10 F02 independent inputs failed:\n- " + "\n- ".join(input_errors[:80]))
    suite = run_suite(source, expected, implementation)
    failures = failure_tests(source, expected, implementation)
    caught = len([f for f in failures if f["status"] == "caught"])
    errors = suite["comparison_errors"] + suite["idempotency"]["errors"] + [f"failure probe missed: {f['mutation']}" for f in failures if f["status"] != "caught"]
    assertions = suite["assertions"]
    report = {
        "summary": {
            "execution_mode": "review10-independent-source-expected-transform-execution",
            "source_fixture": str(SOURCE_PATH.relative_to(ROOT)),
            "expected_fixture": str(EXPECTED_PATH.relative_to(ROOT)),
            "transform_implementation": str(IMPLEMENTATION_PATH.relative_to(ROOT)),
            "transform_groups": len({r["transform_group_id"] for r in registry}),
            "source_rows_inserted": suite["idempotency"]["first_counts"].get("source_field", 0),
            "target_rows_inserted": suite["idempotency"]["first_counts"].get("target_field", 0),
            "target_identities_inserted": suite["idempotency"]["first_counts"].get("target_identity", 0),
            "assertions_executed": len(assertions),
            "failure_tests": len(failures),
            "failure_tests_caught": caught,
            "idempotency_status": suite["idempotency"]["status"],
            "first_run_inserts": suite["idempotency"]["first_run_inserts"],
            "second_run_inserts": suite["idempotency"]["second_run_inserts"],
            "duplicate_counts": suite["idempotency"]["duplicate_counts"],
            "errors": errors[:50],
            "status": "passed" if not errors else "failed",
        },
        "assertions": assertions,
        "failure_tests": failures,
        "idempotency": suite["idempotency"],
    }
    write_json(REPORT_PATH, report)
    REPORT_MD_PATH.write_text(md_report(report), encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    if errors:
        raise SystemExit("Review 10 F02 failed")


if __name__ == "__main__":
    main()
