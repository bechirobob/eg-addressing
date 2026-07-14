# Lifecycle State Machines

Each lifecycle is separate. Every transition records actor/permission/scope, authority, evidence, effective time, recorded time, audit event, visibility, reversal/appeal, and invalid-transition behavior.

## `canonical_record_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | under-review | advance-candidate-to-under-review | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| under-review | active | advance-under-review-to-active | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| active | corrected | advance-active-to-corrected | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| corrected | superseded | advance-corrected-to-superseded | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| superseded | disputed | advance-superseded-to-disputed | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| disputed | retired | advance-disputed-to-retired | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| retired | revoked | advance-retired-to-revoked | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| revoked | <terminal or authority-reopened> | reopen/appeal only when listed by owner | Registry Authority | decision_event required | new interval/version | operator | appeal path explicit | reject |

## `reference_object_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | active | advance-candidate-to-active | Registry/GIS Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| active | corrected | advance-active-to-corrected | Registry/GIS Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| corrected | superseded | advance-corrected-to-superseded | Registry/GIS Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| superseded | retired | advance-superseded-to-retired | Registry/GIS Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| retired | revoked | advance-retired-to-revoked | Registry/GIS Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| revoked | <terminal or authority-reopened> | reopen/appeal only when listed by owner | Registry/GIS Authority | decision_event required | new interval/version | operator | appeal path explicit | reject |

## `operational_area_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| planned | active | advance-planned-to-active | Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| active | suspended | advance-active-to-suspended | Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| suspended | closed | advance-suspended-to-closed | Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| closed | archived | advance-closed-to-archived | Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| archived | <terminal or authority-reopened> | reopen/appeal only when listed by owner | Operations Authority | decision_event required | new interval/version | operator | appeal path explicit | reject |

## `source_authority_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | trusted | advance-candidate-to-trusted | SDA | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| trusted | deprecated | advance-trusted-to-deprecated | SDA | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| deprecated | revoked | advance-deprecated-to-revoked | SDA | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| revoked | <terminal or authority-reopened> | reopen/appeal only when listed by owner | SDA | decision_event required | new interval/version | operator | appeal path explicit | reject |

## `name_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | official-current | advance-candidate-to-official-current | Registry/GIS Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| official-current | official-historical | advance-official-current-to-official-historical | Registry/GIS Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| official-historical | alternate | advance-official-historical-to-alternate | Registry/GIS Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| alternate | disputed | advance-alternate-to-disputed | Registry/GIS Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| disputed | retired | advance-disputed-to-retired | Registry/GIS Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| retired | rejected | advance-retired-to-rejected | Registry/GIS Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| rejected | <terminal or authority-reopened> | reopen/appeal only when listed by owner | Registry/GIS Authority | decision_event required | new interval/version | operator | appeal path explicit | reject |

## `case_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| submitted | under-review | advance-submitted-to-under-review | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| under-review | needs-evidence | advance-under-review-to-needs-evidence | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| needs-evidence | approved | advance-needs-evidence-to-approved | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| approved | rejected | advance-approved-to-rejected | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| rejected | resolved | advance-rejected-to-resolved | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| resolved | closed | advance-resolved-to-closed | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| closed | <terminal or authority-reopened> | reopen/appeal only when listed by owner | Registry Authority | decision_event required | new interval/version | operator | appeal path explicit | reject |

## `geometry_quality_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| accepted-canonical | disputed | advance-accepted-canonical-to-disputed | GIS/Data Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| disputed | observed | advance-disputed-to-observed | GIS/Data Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| observed | quality-checked | advance-observed-to-quality-checked | GIS/Data Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| quality-checked | rejected | advance-quality-checked-to-rejected | GIS/Data Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| rejected | reviewed | advance-rejected-to-reviewed | GIS/Data Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| reviewed | superseded | advance-reviewed-to-superseded | GIS/Data Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| superseded | valid-with-warning | advance-superseded-to-valid-with-warning | GIS/Data Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| valid-with-warning | <terminal or authority-reopened> | reopen/appeal only when listed by owner | GIS/Data Authority | decision_event required | new interval/version | operator | appeal path explicit | reject |

## `publication_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| approval-requested | approved | advance-approval-requested-to-approved | Publication Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| approved | draft | advance-approved-to-draft | Publication Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| draft | published | advance-draft-to-published | Publication Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| published | suspended | advance-published-to-suspended | Publication Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| suspended | withdrawn | advance-suspended-to-withdrawn | Publication Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| withdrawn | <terminal or authority-reopened> | reopen/appeal only when listed by owner | Publication Authority | decision_event required | new interval/version | operator | appeal path explicit | reject |

## `intake_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| closed | duplicate-review | advance-closed-to-duplicate-review | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| duplicate-review | needs-field-check | advance-duplicate-review-to-needs-field-check | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| needs-field-check | promoted-to-canonical | advance-needs-field-check-to-promoted-to-canonical | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| promoted-to-canonical | rejected | advance-promoted-to-canonical-to-rejected | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| rejected | submitted | advance-rejected-to-submitted | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| submitted | under-review | advance-submitted-to-under-review | Registry Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| under-review | <terminal or authority-reopened> | reopen/appeal only when listed by owner | Registry Authority | decision_event required | new interval/version | operator | appeal path explicit | reject |

## `field_verification_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| assigned | cancelled | advance-assigned-to-cancelled | Field Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| cancelled | evidence-approved | advance-cancelled-to-evidence-approved | Field Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| evidence-approved | evidence-rejected | advance-evidence-approved-to-evidence-rejected | Field Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| evidence-rejected | evidence-under-review | advance-evidence-rejected-to-evidence-under-review | Field Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| evidence-under-review | field-captured | advance-evidence-under-review-to-field-captured | Field Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| field-captured | in-progress | advance-field-captured-to-in-progress | Field Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| in-progress | linked-to-canonical | advance-in-progress-to-linked-to-canonical | Field Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| linked-to-canonical | needs-recapture | advance-linked-to-canonical-to-needs-recapture | Field Operations Authority | decision_event + evidence_record | record effective_from/effective_to and recorded_at | operator unless public release | appeal creates case/correction | reject; migration_exception |
| needs-recapture | <terminal or authority-reopened> | reopen/appeal only when listed by owner | Field Operations Authority | decision_event required | new interval/version | operator | appeal path explicit | reject |
