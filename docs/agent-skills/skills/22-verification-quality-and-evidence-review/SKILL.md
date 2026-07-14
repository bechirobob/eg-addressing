# Skill 22 — Verification, Quality, and Evidence Review

## Use when

Use for evidence review, duplicate detection, quality scoring, discrepancy resolution, verification queues, recapture decisions, map/source comparison, or promotion recommendations.

## Objective

Convert observations and evidence into explainable, auditable review decisions without automatically treating algorithms, maps, citizen input, or field capture as canonical truth.

## Procedure

1. Identify the candidate/case, evidence types, source authority, reviewer role/scope, and target decision.
2. Define review dimensions:
   - identity/object match;
   - administrative context;
   - geometry/proximity/accuracy;
   - road/building/entrance relationships;
   - source/evidence completeness;
   - duplicate probability;
   - contradiction/dispute;
   - publication blockers.
3. Separate deterministic validation, quality signals, algorithmic recommendations, and authorized human decisions.
4. Record every signal with source, version, parameters, confidence, time, and explanation.
5. Define duplicate candidate generation, threshold, reviewer comparison, merge/link/reject outcome, and false-positive handling.
6. Define discrepancy categories and routing:
   - data correction;
   - field recapture;
   - GIS review;
   - authority/RFI;
   - suspected fraud/abuse;
   - publication hold.
7. Ensure promotion to canonical or registry-ready state requires explicit authorized decision and evidence lineage.
8. Define reviewer independence, self-review restrictions, escalation, appeal, and SLA.
9. Preserve rejected evidence and prior decisions according to retention/classification; do not silently delete or overwrite.
10. Provide case views with side-by-side evidence, map/text alternatives, timelines, and reasoned decision controls.
11. Test valid, invalid, incomplete, conflicting, duplicate, edge-distance, low-accuracy, map-outage, wrong-scope, and self-approval cases.
12. Monitor backlog, decision time, recapture rate, duplicate precision/recall, reviewer disagreement, overturned decisions, and data-quality trends.

## Required evidence

- Quality/verification rule registry
- Signal-versus-decision distinction
- Duplicate/discrepancy workflow
- Reviewer authority and segregation rules
- Positive/negative/boundary cases
- Reason/audit evidence
- Evidence lineage and retention behavior
- Queue/SLA and performance measures
- Algorithm/source versioning
- Appeal/overturn examples

## Stop and escalate when

- A quality threshold would become national policy without authority.
- An algorithm would auto-publish, auto-merge, or auto-reject high-impact records.
- Evidence source/licence/provenance is unknown.
- Reviewers cannot see why a recommendation was made.
- A dispute affects official geography or publication authority.

## Anti-patterns

- Treating a confidence score as an approval.
- Hiding duplicate evidence behind a single “match” badge.
- Deleting rejected evidence and losing the review trail.
- Using an external map as the deciding authority.
- Allowing the capturing user to be the sole approving user.
- Changing thresholds without versioning and impact analysis.
- Measuring only throughput while ignoring false decisions and recapture.
