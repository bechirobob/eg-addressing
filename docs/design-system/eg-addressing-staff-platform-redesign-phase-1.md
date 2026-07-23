# EG Addressing Staff Platform Redesign — Phase 1 Foundation

**Work order:** NLI-WO-004  
**Status:** In execution  
**Design standard:** BGEDS 1.0.0  
**Functional baseline:** `nli/wo-003-operator-interface-foundation` at `515d90dc20583d10a5ac2ff532247087c7e3fd8a`  
**Scope:** protected staff experience and shared operator design system  
**Preserved:** citizen capture, APIs, database, authorization, lifecycle authority, audit rules, integrations, publication controls, and production configuration

## 1. Executive finding

The current platform has strong underlying capability but its staff experience is organized around accumulated routes and components rather than one coherent operating model. Presentation-only corrections improved legibility and responsive behavior, but the protected interface still carries structural debt:

- the shell is shared with public-page assumptions;
- page identity is inferred from title text;
- route-specific CSS layers compensate for layout problems rather than expressing a stable design system;
- desktop workspaces do not consistently use the width for simultaneous queue, record, evidence, and action context;
- staff administration focuses on account actions rather than personnel, team, territorial, device, and assignment operations;
- navigation describes modules more than daily work;
- workflows require users to understand how separate pages relate;
- visual hierarchy and component behavior vary by route;
- the operator experience does not yet feel like one national platform.

The correct response is a controlled frontend reconstruction over the proven backend, not another presentation-polish layer.

## 2. Rework boundary

### Preserved without redesign

- canonical national location and address model;
- database schema and migration authority;
- API contracts unless a later approved workflow identifies a justified gap;
- authentication and server-side authorization;
- role, institution, and territorial-scope enforcement;
- audit events and evidence rules;
- verification, approval, publication, correction, and retirement authority;
- public/citizen capture journey, except small visual and accessibility refinements;
- official exports, signage, certificate, and partner-release controls;
- existing test evidence as historical baseline.

### Reconstructed

- protected application shell;
- information architecture;
- operator home;
- global search and task access;
- operations queue;
- registry record workspace;
- verification decision workspace;
- field dispatch and capture supervision;
- publication and signage operations;
- mapping workspace;
- analytics and reports;
- agency workspaces;
- staff administration;
- design tokens, components, states, and quality gates;
- desktop, tablet, and mobile behavior.

## 3. Current-system findings

### 3.1 Shell and identity

The current `SiteChrome` combines civic presentation, a large masthead, service inference from page title, environment messaging, and protected role-aware navigation. That structure is useful for public or informational pages but too heavy and indirect for a daily staff workspace.

The replacement shell must:

- use explicit route/workspace metadata rather than title-string inference;
- show institution, role, territorial scope, environment, and active workspace compactly;
- keep national identity visible without consuming operational space;
- provide global search, work alerts, help, and user controls consistently;
- separate public and protected shell implementations.

### 3.2 CSS architecture

The current protected portal imports multiple sequential presentation files to correct earlier layout behavior. This produced a successful presentation audit but makes future change risky because later selectors override earlier selectors without one authoritative component contract.

The replacement must use:

- one token layer;
- one base layer;
- component-scoped styles;
- layout primitives;
- route-specific styles only where the workflow genuinely differs;
- a deprecation plan for old presentation files;
- automated prohibition of new ad hoc global overrides.

### 3.3 Navigation

The existing navigation is route-led. Users must know which module contains the work they need.

The replacement top-level model is:

1. **Home** — personal and team workload.
2. **Operations** — unified tasks, exceptions, approvals, corrections, and service-level risk.
3. **Registry** — authoritative record search and case work.
4. **Mapping** — national spatial workbench and layers.
5. **Field Operations** — dispatch, assignments, teams, devices, capture, and synchronization.
6. **Publication** — approved output, signage, QR, release, and distribution.
7. **Agencies** — institution-specific requests, data exchange, and permitted views.
8. **Analytics** — national and territorial operational intelligence.
9. **Administration** — personnel, teams, roles, territories, equipment, and access.
10. **System** — audit, integrations, configuration, health, and controlled operations.

On smaller screens, navigation is prioritized by role rather than exposing every destination.

### 3.4 Operator home

A new user currently enters a module rather than a personal work surface. The new home must answer:

- What requires my attention now?
- What is urgent or overdue?
- What was assigned to me or my team?
- What changed since I last signed in?
- Is any service, device, or synchronization state affecting work?
- What are my valid next actions?

The home is not a decorative command center. It is an actionable work index.

### 3.5 Registry

The registry should become one consistent record workspace:

- global or scoped search;
- result table with clear identifiers and state;
- selected record header;
- overview, administrative, location, evidence, related records, decisions, agency links, and audit sections;
- decision-critical context shown together;
- valid actions calculated from server-authoritative state;
- route and filter state preserved while moving between records.

### 3.6 Verification

Verification should become a continuous decision workflow rather than a page of loosely related controls:

1. receive or open assigned case;
2. review canonical identity and routing;
3. inspect map, coordinates, photos, source, accuracy, and provenance;
4. review duplicate and conflict signals;
5. compare prior decisions and corrections;
6. choose a valid decision;
7. record reason and required evidence;
8. confirm authority and consequence;
9. receive authoritative resulting state and audit reference;
10. advance automatically to the next assigned case where appropriate.

### 3.7 Field operations

Field operations requires two linked products:

- **Supervisor desktop:** dispatch board, map, assignments, teams, workload, progress, devices, exceptions, and synchronization health.
- **Officer mobile:** assignment, route, GPS confidence, evidence capture, required checks, offline save, sync state, conflict/recapture handling, and completion.

Desktop should not display a mobile capture form stretched into a wider column.

### 3.8 Publication and signage

Publication should resemble a controlled production and release operation:

- approved queue;
- release readiness;
- publication batches;
- signage packs;
- QR and code generation;
- print/export status;
- distribution and installation state;
- release history;
- hold, correction, revocation, and reissue.

Nothing should imply official release before publication authority commits it.

### 3.9 Analytics

Reports should move from isolated report panels to operational intelligence with direct links to underlying authorized records.

Priority views:

- national coverage;
- province and municipality readiness;
- intake and verification volume;
- ageing and service-level risk;
- field productivity and recapture rate;
- publication throughput;
- data-quality exceptions;
- agency use and integration health;
- missing or underserved areas;
- infrastructure and signage readiness.

Every metric must identify scope, period, source, generation time, and classification.

### 3.10 Staff administration

The current account-control emphasis is too narrow for national operations. The replacement information model is:

- personnel;
- institutions;
- teams;
- roles and permissions;
- territorial and data scopes;
- assignments;
- devices and equipment;
- vehicles where required;
- training/readiness;
- credentials and sessions;
- activity;
- audit.

Security actions remain explicit and separate:

- create identity/account;
- grant or remove role;
- change scope;
- rotate credential;
- terminate sessions;
- suspend access;
- deactivate account;
- retain immutable audit history.

## 4. Target operator shell

### 4.1 Persistent regions

- **Institution rail:** compact national and ministry identity, primary navigation, active destination.
- **Top bar:** workspace name, global search, assigned-work count, alerts, help, user/scope control.
- **Context bar:** filters, territory, team, date, record state, or mode relevant to the workspace.
- **Main work surface:** queue, record, map, table, form, or analytics.
- **Inspector/action rail:** selected record context, evidence, valid actions, history, or help.

### 4.2 Role adaptation

The shell changes emphasis without changing product logic:

- field officer sees assignments, capture, sync, and help;
- field supervisor sees dispatch, teams, progress, exceptions, and devices;
- verifier sees assigned queue, evidence, conflicts, decision, and history;
- registry officer sees search, records, corrections, approvals, and audit;
- publication officer sees release queues and output readiness;
- agency viewer sees permitted records and reports only;
- administrator sees personnel, access, configuration, audit, and system controls.

## 5. Initial component foundation

Phase 1 establishes the following reusable contracts before route migration:

- design tokens;
- protected application shell;
- workspace header;
- global search trigger;
- context toolbar;
- split-pane workbench;
- queue/list;
- authoritative record header;
- status text;
- table and mobile record alternative;
- filter field;
- form field group;
- action group;
- decision panel;
- evidence panel;
- map frame and inspector;
- timeline and audit list;
- loading, empty, denied, error, offline, and synchronization states;
- confirmation dialog.

## 6. Design tokens

The first token layer defines:

- neutral canvas and surfaces;
- institutional navy action and navigation colors;
- restrained Equatorial Guinea identity accents;
- semantic success, warning, danger, and information colors;
- primary and secondary text;
- divider strengths;
- focus and selection;
- compact typography scale;
- 8 px spacing rhythm;
- small radius scale;
- temporary-layer shadow only;
- desktop rail, top-bar, and inspector dimensions;
- viewport breakpoints and content constraints.

Project components consume semantic tokens and must not introduce arbitrary local colors or spacing where an approved token exists.

## 7. Migration sequence

### Milestone 1 — Foundation

- publish BGEDS;
- publish EG Addressing redesign findings and target architecture;
- add semantic design tokens;
- create a non-production design lab;
- establish initial component and quality contracts;
- keep current functional routes unchanged.

### Milestone 2 — Protected shell and home

- implement new application shell;
- implement role-aware navigation and context;
- implement global search entry;
- implement actionable operator home;
- validate admin, editor, viewer, agency viewer, desktop, tablet, and mobile.

### Milestone 3 — Operations and verification

- unified queue;
- assignment and service-level state;
- continuous verification decision workflow;
- authoritative action feedback and audit evidence.

### Milestone 4 — Registry record workspace

- search/results/detail model;
- complete record header and tabs;
- corrections, relationships, history, and agency links;
- preserved query and selection state.

### Milestone 5 — Field operations

- supervisor dispatch workspace;
- field mobile workflow;
- map, GPS quality, evidence, offline, sync, and conflict states.

### Milestone 6 — Publication and mapping

- release operations;
- signage and QR batch controls;
- national map workbench and operational layers.

### Milestone 7 — Analytics and agencies

- operational intelligence;
- territory comparisons;
- agency workspaces and integration state.

### Milestone 8 — Administration and system

- personnel and teams;
- role/scope control;
- equipment and sessions;
- audit and system operations.

### Milestone 9 — Consolidation

- remove superseded presentation CSS and components;
- complete localization and accessibility evidence;
- exact-head browser audit;
- production-readiness review.

## 8. Quality gates

Each migrated workflow must prove:

- user, authority, task, and expected state;
- fewer unnecessary navigation and re-entry steps;
- desktop workbench use where simultaneous context is required;
- independent mobile workflow;
- loading, empty, denied, error, offline, conflict, and recovery behavior;
- keyboard and focus operation;
- WCAG 2.2 AA target;
- supported language completeness;
- API allow/deny correctness;
- resulting audit event and record state;
- no regression to citizen capture;
- no body-level horizontal overflow;
- screenshot and machine-readable evidence tied to exact commit.

## 9. Phase 1 completion criteria

Phase 1 is complete when:

- BGEDS is versioned in the repository;
- the staff-platform rework boundary and information architecture are approved by implementation through code and evidence, not only narrative;
- semantic tokens exist in source;
- a non-production design-lab route demonstrates the target shell, workbench, table, status, form, and staff-administration patterns;
- current protected and citizen routes remain functional;
- a draft pull request records exact scope, baseline, and next migration milestone.
