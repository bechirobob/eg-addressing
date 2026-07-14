# Skill 24 — Agency Integrations, Notifications, and Interoperability

## Use when

Use for partner agencies, utilities, postal/emergency/statistics clients, machine identities, scoped APIs, webhooks, event subscriptions, notifications, batch exchange, reconciliation, or integration support.

## Objective

Provide governed, versioned, purpose-limited interoperability without unrestricted database access, shared credentials, data overexposure, or untraceable downstream copies.

## Procedure

1. Identify partner institution, accountable owner, approved use case, purpose, audience, data classes, territory/data scope, environment, and service expectations.
2. Define machine identity and credential mechanism:
   - client ID/service identity;
   - scopes/permissions;
   - expiry/rotation/revocation;
   - production versus non-production separation;
   - stronger assurance such as mTLS or signed assertions where justified.
3. Define contract type:
   - synchronous API;
   - webhook/event subscription;
   - scheduled batch exchange;
   - controlled notification;
   - reconciliation/reporting feed.
4. Use explicit allowlisted projections and versioned schemas.
5. Define idempotency, replay protection, ordering, duplicate delivery, retry/backoff, dead-letter, and reconciliation.
6. Use durable committed events/outbox for official events; Redis or in-memory delivery is not the authoritative event record.
7. Define quotas, rate limits, concurrency, payload limits, support, availability, and suspension policy.
8. Define partner data retention, onward disclosure, deletion, breach/incident duties, and offboarding.
9. For notifications, distinguish informational communication from authoritative state. Record template/version, language, channel, recipient basis, delivery result, retry, and sensitive-content rules.
10. Define deprecation/change process, partner test environment, certification, and migration window.
11. Audit calls, downloads, event deliveries, credential operations, failures, and bulk data release.
12. Test wrong scope/institution, expired/revoked credentials, replay, duplicate, out-of-order, partner outage, webhook signature, retry exhaustion, reconciliation mismatch, schema compatibility, and data minimization.

## Required evidence

- Partner/use-case approval record
- Machine identity/scope matrix
- Versioned API/event/batch contract
- Public/internal/restricted projection definition
- Idempotency/replay/retry tests
- Quota/rate/size controls
- Webhook signing and rotation proof
- Reconciliation and offboarding behavior
- Notification templates/languages/delivery evidence
- Partner audit and incident obligations

## Stop and escalate when

- The partner purpose or authority is missing.
- Direct database access is requested.
- A partner needs unrestricted national data.
- Shared human credentials are proposed.
- An event could be lost because the queue is the only record.
- A notification would disclose restricted data or imply official publication incorrectly.

## Anti-patterns

- One API key shared across institutions or environments.
- Partner scope enforced only through documentation.
- Returning internal database models as partner contracts.
- Fire-and-forget webhooks with no signature or delivery history.
- Using notifications as the authoritative decision record.
- Breaking partner fields without deprecation and transition.
- Ignoring downstream correction/revocation reconciliation.
