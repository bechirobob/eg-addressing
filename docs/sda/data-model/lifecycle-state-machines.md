# Lifecycle State Machines

Transitions are hand-authored. No transition is inferred from vocabulary order. Every transition records actor/permission/scope, authority, evidence, effective time, recorded time, audit event, visibility, reversal/appeal, and invalid-transition behavior.

## `canonical_record_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | under-review | submit-candidate | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| under-review | active | approve-canonical | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| under-review | disputed | open-dispute | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | corrected | approve-correction | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | superseded | approve-supersession | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | disputed | open-dispute | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| disputed | active | resolve-dispute-retain | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| disputed | corrected | resolve-dispute-correct | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | retired | retire-record | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| candidate | revoked | reject-candidate | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: corrected, retired, revoked, superseded.

## `reference_object_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | active | approve-reference | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| candidate | revoked | reject-reference | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | corrected | approve-correction | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | superseded | replace-reference | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | retired | retire-reference | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: corrected, retired, revoked, superseded.

## `administrative_unit_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| proposed | official | approve-administrative-version | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| official | historical | replace-by-new-official-version | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| official | retired | retire-administrative-unit | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| proposed | revoked | reject-proposal | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: historical, retired, revoked.

## `road_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | field-verified | field-verify-road | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| field-verified | official | approve-road | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| official | superseded | replace-road | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| official | retired | retire-road | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: retired, superseded.

## `road_segment_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| draft | active | approve-segment | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | realigned | approve-realignment | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | retired | retire-segment | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: realigned, retired.

## `building_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | active | approve-building | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | demolished | record-demolition | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | retired | retire-building | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| candidate | revoked | reject-building | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: demolished, retired, revoked.

## `unit_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | active | approve-unit | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | merged | merge-unit | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | split | split-unit | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | retired | retire-unit | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: merged, retired, split.

## `locality_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | official | approve-locality | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| official | renamed | approve-rename | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| official | retired | retire-locality | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: renamed, retired.

## `operational_area_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| planned | active | activate-area | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | suspended | suspend-area | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| suspended | active | reactivate-area | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| active | closed | close-area | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| closed | archived | archive-area | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: archived.

## `source_authority_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | trusted | approve-source | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| trusted | deprecated | deprecate-source | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| trusted | revoked | revoke-source | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| candidate | revoked | reject-source | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: deprecated, revoked.

## `name_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | official-current | approve-official-name | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| official-current | official-historical | replace-official-name | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| candidate | alternate | approve-alternate | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| official-current | disputed | open-name-dispute | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| disputed | official-current | resolve-name-dispute-retain | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| candidate | rejected | reject-name | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| alternate | retired | retire-alternate | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: official-historical, rejected, retired.

## `case_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| submitted | under-review | triage-case | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| under-review | needs-evidence | request-evidence | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| needs-evidence | under-review | evidence-received | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| under-review | approved | approve-case | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| under-review | rejected | reject-case | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| approved | resolved | apply-decision | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| rejected | closed | close-rejected-case | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| resolved | closed | close-resolved-case | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: closed.

## `geometry_quality_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| observed | quality-checked | run-quality-check | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| quality-checked | reviewed | review-quality-result | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| reviewed | accepted-canonical | accept-canonical-geometry | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| reviewed | valid-with-warning | accept-with-warning | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| reviewed | rejected | reject-geometry | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| reviewed | disputed | open-geometry-dispute-before-acceptance | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| accepted-canonical | superseded | replace-canonical-geometry | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| disputed | reviewed | resolve-geometry-dispute-for-review | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: rejected, superseded, valid-with-warning.

## `publication_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| draft | approval-requested | request-publication-approval | publication-authority | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| approval-requested | approved | approve-publication | publication-authority | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| approval-requested | withdrawn | withdraw-request | publication-authority | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| approved | published | publish-release | publication-authority | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| published | suspended | suspend-publication | publication-authority | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| suspended | published | reinstate-publication | publication-authority | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| published | withdrawn | withdraw-publication | publication-authority | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: withdrawn.

## `intake_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| submitted | under-review | triage-intake | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| under-review | duplicate-review | detect-duplicate | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| under-review | needs-field-check | send-field-check | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| needs-field-check | under-review | field-check-returned | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| duplicate-review | under-review | clear-duplicate | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| under-review | promoted-to-canonical | promote-to-canonical | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| under-review | rejected | reject-intake | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| promoted-to-canonical | closed | close-promoted-intake | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| rejected | closed | close-rejected-intake | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: closed.

## `field_verification_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| assigned | in-progress | start-field-task | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| in-progress | field-captured | capture-field-evidence | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| field-captured | evidence-under-review | submit-evidence-review | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| evidence-under-review | evidence-approved | approve-evidence | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| evidence-under-review | evidence-rejected | reject-evidence | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| evidence-rejected | needs-recapture | request-recapture | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| needs-recapture | in-progress | restart-field-task | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| evidence-approved | linked-to-canonical | link-approved-evidence | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |
| assigned | cancelled | cancel-field-task | authority-owner | decision_event + evidence_record required | record effective time and recorded time | operator until release prerequisite permits public projection | appeal/correction opens case record; terminal states do not silently reopen | reject and audit; migration_exception only for legacy migration inputs |

Terminal values: cancelled, linked-to-canonical.
