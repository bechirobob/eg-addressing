# S29 — Performance, Scalability, and Resilience

## Invoke when

- changing high-volume queries, caching, queues, concurrency, storage, or field sync;
- setting latency, throughput, capacity, availability, or national rollout assumptions;
- addressing external dependency failure, backpressure, or horizontal scaling.

## Required inputs

- representative data/workload profile;
- service objectives or unresolved RFI;
- database/query/index and worker/queue behavior;
- infrastructure/dependency topology;
- operational metrics, recovery, and rollout constraints.

## Procedure

1. Define records/events/evidence volumes, users/clients, read/write mix, spatial work, batch/export load, sync peaks, and retention.
2. State source, baseline date, confidence range, horizon, and owner for every assumption.
3. Identify critical paths and consistency/authority requirements.
4. Measure baseline behavior with representative distributions and complexity.
5. Inspect query plans, indexes, locks, connections, storage, and hot rows.
6. Use cache only for reconstructable data; define invalidation, staleness, privacy, and failure.
7. Define queue capacity, backpressure, retries, dead letters, concurrency, and maximum age.
8. Define horizontal scaling/statelessness and distributed rate/coordination controls.
9. Define graceful degradation for Redis, maps/geocoders, notifications, object storage, identity, and partner services.
10. Execute load, soak, spike, contention, failure-injection, resource-limit, and recovery tests.
11. Introduce partitioning/read models/tile services only at measured thresholds and with ADRs where required.
12. Monitor latency, errors, saturation, queue age, locks, slow queries, storage, cache staleness, sync backlog, and dependency health.

## Outputs

- workload/capacity model;
- SLO/target or RFI;
- load/soak/failure results;
- query/index/cache/queue rationale;
- scaling/degradation design;
- monitoring and rollout gates.

## Stop or RFI conditions

Stop when:

- national scale is claimed from tiny fixture data;
- objectives lack owner/measurement;
- cache could serve revoked/restricted/unpublished data;
- queue backlog is unbounded;
- scaling requires a new service/database without ADR;
- field/connectivity conditions are unknown but material.

## Evidence gate

Before review:

- assumptions and representative datasets are explicit;
- critical-path load and failure tests pass;
- query/index/cache/queue behavior is measured;
- dependency degradation preserves authoritative state;
- monitoring and rollout abort/capacity gates are defined.

## Anti-patterns

- Optimizing before measuring.
- Adding indexes without access-path evidence.
- Using average latency alone.
- In-memory rate limiting for multi-instance authority.
- Making Redis required for official writes.
- Partitioning every table before thresholds exist.
