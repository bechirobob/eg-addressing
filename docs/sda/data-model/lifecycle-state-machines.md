# Lifecycle State Machines

**Status:** Draft for SDA review

## 1. Candidate / intake case

| From | Event | To | Required authority/evidence |
|---|---|---|---|
| — | citizen/operator submits | `submitted` | Submission payload, source, timestamp. |
| `submitted` | reviewer starts review | `under-review` | Operator actor. |
| `under-review` | field evidence needed | `needs-field-check` | Reason recorded. |
| `needs-field-check` | field task assigned | `under-review` | Field assignment/evidence link. |
| `under-review` | duplicate suspected | `duplicate-review` | Duplicate evidence. |
| `duplicate-review` | merge/close decision | `closed` | Resolution event. |
| `under-review` | reject | `rejected` | Reviewer note. |
| `under-review` | promote | `promoted-to-canonical` | Canonical approval event. |

## 2. Field verification

`assigned -> in-progress -> field-captured -> evidence-under-review -> evidence-approved -> linked-to-canonical`

Failure paths: `evidence-rejected`, `cancelled`, `needs-recapture`.

## 3. Canonical location record

| From | Event | To |
|---|---|---|
| `draft-candidate` | registry approval | `registry-ready` |
| `registry-ready` | activated internally | `active` |
| `active` | correction accepted | `corrected` then new `active` version |
| `active` | supersession approved | `superseded` |
| `active` | dispute opened | `disputed` |
| `disputed` | dispute resolved | previous valid state or `corrected` |
| `active` | retirement approved | `retired` |
| any non-final | authority revokes | `revoked` |

## 4. Publication

| From | Event | To | Notes |
|---|---|---|---|
| `not-public` | internal registry approval | `internal-registry` | No public exposure. |
| `internal-registry` | release requested | `release-requested` | Approval package opened. |
| `release-requested` | authority approves | `release-approved` | Authority reference required. |
| `release-approved` | release effective | `publicly-released` | Public lookup/certificate/signage/partner projections allowed per release item. |
| `publicly-released` | suspend | `suspended` | Public projection blocked or marked. |
| `publicly-released` | withdraw | `withdrawn` | Public release terminated but history retained. |

## 5. Geometry quality

`unvalidated -> valid | valid-with-warning | needs-review | rejected`. Current geometry can only be canonical if quality is `valid` or accepted `valid-with-warning` with authority note.

## 6. Correction/dispute case

`submitted -> triaged -> under-review -> accepted | rejected | needs-field-check -> resolved`.

Accepted correction creates a new canonical version and an event linking old/new values.

## 7. Road/name approval

Road geometry and road name approval are separate. A road segment may be geometrically valid while its name remains candidate or disputed.

## 8. Administrative geography

Administrative geography changes are versioned, not overwritten: `proposed -> active -> superseded/retired/disputed`. Boundary changes create a new boundary version with effective dates.
