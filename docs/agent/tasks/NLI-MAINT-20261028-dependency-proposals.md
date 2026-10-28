# NLI-MAINT-20261028 — Proposal-only dependency maintenance

**Version/status:** 1 / Proposed; local implementation, independent review pending.
**Owner:** implementation agent for repository maintainers; no SDA acceptance claimed.
**Prepared:** 2026-10-28. **Audience:** maintainers and technical reviewers.
**Repository/base:** bechirobob/eg-addressing, main `548f62c022caed0208ff7e7606cc6eb2e49aed4d`, tree `4eed53b0db66ad6e5f565685cf4d81ec260b172b`.
**Task branch:** `nli/maintenance-dependency-proposals-20261028`; initial head equals base.
**PR/remote/CI:** not submitted; no remote task branch or exact-head run asserted. Final implementation SHA belongs in subsequent PR evidence, not this self-referential record.

## 1. Authority

The owner explicitly approved a separate bundled maintenance task on 2026-10-28 at 02:45:05 UTC: weekly proposal-only dependency checks, with no upgrades, automatic merges, live deployments, credentials or permissions changes. The government feature hold remains in place.

This is separate maintenance, **not** implementation under active [NLI-WO-002](../../sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md). No work-order, ADR, review finding or SDA disposition is changed. [Testing and Release §2](../../sda/standards/testing-and-release.md) requires normal tests/review for Class C; [Charter §4](../../sda/charter.md) delegates reversible implementation details within existing boundaries.

**Effects-based Class C rationale:** only GitHub's existing repository-native proposal configuration changes. It asks for reviewable updates to existing dependency manifests and Actions; it neither installs dependencies nor changes workflow execution, merge/release gates, repository visibility, access, runtime contracts, authority or material operational dependencies. A future proposal is a separate change requiring its own classification, review and applicable tests. Stop and escalate if new permissions, external services, credentials, costs, gate changes or material dependency effects become necessary.

Readiness boundary: locally validated maintenance configuration only. SDA status **NOT REVIEWED**; no pilot, publication, production or feature-work authorization follows.

## 2. Whole-project impact map and current evidence

- Repository area: `.github/dependabot.yml`; supporting record under `docs/agent/tasks/`.
- Bounded domain: repository platform maintenance only; no NLI business-domain behavior.
- Modules: existing `apps/admin-portal/package.json` and lockfile, `services/api/requirements.txt`, `.github/workflows/*.yml` are read targets, not modified outputs.
- Roles/environment: repository maintainers reviewing proposals in existing GitHub visibility; no citizen, operator, field, agency, government institution or territorial/data scope changes.
- Trust/data: existing repository metadata/dependency manifests only; no runtime, personal, identity, location or evidence data. No secret/private-registry configuration.
- Writer-reader-authority: reviewed configuration controls GitHub proposal scheduling; maintainers read proposals and retain merge authority. Proposed versions are not accepted runtime authority.
- Lifecycle: maintenance discovery and review, not application release. Expected effect is bounded proposal/CI review workload, not a guaranteed speed or security improvement.
- Existing Actions remain unchanged: frontend-ci, api-ci and agent-skills-ci. No browser image/cache, installation command or application test pipeline is added.

## 3. Selected skills and required reading

Read root AGENTS, SDA README/charter, active NLI-WO-002 scope, referenced ADR-001–004 and applicable standards, plus agent README, master operating protocol, skill manifest and whole-project coverage matrix. Follow the task-context, exact-head and self-audit templates; this single record combines their applicable sections without replacing an authority record.

| Selected | Trigger and output |
|---|---|
| S01, S03 | Authority, separate scope and AC plan in §§1/4/5 |
| S02 | Exact repository impact and writer-reader boundary in §2 |
| S11 | Parsed configuration, executable forbidden mutations and limitations in §7 |
| S12 | Separate branch; truthful local state and later exact-head submission requirements |
| S14 | Isolation from design-only NLI-WO-002 and held government features |
| S15, S28 | Bounded repository configuration/maintenance effect; recovery and no deployment boundary |
| S16 | Self-audit and exact continuation below |
| S31 | Separate maintenance sequencing; no programme readiness or feature-status uplift |

Considered not applicable: S04 (no new reserved decision), S05–S10 (no schema/current-domain model, data, API/auth, GIS, publication or user workflow), S13 (not SDA-finding remediation), S17–S27 (no architecture, application, citizen, registry, field, verification, publication, agency, worker or analytics implementation), S29 (no runtime load/capacity change), S30 (no end-user training/adoption change). Repository maintainers need only the scheduling/recovery note here. Future dependency PRs must reroute skills by actual effects.

## 4. Scope matrix

- **In scope:** add `.github/dependabot.yml` with three exact existing targets.
- **Supporting evidence:** this task record and its reproducible local checks.
- **Separate maintenance:** this entire task is isolated from NLI-WO-002; no dependency on feature-work acceptance.
- **Prohibited:** manifests/lockfiles/requirements, workflows, source code, schema/migrations, accepted authority/review records, runtime data/configuration, credentials, roles, gates, visibility, deployment and automatic merge changes.

## 5. Acceptance-criterion plan (defined before configuration edits)

| AC | Observable result and implementation | Positive proof | Negative/boundary proof | Recovery/authority |
|---|---|---|---|---|
| AC1 | Exact npm `/apps/admin-portal` cap2, pip `/services/api` cap2 and github-actions `/` cap1; weekly Monday05:00 Africa/Accra | YAML parses to independently specified complete object; all time scalars explicitly quoted | Altered target, schedule or cap rejected; unquoted time rejected by raw serialization check | Owner's bounded proposal scope; revert config removes future schedule |
| AC2 | No upgrade, automerge, ignore suppression, registry secrets, added targets or permissions | Exact allowed-key/object comparison and Git changed-path check | Inject forbidden keys/additional target; validation must raise | Future PRs require review; existing dependencies/gates remain byte-identical |
| AC3 | Separate truthful maintenance record, reproducible evidence and normal review | Existing skill-pack/link validator and scope review | No submitted/accepted/runtime claim without evidence | Independent technical review and exact-head remote verification remain pending |

Expected policy comes from the explicit owner scope and this pre-edit plan, not a parser-derived copy of the observed configuration. Tests validate configuration semantics, not execution of GitHub's scheduler.

## 6. Execution, effects and recovery

Sequence: inspect authority/base → isolate branch → define ACs → add config/record → run focused checks → independent technical review → parent-owned remote submission/verification.

No architecture, database, API, identity, GIS, frontend/localization/accessibility, backend, citizen, registry, field, verification, publication, integration, worker, analytics, infrastructure topology, performance, backup or disaster-recovery behavior changes. No screenshots, database tests or application rebuild are warranted for these unchanged surfaces. No existing source is modified.

Recovery: revert/remove this configuration to stop future version-update scheduling; already opened proposal branches/PRs may remain and need normal review/closure. No database rollback, credentials rotation, service cutover or data restore is involved. Caps bound version-update PR backlog (not a universal security-update or compute quota). No automatic merge or dependency approval is configured. No notifications, subscriptions or external messages are sent by this local task; future normal GitHub proposal activity is the authorized effect.

## 7. Reproducible local evidence

Use the already installed PyYAML; no package installation or project dependency is added. From repository root:

```bash
python3 - <<'PY'
import copy
import re
from pathlib import Path
import yaml
schedule = dict(interval='weekly', day='monday', time='05:00', timezone='Africa/Accra')
expected = {'version': 2, 'updates': []}
for ecosystem, directory, cap in [('npm','/apps/admin-portal',2), ('pip','/services/api',2), ('github-actions','/',1)]:
    entry = {'package-ecosystem': ecosystem, 'directory': directory,
             'schedule': schedule.copy(), 'open-pull-requests-limit': cap}
    if ecosystem != 'github-actions':
        entry['groups'] = {'minor-and-patch': {'update-types': ['minor','patch']}}
    expected['updates'].append(entry)
def read_config(raw):
    assert re.findall(r'^\s*time:\s*(.*?)\s*$', raw, re.M) == ['"05:00"'] * 3, 'Schedule time must be quoted'
    return yaml.safe_load(raw)
raw = Path('.github/dependabot.yml').read_text()
actual = read_config(raw)
try: read_config(raw.replace('"05:00"', '05:00', 1))
except AssertionError as error: assert str(error) == 'Schedule time must be quoted'
else: raise AssertionError('Unquoted schedule accepted')
def verify(value):
    assert value == expected, 'Maintenance scope/policy differs'
verify(actual)
mutations = []
for key, value in [('registries', {'private': {}}), ('ignore', [{'dependency-name':'*'}]), ('auto-merge', True), ('permissions', {'contents':'write'})]:
    changed = copy.deepcopy(actual); changed['updates'][0][key] = value; mutations.append(changed)
for index in range(3):
    changed = copy.deepcopy(actual); changed['updates'][index]['directory'] = '/unapproved'; mutations.append(changed)
    changed = copy.deepcopy(actual); changed['updates'][index]['open-pull-requests-limit'] = 99; mutations.append(changed)
changed = copy.deepcopy(actual); changed['updates'].append(copy.deepcopy(actual['updates'][0])); mutations.append(changed)
changed = copy.deepcopy(actual); changed['updates'][0]['schedule']['interval'] = 'daily'; mutations.append(changed)
for changed in mutations:
    try: verify(changed)
    except AssertionError as error: assert str(error) == 'Maintenance scope/policy differs'
    else: raise AssertionError('Forbidden configuration accepted')
print('PASS: exact policy, quoted serialization, and 13 executed forbidden mutations')
PY
python3 docs/agent/scripts/validate_skill_pack.py
git diff --check
```

Observed on 2026-10-28 with Python3.12.14/PyYAML6.0.3: exact parsed policy, explicitly quoted time serialization and all13 forbidden mutations passed; existing skill validator passed31skills/5mandatory/72Markdownfiles; Git scope check confirmed exactly two added files and every baseline tracked byte unchanged. Initial Markdown hard-break whitespace was removed; final staged diff-check passed. AC1 and AC2 have local static proof; AC3 local records/link checks passed, while independent review and hosted exact-head evidence remain pending. These checks do not demonstrate a scheduled Dependabot run, proposal creation, vulnerability remediation, or exact-head hosted CI. No new update is installed. A future reviewer must inspect the actual two-file diff and existing rules rather than infer approval from a green validator.

## 8. Submission plan and self-audit

Normal independent technical review is pending. Parent owns publication and exact-head reconciliation; this worker is local-only. A subsequent draft PR must name this maintenance ID, changed paths, AC results, skills, base and exact implementation SHA, actual workflow/job IDs and skipped checks with reasons. `agent-skills-ci` applies because this record is under `docs/agent/`; app CI applicability must be inspected from actual triggers without duplicate dispatch. No SDA status may be self-promoted.

Self-audit: authority/feature hold separated; all31 skills considered by effects; expected policy independent; no accepted review record changed; no secrets/personal data; no runtime/data effect or readiness claim; rollback and residual workload disclosed. Submission, exact-head CI and independent review are deliberately **pending**, not passed. Database/API/GIS/UI/migration/DR evidence is not applicable to the unchanged runtime. No RFI is presently required for the bounded Class C effect; escalate if scope changes.

Implementation/model status: IMPLEMENTED LOCALLY.
Verification status and exact SHA: LOCAL ONLY; base identified above; final implementation SHA not yet created.
Remote submission status: NOT PUSHED.
SDA status: NOT REVIEWED; no acceptance requested or claimed by this record.
Open findings/RFIs: independent technical review and remote verification pending.
Separate maintenance dependencies: none; no feature-work dependency.
Affected modules/roles/environments: repository proposal configuration / maintainers / existing GitHub repository only.
Operational/training/rollout status: no app rollout or end-user training; configuration activation and scheduler behavior unverified.
Readiness boundary: local maintenance source and focused checks only.
Exact next action: independent review, then parent-owned draft publication and exact-head verification within the owner's approved bundle.
