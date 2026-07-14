# Skill 21 — Field Operations, Mobile, and Offline Synchronization

## Use when

Use for enumerator/supervisor applications, assignments, devices, capture packages, GPS/photos/documents, offline storage, synchronization, recapture, conflict resolution, or field productivity.

## Objective

Support reliable field work under intermittent connectivity without losing evidence, duplicating official state, exceeding assignment scope, or confusing local capture with registry acceptance.

## Procedure

1. Define field roles, team, device, assignment, geography, campaign, and effective period.
2. Define the offline package:
   - assignment metadata;
   - reference/admin/road data;
   - forms and controlled vocabularies;
   - map/cache assets;
   - permissions and expiry;
   - package version/hash.
3. Use stable local/provisional identifiers that reconcile to canonical IDs through explicit crosswalks.
4. Encrypt sensitive local data and protect device/session credentials.
5. Capture source/provenance:
   - device and app version;
   - actor/team/assignment;
   - capture time and timezone;
   - coordinates and reported accuracy;
   - method and evidence metadata;
   - offline/online state.
6. Keep local states distinct:
   - draft;
   - saved locally;
   - queued;
   - synchronizing;
   - synchronized;
   - accepted for review;
   - rejected/needs recapture.
7. Make synchronization idempotent, resumable, ordered where necessary, and tolerant of duplicate delivery.
8. Define conflict rules for assignment changes, reference-data updates, concurrent edits, revoked credentials, duplicate captures, and expired packages.
9. Store official workflow history in PostgreSQL; queues/local storage are transport, not authority.
10. Support supervisor review, reassignment, recapture, escalation, and productivity evidence without incentivizing poor-quality capture.
11. Test airplane mode, network interruption, app restart, device clock skew, duplicate sync, partial upload, revoked user, expired assignment, low storage, large evidence, and server conflict.
12. Measure sync duration, retry/backlog, failure, battery/storage, GPS quality, and field completion.

## Required evidence

- Offline state machine
- Package schema/version/expiry/hash
- Local security and data-retention design
- Idempotency/crosswalk/conflict rules
- GPS/evidence provenance proof
- Intermittent-network and restart tests
- Duplicate/partial/retry tests
- Supervisor/recapture workflow evidence
- Device/field capacity assumptions
- Support/runbook and remote-wipe/revocation behavior where applicable

## Stop and escalate when

- Offline IDs could become public/canonical without reconciliation.
- Assignment or territorial authority is unclear.
- Sensitive evidence cannot be protected on the device.
- Conflict policy would discard either accepted server state or unsynchronized evidence.
- A proprietary map/package source has unresolved licensing or offline-use terms.

## Anti-patterns

- Treating “saved on device” as “submitted.”
- Reusing human-readable public codes as offline primary keys.
- Assuming device time or GPS precision is authoritative.
- Retrying non-idempotent uploads blindly.
- Keeping unlimited evidence indefinitely on devices.
- Allowing field users to download national data outside assignment scope.
- Measuring enumerators only by volume without quality and recapture context.
