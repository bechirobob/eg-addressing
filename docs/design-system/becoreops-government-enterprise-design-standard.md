# BeCoreOps Government & Enterprise Design Standard (BGEDS)

**Version:** 1.0.0  
**Status:** Mandatory foundation  
**Owner:** BeCoreOps product and engineering  
**Applies to:** government platforms, enterprise systems, staff portals, citizen services, field applications, operational dashboards, reports, public websites, and future BeCoreOps products

## 1. Purpose

BGEDS establishes one durable product-design standard across BeCoreOps projects. Branding may change by product, institution, or sector, but interaction quality, information hierarchy, accessibility, workflow logic, and implementation discipline must remain recognizably consistent.

The standard is designed for software that must feel permanent, trustworthy, understandable, and operationally serious. It explicitly rejects generic startup-dashboard styling and interfaces assembled from unrelated components.

BGEDS has four product profiles:

1. **Government operator:** dense, authoritative, auditable, role-aware workspaces.
2. **Citizen service:** simple, reassuring, task-focused public journeys.
3. **Enterprise operations:** efficient, measurable, workflow-driven business tools.
4. **Field operations:** mobile-first capture, offline resilience, evidence integrity, and clear synchronization state.

## 2. Non-negotiable principles

### 2.1 Workflow before page

Every interface begins with a user goal, authority boundary, record state, required evidence, decision, and next state. Page inventories do not substitute for workflow design.

Each critical workflow must document:

- actor, institution, role, and territorial scope;
- trigger and expected outcome;
- prerequisite data and evidence;
- permitted and prohibited actions;
- automated steps and human decisions;
- exception and recovery paths;
- audit events and resulting record state;
- desktop, tablet, mobile, offline, and localization requirements.

### 2.2 Information before decoration

The interface exists to help a person understand a situation and complete work. Decorative graphics, gradients, novelty animation, oversized headings, empty cards, and unnecessary visual effects are prohibited when they do not improve comprehension.

### 2.3 Calm authority

Government and enterprise software should feel controlled rather than exciting. Use restrained color, clear typography, stable layouts, precise language, and predictable interaction patterns.

### 2.4 Automation by default

Routine routing, validation, deduplication, synchronization, notifications, and status progression should be automated where policy allows. Human attention is reserved for judgment, exceptions, approval, escalation, and accountability.

Automation must never create false certainty. The interface must distinguish local save, queued synchronization, server acceptance, review, approval, publication, and external release.

### 2.5 One product, not a collection of modules

Navigation, terminology, search, record layouts, tables, status treatment, forms, errors, and actions must follow one system. A user moving between modules should not need to relearn the product.

### 2.6 Five-minute rule

A new user with the correct role should understand within five minutes:

- what the system is;
- where they are;
- what work requires attention;
- what action to take next;
- how to find a record;
- how to recover from a mistake or request help.

### 2.7 Thirty-second screen rule

A first-time user should understand the purpose, primary state, and next action of a normal screen within thirty seconds.

## 3. Visual posture

### Required

- flat, restrained surfaces;
- small radii used only where they improve grouping or touch usability;
- thin dividers and alignment instead of boxed cards;
- limited shadows, reserved for temporary layers such as menus and dialogs;
- compact, readable typography;
- strong information hierarchy;
- purposeful whitespace;
- data-dense desktop workspaces;
- clear focus and selected states;
- official identity used with restraint.

### Prohibited

- pill-shaped containers as default layout devices;
- glowing panels, glass effects, decorative gradients, or neon accents;
- large empty cards with a metric in the center;
- oversized hero typography inside staff software;
- decorative left-edge color shadows on information containers;
- excessive rounded rectangles;
- icon-only controls without accessible labels;
- floating action buttons in desktop operator systems without a documented need;
- mobile layouts stretched across desktop widths;
- inconsistent component patterns between routes;
- status communicated by color alone;
- unverified success messages.

## 4. Product architecture

### 4.1 Government operator shell

The standard shell contains:

- institutional identity;
- active environment when not production;
- user, institution, role, and scope;
- global search;
- primary navigation;
- current workspace title and context;
- alerts and assigned work;
- help and sign-out.

The shell must remain visually quiet. The content and work state should dominate.

### 4.2 Recommended top-level navigation

Government platforms should normally use no more than eight primary destinations:

1. Home
2. Operations
3. Registry
4. Mapping or domain workspace
5. Agencies or partners
6. Analytics
7. Administration
8. System

Product-specific names may change, but navigation should group work by purpose rather than by technical subsystem.

### 4.3 Workspace modes

A workspace mode may adapt secondary navigation, commands, and context without creating a separate application. Modes must share the same shell, search, record patterns, terminology, and authorization model.

### 4.4 Home is a work surface

The operator home should prioritize:

- assigned work;
- urgent exceptions;
- pending approvals;
- deadlines and service levels;
- recent activity;
- system or synchronization warnings;
- role-relevant performance indicators.

It must not become a decorative command center or generic analytics dashboard.

## 5. Layout system

### 5.1 Breakpoint intent

Responsive design is not proportional scaling. Each viewport class has a distinct purpose:

- **Desktop, 1280 px and above:** multi-pane workbench, persistent navigation, dense tables, side context, keyboard efficiency.
- **Compact desktop/tablet landscape, 960–1279 px:** reduced side panels, collapsible secondary navigation, preserved core table and record workflows.
- **Tablet portrait, 720–959 px:** one primary work surface with contextual drawers or sequential panels.
- **Mobile, below 720 px:** task-first flow, large touch targets, no desktop table compression, explicit offline and sync state.

### 5.2 Grid

Use a 12-column desktop grid with consistent gutters and a maximum readable content width where full-width data is unnecessary. Map, table, dispatch, and registry workbenches may use the full available width.

### 5.3 Pane patterns

Approved operator patterns include:

- **Queue / record / context:** queue on the left, record in the center, evidence/actions on the right.
- **Search / results / detail:** persistent filters, results table, selected record.
- **Map / list / inspector:** map and list synchronized with a record inspector.
- **Form / evidence:** main structured form with a supporting evidence panel.
- **Single record:** header, key state, tabs, timeline, related records, actions.

Do not stack every panel vertically on desktop when comparison or simultaneous context is required.

### 5.4 Spacing

Use an 8 px base rhythm. Preferred spacing steps:

- 4 px: micro alignment only;
- 8 px: related control spacing;
- 12 px: compact content spacing;
- 16 px: standard internal spacing;
- 24 px: section separation;
- 32 px: major group separation;
- 48 px: page-level separation, used sparingly in operator software.

## 6. Typography

### 6.1 Typeface posture

Use a neutral, highly legible sans-serif with broad language support. Product branding must not compromise operational readability. System fonts are acceptable when deployment or licensing requirements make them preferable.

### 6.2 Scale

The default operator scale is compact:

- Display: 32 px / 40 px, public or major landing contexts only;
- Page title: 24 px / 32 px;
- Section title: 18 px / 26 px;
- Subsection title: 16 px / 24 px;
- Body: 14 px / 21 px;
- Small body: 13 px / 19 px;
- Label: 12 px / 16 px, medium weight;
- Metadata: 12 px / 16 px;
- Table: 13–14 px / 18–20 px.

Staff software must not use giant headings. Use weight, spacing, and alignment before increasing size.

### 6.3 Writing style

Interface copy must be:

- direct and specific;
- written in complete plain-language sentences where explanation is necessary;
- consistent with official workflow states;
- free of technical implementation terms unless the user role requires them;
- explicit about consequences, authority, and recovery.

Avoid vague labels such as `Manage`, `Process`, `Continue`, or `Submit` when a more specific action is available.

## 7. Color and identity

### 7.1 Semantic use

Color is reserved for identity, selection, focus, status, warnings, errors, charts, and maps. Large decorative color fields should be rare.

### 7.2 Required semantic roles

Every product theme must define:

- canvas;
- surface;
- elevated surface;
- text primary and secondary;
- divider and strong divider;
- action primary and action hover;
- focus ring;
- selected background;
- informational;
- success;
- warning;
- danger;
- disabled;
- map and chart categorical palette.

### 7.3 Official identity

Government products may use the national coat of arms, institutional name, flag colors, and formal typography. Identity must support trust without overwhelming daily work. The coat of arms should not be repeated inside every panel.

## 8. Navigation

- Primary navigation must be stable across modules.
- Selected state must be clear without relying only on color.
- Group labels should describe user purpose, not internal architecture.
- Frequently used destinations should require no more than one primary navigation action.
- Breadcrumbs are required for deep hierarchical contexts, not as decoration on every page.
- Back actions must preserve filters, selection, and work state where possible.
- Mobile navigation must be purpose-built; it must not simply shrink the desktop sidebar.

## 9. Search

Government and enterprise systems require a consistent global search model.

Search should support, where permitted:

- official identifier;
- human-readable code;
- person or organization reference;
- administrative area;
- record state;
- date or range;
- related agency reference;
- exact and partial matching;
- recent searches and saved filters for operational roles.

Search results must identify record type, current state, jurisdiction, and authoritative identifier before the user opens the record.

## 10. Record views

Every authoritative record should use a consistent header containing:

- record type and official identifier;
- human-readable name or address;
- current lifecycle state;
- publication or external-release state;
- institution and territorial scope;
- last authoritative change;
- primary valid actions.

Recommended record tabs:

1. Overview
2. Location or domain data
3. Evidence
4. Related records
5. Decisions and history
6. Agency links
7. Audit

Tabs must not hide information required for the current decision. Decision-critical evidence should be co-located.

## 11. Tables

Tables are the default for dense operational comparison on desktop.

Requirements:

- visible column headers;
- stable row height;
- clear selected row;
- meaningful sorting and filtering;
- persistent query state;
- pagination or virtualization appropriate to data volume;
- explicit bulk-selection count and consequences;
- keyboard navigation for critical workflows;
- no horizontal page overflow;
- contained table scrolling when necessary;
- responsive mobile alternatives that preserve record identity and primary state.

Avoid using cards to represent large operational lists on desktop.

## 12. Forms

- Labels remain visible after entry; placeholders do not replace labels.
- Group fields according to the operator's decision, not database tables.
- Required fields and accepted formats must be clear before submission.
- Use authoritative selectors instead of free text where canonical values exist.
- Dependent selectors must update predictably and preserve valid choices.
- Validation messages must state the problem and correction.
- Recoverable failures must preserve entered work.
- Long forms require save state, progress context, and safe interruption.
- Destructive or high-impact actions require reason, consequence, authority context, and confirmation.

## 13. Status and state

Status treatment must combine text, shape or icon where appropriate, and semantic color. Status labels should be compact but must not become decorative pills scattered across the interface.

State language must be canonical. For example, `verified`, `approved`, `published`, and `released` are not interchangeable.

Every asynchronous action must show:

- pending state;
- authoritative success only after commit;
- affected record;
- resulting state;
- retry or escalation path;
- correlation reference where support may be required.

## 14. Maps and geospatial interfaces

- Maps must have synchronized list or textual alternatives for essential operations.
- Official, proposed, observed, and uncertain geometry must be visually distinct.
- Source, timestamp, accuracy, and provenance must be available.
- Selected features must remain identifiable at common zoom levels.
- Layer controls should group by operational purpose.
- The map must not become background decoration.
- Field capture must show offline, GPS quality, unsynced evidence, and conflict state honestly.

## 15. Data visualization

Charts are used only when they improve comparison, trend recognition, coverage assessment, or operational decision-making.

Each chart must include:

- title phrased as a question or decision context where useful;
- time period and scope;
- source and generation time;
- accessible text summary;
- legible axes and units;
- non-color distinctions when needed;
- link or route to underlying records when authorized.

Avoid donut-chart collections, decorative gauges, and meaningless metric walls.

## 16. Staff administration

Staff administration is an operational personnel workspace, not a collection of account cards.

The standard information model includes:

- personnel;
- institutions;
- teams;
- roles and permissions;
- territorial scopes;
- assignments;
- devices and equipment;
- credential and session state;
- training or readiness where relevant;
- activity and audit history.

Account security actions must clearly separate identity, authorization, credentials, session control, deactivation, and audit.

## 17. Field and mobile applications

Field interfaces must prioritize:

- assignment identity and destination;
- navigation and map context;
- GPS confidence;
- camera and evidence capture;
- required checks;
- offline save;
- synchronization state;
- conflict and recapture instructions;
- minimal typing;
- large touch targets;
- sunlight-readable contrast;
- battery and network awareness where technically available.

Mobile is a distinct workflow design, not a responsive copy of the desktop portal.

## 18. Citizen services

Citizen journeys should usually present one primary task at a time.

Required qualities:

- clear eligibility and required information;
- simple language;
- visible progress;
- privacy and consent context;
- save and recovery where appropriate;
- confirmation reference;
- truthful status tracking;
- accessibility and low-bandwidth support;
- no exposure of internal staff terminology.

## 19. Accessibility

All web products target WCAG 2.2 Level AA unless a documented exception identifies the barrier, mitigation, owner, and review date.

Minimum requirements include:

- full keyboard operation;
- visible focus;
- semantic landmarks and headings;
- programmatic names, roles, descriptions, and errors;
- sufficient contrast;
- zoom and reflow support;
- touch targets appropriate to context;
- color-independent meaning;
- reduced-motion support;
- accessible tables and mobile alternatives;
- map alternatives;
- screen-reader announcements for material state changes.

Automated checks do not replace manual keyboard, zoom, screen-reader, and field-device review of critical workflows.

## 20. Localization

Language support must cover the complete workflow, including navigation, validation, errors, empty states, confirmation, help, reports, exports, and notifications. Mixed-language screens are not acceptable in production.

Dates, numbers, sorting, names, official terminology, and administrative units must be locale-aware while canonical stored values remain stable.

## 21. Component governance

Every reusable component requires:

- purpose and approved use;
- supported states;
- accessibility behavior;
- desktop and mobile behavior;
- localization support;
- examples and anti-examples;
- automated tests where feasible;
- owner and version.

New components must not duplicate an existing pattern without a documented reason.

The initial mandatory component set is:

- application shell;
- page and record header;
- navigation;
- toolbar and command group;
- search and filter controls;
- data table;
- record summary;
- tabs;
- form field and field group;
- status text;
- alert and validation summary;
- dialog and confirmation;
- timeline and audit history;
- map frame and inspector;
- empty, loading, error, denied, and offline states.

## 22. Testing and evidence

A critical interface change is incomplete without evidence for:

- intended user, authority, task, and record state;
- desktop, tablet, and mobile behavior;
- supported languages;
- loading, empty, error, denied, offline, and recovery states;
- keyboard and focus behavior;
- contrast and zoom/reflow;
- server-side allow and deny behavior;
- audit and resulting record state;
- no body-level horizontal overflow;
- no regression to citizen or public workflows;
- exact commit and environment used for evidence.

## 23. Design review gates

A feature cannot be accepted when any of the following is true:

- the interface is a stretched mobile layout on desktop;
- the primary task is unclear;
- critical context is hidden across unnecessary pages;
- routine work requires repeated data entry already known to the system;
- authorization is implied only by hidden controls;
- success is shown before authoritative confirmation;
- destructive consequences are vague;
- the design relies on excessive cards, pills, shadows, or decorative effects;
- mobile is unusable without horizontal scrolling;
- accessibility or localization is incomplete;
- the workflow cannot recover from a realistic failure.

## 24. Adoption across projects

Each project must maintain a small theme layer for brand identity and a product-specific extension for domain patterns. Core spacing, typography, interaction, status, accessibility, layout, and quality gates remain shared.

Adoption order:

1. establish tokens and base components;
2. map workflows and information architecture;
3. build a design-lab reference;
4. migrate one complete high-value workflow;
5. validate with evidence;
6. migrate remaining workflows;
7. remove superseded components and CSS;
8. publish a versioned release of the product design system.

## 25. Definition of done

A BGEDS-compliant product feels coherent across every route, supports fast and accurate work, explains state and authority, works independently on desktop and mobile, passes accessibility review, and avoids the visual patterns associated with generic templates or machine-assembled interfaces.
