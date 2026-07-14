# Skill 25 — Import, Export, Worker, and Batch Processing

## Use when

Use for bulk imports, exports, reports/artifacts, background jobs, queues, retries, reconciliation, scheduled work, large geospatial processing, or notification delivery.

## Objective

Process high-volume and asynchronous work safely, idempotently, observably, and without making queues or generated files a second source of truth.

## Procedure

1. Define job purpose, owner domain, actor/client, institution/scope, classification, input, output, and authoritative database effects.
2. For imports:
   - retain original source file/hash/source authority;
   - stage before commit;
   - define schema/version/mapping;
   - validate types, controlled values, references, duplicates, geometry, authority, and row limits;
   - produce row-level errors and summary;
   - require explicit commit/approval where applicable.
3. For exports:
   - define purpose, approval, selection, projection, schema version, classification, count, expiry, and manifest;
   - protect identifiers and spreadsheet/CSV formula injection;
   - use short-lived scoped retrieval.
4. For worker jobs:
   - create durable authoritative job/request record before queue dispatch;
   - use idempotency key and deterministic retry semantics;
   - record attempts, progress, checkpoint, output, failure, cancellation, and dead-letter state;
   - ensure queue loss delays work but does not erase official state.
5. Define batching, transaction size, locking, memory/storage limits, timeout, cancellation, and backpressure.
6. Define partial failure and restart behavior; large jobs must be resumable.
7. Reconcile external or generated effects against authoritative state.
8. Audit input, actor, approvals, output access, commit, cancellation, and failure.
9. Test duplicate dispatch, worker crash, queue outage, retry exhaustion, partial batch, malformed file, oversized payload, formula injection, expired download, cancellation, and reconciliation mismatch.
10. Measure queue depth/age, throughput, failure/retry, processing duration, artifact size, storage growth, and exception backlog.

## Required evidence

- Import/export/job state model
- Input/output schemas and manifests
- Staging/validation/commit workflow
- Idempotency/retry/checkpoint tests
- Queue-loss and worker-crash behavior
- Partial/restart/cancel tests
- Formula injection and file-safety tests
- Artifact access/expiry audit
- Capacity and operational metrics
- Reconciliation result

## Stop and escalate when

- A bulk import would bypass normal authority or validation.
- A job can produce external effects before authoritative commit.
- A queue is the only record of an official action.
- A large export lacks purpose, approval, classification, or expiry.
- A job cannot be made idempotent or safely resumable.

## Anti-patterns

- Writing import rows directly into canonical tables without staging.
- Treating `queued` as completed.
- Retrying a non-idempotent publication/export job blindly.
- Storing large export files indefinitely with public URLs.
- Returning raw import exceptions containing sensitive data.
- One huge transaction for a national data load.
- Generating official artifacts from unaccepted or unpublished records.
