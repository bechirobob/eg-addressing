# S22 — Field Operations, Mobile, and Offline Synchronization

## Invoke when

- changing enumerator/supervisor assignments, devices, mobile capture, GPS, photos, or evidence;
- adding offline packages, local persistence, synchronization, recapture, or field productivity;
- changing field territorial scope or constrained-network behavior.

## Required inputs

- field roles, assignments, areas, devices, and scope model;
- canonical/evidence/GIS models;
- mobile/offline security and retention rules;
- synchronization API/job contracts;
- field connectivity, device, and operational assumptions.

## Procedure

1. Define role, team, device, assignment, geography, campaign, and effective period.
2. Define offline package content, version, hash, expiry, permissions, maps/reference data, and controlled vocabularies.
3. Use stable local/provisional IDs reconciled through explicit crosswalks; never use public codes as local primary keys.
4. Encrypt sensitive local data and protect device/session credentials.
5. Capture device/app/actor/assignment/time/GPS accuracy/method/evidence provenance.
6. Distinguish draft, saved locally, queued, syncing, synchronized, accepted for review, rejected, and recapture states.
7. Make synchronization idempotent, resumable, duplicate-safe, and ordered where required.
8. Define conflict rules for assignment/reference changes, concurrent edits, revoked users, duplicates, and expired packages.
9. Keep official workflow history in PostgreSQL; local stores and queues are transport only.
10. Support supervisor review, reassignment, recapture, escalation, and quality-aware productivity.
11. Test airplane mode, interruption, restart, clock skew, duplicate sync, partial evidence, revoked identity, expired assignment, low storage, and conflict.
12. Measure sync duration, retry/backlog, evidence size, GPS quality, battery/storage, recapture, and completion.

## Outputs

- offline state machine and package contract;
- local security/retention design;
- ID/crosswalk/idempotency/conflict rules;
- GPS/evidence provenance model;
- supervisor/recapture workflow;
- device/network/capacity evidence and runbooks.

## Stop or RFI conditions

Stop when:

- offline IDs could become public/canonical without reconciliation;
- assignment or territorial authority is unclear;
- sensitive evidence cannot be protected on-device;
- conflict policy would discard server state or unsynchronized evidence;
- map/package licensing or offline-use authority is unresolved.

## Evidence gate

Before review:

- interruption/restart/duplicate/partial/revocation tests pass;
- local versus synchronized versus accepted state is unambiguous;
- assignment scope and package expiry are enforced;
- evidence provenance and cleanup/retention are verified;
- field and supervisor workflows are evidenced on target devices/viewports.

## Anti-patterns

- Treating saved-on-device as submitted.
- Trusting device time or decimal precision as authority.
- Blindly retrying non-idempotent uploads.
- Keeping unlimited evidence indefinitely on devices.
- Allowing field users national data outside assignment scope.
- Measuring enumerators only by volume.
