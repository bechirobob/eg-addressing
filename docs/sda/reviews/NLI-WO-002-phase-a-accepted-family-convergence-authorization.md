# SDA Authorization — Accepted-Family Convergence

**Control:** `NLI-WO-002-PA-CONVERGENCE-01-AUTHORIZATION`  
**Reviewed mapping:** `1ff0f9ee53728c96291ce1e24de2cf2faf6ed9ba`  
**Outcome:** `ONE CONVERGENCE HARNESS AUTHORIZED`

Implement one design-harness command only:

```text
accepted-family-convergence
```

Use only the seven already accepted explicit callables. Do not implement or modify a transform group.

Reviewer control:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-accepted-family-convergence-control.json
Git blob: 3c4c59fa5eeb004cfb8ef2520241d74c130fa926
SHA-256: d714b32ea170e05b5feef240d587d860ed0c712812036f384e357381a60b3b8a
```

The convergence fixture must not pre-create any of the sixteen accepted-family owned rows or broad versions, aliases or relationships for the three accepted identities. Counts are scoped to the exact accepted-family owned union, not global table counts.

The point-observation crosswalk directly depends on both the addresses identity rows and the accepted point geometry observation.

Expected first family execution: 16 inserts. Expected second family execution: 0 inserts and 0 updates. Use live narrow specifications and never invoke the generic broad transformer. Compare the complete owned union through a separate read-only connection in both directions.

The report must remain free of raw citizen source values. Preserve every accepted oracle/control and the frozen broad specification.

This authorization does not accept broad Phase A, close F02/F14, authorize Review 12 or Phase B, authorize deployment/merge, or authorize another transform group.

Stop after exact-head evidence and request SDA convergence assessment.
