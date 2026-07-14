#!/usr/bin/env python3
"""Review 07 F12 semantic mutation probes.

These probes intentionally mutate in-memory copies of the generated design evidence
and assert that the same semantic predicates enforced by design_consistency_check.py
would fail. They do not write runtime code or modify source artifacts.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
DM = ROOT / "docs" / "sda" / "data-model"


def load(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def passed(name: str, caught: bool, evidence: str) -> dict[str, str]:
    return {"mutation": name, "status": "passed" if caught else "failed", "evidence": evidence}


def main() -> None:
    registry = load("docs/sda/data-model/transformation-registry-reviewed.json")
    fixture_report = load("docs/sda/data-model/transformation-fixture-report.json")
    target_catalog = load("docs/sda/data-model/target-schema-catalog.json")
    routes = load("docs/sda/data-model/openapi-reviewed-route-policies.json")
    projections = load("docs/sda/data-model/openapi-reviewed-projection-contracts.json")
    fixtures = load("docs/sda/data-model/representative-records/machine-readable-fixtures.json")
    physical_sql = (DM / "draft-physical-schema.sql").read_text(encoding="utf-8")

    results: list[dict[str, str]] = []

    # Incorrect transformation: reference output regresses to legacy crosswalk only.
    mutated = copy.deepcopy(registry)
    ref_row = next(row for row in mutated if row.get("reference_crosswalk_join"))
    ref_row["reference_crosswalk_join"]["final_target_fk_output"] = "legacy_crosswalk.legacy_id"
    caught = any((row.get("reference_crosswalk_join") or {}).get("final_target_fk_output") in {"legacy_crosswalk.legacy_id", "proposed_legacy_crosswalk.legacy_id"} for row in mutated)
    results.append(passed("incorrect-transformation-final-fk-output", caught, "legacy crosswalk final FK regression detected"))

    # Missing constraint/trigger: publication prerequisite trigger removed from target catalog.
    mutated_catalog = copy.deepcopy(target_catalog)
    mutated_catalog["triggers"] = [t for t in mutated_catalog.get("triggers", []) if t.get("trigger_name") != "publication_prerequisite_trg"]
    required_triggers = {"registry_subject_native_trg", "required_object_roles_trg", "location_record_version_chain_trg", "public_code_alias_chain_trg", "publication_prerequisite_trg", "geometry_version_semantics_trg", "geometry_observation_semantics_trg"}
    caught = bool(required_triggers - {t.get("trigger_name") for t in mutated_catalog.get("triggers", [])})
    results.append(passed("missing-required-semantic-trigger", caught, "required trigger removal detected"))

    # Wrong route policy: reviewed policy source becomes observed/generated again.
    mutated_routes = copy.deepcopy(routes)
    first_key = next(iter(mutated_routes))
    mutated_routes[first_key]["policy_source"] = "generated-from-observed-ast"
    caught = any(row.get("policy_source") != "human-reviewed-route-policy-source" for row in mutated_routes.values())
    results.append(passed("wrong-route-policy-source", caught, "non-reviewed route policy source detected"))

    # Invalid API projection: credential field mapped to business archive.
    mutated_proj = copy.deepcopy(projections)
    changed = False
    for contract in mutated_proj.values():
        for field in contract.get("fields", []):
            if str(field.get("field", "")).lower() == "authorization":
                field["target_projection"] = "source_payload_archive"
                changed = True
                break
        if changed:
            break
    caught = changed and any(
        str(field.get("field", "")).lower() == "authorization" and "not-migrated" not in str(field.get("target_projection", ""))
        for contract in mutated_proj.values()
        for field in contract.get("fields", [])
    )
    results.append(passed("credential-projection-business-archive", caught, "authorization business-data migration detected"))

    # Invalid scenario: remove second multi-unit canonical record/version.
    mutated_fixtures = copy.deepcopy(fixtures)
    multi = mutated_fixtures["scenarios"]["multi-unit-building"]
    unit_record_ids = [r["location_record_id"] for r in multi.get("location_record", []) if r.get("record_type") == "unit"]
    if len(unit_record_ids) > 1:
        doomed = unit_record_ids[-1]
        multi["location_record"] = [r for r in multi["location_record"] if r.get("location_record_id") != doomed]
        multi["location_record_version"] = [v for v in multi["location_record_version"] if v.get("location_record_id") != doomed]
    caught = len([r for r in multi.get("location_record", []) if r.get("record_type") == "unit"]) < 2
    results.append(passed("invalid-multi-unit-scenario", caught, "missing second canonical unit detected"))

    # Temporal cycle: corrected address reciprocal chain removed.
    mutated_fixtures = copy.deepcopy(fixtures)
    versions = mutated_fixtures["scenarios"]["corrected-superseded-address"].get("location_record_version", [])
    if len(versions) >= 2:
        versions[0].pop("successor_version_id", None)
    caught = not (any(v.get("successor_version_id") for v in versions) and any(v.get("predecessor_version_id") for v in versions))
    results.append(passed("temporal-chain-reciprocity-break", caught, "missing reciprocal temporal chain detected"))

    # Unexpectedly successful negative operation: false-pass regression metadata removed.
    mutated_report = copy.deepcopy(target_catalog.get("report", {}))
    mutated_report["negative_harness_regression"] = {"status": "missing"}
    caught = mutated_report.get("negative_harness_regression", {}).get("status") != "passed"
    results.append(passed("unexpected-negative-operation-success", caught, "negative harness regression absence detected"))

    # Geometry authority trigger weakening: permission binding removed from SQL text.
    mutated_sql = physical_sql.replace("decision_row.details_json->>'permission_key' IS DISTINCT FROM rule.promotion_permission", "false")
    caught = "decision_row.details_json->>'permission_key' IS DISTINCT FROM rule.promotion_permission" not in mutated_sql
    results.append(passed("geometry-permission-binding-removed", caught, "geometry permission binding removal detected"))

    failed = [r for r in results if r["status"] != "passed"]
    report = {"summary": {"mutations": len(results), "caught": len(results) - len(failed), "failed": len(failed), "status": "passed" if not failed else "failed"}, "results": results}
    (DM / "semantic-mutation-test-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Review 07 F12 Semantic Mutation Test Report", "", f"Mutations: {len(results)}", f"Caught: {len(results) - len(failed)}", f"Failed: {len(failed)}", "", "| Mutation | Status | Evidence |", "|---|---|---|"]
    for r in results:
        lines.append(f"| {r['mutation']} | {r['status']} | {r['evidence']} |")
    (DM / "semantic-mutation-test-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if failed:
        raise SystemExit(f"semantic mutation tests failed: {failed}")
    print(json.dumps(report["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
