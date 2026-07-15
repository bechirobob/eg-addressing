# NLI-WO-002 Phase A Address Points Geometry Slice — C01-C07 Correction Context

**Reviewer-owned head synchronized:** `04110902f655102fc859a884477fd2a373065042`  
**Reviewed implementation head:** `eff62b263abb3f5ea2ab24675afc05449e97b5cb`  
**Assessment:** `docs/sda/reviews/NLI-WO-002-phase-a-address-points-geometry-assessment.md`  
**Correction oracle:** `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-correction-oracle.json`  
**Parent oracle:** `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-expected.json`

## Authority

`CORRECTION REQUIRED — SAME VERTICAL SLICE ONLY`.

Authorized work is strictly limited to C01-C07 for `WO002-R06-geometry-observation-address_points`.

## Immutable reviewer-owned controls

- Parent oracle SHA-256: `cf699de04e0ca500c3a7826f257e190d24835356ef96db1650160d7d438edaea`
- Correction oracle SHA-256: `12214d3967c6561eaa30c4577d9ab445a9b90d14b6d5c3374a842868e4e62bea`
- Neither oracle may be modified.

## Corrections implemented by this checkpoint

| Finding | Correction target |
|---|---|
| C01 | Preserve source coordinate precision through typed `ST_MakePoint(%s,%s)` numeric insertion. |
| C02 | Derive source key, source record, evidence object, geometry ID, exception ID, and exception source key from the queried source row. |
| C03 | Load and validate the reviewed transform-spec row before dispatch. |
| C04 | Compare through a separate read-only connection and query the complete source-attributable target set. |
| C05 | Mutate implementation longitude after source query, not the source row. |
| C06 | Mutate actual `current_source.address_points` for invalid-coordinate test. |
| C07 | Prove same-database rollback equality before any reset. |

## Explicitly out of scope

- Other 89 transform groups.
- Broad Phase A reassessment.
- SDA Review 12.
- F04-F12.
- Runtime app/frontend/API changes.
- Executable migrations or `infra/scripts/migrate.py`.
- Docker runtime configuration.
- Production/pilot data, secrets, `.env*`, or PR #8.

## Evidence artifact

The command `address-points-geometry-slice` writes:

`docs/sda/data-model/phase-a-address-points-geometry-slice-report.json`

This report is the checkpoint evidence for C01-C07 and the preserved original slice tests.
