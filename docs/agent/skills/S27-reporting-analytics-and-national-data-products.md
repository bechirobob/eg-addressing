# S27 — Reporting, Analytics, and National Data Products

## Invoke when

- adding operational reports, dashboards, KPIs, data-quality or SLA measures;
- producing national statistics, analytical extracts, maps, or governed data products;
- changing metric logic, historical reporting, aggregation, or BI/read models.

## Required inputs

- metric/data-product purpose and owner;
- authoritative entity/event/time model;
- classification, privacy, release, and export rules;
- boundary/version and territorial semantics;
- current reporting queries, consumers, and operations.

## Procedure

1. Identify audience, decision/use case, metric owner, period, scope, classification, and refresh.
2. Define every metric: numerator, denominator, inclusion/exclusion, source versions/events, time semantics, geography, late-arriving behavior, and review date.
3. Separate operational current-state, historical reconstruction, audit/compliance, and analytical/statistical products.
4. Build reproducible read models/extracts with lineage, schema version, and freshness metadata.
5. Apply minimization, aggregation, de-identification, suppression, and release rules.
6. Ensure analytics cannot mutate canonical state.
7. Define boundary-version and correction/restatement behavior.
8. Provide accessible tables/charts with definitions and governed downloads where approved.
9. Test source-to-aggregate parity, scope isolation, historical reconstruction, late updates, null/unknown, boundary change, de-identification, and export controls.
10. Monitor refresh duration, freshness, failures, exceptions, query cost, and usage.
11. Version metric definitions, schemas, releases, and deprecation.

## Outputs

- metric/data-product dictionary;
- lineage and transformation specification;
- classification/disclosure decision;
- reproducible query/read model;
- dashboard/report and accessible evidence;
- refresh/operations/version policy.

## Stop or RFI conditions

Stop when:

- a metric lacks an owner or stable definition;
- a public/partner product could identify persons or restricted locations;
- analytics would become editable canonical state;
- boundary/time semantics make comparison misleading;
- a statistic would be called official without authority.

## Evidence gate

Before review:

- metric definitions and lineage are complete;
- aggregate parity and scope/privacy tests pass;
- historical/boundary/restatement behavior is verified;
- dashboards are accessible and bilingual where required;
- refresh, freshness, ownership, and release/version controls are operationally defined.

## Anti-patterns

- Building dashboards before defining metrics.
- Counting current rows as historical facts.
- Mixing fixtures with operational records.
- Publishing precise sensitive locations.
- Copying full registry data into BI without purpose/retention controls.
- Changing KPI logic silently.
