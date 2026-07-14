# Lifecycle State Machines

Transitions are hand-authored. No transition is inferred from vocabulary order. Every transition records actor/permission/scope, authority, evidence, effective time, recorded time, audit event, visibility, reversal/appeal, and invalid-transition behavior.

## `canonical_record_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | under-review | submit-candidate | registry.record.submit | citizen/field intake evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | withdraw candidate or reject | reject transition and audit |
| under-review | active | approve-canonical | registry.record.approve | approved verification bundle | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | eligible for release after publication item | correction/dispute case | deny without authority/evidence |
| under-review | disputed | open-dispute | registry.dispute.open | dispute submission | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not public unless already released | resolve dispute | deny invalid dispute target |
| active | corrected | approve-correction | registry.record.correct | correction case + before/after proof | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | new version required before public change | appeal correction case | deny if no successor version |
| active | superseded | approve-supersession | registry.record.supersede | successor record/version link | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | old public alias retained as historical | restore through SDA decision | deny non-reciprocal successor |
| active | retired | retire-record | registry.record.retire | retirement authority decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | remove from current public release after withdrawal | reinstate through SDA case | deny if active publication not handled |
| candidate | revoked | reject-candidate | registry.record.reject | review denial reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | never public | resubmit new candidate | deny missing reason |

Terminal values: corrected, disputed, retired, revoked, superseded.

## `administrative_unit_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| proposed | official | approve-administrative-version | admin.unit.approve | official gazette/source record | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | eligible for government projection | replace with newer version | deny without authority |
| official | historical | replace-by-new-official-version | admin.unit.replace | new version and boundary evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | current public switches after release | restore by SDA correction | deny non-contained interval |
| official | retired | retire-administrative-unit | admin.unit.retire | retirement order | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not current public | reinstate by official order | deny if active children unresolved |
| proposed | revoked | reject-proposal | admin.unit.reject | review denial | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | never public | resubmit | deny missing reason |

Terminal values: historical, retired, revoked.

## `road_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | field-verified | field-verify-road | road.verify | field geometry and name evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | recapture | deny missing geometry |
| field-verified | official | approve-road | road.approve | approved geometry/name | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public only after release | correct/supersede | deny without authority |
| official | superseded | replace-road | road.supersede | replacement road link | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | historical public if released | restore by decision | deny cycle |
| official | retired | retire-road | road.retire | retirement evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | remove from current public after release | reinstate by decision | deny active dependent unresolved |

Terminal values: retired, superseded.

## `road_segment_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| draft | active | approve-segment | road.segment.approve | segment geometry | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator until release | realign | deny missing road |
| active | realigned | approve-realignment | road.segment.realign | new segment geometry | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public after release | appeal | deny no successor |
| active | retired | retire-segment | road.segment.retire | retirement decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | remove current | reinstate | deny dependents |

Terminal values: realigned, retired.

## `building_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | active | approve-building | building.approve | field point/footprint evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public after address release | correct/retire | deny missing subject |
| active | demolished | record-demolition | building.demolish | demolition evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | remove current public after release | appeal | deny active units unresolved |
| active | retired | retire-building | building.retire | retirement decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | remove current | reinstate | deny active links |
| candidate | revoked | reject-building | building.reject | review reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | never public | resubmit | deny missing reason |

Terminal values: demolished, retired, revoked.

## `unit_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | active | approve-unit | unit.approve | building and unit evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public after release if allowed | merge/split/retire | deny missing building |
| active | merged | merge-unit | unit.merge | merge decision and successor | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | historical only | appeal | deny no successor |
| active | split | split-unit | unit.split | split decision and successors | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | historical only | appeal | deny no successors |
| active | retired | retire-unit | unit.retire | retirement evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | remove current | reinstate | deny active publication |

Terminal values: merged, retired, split.

## `locality_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | official | approve-locality | locality.approve | locality authority evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public after release | rename/retire | deny missing admin context |
| official | renamed | approve-rename | locality.rename | name replacement | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | new name after release | appeal | deny no historical name |
| official | retired | retire-locality | locality.retire | retirement decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | remove current | reinstate | deny active links |

Terminal values: renamed, retired.

## `country_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| active | retired | retire-country-row | country.retire | retirement decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not current | reinstate by SDA | deny missing decision |

Terminal values: retired.

## `entrance_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | active | approve-entrance | entrance.approve | entrance evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public through address release | retire/revoke | deny missing evidence |
| active | retired | retire-entrance | entrance.retire | retirement decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not current | reinstate | deny active links |
| candidate | revoked | reject-entrance | entrance.reject | rejection reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | never public | resubmit | deny missing reason |

Terminal values: retired, revoked.

## `landmark_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | official | approve-landmark | landmark.approve | landmark evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public after release | retire/revoke | deny missing evidence |
| official | retired | retire-landmark | landmark.retire | retirement decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not current | reinstate | deny active links |
| candidate | revoked | reject-landmark | landmark.reject | rejection reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | never public | resubmit | deny missing reason |

Terminal values: retired, revoked.

## `non_building_object_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | active | approve-object | object.approve | object evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public through release if allowed | retire/revoke | deny missing evidence |
| active | retired | retire-object | object.retire | retirement decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not current | reinstate | deny active links |
| candidate | revoked | reject-object | object.reject | rejection reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | never public | resubmit | deny missing reason |

Terminal values: retired, revoked.

## `operational_area_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| planned | active | activate-area | ops.area.activate | work plan approval | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | suspend/close | deny missing owner |
| active | suspended | suspend-area | ops.area.suspend | suspension reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | reactivate | deny missing reason |
| suspended | active | reactivate-area | ops.area.reactivate | reactivation approval | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | suspend/close | deny missing approval |
| active | closed | close-area | ops.area.close | closure report | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | archive | deny open work |
| closed | archived | archive-area | ops.area.archive | archive approval | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | none | deny retention not met |

Terminal values: archived.

## `source_authority_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | trusted | approve-source | source.approve | source accreditation | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator authority list | deprecate/revoke | deny incomplete accreditation |
| trusted | deprecated | deprecate-source | source.deprecate | deprecation decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator warning | reinstate by SDA | deny replacement missing |
| trusted | revoked | revoke-source | source.revoke | revocation decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not used for new facts | appeal to SDA | deny missing decision |
| candidate | revoked | reject-source | source.reject | review denial | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | never trusted | resubmit | deny missing reason |

Terminal values: deprecated, revoked.

## `name_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| candidate | official-current | approve-official-name | name.approve.official | language/name authority evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public after release | replace/dispute | deny duplicate current |
| official-current | official-historical | replace-official-name | name.replace.official | replacement name | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | old name historical | appeal | deny no successor |
| candidate | alternate | approve-alternate | name.approve.alternate | alternate name evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator/public if release allows | retire | deny missing evidence |
| official-current | disputed | open-name-dispute | name.dispute.open | dispute case | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator warning | resolve | deny no case |
| disputed | official-current | resolve-name-dispute-retain | name.dispute.resolve | resolution decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | restore public if released | appeal | deny missing decision |
| candidate | rejected | reject-name | name.reject | denial reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | never public | resubmit | deny missing reason |
| alternate | retired | retire-alternate | name.retire | retirement reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not current | reinstate | deny missing reason |

Terminal values: official-historical, rejected, retired.

## `case_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| submitted | under-review | triage-case | case.triage | case submission | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | request evidence | deny invalid target |
| under-review | needs-evidence | request-evidence | case.request_evidence | evidence request | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | receive evidence | deny no requester |
| needs-evidence | under-review | evidence-received | case.evidence.receive | submitted evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | approve/reject | deny missing evidence |
| under-review | approved | approve-case | case.approve | decision record | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | may affect public after release | appeal | deny missing authority |
| under-review | rejected | reject-case | case.reject | denial reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | appeal/resubmit | deny missing reason |
| approved | resolved | apply-decision | case.resolve | applied change proof | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public only through release | reopen by SDA | deny unapplied change |
| rejected | closed | close-rejected-case | case.close | closure note | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | none | reopen by appeal | deny open appeal |
| resolved | closed | close-resolved-case | case.close | closure note | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | none | reopen by SDA | deny open work |

Terminal values: closed.

## `geometry_quality_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| observed | quality-checked | run-quality-check | geometry.quality.run | quality check output | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | rerun | deny invalid geometry |
| quality-checked | reviewed | review-quality-result | geometry.quality.review | review decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | return to observed | deny missing reviewer |
| reviewed | accepted-canonical | accept-canonical-geometry | geometry.promote | accepted quality + evidence bundle | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | eligible for release | supersede | deny missing evidence |
| reviewed | valid-with-warning | accept-with-warning | geometry.accept.warning | warning decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator warning | recheck | deny missing warning |
| reviewed | rejected | reject-geometry | geometry.reject | rejection reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not public | recapture | deny missing reason |
| reviewed | disputed | open-geometry-dispute-before-acceptance | geometry.dispute.open | geometry dispute case | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | resolve | deny no case |
| accepted-canonical | superseded | replace-canonical-geometry | geometry.supersede | successor geometry | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | old geometry historical | appeal | deny cycle |
| disputed | reviewed | resolve-geometry-dispute-for-review | geometry.dispute.resolve | resolution evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | accept/reject | deny missing decision |

Terminal values: rejected, superseded, valid-with-warning.

## `publication_lifecycle` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| draft | approval-requested | request-publication-approval | publication.request | release package | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not public | withdraw | deny empty package |
| approval-requested | approved | approve-publication | publication.approve | approval record | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | ready to publish | withdraw | deny missing checks |
| approval-requested | withdrawn | withdraw-request | publication.withdraw | withdrawal note | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not public | new draft | deny missing reason |
| approved | published | publish-release | publication.publish | published manifest | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public release active | suspend/withdraw | deny missing manifest |
| published | suspended | suspend-publication | publication.suspend | suspension reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public hidden/suspended | reinstate | deny missing reason |
| suspended | published | reinstate-publication | publication.reinstate | reinstatement decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public active | suspend | deny missing decision |
| published | withdrawn | withdraw-publication | publication.withdraw | withdrawal decision | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public withdrawn | new release | deny retention gap |

Terminal values: withdrawn.

## `intake_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| submitted | under-review | triage-intake | intake.triage | submission | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | reject/promote | deny invalid submission |
| under-review | duplicate-review | detect-duplicate | intake.duplicate | duplicate evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | clear duplicate | deny no match |
| under-review | needs-field-check | send-field-check | intake.field_check | field task request | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | return field check | deny no task |
| needs-field-check | under-review | field-check-returned | intake.field_return | field evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | promote/reject | deny missing evidence |
| duplicate-review | under-review | clear-duplicate | intake.clear_duplicate | clearance note | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | promote/reject | deny missing note |
| under-review | promoted-to-canonical | promote-to-canonical | intake.promote | canonical link | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | public after release | correct | deny no canonical target |
| under-review | rejected | reject-intake | intake.reject | denial reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not public | resubmit | deny missing reason |
| promoted-to-canonical | closed | close-promoted-intake | intake.close | closure note | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | none | reopen by SDA | deny missing canonical proof |
| rejected | closed | close-rejected-intake | intake.close | closure note | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | none | appeal | deny open appeal |

Terminal values: closed.

## `field_verification_state` transitions

| From | To | Event | Actor/permission/scope | Authority/evidence | Effective/recorded time | Visibility | Reversal/appeal | Invalid transition |
|---|---|---|---|---|---|---|---|---|
| assigned | in-progress | start-field-task | field.start | assignment | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | cancel | deny wrong assignee |
| in-progress | field-captured | capture-field-evidence | field.capture | GPS/photo/evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | review | deny missing capture |
| field-captured | evidence-under-review | submit-evidence-review | field.submit_review | submitted evidence | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | approve/reject | deny incomplete evidence |
| evidence-under-review | evidence-approved | approve-evidence | field.evidence.approve | approval record | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | eligible canonical evidence | link canonical | deny missing authority |
| evidence-under-review | evidence-rejected | reject-evidence | field.evidence.reject | rejection reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | not public | recapture | deny missing reason |
| evidence-rejected | needs-recapture | request-recapture | field.recapture.request | recapture task | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | restart | deny missing reason |
| needs-recapture | in-progress | restart-field-task | field.restart | restart assignment | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | capture | deny wrong assignee |
| evidence-approved | linked-to-canonical | link-approved-evidence | field.link | canonical link | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only/public via release | unlink by correction | deny missing canonical |
| assigned | cancelled | cancel-field-task | field.cancel | cancel reason | record effective_at and recorded_at; close recorded_to on replacement where bitemporal | operator-only | reassign | deny missing reason |

Terminal values: cancelled, linked-to-canonical.
