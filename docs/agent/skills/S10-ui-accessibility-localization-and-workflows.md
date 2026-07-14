# S10 — UI, Accessibility, Localization, and Workflows

## Invoke when

- changing a public, operator, administrative, field, report, certificate, or training interface;
- adding a workflow step or record state;
- changing Spanish or English content;
- changing responsive, keyboard, map, error, loading, or offline behavior.

## Required inputs

- UI/accessibility/workflow standard;
- affected API and authorization policy;
- current screenshots and workflow evidence;
- approved terminology and controlled states;
- target roles, institutions, scopes, languages, and device classes.

## Procedure

### 1. Define the workflow contract

Record:

```text
Role/institution/scope:
Task and decision:
Prerequisites:
Information needed:
Allowed actions:
Prohibited actions:
Resulting state:
Audit/evidence created:
Error and recovery path:
Language/device/connectivity assumptions:
```

### 2. Minimize interaction without weakening authority

Count and review:

- pages and navigation changes;
- form fields;
- confirmations;
- handoffs;
- repeated data entry;
- modals and disclosure panels;
- required approvals.

Remove accidental friction, not legally or operationally required segregation of duties.

### 3. Preserve role and state clarity

Show active institution, role, and scope where authority could be confused. Distinguish:

- submitted;
- under review;
- needs evidence/field recapture;
- registry-ready;
- publication pending;
- published;
- disputed;
- corrected/superseded;
- retired/revoked.

Do not use approved, verified, official, and published interchangeably.

### 4. Implement complete localization

For Spanish and English include:

- labels;
- validation and errors;
- loading and empty states;
- confirmation and success states;
- help and privacy text;
- reports, certificates, and notifications.

Preserve official names, accents, legal terms, and canonical values separately from translated presentation.

### 5. Meet accessibility requirements

Target WCAG 2.2 AA. Verify:

- keyboard access and focus order;
- visible focus;
- semantic labels/headings/landmarks;
- contrast and non-color state indicators;
- zoom/reflow;
- associated validation errors;
- status announcements;
- touch targets;
- table responsiveness;
- map alternatives;
- reduced motion;
- accessible generated documents.

### 6. Design resilient form behavior

- preserve entered values after recoverable errors;
- prevent duplicate submission;
- show pending and unsynced states honestly;
- distinguish local/offline save from registry acceptance;
- label external map/geocoder results as suggestions;
- explain purpose and privacy before sensitive data collection.

### 7. Capture workflow evidence

For each critical state record:

- route/workflow;
- role, institution, and scope;
- language;
- viewport/device;
- environment and fixture classification;
- commit and date;
- initial state, action, result, and expected audit event.

Capture loading, empty, error, denied, recovery, and completion states where applicable.

## Outputs

- workflow contract and before/after steps;
- role/language/viewport screenshot pack;
- accessibility and keyboard results;
- localization completeness evidence;
- server-side allow/deny confirmation;
- audit/state-transition evidence.

## Stop or RFI conditions

Stop when:

- a new state, role, permission, or sensitive field lacks authority;
- UI copy implies official publication without authority;
- a workflow can only be completed with a mouse or map;
- public and protected routes share sensitive projections;
- a localization change alters legal or official meaning;
- offline conflict resolution is undefined.

## Evidence gate

Before review:

- server-side policy passes independently of UI visibility;
- critical paths work in both languages;
- keyboard and accessibility checks pass;
- required screenshots are tied to the exact commit;
- error/recovery and denied states are captured;
- no extra decorative interaction obscures operational state.

## Anti-patterns

- Reviewing only the happy-path screenshot.
- Hiding unauthorized controls and calling that security.
- Translating navigation while leaving errors and confirmations in one language.
- Treating a locally queued field record as accepted.
- Adding redundant confirmations to every action.
- Using maps as the only way to understand or enter a location.
