# S26 — Import, Export, Worker, and Batch Processing

## Invoke when

- adding bulk imports, exports, generated reports/artifacts, scheduled jobs, queues, retries, or reconciliation;
- changing long-running geospatial/data work, notification delivery, or worker capacity;
- handling large files, batch validation, or asynchronous state.

## Required inputs

- owning domain/use case and authoritative database effects;
- import/export/job schemas and classification;
- worker/queue/object-storage architecture;
- idempotency, audit, retention, and operations standards;
- capacity and failure assumptions.

## Procedure

1. Define job purpose, actor/client, institution/scope, input, output, classification, and authoritative effects.
2. For imports, retain source file/hash/authority, stage before commit, map schema/version, validate references/vocabularies/duplicates/geometry, report row errors, and require explicit commit where applicable.
3. For exports, define purpose/approval, selection, projection, schema version, classification, count, expiry, manifest, and safe retrieval.
4. Create a durable job/request record before queue dispatch; the queue is not the official record.
5. Define idempotency key, attempts, progress, checkpoints, retry/backoff, dead letter, cancellation, and output.
6. Bound transaction size, locks, memory/storage, timeout, concurrency, and backpressure.
7. Make partial failure resumable and reconciliation explicit.
8. Protect files from formula injection, path/executable risks, sensitive error disclosure, and indefinite public access.
9. Audit input, actor, approvals, output access, commit, retry, cancellation, and failure.
10. Test duplicate dispatch, worker crash, queue outage, malformed/oversized file, partial batch, retry exhaustion, cancellation, expired download, formula injection, and reconciliation mismatch.
11. Monitor queue depth/age, duration, throughput, failures, retries, storage, output size, and exception backlog.

## Outputs

- import/export/job state model;
- input/output schema and manifest;
- staging/validation/commit workflow;
- idempotency/retry/checkpoint design;
- artifact access/expiry policy;
- capacity, monitoring, recovery, and audit evidence.

## Stop or RFI conditions

Stop when:

- import bypasses normal authority/validation;
- external effects occur before authoritative commit;
- queue state is the only official history;
- export lacks purpose, approval, classification, or expiry;
- a job cannot be made idempotent/resumable.

## Evidence gate

Before review:

- staging, validation, commit, retry, crash, partial, cancellation, and reconciliation cases execute;
- exports have governed manifests and safe expiry/access;
- source and output counts/hashes/relationships are verified;
- queue loss delays but does not lose official state;
- capacity and runbooks are documented.

## Anti-patterns

- Importing directly into canonical tables.
- Treating queued as completed.
- Blind retry of non-idempotent publication/export.
- Permanent public export URLs.
- One giant national-load transaction.
- Generating official artifacts from unpublished records.
