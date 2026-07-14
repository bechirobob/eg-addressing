# Implementation Plan — NLI-WO-002 Review 02 Remediation

**Work order:** `NLI-WO-002`  
**Implementation branch:** `nli/wo-002-canonical-location-model`  
**Planning commit:** `cdd50293a301048ce820b2b1841687afd1d3eb0d`  
**Prepared by:** `Implementation Agent`  
**Status:** `REVISED`

## Objective understood

Resolve SDA Review 02 findings F01-F12 by replacing heuristic generation with typed authoritative metadata and semantic validation. Runtime code and executable migrations remain unchanged.

## Acceptance-criterion map

See `docs/sda/data-model/README.md` for the AC-01 through AC-22 matrix.

## Test plan

1. Regenerate design pack with `python3 docs/sda/data-model/scripts/generate_design_catalog.py`.
2. Run semantic checker with `python3 docs/sda/data-model/scripts/design_consistency_check.py`.
3. Verify regeneration leaves no unexplained diff.
4. Verify PR #7 final-head API/frontend workflows are green and PR remains draft.
