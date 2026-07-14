# S23 — Verification, Quality, and Evidence Review

## Invoke when

- changing evidence review, duplicate detection, discrepancy resolution, quality scoring, or verification queues;
- adding recapture, human review, map/source comparison, or promotion recommendations;
- changing review thresholds, signals, explanations, or reviewer authority.

## Required inputs

- candidate/evidence/canonical model;
- source authority, GIS quality, and audit standards;
- reviewer role/scope/segregation rules;
- duplicate/discrepancy policies;
- current queues, thresholds, and operational measures.

## Procedure

1. Identify candidate/case, evidence types, source authority, reviewer scope, and target decision.
2. Define review dimensions: identity/object match, admin context, geometry/accuracy, road/building/access relationships, completeness, duplicates, contradiction, dispute, and publication blockers.
3. Separate deterministic validation, quality signals, algorithmic recommendations, and authorized human decisions.
4. Record every signal with source/version/parameters/confidence/time/explanation.
5. Define duplicate candidate generation, threshold, comparison, merge/link/reject outcomes, and false-positive handling.
6. Route discrepancies to correction, recapture, GIS review, RFI/authority, abuse investigation, or publication hold.
7. Require explicit authorized decision and evidence lineage before canonical or registry-ready promotion.
8. Define reviewer independence, self-review restrictions, escalation, appeal, and SLA.
9. Preserve rejected evidence and prior decisions according to retention; never silently overwrite/delete.
10. Test valid, invalid, incomplete, conflicting, duplicate, boundary-distance, low-accuracy, map-outage, wrong-scope, and self-approval cases.
11. Monitor backlog, decision time, recapture, duplicate precision/recall, disagreement, overturned decisions, and quality trends.

## Outputs

- quality/verification rule registry;
- signal-versus-decision model;
- duplicate/discrepancy workflows;
- reviewer authority and segregation matrix;
- evidence lineage/audit behavior;
- queue/SLA and quality metrics.

## Stop or RFI conditions

Stop when:

- a threshold would become national policy without authority;
- an algorithm would auto-publish, auto-merge, or auto-reject high-impact records;
- source/licence/provenance is unknown;
- reviewers cannot explain a recommendation;
- a dispute affects official geography or publication authority.

## Evidence gate

Before review:

- positive, negative, boundary, and self-approval cases execute;
- algorithmic signals are versioned and explainable;
- canonical promotion requires authorized decision/evidence;
- rejection/recapture/appeal history is preserved;
- quality and operational metrics are defined and reproducible.

## Anti-patterns

- Treating confidence as approval.
- Hiding duplicate evidence behind a single badge.
- Deleting rejected evidence.
- Using external maps as final authority.
- Allowing the capturing user to be sole approver.
- Changing thresholds without versioning and impact analysis.
