# Lifecycle State Machines

All transitions record `decision_event` or equivalent audit context with actor/permission/scope, authority, evidence/reason, effective time, recorded time, visibility, reversal/appeal behavior, and invalid-transition handling. Invalid transitions are rejected in service logic and surfaced as migration exceptions during WO-002B backfills.

## `intake_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|
| submitted | under-review | open review | registry reviewer | source_record | internal | close/reject/promote | Reject transition; log decision/migration exception |
| under-review | needs-field-check | requires field proof | registry reviewer | review note | internal | return to under-review | Reject transition; log decision/migration exception |
| needs-field-check | promoted-to-canonical | evidence accepted | registry authority | field_observation + decision_event | internal | correction/dispute | Reject transition; log decision/migration exception |
| under-review | rejected | invalid/duplicate | registry reviewer | reason | restricted | appeal via correction/dispute | Reject transition; log decision/migration exception |
| promoted-to-canonical | closed | case closed | system | location_record | internal | none | Reject transition; log decision/migration exception |

Vocabulary coverage for `intake_state`: `submitted`, `under-review`, `needs-field-check`, `duplicate-review`, `rejected`, `promoted-to-canonical`, `closed`. Values not shown as a `From` state are terminal, exception, or derived states handled by invalid-transition rejection and audit/exception records.

## `field_verification_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|
| assigned | in-progress | work started | field team | assignment | internal | cancel | Reject transition; log decision/migration exception |
| in-progress | field-captured | capture complete | field team | geometry/evidence | restricted | needs-recapture | Reject transition; log decision/migration exception |
| field-captured | evidence-under-review | submit review | supervisor | evidence | restricted | reject/approve | Reject transition; log decision/migration exception |
| evidence-under-review | evidence-approved | approve | supervisor | decision_event | internal | dispute | Reject transition; log decision/migration exception |
| evidence-approved | linked-to-canonical | promote/link | registry authority | location_record_assertion | internal | correction | Reject transition; log decision/migration exception |
| evidence-under-review | needs-recapture | quality fail | supervisor | quality reason | internal | recapture | Reject transition; log decision/migration exception |

Vocabulary coverage for `field_verification_state`: `assigned`, `in-progress`, `field-captured`, `evidence-under-review`, `evidence-approved`, `evidence-rejected`, `needs-recapture`, `linked-to-canonical`, `cancelled`. Values not shown as a `From` state are terminal, exception, or derived states handled by invalid-transition rejection and audit/exception records.

## `lifecycle_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|
| draft-candidate | registry-review | review opened | registry reviewer | source/evidence | internal | reject | Reject transition; log decision/migration exception |
| registry-review | registry-ready | approved internal | registry authority | decision_event | internal | correction/dispute | Reject transition; log decision/migration exception |
| registry-ready | active | activate | registry authority | effective version | internal unless release | supersede/retire | Reject transition; log decision/migration exception |
| active | disputed | dispute opened | authorized reporter/operator | dispute_case | public caution only if release policy allows | resolve | Reject transition; log decision/migration exception |
| active | superseded | successor approved | registry authority | relationship | public alias redirect/warning by release | none | Reject transition; log decision/migration exception |
| active | retired | retire | registry authority | reason | retired public behavior by release | new decision | Reject transition; log decision/migration exception |

Vocabulary coverage for `lifecycle_state`: `draft-candidate`, `registry-review`, `registry-ready`, `active`, `corrected`, `superseded`, `retired`, `disputed`, `revoked`. Values not shown as a `From` state are terminal, exception, or derived states handled by invalid-transition rejection and audit/exception records.

## `geometry_quality_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|
| observed | quality-checked | automated checks | GIS system | quality_assessment | restricted | reject/review | Reject transition; log decision/migration exception |
| quality-checked | reviewed | human review | GIS reviewer | evidence | restricted | reject | Reject transition; log decision/migration exception |
| reviewed | accepted-canonical | approve | GIS authority | decision_event | operator/public per release | dispute/supersede | Reject transition; log decision/migration exception |
| accepted-canonical | disputed | dispute | authorized actor | dispute_case | public caution/suspend | resolve | Reject transition; log decision/migration exception |
| accepted-canonical | superseded | new version | GIS authority | successor | historical only | none | Reject transition; log decision/migration exception |

Vocabulary coverage for `geometry_quality_state`: `observed`, `quality-checked`, `reviewed`, `accepted-canonical`, `valid-with-warning`, `rejected`, `disputed`, `superseded`. Values not shown as a `From` state are terminal, exception, or derived states handled by invalid-transition rejection and audit/exception records.

## `publication_release_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|
| draft | approval-requested | submit | publication preparer | manifest | internal | withdraw | Reject transition; log decision/migration exception |
| approval-requested | approved | approve | Publication Authority | authority_reference | internal | withdraw | Reject transition; log decision/migration exception |
| approved | published | publish | Publication Authority | immutable manifest | public/partner | suspend/withdraw | Reject transition; log decision/migration exception |
| published | suspended | suspend | Publication Authority | reason | hidden/caution | republish/withdraw | Reject transition; log decision/migration exception |
| published | withdrawn | withdraw | Publication Authority | reason | withdrawn | new release only | Reject transition; log decision/migration exception |

Vocabulary coverage for `publication_release_state`: `draft`, `approval-requested`, `approved`, `published`, `suspended`, `withdrawn`. Values not shown as a `From` state are terminal, exception, or derived states handled by invalid-transition rejection and audit/exception records.

## `case_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|
| submitted | under-review | triage | case reviewer | case | restricted | close/reject | Reject transition; log decision/migration exception |
| under-review | needs-evidence | evidence missing | case reviewer | reason | restricted | resume | Reject transition; log decision/migration exception |
| under-review | approved | approve | authority | decision_event | internal | resolve | Reject transition; log decision/migration exception |
| approved | resolved | apply outcome | system/authority | version/release | operator/public if released | closed | Reject transition; log decision/migration exception |
| under-review | rejected | reject | authority | reason | restricted | appeal | Reject transition; log decision/migration exception |
| resolved | closed | close | system | resolution | internal | none | Reject transition; log decision/migration exception |

Vocabulary coverage for `case_state`: `submitted`, `under-review`, `needs-evidence`, `approved`, `rejected`, `resolved`, `closed`. Values not shown as a `From` state are terminal, exception, or derived states handled by invalid-transition rejection and audit/exception records.

## `name_status` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|
| candidate | under-review | review | GIS/registry reviewer | source | internal | reject/approve | Reject transition; log decision/migration exception |
| under-review | official-current | approve | GIS/registry authority | decision_event | public after release | historical/retire | Reject transition; log decision/migration exception |
| official-current | official-historical | new name approved | GIS/registry authority | successor | history | none | Reject transition; log decision/migration exception |
| under-review | alternate | approve alternate | authority | source | public/internal per classification | retire | Reject transition; log decision/migration exception |
| under-review | rejected | reject | authority | reason | internal | resubmit | Reject transition; log decision/migration exception |

Vocabulary coverage for `name_status`: `candidate`, `under-review`, `official-current`, `official-historical`, `alternate`, `retired`, `rejected`, `disputed`. Values not shown as a `From` state are terminal, exception, or derived states handled by invalid-transition rejection and audit/exception records.
