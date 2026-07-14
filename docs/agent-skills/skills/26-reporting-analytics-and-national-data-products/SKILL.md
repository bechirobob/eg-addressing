# Skill 26 — Reporting, Analytics, and National Data Products

## Use when

Use for operational reports, dashboards, KPIs, data-quality measures, SLA views, national statistics, analytical extracts, maps, or de-identified/aggregated data products.

## Objective

Produce reproducible, governed, purpose-limited analytics that support operations and national planning without becoming an ungoverned second registry or exposing sensitive data.

## Procedure

1. Identify audience, decision/use case, metric owner, period, scope, classification, and refresh requirement.
2. Define every metric precisely:
   - name and purpose;
   - numerator/denominator;
   - inclusion/exclusion;
   - source entities/versions;
   - event/effective/recorded time;
   - territorial and institutional scope;
   - refresh and late-arriving behavior;
   - owner and review date.
3. Distinguish operational current-state reports, historical registry reconstruction, audit/compliance reports, and analytical/statistical products.
4. Build reproducible read models or extracts from authoritative sources with lineage, version, and freshness metadata.
5. Apply classification, minimization, aggregation, de-identification, suppression, and public/partner release rules.
6. Ensure analytics cannot mutate canonical state.
7. Define dimensional/geographic consistency and boundary-version handling.
8. Define correction/restatement behavior when source data or metric logic changes.
9. Provide accessible tables and meaningful charts; include underlying definitions and downloadable governed data where approved.
10. Test row/aggregate parity, scope isolation, historical reconstruction, late updates, null/unknown handling, boundary change, de-identification, and export controls.
11. Measure query cost, refresh duration, freshness, failed jobs, data-quality exceptions, and report usage.
12. Version data products, schemas, metric definitions, and release notes.

## Required evidence

- Metric/data-product dictionary
- Source lineage and transformation specification
- Classification and disclosure review
- Reproducible query/read-model tests
- Aggregate-to-source validation
- Historical/boundary-version behavior
- Scope and de-identification tests
- Dashboard accessibility and bilingual evidence
- Refresh/freshness/operations metrics
- Version/deprecation policy

## Stop and escalate when

- A metric has no accountable owner or stable definition.
- A public/partner data product could identify persons or restricted locations.
- An analytics database would become editable canonical state.
- Boundary or time semantics make comparisons misleading.
- A national statistic would be labelled official without institutional authority.

## Anti-patterns

- Building dashboards before defining metrics.
- Counting current rows as historical facts.
- Mixing pilot fixtures and operational records.
- Publishing precise sensitive locations through a map.
- Copying full registry data into BI without purpose/retention controls.
- Changing KPI logic silently.
- Treating a screenshot as analytical reproducibility evidence.
