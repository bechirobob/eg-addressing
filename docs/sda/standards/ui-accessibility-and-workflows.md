# SDA Standard — UI, Accessibility, Localization, and Workflows

**Version:** 0.1  
**Status:** Mandatory  
**Applies to:** public, operator, administrative, field, report, certificate, and training interfaces

## 1. Design posture

The established visual direction is restrained, clear, and human-designed. Changes MUST preserve it unless an approved work order explicitly changes the design system.

Avoid:

- generic SaaS-dashboard styling;
- decorative gradients, glass effects, heavy shadows, and excessive cards;
- pill-shaped controls used without semantic reason;
- animation that delays work or obscures state;
- dense icon-only interfaces;
- decorative data visualizations without operational purpose;
- unnecessary steps, confirmation screens, or modal chains.

Visual restraint does not mean low information density. Operator screens should present the right evidence and actions together without hiding critical context.

## 2. Workflow-first design

Every screen MUST serve a defined user, authority, task, and record state. Before implementation, document:

- primary role and scope;
- user goal and decision required;
- prerequisite information;
- allowed and prohibited actions;
- expected next state;
- audit/evidence generated;
- error and recovery path;
- desktop, mobile, field-connectivity, and language needs.

Critical government workflows MUST minimize handoffs and repeated data entry without collapsing required segregation of duties.

## 3. Role and authority clarity

- The interface MUST show the user's active institution, role, and territorial/data scope where ambiguity could cause an authority error.
- Hidden controls are not authorization; the API remains authoritative.
- Disabled actions MUST explain the missing permission, prerequisite, record state, or approval without exposing restricted information.
- High-impact actions MUST identify the target, consequence, authority, and required reason before submission.
- Capture, review, approval, publication, audit, and platform-operation actions MUST remain visually and conceptually distinct.

## 4. Accessibility target

Public and protected web interfaces MUST target WCAG 2.2 Level AA unless an approved exception records the barrier, mitigation, owner, and review date.

At minimum:

- all functionality is keyboard operable;
- focus order and visible focus are reliable;
- headings, landmarks, labels, names, roles, and states are semantic;
- text and controls meet contrast requirements;
- zoom/reflow does not hide essential content;
- errors are identified, described, and associated with fields;
- status changes are announced appropriately;
- touch targets are usable on field/mobile devices;
- color is not the sole carrier of meaning;
- motion can be reduced and is never required to understand state;
- tables have headers and usable responsive alternatives;
- maps have non-map text alternatives for essential tasks;
- certificates, reports, and training artefacts are accessible within their supported format constraints.

Automated accessibility checks are required but do not replace keyboard and assistive-technology review of critical workflows.

## 5. Spanish and English localization

- Spanish and English support MUST cover complete affected workflows, including labels, validation, errors, empty states, confirmation, help, certificates, reports, and notifications.
- Source text MUST not be embedded ad hoc across components when localization infrastructure applies.
- Do not treat proper names, legal terms, administrative names, or address strings as ordinary translatable copy.
- Date, number, units, and sorting behavior MUST be locale aware while stored values remain canonical.
- Translation changes affecting legal or official meaning require review.
- Missing translations MUST fail quality checks for production-relevant routes rather than silently mixing languages.

## 6. Forms and data capture

- Ask only for data required by the current purpose.
- Use canonical selectors and lookups rather than free text when authoritative values exist.
- Preserve entered data after recoverable validation or network failure.
- Validation MUST be timely, specific, and consistent with server rules.
- Required fields, format, units, privacy notice, and consequences MUST be clear before submission.
- Precise coordinates, identity, and evidence collection require clear purpose and consent/notice behavior defined by policy.
- Autocomplete or map suggestions MUST be labeled as suggestions and require review when not authoritative.

## 7. Record and case views

A reviewer should be able to understand a case without excessive navigation. Critical case views SHOULD co-locate:

- identity and canonical identifiers;
- current state and publication state;
- institution and territorial routing;
- map/location evidence with provenance and quality;
- duplicate/conflict signals;
- timeline and prior decisions;
- corrections/disputes/holds;
- next valid actions and required approval;
- public projection preview where relevant.

Sensitive fields MUST be purpose-limited and masked or omitted according to role.

## 8. State, feedback, and errors

Every async or state-changing action MUST provide:

- clear pending state;
- prevention of accidental duplicate submission;
- result tied to the affected record;
- recoverable retry or escalation path;
- no false success before authoritative commit;
- correlation/tracking reference where support may be needed.

Interfaces MUST distinguish:

- draft;
- submitted;
- under review;
- needs field verification/recapture;
- registry-ready;
- published;
- disputed, corrected, superseded, retired, or rejected.

Do not use “approved,” “official,” “published,” or “verified” interchangeably.

## 9. Confirmation and destructive actions

Confirmation is required when an action is difficult to reverse, changes authority, affects many records, discloses restricted data, or triggers external effects.

A confirmation MUST state:

- exact action and affected count/record;
- resulting state and external effects;
- whether rollback is possible;
- required reason or approval;
- actor's active authority context.

Routine low-risk actions should not receive redundant confirmations that train users to click through warnings.

## 10. Maps and spatial workflows

- Maps MUST display source, confidence, and official/pending status.
- Essential information and actions MUST have a list/text alternative.
- Coordinate accuracy and uncertainty MUST be understandable to operators.
- Pin placement MUST not imply official geometry without the correct status.
- Map controls must be keyboard/touch accessible where technically supported, with an alternative input path.
- Offline or weak-connectivity behavior must preserve captures and show synchronization state honestly.

## 11. Responsive and field operation

- Public workflows MUST function on common mobile widths.
- Operator workbenches may prioritize desktop but MUST remain usable at documented minimum widths.
- Field workflows MUST account for sunlight, touch, intermittent connectivity, battery, GPS uncertainty, and interrupted sessions.
- Offline actions MUST use stable local identifiers, idempotent synchronization, conflict handling, and visible unsynced state.
- Do not represent locally saved or queued work as accepted by the registry.

## 12. Reports, exports, certificates, and signage

- Reports MUST identify data period, scope, source, generation time, and classification.
- Exports MUST not be initiated by ambiguous controls and must show purpose/approval where required.
- Certificates and public proofs MUST identify publication state, verification method, issue time, and revocation/correction path.
- QR codes and public codes require a readable text alternative.
- Physical signage artefacts MUST be generated only from authorized published records.
- Formal documents should use restrained document design rather than web-card styling.

## 13. Workflow evidence pack

For every critical route and role, maintain repeatable evidence labeled with:

- workflow and route;
- role, institution, and scope;
- language;
- desktop/mobile viewport;
- environment and fixture classification;
- commit and date;
- initial state, action, result, and expected audit event.

Critical workflows include login, citizen submission/tracking, field capture/sync, verification, duplicate resolution, correction, registry approval, publication, export, staff/scope administration, audit, and incident/operator actions.

## 14. Required evidence

UI/workflow changes require:

- user/authority/task statement;
- before/after workflow steps and click/interaction count where material;
- screenshots for roles, languages, viewport classes, and key states;
- keyboard and accessibility evidence;
- server-side allow/deny confirmation;
- loading, validation, empty, error, denied, and recovery states;
- localization check;
- audit and record-state effect;
- no-regression result from design-system and route-ownership guards.
