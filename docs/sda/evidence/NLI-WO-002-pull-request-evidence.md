# Pull Request Evidence — NLI-WO-002 Review 02 Remediation

**PR:** `#7`  
**Branch:** `nli/wo-002-canonical-location-model`  
**Final head:** Exact final head is recorded in PR #7 body and SDA Review 03 request comment after push.  
**Status:** Draft; request SDA Review 03 after final-head workflows are green.

## Acceptance criteria

| Criterion | Agent status | Exact evidence | Validation | Remaining condition |
|---|---|---|---|---|
| AC-01 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-02 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-03 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-04 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-05 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-06 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-07 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-08 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-09 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-10 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-11 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-12 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-13 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-14 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-15 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-16 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-17 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-18 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-19 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-20 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-21 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |
| AC-22 | READY FOR SDA REVIEW | See `docs/sda/data-model/README.md` criterion row with exact artifact | Semantic design checker + final-head CI | SDA Review 03 pending |

## Local validation

- `python3 docs/sda/data-model/scripts/generate_design_catalog.py`
- `python3 docs/sda/data-model/scripts/design_consistency_check.py`
- `git diff --exit-code docs/sda/data-model docs/sda/adrs docs/sda/rfis docs/sda/evidence docs/sda/implementation-plans docs/sda/reviews` after regeneration

## No-runtime-change boundary

Forbidden paths for this work order: `services/api/**`, `infra/migrations/**`, `apps/**`, `infra/docker/**`, `data/**`, `.env*`. The only non-`docs/sda/**` change allowed in this remediation is GitHub CI configuration to run the design checker.
