# Skill 28 — Performance, Scalability, and Resilience

## Use when

Use for latency, throughput, capacity, query/index design, caching, queues, large datasets, concurrent users, field synchronization peaks, external dependency failure, or national scaling.

## Objective

Make performance and resilience measurable and evidence-based so the NLI can scale without weakening authority, consistency, security, or recoverability.

## Procedure

1. Define the workload and service tier:
   - record/event/evidence volumes;
   - public/operator/partner concurrency;
   - read/write mix;
   - spatial queries;
   - imports/exports;
   - field-sync peaks;
   - evidence size and retention;
   - latency/throughput/freshness objectives.
2. State assumptions, source, baseline date, confidence range, horizon, and owner.
3. Identify critical paths and authoritative consistency requirements.
4. Measure baseline behavior with representative data distributions and complexity.
5. Inspect database query plans, indexes, locks, connections, and storage growth.
6. Use caching only for reconstructable data; define invalidation, staleness, privacy, and failure behavior.
7. Define queue capacity, backpressure, retry, dead-letter, worker concurrency, and maximum age.
8. Define horizontal scaling and statelessness; remove per-process authority/rate state where multi-instance behavior matters.
9. Define graceful degradation for Redis, maps/geocoders, notifications, object storage, identity, and partner dependencies.
10. Add load, soak, spike, contention, failure-injection, resource-limit, and recovery tests.
11. Define partitioning/read-model/tile-service candidates only when measured thresholds justify them.
12. Monitor latency, errors, saturation, queue age, database locks, slow queries, storage, cache hit/staleness, sync backlog, and external dependency health.
13. Set abort/capacity gates for rollout waves and release changes.

## Required evidence

- Workload and capacity model
- SLO/target or unresolved RFI
- Representative dataset description
- Load/soak/spike results
- Query plans/index rationale
- Cache/queue/backpressure design
- Dependency failure tests
- Scaling and resource limits
- Monitoring/alert thresholds
- Capacity/rollout gate

## Stop and escalate when

- “National scale” is claimed from small fixture data.
- Availability/latency objectives have no owner or measurement rule.
- Caching could serve revoked, restricted, or unpublished data incorrectly.
- Queue backlog can grow without bound.
- Scaling requires a new database/service boundary without an ADR.
- Field/connectivity conditions are unknown but central to the design.

## Anti-patterns

- Optimizing before measuring.
- Adding indexes without query-path evidence.
- Treating average latency as sufficient.
- Using in-memory rate limiting in a multi-instance environment.
- Making Redis required for authoritative writes.
- Retrying external calls without timeout/backoff/circuit behavior.
- Partitioning every table “for scale” before thresholds exist.
