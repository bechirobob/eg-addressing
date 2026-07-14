#!/usr/bin/env python3
"""Review 08 F12 actual pipeline/checker mutation executions.

Each case copies the design source/evidence pack to a temporary workspace, applies one
controlled mutation, runs the actual design consistency checker from that workspace,
and requires failure from the expected gate/reason.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[4]
DM = ROOT / "docs" / "sda" / "data-model"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_workspace(tmp: Path) -> Path:
    work = tmp / "repo"
    (work / "docs" / "sda").mkdir(parents=True)
    shutil.copytree(DM, work / "docs" / "sda" / "data-model")
    reviews = ROOT / "docs" / "sda" / "reviews"
    if reviews.exists():
        shutil.copytree(reviews, work / "docs" / "sda" / "reviews")
    return work


def run_checker(work: Path) -> tuple[int, str]:
    script = work / "docs" / "sda" / "data-model" / "scripts" / "design_consistency_check.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "services" / "api")
    proc = subprocess.run([os.environ.get("PYTHON", "python3"), str(script)], cwd=work, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    return proc.returncode, proc.stdout


def mutate_wrong_transformed_output(work: Path) -> None:
    p = work / "docs/sda/data-model/transformation-fixture-report.json"
    data = load_json(p)
    data["assertions"][0]["evidence"]["target_value_hash"] = ""
    write_json(p, data)


def mutate_missing_archive_or_fk(work: Path) -> None:
    p = work / "docs/sda/data-model/transformation-fixture-report.json"
    data = load_json(p)
    for assertion in data["assertions"]:
        if assertion.get("assertion_class") == "archive-created":
            assertion["evidence"]["archive_id"] = None
            break
    for assertion in data["assertions"]:
        if assertion.get("assertion_class") == "reference-final-fk":
            assertion["evidence"]["final_canonical_fk"] = None
            break
    write_json(p, data)


def mutate_wrong_field_classification(work: Path) -> None:
    p = work / "docs/sda/data-model/openapi-reviewed-projection-contracts.json"
    data = load_json(p)
    first = next(iter(data.values()))
    first["fields"][0]["classification"] = ""
    write_json(p, data)


def mutate_removed_cardinality_constraint(work: Path) -> None:
    p = work / "docs/sda/data-model/target-schema-catalog.json"
    data = load_json(p)
    data["triggers"] = [t for t in data.get("triggers", []) if t.get("trigger_name") != "required_object_roles_trg"]
    write_json(p, data)


def mutate_temporal_cycle_or_overlap(work: Path) -> None:
    p = work / "docs/sda/data-model/target-schema-catalog.json"
    data = load_json(p)
    data["report"]["negative_results"]["invalid-temporal-overlap"]["status"] = "passed-invalidly"
    write_json(p, data)


def mutate_weakened_geometry_authority(work: Path) -> None:
    p = work / "docs/sda/data-model/draft-physical-schema.sql"
    text = p.read_text(encoding="utf-8")
    text = text.replace("decision_row.details_json->>'permission_key' IS DISTINCT FROM rule.promotion_permission", "false")
    p.write_text(text, encoding="utf-8")


def mutate_missing_lifecycle_transition(work: Path) -> None:
    p = work / "docs/sda/data-model/target-schema-catalog.json"
    data = load_json(p)
    key = next(iter(data["report"]["lifecycle_transition_assertions"]))
    del data["report"]["lifecycle_transition_assertions"][key]
    write_json(p, data)


def mutate_wrong_api_policy(work: Path) -> None:
    p = work / "docs/sda/data-model/openapi-reviewed-route-policies.json"
    data = load_json(p)
    first = next(iter(data.values()))
    first["policy_source"] = "generated-from-observed-ast"
    write_json(p, data)


def mutate_missing_api_response_projection(work: Path) -> None:
    p = work / "docs/sda/data-model/openapi-reviewed-projection-contracts.json"
    data = load_json(p)
    for contract in data.values():
        response_fields = [f for f in contract.get("fields", []) if str(f.get("direction", "")).startswith("response:2")]
        if response_fields:
            status = response_fields[0]["direction"]
            contract["fields"] = [f for f in contract["fields"] if f.get("direction") != status]
            break
    write_json(p, data)


def mutate_broken_scenario_output(work: Path) -> None:
    p = work / "docs/sda/data-model/target-schema-catalog.json"
    data = load_json(p)
    scenario = data["report"]["review08_scenario_query_results"]["multi-unit-building"]
    scenario["public_projection"] = []
    write_json(p, data)


def mutate_negative_harness_false_pass(work: Path) -> None:
    p = work / "docs/sda/data-model/target-schema-catalog.json"
    data = load_json(p)
    data["report"]["negative_harness_regression"] = {"status": "missing"}
    write_json(p, data)


MUTATIONS: list[tuple[str, Callable[[Path], None], str]] = [
    ("wrong-transformed-output", mutate_wrong_transformed_output, "named transform assertion must come from disposable DB execution"),
    ("missing-archive-or-final-fk", mutate_missing_archive_or_fk, "archive-created assertion must include governed archive row evidence"),
    ("wrong-field-classification", mutate_wrong_field_classification, "missing classification"),
    ("removed-cardinality-constraint", mutate_removed_cardinality_constraint, "target schema actual trigger catalog missing required semantic triggers"),
    ("temporal-cycle-or-overlap", mutate_temporal_cycle_or_overlap, "invalid-temporal-overlap was not produced by real SQL/policy execution"),
    ("weakened-geometry-authority", mutate_weakened_geometry_authority, "geometry promotion trigger does not bind actor permission"),
    ("missing-lifecycle-transition", mutate_missing_lifecycle_transition, "every authored lifecycle transition"),
    ("wrong-api-policy", mutate_wrong_api_policy, "route policy must be independently reviewed"),
    ("missing-api-response-field-projection", mutate_missing_api_response_projection, "every successful response must have exact reviewed response fields"),
    ("broken-scenario-output", mutate_broken_scenario_output, "F10 scenario must include persisted query evidence"),
    ("negative-harness-false-pass-regression", mutate_negative_harness_false_pass, "negative harness false-pass regression"),
]


def main() -> None:
    results = []
    for name, mutate, expected in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="nli-wo002-r08-mut-") as td:
            work = copy_workspace(Path(td))
            mutate(work)
            code, output = run_checker(work)
            caught = code != 0 and expected in output
            results.append({
                "mutation": name,
                "status": "passed" if caught else "failed",
                "execution_mode": "temp-workspace-actual-design-checker",
                "expected_reason": expected,
                "exit_code": code,
                "observed_excerpt": output[-1600:],
            })
    failed = [r for r in results if r["status"] != "passed"]
    report = {"summary": {"execution_mode": "review08-temp-workspace-actual-pipeline-checker", "mutations": len(results), "caught": len(results) - len(failed), "failed": len(failed), "status": "passed" if not failed else "failed"}, "results": results}
    (DM / "semantic-mutation-test-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Review 08 F12 Semantic Mutation Test Report", "", "Each mutation is applied in a copied temporary design workspace and verified by running the actual `design_consistency_check.py` gate.", "", f"Mutations: {len(results)}", f"Caught: {len(results) - len(failed)}", f"Failed: {len(failed)}", "", "| Mutation | Status | Expected reason |", "|---|---|---|"]
    for r in results:
        lines.append(f"| {r['mutation']} | {r['status']} | {r['expected_reason']} |")
    (DM / "semantic-mutation-test-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    if failed:
        raise SystemExit(f"Review 08 semantic mutations failed: {[r['mutation'] for r in failed]}")


if __name__ == "__main__":
    main()
