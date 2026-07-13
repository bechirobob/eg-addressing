# Controlled Vocabularies

**Status:** Draft for SDA review

## 1. Vocabulary rules

- Controlled values use lowercase kebab-case.
- A value belongs to exactly one vocabulary.
- Runtime code must not create status strings ad hoc in future implementation work.
- Legacy values remain mapped during transition but are not automatically canonical.

## 2. Administrative unit status

| Value | Meaning |
|---|---|
| `proposed` | Not yet approved as reference geography. |
| `active` | Current approved unit. |
| `superseded` | Replaced by later unit/version. |
| `retired` | No longer current but preserved historically. |
| `disputed` | Under authority review. |

## 3. Operational area status

`draft`, `active`, `paused`, `completed`, `retired`.

## 4. Candidate/intake status

`submitted`, `under-review`, `needs-field-check`, `duplicate-review`, `rejected`, `promoted-to-canonical`, `closed`.

Current mappings:

| Current value | Target vocabulary/value |
|---|---|
| `submitted` | candidate/intake `submitted` |
| `under-review` | candidate/intake `under-review` |
| `needs-field-check` | candidate/intake `needs-field-check` |
| `retired-fixture` | fixture/testing state, not production vocabulary |

## 5. Field verification status

`assigned`, `in-progress`, `field-captured`, `evidence-under-review`, `evidence-approved`, `evidence-rejected`, `cancelled`.

## 6. Canonical lifecycle state

`draft-candidate`, `registry-review`, `registry-ready`, `active`, `corrected`, `superseded`, `retired`, `disputed`, `revoked`.

Current mappings:

| Current value | Target value | Note |
|---|---|---|
| `registry-ready` | `registry-ready` | Internal registry approval only. |
| `published` | publication state `publicly-released`, not canonical lifecycle. |
| `official` | verification/authority flag, not lifecycle. |
| `provisional` | evidence confidence/verification, not lifecycle. |

## 7. Publication state

`not-public`, `internal-registry`, `release-requested`, `release-approved`, `publicly-released`, `partner-released`, `suspended`, `withdrawn`.

Current mappings:

| Current value | Target value |
|---|---|
| `not-public` | `not-public` |
| `internal-registry` | `internal-registry` |
| `published` | `publicly-released` |
| `publication-approved` | event type producing `release-approved` |
| `publication-simulation` | simulation event only; no state change. |
| `ready-for-export` | projection/export readiness, not record state. |

## 8. Geometry quality state

`unvalidated`, `valid`, `valid-with-warning`, `needs-review`, `rejected`, `superseded`, `disputed`.

## 9. Name status

`candidate`, `under-review`, `official-current`, `official-historical`, `alternate`, `retired`, `rejected`, `disputed`.

## 10. Public code state

`reserved-internal`, `active-public`, `superseded`, `retired`, `revoked`, `blocked`.

## 11. Source authority class

`official-government`, `operator-confirmed`, `field-verified`, `citizen-submitted`, `imported-reference`, `external-map-suggestion`, `derived`, `test-fixture`.

## 12. Data classification

Use the platform security standard: `public`, `government-internal`, `restricted`, `highly-restricted`.
