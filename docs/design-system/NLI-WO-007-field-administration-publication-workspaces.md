# NLI-WO-007 — Field, Administration, and Publication Government Workspaces

**Status:** Implementation in progress  
**Design authority:** BGEDS 1.0  
**Functional baseline:** `00704bcd9cb5481bc7fa581b6a1a0e5c7d0a587a`

## Objective

Complete the protected operational redesign through Publication by migrating Field Operations, personnel-centred Administration, Publication, and administrator-only Publication Outputs into the institutional government shell.

The milestone preserves the existing database, migrations, API contracts, authentication, authorization, audit, lifecycle, citizen capture, and production configuration. Presentation and workflow orchestration may improve, but authoritative state remains owned by the existing services.

## Field Operations

The Field Operations workspace MUST provide:

- assignment, citizen location-check, recent-submission, and device-sync queues;
- a stable work-item inspector with territorial, mapped, GNSS, and evidence context;
- authorized field-status and evidence-reference actions through existing endpoints;
- road and building GNSS capture with explicit accuracy visibility;
- protected evidence-file upload through the existing submission endpoint;
- device-held synchronization for offline or interrupted field work;
- explicit disclosure that device-held work is not a national record until accepted by the API;
- direct handoff to Verification;
- no invented assignment mutation or dispatch authority where the backend does not expose it.

## Administration

The Administration workspace MUST provide:

- a personnel register with search, role, and account-state filtering;
- stable identity, role-authority, session, and safeguard context;
- authorized account creation and controlled update operations;
- password rotation, session revocation, and account disablement through existing endpoints;
- visible current-admin and last-active-admin protections;
- least-privilege guidance and explicit role authority descriptions;
- no exposure to non-administrator roles.

## Publication

The Publication workspace MUST provide:

- review/readiness, release-hold, official-output, and controlled-intake sections;
- location, identity, road-name, duplicate, field, and automation context in one case view;
- existing under-review, field-check, registry-ready, rejection, duplicate, identity, and road-suggestion actions;
- a release simulation that does not publish;
- administrator-only public release protected by `NEXT_PUBLIC_PUBLICATION_RELEASE_ENABLED`;
- publication-pack creation and administrator-only pack publication;
- signage CSV and signage-pack generation from controlled output endpoints;
- certificate access for published cases;
- explicit separation of preparation, approval, publication, certificate, and physical-signage states.

## Automation posture

Routine routing, readiness summaries, blocker detection, SLA visibility, device-connection state, and evidence completeness are system-led. Humans remain responsible for field truth, identity confirmation, exception handling, authoritative review, institutional approval, public release, and personnel authority.

## Branding and presentation controls

Every migrated route MUST retain:

- the official Coat of Arms of the Republic of Equatorial Guinea;
- consistent icon-led navigation;
- the approved attribution: `Developed by BeCoreOps for the Government of the Republic of Equatorial Guinea`;
- no ChatGPT, OpenAI, AI-generated, or similar attribution;
- flat institutional surfaces without decorative gradients, glass effects, or pill-shaped navigation;
- independent desktop, tablet, and mobile behavior.

## Evidence gates

- frontend build and generated API contract verification;
- role and route authority guards;
- government workspace, registry, verification, and service-delivery source guards;
- exact-head Chromium evidence for Field Operations, Administration, Publication, and Publication Outputs;
- role-denial evidence for unauthorized routes;
- no citizen/public regression;
- API and agent-skill CI green on the exact head.
