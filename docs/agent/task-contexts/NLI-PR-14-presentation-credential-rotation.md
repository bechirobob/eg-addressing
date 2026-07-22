# Agent Task Context Pack — PR #14 Presentation Credential Rotation

**Repository:** `bechirobob/eg-addressing`  
**Base branch/SHA:** `nli/wo-003-operator-interface-foundation` / `515d90dc20583d10a5ac2ff532247087c7e3fd8a`  
**Task branch/SHA:** `preview/presentation-ready-2026-07-22` / pre-change `b6b8077e787dddf58df4e0f64a1626b1c8efe061`  
**PR/issue:** PR #14  
**Working tree:** controlled preview workflow change plus supporting records  
**Prepared at:** 2026-07-22

## 1. Authority

- Programme: Equatorial Guinea National Location Infrastructure.
- Programme Owner direction: rotate presentation credentials and provide links expected to remain stable for at least 48 hours.
- Active work order: NLI-WO-003 — Operator Interface and Navigation Foundation.
- Current SDA outcome/review: implementation head tested; SDA acceptance and deployment authority are not recorded by this task.
- Change class: credential rotation is Class C controlled presentation maintenance; persistent presentation hosting is Class B and blocked by RFI.
- Applicable ADRs: ADR-001 through ADR-004 are preserved; no architecture or publication decision changes.
- Mandatory standards: security, identity and access, testing and release, operations and disaster recovery, documentation and records.
- Readiness boundary: isolated development fixtures, protected presentation access, publication disabled, no production data, no pilot/production deployment claim.

## 2. Whole-project impact map

- Repository areas: `.github/workflows`, `docs/agent/task-contexts`, `docs/sda/rfis`.
- Bounded domains/modules: Identity and Trust; platform operations only.
- User roles: `admin`, `editor`, `viewer`, `agency_viewer` temporary presentation identities.
- Trust zones: GitHub-hosted runner, isolated Docker network, two external HTTPS quick tunnels.
- Environment: development-only presentation preview.
- External dependency: Cloudflare Quick Tunnels, already present in PR #14.
- Operational impact: old runner/tunnels terminate through concurrency cancellation; replacement credentials are independently generated and verified.

## 3. Selected skills

### Cross-cutting S01–S16

| Skill | Trigger | Required output |
|---|---|---|
| S01 | Every task and scope boundary | Authority and prohibited-path classification |
| S03 | Acceptance and RFI control | Result/evidence map and persistent-hosting blocker |
| S04 | New persistent external hosting decision | RFI-NLI-WO-003-001 |
| S08 | Credential and session effects | Positive/negative authentication evidence |
| S11 | Completion claims | Executed allow/deny checks |
| S12 | PR workflow and exact-head run | Remote SHA and workflow/job evidence |
| S14 | Preview-only security maintenance | Isolation from NLI-WO-003 application implementation |
| S15 | Runtime replacement and teardown | Handoff, failure boundary, cleanup |
| S16 | Submission and handoff | Self-audit and bounded completion statement |

### Whole-project S17–S31

| Skill | Trigger | Required output |
|---|---|---|
| S28 | Environment, secrets and ingress | Ephemeral secret generation, isolation, teardown |
| S29 | Availability request | Explicit Quick Tunnel limitation and persistent-host RFI |
| S30 | Ministry presentation access | Clear role/access handoff and limitation notice |

### Considered but not applicable

| Skill | Why not applicable |
|---|---|
| S06/S07 | No schema, migration, reference-data or fixture-package change |
| S09 | No geometry, evidence or publication behavior change |
| S10/S18 | No application UI, localization or design change |
| S19–S27 | No backend, citizen, registry, field, partner, worker or analytics behavior change |
| S31 | No programme release or national rollout authorization |

## 4. Scope matrix

### In scope

- Replace one shared preview password with four independently generated role credentials.
- Revoke bootstrap/previous preview sessions before public verification.
- Verify positive login and protected session for every role through both domains.
- Verify the former deterministic shared-password pattern and known defaults receive HTTP 401.
- Preserve publication locks and isolated development fixtures.

### Supporting evidence

- This task context pack.
- RFI-NLI-WO-003-001 for the requested 48-hour stable hostname.
- Exact-head GitHub workflow/job and access artifact.

### Separate maintenance

- Persistent named tunnel or staging-host implementation after explicit SDA/Security/Operations decision and access provisioning.

### Prohibited

- Production/pilot data, deployment, publication, signage, certificate or partner release.
- Application authentication/authorization contract or role changes.
- Secrets in source, logs, issue text or PR text.
- Claiming a Quick Tunnel URL has a 48-hour SLA.

## 5. Current-state evidence inspected

| Object | Source | What it establishes |
|---|---|---|
| PR #14 | GitHub PR metadata and diff | One workflow creates a five-hour isolated preview with shared credentials |
| Current run | GitHub run `29879774894`, job `88797851875` | Existing preview is live but time-limited |
| NLI-WO-003 | `docs/sda/work-orders/NLI-WO-003-operator-interface-foundation.md` | Deployment and external-service changes are outside the work order |
| Cloudflare guidance | Official Quick Tunnel documentation | Quick Tunnels have random URLs and no uptime SLA |

## 6. Acceptance-criterion plan

| AC | Observable result | Positive test | Negative test | Operational check | Evidence/RFI |
|---|---|---|---|---|---|
| CR-01 | Four roles have distinct runtime credentials | Login plus `/auth/me` for each role | Shared deterministic pattern and defaults return 401 | Old run cancelled by concurrency handoff | Exact-head workflow |
| CR-02 | Both public domains enforce the same credentials | Every role verified through primary and backup | Wrong/default credentials rejected on both | Heartbeat retains at least one domain | Exact-head workflow |
| CR-03 | Preview remains non-production | Health and login only use development fixtures | Publication flags remain false | Teardown always runs | Workflow diff and diagnostics |
| ST-01 | 48-hour link is not falsely claimed | N/A until host approved | Quick Tunnel cannot satisfy requirement | Stop persistent-hosting work | RFI-NLI-WO-003-001 |

## 7. Expected changed paths

### Add

- `docs/agent/task-contexts/NLI-PR-14-presentation-credential-rotation.md`
- `docs/sda/rfis/RFI-NLI-WO-003-001-stable-presentation-hosting.md`

### Modify

- `.github/workflows/operator-ui-cloudflare-reviewed-preview.yml`

### Remove/deprecate

- None.

## 8. Effect assessment

- API/contracts/roles: unchanged; only temporary fixture hashes differ per existing role.
- Security: stronger separation; credentials masked, bootstrap credential removed from final accounts, auth tokens cleared.
- Infrastructure: same isolated runner and two Quick Tunnels; no persistent host introduced.
- Resilience: dual tunnels and heartbeats remain; 48-hour stability remains blocked.
- Recovery: cancel/new-run handoff destroys the old runner, tunnel processes, database and sessions; rerun restores a clean environment.
- Support: access artifact lists the four role-specific credentials for controlled handoff.

## 9. Decisions and RFIs

| Decision | Classification | Owner | ADR/RFI | Blocking? |
|---|---|---|---|---|
| Persistent 48-hour presentation ingress and host | Class B infrastructure/external service | SDA, Security, Operations | RFI-NLI-WO-003-001 | Yes, for stable hostname only |

## 10. Execution sequence

1. Update credential generation, per-role hash rotation and allow/deny checks.
2. Validate workflow syntax and secret hygiene locally.
3. Push the bounded PR #14 update.
4. Observe the exact-head run through external role/session verification.
5. Download the controlled access artifact and hand credentials to the Programme Owner.
6. Stop at the persistent-hosting RFI until authority and provider access exist.

## 11. Recovery and compatibility

- Rollback safe: restore the prior workflow commit; no persistent data exists.
- Forward recovery: rerun from the corrected exact head.
- Compatibility: application code, API, schema and role names are unchanged.
- External effect: old quick tunnels stop when the new run cancels the old concurrency group.
- Rollout gate: do not call the preview stable for 48 hours without the approved persistent-host decision.

## 12. Submission plan

- Draft PR target: existing PR #14.
- Required workflow: `operator-ui-cloudflare-reviewed-preview` exact head.
- Required evidence: remote head equality; local and public allow/deny checks; access artifact; heartbeat status.
- Review request: credential-rotation review only; no deployment or production-readiness request.

## 13. Agent declaration

- [x] Authority and scope are explicit.
- [x] Whole-project impact is mapped.
- [x] Applicable skills are selected.
- [x] Positive and negative evidence is criterion-specific.
- [x] Persistent hosting is not silently introduced.
- [x] Publication, production and data boundaries remain prohibited.

