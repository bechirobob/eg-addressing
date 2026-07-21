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


## Final control correction C08-C11

**Reviewer-owned head synchronized:** `6739d736e9be134679b42069766f5f908f710377`
**Reviewed implementation head:** `64ad44b8553dcd0f18bd7dd41363230fb492862b`
**Assessment:** `docs/sda/reviews/NLI-WO-002-phase-a-address-points-geometry-assessment-02.md`
**Final correction oracle:** `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-final-correction-oracle.json`

Authorized work remains strictly limited to the same `WO002-R06-geometry-observation-address_points` vertical slice.

### Final controls

| Finding | Correction target |
|---|---|
| C08 | Transform output producer no longer reads any acceptance oracle; oracle access is gated to comparator/test authority blocks. |
| C09 | The reviewed transform-spec row now declares `required_context_fields` and `source_method_translation`; validator checks both actual spec values. |
| C10 | The address identity crosswalk is the reviewed address-level crosswalk `phase-a-crosswalk-addresses-id-to-location-record`; two address-point rows share exactly one address identity crosswalk. |
| C11 | Missing-source uses the common same-database rollback evidence path with measured pre/post rows and hashes. |

No other transform group, broad reassessment, SDA Review 12, F04-F12, runtime code, executable migration, Docker runtime config, production/pilot data, secrets, `.env*`, or PR #8 scope is authorized or changed.
