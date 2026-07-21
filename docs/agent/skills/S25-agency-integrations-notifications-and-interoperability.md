# S25 — Agency Integrations, Notifications, and Interoperability

## Invoke when

- onboarding agencies, utilities, postal, emergency, statistics, or other partners;
- adding machine identities, partner APIs, webhooks, event subscriptions, notifications, or batch exchange;
- changing reconciliation, quotas, partner support, or contract versioning.

## Required inputs

- partner institution/use-case approval;
- identity, API, security, audit, and data-classification standards;
- authoritative source/projection model;
- service expectations, retention, incident, and offboarding obligations;
- current integration and worker capabilities.

## Procedure

1. Identify institution, accountable owner, approved purpose, audience, data classes, scope, environment, and service expectations.
2. Define machine identity, credentials, endpoint/data scopes, expiry, rotation, revocation, and environment separation.
3. Select contract type: synchronous API, webhook/event, scheduled batch, notification, or reconciliation feed.
4. Use explicit allowlisted projections and versioned schemas.
5. Define idempotency, replay, ordering, duplicate delivery, retry/backoff, dead-letter, and reconciliation.
6. Use durable committed events/outbox for official events; queues are transport only.
7. Define quotas, rate/concurrency/payload limits, support, monitoring, and suspension.
8. Define partner retention, onward disclosure, deletion, incident duties, correction/revocation handling, and offboarding.
9. For notifications, record template/version, language, recipient basis, channel, delivery result, retry, and sensitive-content rules; notifications are not authority records.
10. Define contract deprecation, test/certification environment, migration window, and partner communication.
11. Test wrong scope/institution, expired credentials, replay, duplicate/out-of-order, outage, signature, retry exhaustion, reconciliation mismatch, schema compatibility, and data minimization.

## Outputs

- partner/use-case record;
- machine identity/scope matrix;
- versioned API/event/batch contracts;
- webhook/notification/retry design;
- quota, reconciliation, incident, and offboarding rules;
- partner audit and certification evidence.

## Stop or RFI conditions

Stop when:

- partner purpose or authority is missing;
- direct database access or unrestricted national data is requested;
- shared human credentials are proposed;
- the queue/webhook is the only record of an official event;
- notification content would expose restricted data or imply publication.

## Evidence gate

Before review:

- service credentials/scopes/rotation and production separation are proven;
- retry/replay/idempotency/signature tests pass;
- projections are purpose-limited and audited;
- reconciliation, correction/revocation, outage, and offboarding behavior execute;
- partner contract/version/support responsibilities are recorded.

## Anti-patterns

- One API key shared across institutions or environments.
- Partner scope enforced only in documentation.
- Returning internal database models as partner contracts.
- Fire-and-forget unsigned webhooks.
- Using notifications as the authoritative decision record.
- Ignoring downstream corrections or revocations.
