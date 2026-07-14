# Lifecycle State Machines

All state values reference `controlled-vocabularies.md`. Each transition records actor/permission, authority, reason, evidence, effective time, recorded time, audit event, visibility, reversal rule, and invalid-transition behavior.

## Canonical record lifecycle

| From | Event | To | Actor/permission | Evidence/reason | Effective/recorded time | Public behavior | Reversal/appeal | Audit event |
|---|---|---|---|---|---|---|---|---|
| `draft-candidate` | registry review opened | `registry-review` | registry reviewer | intake/source record | effective now / recorded now | not public | cancel to rejected/closed | `decision_event` |
| `registry-review` | approve internal registry | `registry-ready` | registry authority | evidence bundle + validation | decision effective date / recorded now | internal only | correction/dispute | `registry-approved` |
| `registry-ready` | activate canonical record | `active` | registry authority | canonical version | effective from approved date / recorded now | still not public unless release exists | supersede/retire/dispute | `record-activated` |
| `active` | accepted correction | `corrected` -> new `active` version | correction authority | correction case | may be backdated with reason / recorded now | public snapshot unchanged until release | appeal/dispute | `correction-applied` |
| `active` | supersession approved | `superseded` | registry authority | successor link | effective date required / recorded now | old public alias redirects or warns per release policy | appeal | `record-superseded` |
| `active` | dispute opened | `disputed` | authorized operator/public correction channel | dispute case | effective now / recorded now | public release may suspend or show caution | resolve to previous/corrected/retired | `dispute-opened` |
| `active` | retirement approved | `retired` | registry authority | retirement reason | effective date required / recorded now | public retired/superseded behavior by release policy | reopen only by new decision | `record-retired` |

## Publication lifecycle

`not-public -> internal-registry -> release-requested -> release-approved -> publicly-released|partner-released -> suspended|withdrawn`. Release items snapshot exact `location_record_version_id`, `public_code_alias_id`, label, geometry policy, projection hash, effective_at, and recorded_at.

## Geometry lifecycle

`geometry_observation` is never approved geometry. `geometry_version` quality follows `unvalidated -> needs-review -> valid|valid-with-warning|rejected`, with `superseded` and `disputed` paths. One current geometry per `(subject_table, subject_id, geometry_role)` is enforced by a partial unique constraint in the draft SQL and later by triggers for subject integrity.

## Field verification lifecycle

`assigned -> in-progress -> field-captured -> evidence-under-review -> evidence-approved -> linked-to-canonical`; exception paths: `needs-recapture`, `evidence-rejected`, `cancelled`.

## Backdated decisions

Backdated effective times are allowed only with authority, reason, evidence, recorded_at preserved as the actual decision time, and publication snapshots left immutable. A backdated correction cannot rewrite old release items; it creates a new release or correction notice.
