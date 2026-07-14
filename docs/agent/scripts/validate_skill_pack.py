#!/usr/bin/env python3
"""Validate the complete NLI delivery-agent skill pack.

The validator uses only the Python standard library. It validates the restricted
manifest structure used by this repository, the S01-S31 skill-card contract,
whole-project coverage files, local Markdown links, and AGENTS.md integration.
It does not replace SDA review of skill semantics or active work-order compliance.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AGENT = ROOT / "docs" / "agent"
MANIFEST = AGENT / "skill-manifest.yaml"
COVERAGE = AGENT / "PROJECT-COVERAGE-MATRIX.md"

REQUIRED_SKILLS = {f"S{i:02d}" for i in range(1, 32)}
CROSS_CUTTING_SKILLS = {f"S{i:02d}" for i in range(1, 17)}
WHOLE_PROJECT_SKILLS = {f"S{i:02d}" for i in range(17, 32)}
REQUIRED_CARD_HEADINGS = {
    "## Invoke when",
    "## Required inputs",
    "## Procedure",
    "## Outputs",
    "## Evidence gate",
    "## Anti-patterns",
}
MANDATORY_REFERENCES = {
    "README.md",
    "master-operating-protocol.md",
    "BOOTSTRAP-PROMPT.md",
    "PROJECT-COVERAGE-MATRIX.md",
    "templates/task-context-pack.md",
    "templates/finding-resolution-matrix.md",
    "templates/exact-head-evidence.md",
    "templates/self-audit.md",
}


def parse_manifest(text: str) -> tuple[dict[str, str], set[str]]:
    skills: dict[str, str] = {}
    mandatory: set[str] = set()
    current_id: str | None = None
    in_mandatory = False

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if stripped == "mandatory_for_every_task:":
            in_mandatory = True
            current_id = None
            continue
        if stripped == "skills:":
            in_mandatory = False
            continue
        if in_mandatory:
            match = re.fullmatch(r"-\s+(S\d{2})", stripped)
            if match:
                mandatory.add(match.group(1))
            continue
        match = re.fullmatch(r"-\s+id:\s+(S\d{2})", stripped)
        if match:
            current_id = match.group(1)
            if current_id in skills:
                raise ValueError(f"duplicate skill id {current_id}")
            skills[current_id] = ""
            continue
        if current_id:
            match = re.fullmatch(r"file:\s+(.+)", stripped)
            if match:
                skills[current_id] = match.group(1).strip()

    return skills, mandatory


def markdown_links(path: Path, text: str) -> list[Path]:
    results: list[Path] = []
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        results.append((path.parent / target).resolve())
    return results


def require_markers(path: Path, markers: list[str], errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"missing required file {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            errors.append(f"{path.relative_to(ROOT)} missing marker: {marker}")


def main() -> int:
    errors: list[str] = []

    if not MANIFEST.exists():
        print(f"ERROR: missing {MANIFEST.relative_to(ROOT)}")
        return 1

    try:
        skills, mandatory = parse_manifest(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot parse manifest: {exc}")
        return 1

    if set(skills) != REQUIRED_SKILLS:
        errors.append(
            f"manifest skill IDs differ: missing={sorted(REQUIRED_SKILLS - set(skills))}, "
            f"extra={sorted(set(skills) - REQUIRED_SKILLS)}"
        )

    expected_mandatory = {"S01", "S03", "S11", "S12", "S16"}
    if mandatory != expected_mandatory:
        errors.append(
            f"mandatory skills differ: expected={sorted(expected_mandatory)}, "
            f"observed={sorted(mandatory)}"
        )

    if not CROSS_CUTTING_SKILLS.issubset(skills):
        errors.append("manifest is missing one or more S01-S16 cross-cutting skills")
    if not WHOLE_PROJECT_SKILLS.issubset(skills):
        errors.append("manifest is missing one or more S17-S31 whole-project skills")

    for skill_id, relative in sorted(skills.items()):
        if not relative:
            errors.append(f"{skill_id} has no file in manifest")
            continue
        path = AGENT / relative
        if not path.is_file():
            errors.append(f"{skill_id} references missing file {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(S\d{2})\s+—", text, re.MULTILINE)
        if not title_match or title_match.group(1) != skill_id:
            errors.append(f"{path.relative_to(ROOT)} title does not match {skill_id}")
        missing_headings = sorted(heading for heading in REQUIRED_CARD_HEADINGS if heading not in text)
        if missing_headings:
            errors.append(f"{path.relative_to(ROOT)} missing headings {missing_headings}")

    for relative in sorted(MANDATORY_REFERENCES):
        if not (AGENT / relative).is_file():
            errors.append(f"missing required pack file docs/agent/{relative}")

    for path in sorted(AGENT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for target in markdown_links(path, text):
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)} links outside repository to {target}")
                continue
            if not target.exists():
                errors.append(f"{path.relative_to(ROOT)} has broken local link to {target.relative_to(ROOT)}")

    require_markers(
        AGENT / "README.md",
        [
            "S01–S16",
            "S17–S31",
            "PROJECT-COVERAGE-MATRIX.md",
            "Whole-project product and platform",
        ],
        errors,
    )
    require_markers(
        AGENT / "BOOTSTRAP-PROMPT.md",
        [
            "S01–S16",
            "S17–S31",
            "PROJECT-COVERAGE-MATRIX.md",
            "Affected modules/roles/environments",
        ],
        errors,
    )
    require_markers(
        AGENT / "master-operating-protocol.md",
        [
            "Whole-project skills S17-S31",
            "Affected modules/roles/environments",
            "support, training, rollout",
        ],
        errors,
    )
    require_markers(
        AGENT / "templates" / "task-context-pack.md",
        [
            "Whole-project impact map",
            "Whole-project S17–S31",
            "Support/training/change adoption",
            "Programme roadmap/release/rollout",
        ],
        errors,
    )
    require_markers(
        COVERAGE,
        [
            "Repository surface coverage",
            "NLI bounded-domain coverage",
            "Current platform module coverage",
            "User-role coverage",
            "Service lifecycle coverage",
            "National-readiness coverage",
            "Future-service extension rule",
        ],
        errors,
    )
    require_markers(
        ROOT / "AGENTS.md",
        [
            "docs/agent/PROJECT-COVERAGE-MATRIX.md",
            "S17 through S31",
            "affected modules/roles/environments",
        ],
        errors,
    )

    if errors:
        print(f"Skill-pack validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Skill-pack validation passed: "
        f"{len(skills)} skills "
        f"({len(CROSS_CUTTING_SKILLS)} cross-cutting, "
        f"{len(WHOLE_PROJECT_SKILLS)} whole-project), "
        f"{len(mandatory)} mandatory skills, "
        f"{len(list(AGENT.rglob('*.md')))} Markdown files."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
