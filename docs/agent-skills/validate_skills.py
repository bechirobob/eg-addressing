#!/usr/bin/env python3
"""Validate the repository-native NLI implementation-agent skills system.

The validator is intentionally dependency-free so it can run locally and in GitHub
Actions. It checks structure and routing coverage; it does not replace SDA review of
skill content or active work-order compliance.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = ROOT / "docs" / "agent-skills"
MANIFEST_PATH = SKILLS_ROOT / "skills-manifest.json"
README_PATH = SKILLS_ROOT / "README.md"
COVERAGE_PATH = SKILLS_ROOT / "PROJECT-COVERAGE-MATRIX.md"
BOOTSTRAP_PATH = SKILLS_ROOT / "AGENT-BOOTSTRAP.md"
FAILURE_PATH = SKILLS_ROOT / "FAILURE-PREVENTION.md"
AGENTS_PATH = ROOT / "AGENTS.md"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "agent-skills-ci.yml"


def load_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive reporting
        errors.append(f"cannot read {path.relative_to(ROOT)}: {exc}")
        return ""


def load_manifest(errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"cannot parse {MANIFEST_PATH.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append("skills manifest root must be an object")
        return {}
    return value


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    manifest = load_manifest(errors)
    skills = manifest.get("skills", []) if isinstance(manifest, dict) else []
    if not isinstance(skills, list):
        errors.append("skills manifest 'skills' must be a list")
        skills = []

    readme = load_text(README_PATH, errors)
    coverage = load_text(COVERAGE_PATH, errors)
    bootstrap = load_text(BOOTSTRAP_PATH, errors)
    failure = load_text(FAILURE_PATH, errors)
    agents = load_text(AGENTS_PATH, errors)
    workflow = load_text(WORKFLOW_PATH, errors)

    required_top_level = [
        README_PATH,
        COVERAGE_PATH,
        BOOTSTRAP_PATH,
        FAILURE_PATH,
        MANIFEST_PATH,
        Path(__file__),
        WORKFLOW_PATH,
    ]
    for path in required_top_level:
        if not path.exists():
            errors.append(f"missing required file {path.relative_to(ROOT)}")

    expected_ids = [f"{number:02d}" for number in range(1, 31)]
    observed_ids: list[str] = []
    observed_slugs: list[str] = []
    layer_counts = {"cross-cutting": 0, "project-domain": 0}

    required_skill_keys = {"id", "slug", "title", "layer", "triggers", "project_surfaces"}
    for item in skills:
        if not isinstance(item, dict):
            errors.append("manifest contains a non-object skill entry")
            continue
        missing = sorted(required_skill_keys - set(item))
        if missing:
            errors.append(f"skill entry missing keys {missing}: {item}")
            continue

        skill_id = str(item["id"])
        slug = str(item["slug"])
        title = str(item["title"])
        layer = str(item["layer"])
        observed_ids.append(skill_id)
        observed_slugs.append(slug)

        if layer not in layer_counts:
            errors.append(f"skill {skill_id} has invalid layer {layer}")
        else:
            layer_counts[layer] += 1

        if not re.fullmatch(r"\d{2}", skill_id):
            errors.append(f"skill id must be two digits: {skill_id}")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            errors.append(f"skill {skill_id} has invalid slug {slug}")
        if not isinstance(item.get("triggers"), list) or not item["triggers"]:
            errors.append(f"skill {skill_id} has no triggers")
        if not isinstance(item.get("project_surfaces"), list) or not item["project_surfaces"]:
            errors.append(f"skill {skill_id} has no project surfaces")

        skill_dir = SKILLS_ROOT / "skills" / f"{skill_id}-{slug}"
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            errors.append(f"missing skill file {skill_file.relative_to(ROOT)}")
            continue
        text = load_text(skill_file, errors)
        expected_heading = f"# Skill {skill_id} — {title}"
        if expected_heading not in text:
            errors.append(
                f"{skill_file.relative_to(ROOT)} missing exact heading {expected_heading!r}"
            )
        for required_heading in [
            "## Use when",
            "## Objective",
            "## Procedure",
            "## Stop and escalate when",
            "## Anti-patterns",
        ]:
            if required_heading not in text:
                errors.append(f"{skill_file.relative_to(ROOT)} missing {required_heading}")
        if not any(
            heading in text
            for heading in ["## Required evidence", "## Required output", "## Required artifacts"]
        ):
            errors.append(
                f"{skill_file.relative_to(ROOT)} must contain Required evidence, output, or artifacts"
            )

        if f"`{skill_id}-{slug}`" not in readme and f"{skill_id}-{slug}/SKILL.md" not in readme:
            errors.append(f"README routing/file list does not reference {skill_id}-{slug}")
        if skill_id not in coverage:
            warnings.append(f"coverage matrix does not visibly reference skill id {skill_id}")

    if sorted(observed_ids) != expected_ids:
        errors.append(f"manifest skill ids must be exactly 01-30; observed {sorted(observed_ids)}")
    if len(set(observed_ids)) != len(observed_ids):
        errors.append("duplicate skill ids in manifest")
    if len(set(observed_slugs)) != len(observed_slugs):
        errors.append("duplicate skill slugs in manifest")
    if layer_counts["cross-cutting"] != 15:
        errors.append(f"expected 15 cross-cutting skills, found {layer_counts['cross-cutting']}")
    if layer_counts["project-domain"] != 15:
        errors.append(f"expected 15 project-domain skills, found {layer_counts['project-domain']}")

    for marker in [
        "Cross-cutting delivery and governance skills (`01–15`)",
        "Whole-project product and platform skills (`16–30`)",
        "PROJECT-COVERAGE-MATRIX.md",
    ]:
        if marker not in readme:
            errors.append(f"README missing whole-project routing marker: {marker}")

    for marker in [
        "Repository surface coverage",
        "NLI bounded-domain coverage",
        "Current platform module coverage",
        "User-role coverage",
        "Service lifecycle coverage",
        "National-readiness coverage",
    ]:
        if marker not in coverage:
            errors.append(f"coverage matrix missing section: {marker}")

    for marker in [
        "Cross-cutting delivery skills `01–15`",
        "Whole-project domain skills `16–30`",
        "PROJECT-COVERAGE-MATRIX.md",
        "skills-manifest.json",
    ]:
        if marker not in bootstrap:
            errors.append(f"bootstrap missing routing marker: {marker}")

    for marker in [
        "Cross-cutting delivery and governance skills `01–15`",
        "Whole-project product and platform skills `16–30`",
        "PROJECT-COVERAGE-MATRIX.md",
        "skills-manifest.json",
    ]:
        if marker not in agents:
            errors.append(f"AGENTS.md missing whole-project routing marker: {marker}")

    for marker in [
        "Validate all 30 skills and whole-project coverage",
        "python docs/agent-skills/validate_skills.py",
    ]:
        if marker not in workflow:
            errors.append(f"agent skills workflow missing marker: {marker}")

    if len(failure.splitlines()) < 100:
        warnings.append("failure-prevention handbook is unexpectedly short")

    print("NLI agent skills validation")
    print(f"skills: {len(skills)}")
    print(f"cross-cutting: {layer_counts['cross-cutting']}")
    print(f"project-domain: {layer_counts['project-domain']}")
    print(f"errors: {len(errors)}")
    print(f"warnings: {len(warnings)}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nPASS — all 30 skills and whole-project routing controls are structurally valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
