# NLI Request for Information — RFI-NLI-WO-003-001

**Related work order:** NLI-WO-003 — Operator Interface and Navigation Foundation
**Raised by:** Implementation Agent
**Date:** 2026-07-22
**Required by:** Before provisioning a persistent presentation hostname or host
**Status:** OPEN

## 1. Decision question

Which approved non-production hosting boundary and ingress method may serve the audited operator-interface presentation for a continuous minimum of 48 hours?

## 2. Why this decision is required

NLI-WO-003 explicitly prohibits deployment and new external services. PR #14 currently uses Cloudflare Quick Tunnels on a GitHub-hosted runner. Those tunnels use random hostnames, exist only while the runner job is active and carry no uptime SLA. Extending them cannot truthfully provide a stable 48-hour URL.

The requested result therefore requires a Class B environment/ingress decision, named operational ownership and provider access. Guessing would bypass the work-order boundary and could expose a protected operator surface without approved secrets, monitoring, teardown or incident ownership.

## 3. Current evidence

- NLI-WO-003 scope and prohibited deployment/external-service clauses.
- PR #14 workflow and current run `29879774894`.
- Mandatory security, identity, testing/release and operations/DR standards.
- Official Cloudflare Quick Tunnel documentation stating that Quick Tunnels are testing-only, use random `trycloudflare.com` hostnames and have no uptime SLA.
- Application staging contract under `env/.env.staging.example` and Docker topology under `infra/docker/docker-compose.yml`.

## 4. Options considered

### Option A — Approved staging host with TLS ingress

- Behavior: deploy the exact audited presentation commit to an approved non-production server, use a controlled hostname and retain publication locks.
- Benefits: straightforward 48-hour continuity, restart policy, logs, health checks and controlled teardown.
- Risks/costs: requires an approved host, DNS/TLS, SSH or deployment identity, firewall rules, monitoring and accountable operations owner.
- Compatibility effect: no application contract change; environment configuration and deployment evidence required.
- Security/operations effect: preferred when an existing approved staging boundary exists; secrets remain outside source and operator access is auditable.

### Option B — Named Cloudflare Tunnel on an approved persistent connector

- Behavior: bind a stable hostname to the exact reviewed preview behind a named tunnel running on an approved persistent host.
- Benefits: stable bookmarkable URL and outbound-only origin connection.
- Risks/costs: requires a Cloudflare-managed zone/account, scoped tunnel token, persistent connector host, monitoring and provider ownership. A named hostname alone does not solve origin availability.
- Compatibility effect: no application contract change; ingress allowlist/configuration may require review.
- Security/operations effect: tunnel token must be stored as a secret, rotated after the event and paired with explicit shutdown.

### Option C — Continue Quick Tunnel refreshes

- Behavior: relaunch PR #14 every few hours and issue new URLs.
- Benefits: no additional account or host.
- Risks/costs: URLs change, sessions disappear, links cannot be bookmarked reliably and no 48-hour guarantee exists.
- Compatibility effect: none.
- Security/operations effect: acceptable only for short attended review; does not meet the Programme Owner's stated stability requirement.

## 5. Agent recommendation

Approve Option A when an existing controlled staging server is available. Otherwise approve Option B only with a persistent connector host and named security/operations owner. Reject Option C as the answer to the 48-hour requirement, while retaining it as the safe interim presentation mechanism.

## 6. Consequence of no decision

Credential rotation and a fresh short-lived dual-link preview may proceed. Persistent hosting, a stable hostname and any claim of 48-hour availability must stop. The operational risk of guessing is an unapproved protected-surface deployment with unmanaged credentials and no accountable recovery/teardown path.

## 7. Requested decision authority

`SDA | Security Authority | Operations Authority | Programme Owner`

## 8. Decision

**Decision:** Pending
**Rationale:**
**Conditions:**
**Affected standards/ADR/work order:**
**Decision date and authority:**

## 9. Implementation acknowledgment

- [ ] Plan updated.
- [ ] Acceptance-criterion map updated.
- [ ] New risks/conditions recorded.
- [ ] Separate hosting work order or explicit scope authorization issued.
