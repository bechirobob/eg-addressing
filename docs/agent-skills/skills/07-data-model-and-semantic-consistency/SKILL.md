# Skill 07 — Data Model and Semantic Consistency

## Use when

Use for canonical entities, current-to-target mapping, identifiers, controlled vocabularies, lifecycle states, temporal history, classifications, physical-schema proposals, convergence planning, or model-validation tooling.

## Objective

Produce one coherent, authoritative model whose conceptual, logical, physical, API, mapping, scenario, and decision artifacts describe the same system.

## Procedure

1. **Inventory current state from reality.** Apply accepted migrations to disposable PostGIS and query `pg_catalog`. Inventory actual OpenAPI and code readers/writers where required.
2. **Declare one canonical authority.** Identify authoritative records, evidence/candidates, derived projections, and historical events. Eliminate competing canonical tables or explain convergence.
3. **Create authoritative typed metadata.** For every target field define:
   - meaning;
   - exact PostgreSQL type;
   - nullability/default;
   - PK/FK/relationship;
   - vocabulary;
   - authority owner;
   - classification;
   - projection eligibility;
   - temporal behavior;
   - constraints/index rationale.
4. **Model identifiers separately.** Internal identity, public aliases, external IDs, legacy IDs, provisional/offline IDs, and labels must not be conflated.
5. **Model lifecycle and temporal behavior.** Separate candidate, verification, canonical, geometry, correction/dispute, publication, and retirement states. Define effective and recorded time where required.
6. **Build a reviewed transformation registry.** Each source field/group must have:
   - stable source row keys;
   - exact source meaning;
   - target rows/fields;
   - crosswalk joins;
   - controlled-value mapping;
   - governed archive/exception behavior;
   - example input/output;
   - executable validation/no-loss test;
   - authority/RFI status.
7. **Generate or validate physical SQL.** Execute the non-runtime proposal in disposable PostGIS. Compare actual catalog to typed metadata field by field.
8. **Create real scenario fixtures.** Use distinct datasets for required urban, rural, multi-unit, no-road, correction, dispute, and boundary-change cases.
9. **Execute negative cases.** Cardinality, FK/subject, vocabulary, temporal overlap, chain cycle, geometry, publication, and lifecycle failures must actually fail.
10. **Validate cross-artifact parity.** Conceptual model, ERD, dictionary, vocabulary registry, lifecycle graph, field map, API projections, scenarios, ADRs, convergence plan, and SQL must agree.
11. **Build convergence only from accepted transformations.** Sequence identity, reference, candidate/evidence, canonical, geometry, publication, compatibility, and retirement work through explicit migration units.

## Semantic validation minimums

- Every current field has one explicit target/group/archive/exception/loss decision.
- Every target reference exists and type/nullability is compatible.
- Controlled maps use observed source values and valid target values.
- Every stateful field binds to exactly one vocabulary and graph.
- Every claimed constraint appears in typed metadata and physical validation.
- Scenario fixtures use valid fields/vocabularies and assert expected projections.
- Expected registries are independent from observed/generated outputs.

## Required evidence

- Live current catalog
- Typed target registry
- Field-complete mapping registry
- Executed target-schema catalog comparison
- Vocabulary/transition validation
- Scenario and negative results
- API projection impact
- Migration-unit plan
- ADR/RFI coverage

## Stop and escalate when

- Two concepts both claim canonical authority.
- A field’s meaning is uncertain.
- A public code or hierarchy decision needs institutional authority.
- A no-loss mapping can only preserve a hash.
- A future implementer would need to invent cardinality, temporal, or authority rules.

## Anti-patterns

- Inferring nullability/type/authority from field names.
- Mapping to any field that happens to exist.
- Converting unknown mappings into automatically approved exceptions.
- Using one generic lifecycle for unrelated entities.
- Keeping a code on both identity and effective-dated history.
- Reusing one generic fixture for every scenario.
- Reporting semantic PASS from counts, substrings, or file presence.
