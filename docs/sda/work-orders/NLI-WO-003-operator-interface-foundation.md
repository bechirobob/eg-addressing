# NLI-WO-003 — Operator Interface and Navigation Foundation

**Status:** ISSUED — CONTROLLED IMPLEMENTATION  
**Priority:** P1 operator effectiveness  
**Issued:** 2026-07-21  
**Authority:** System Design Authority, following Programme Owner direction  
**Implementation branch:** `nli/wo-003-operator-interface-foundation`  
**Change class:** Class B — Core platform frontend  
**Readiness boundary:** protected operator-interface presentation and navigation only; this work order does not authorize data-model, API, workflow-state, role, publication-authority, deployment, or production-readiness changes

## 1. Objective

Make the protected Equatorial Guinea National Location Infrastructure operator experience faster to understand and easier to navigate on desktop and mobile while preserving the accepted civic visual identity, coat of arms, national colour accents, public/staff boundary, server-side authorization, and existing workflow semantics.

The implementation must move protected pages away from a generic page-by-page web application layout toward a consistent national operational workspace without introducing dashboard decoration, fake metrics, additional external services, or new institutional claims.

## 2. Mandatory reading

- repository `AGENTS.md`;
- `docs/sda/README.md`;
- `docs/sda/standards/ui-accessibility-and-workflows.md`;
- `docs/sda/standards/security.md`;
- `docs/sda/standards/documentation-and-records.md`;
- `apps/admin-portal/DESIGN.md`;
- `docs/agent/README.md`;
- `docs/agent/master-operating-protocol.md`;
- `docs/agent/skill-manifest.yaml`;
- `docs/agent/PROJECT-COVERAGE-MATRIX.md`;
- S01, S03, S10, S11, S12, S16, S18, S20, S21, S22, S23, S24, S27, S29, S30, and S31 skill cards.

## 3. Primary users and environments

- **Editor:** registry and field work on desktop and common mobile widths.
- **Administrator:** the same operator work plus staff account control.
- **Viewer / agency viewer:** read-only reporting within the existing role policy.
- **Public guest:** existing citizen and public verification pages; public routes are regression-only for this work order.
- **Environment:** controlled pilot and development/staging. No national-production claim is authorized.

## 4. In scope

1. A shared protected operator workspace shell with:
   - stable grouped navigation;
   - current-section orientation;
   - visible signed-in user and role context;
   - direct sign-out access;
   - mobile navigation drawer;
   - compact mobile quick navigation for existing authorized routes.
2. Compact protected-route mastheads while retaining the coat of arms and national identity.
3. Increased useful information density for existing protected tables, forms, disclosures, record lists, empty/error states, and map containers.
4. Clear responsive differences between desktop tables and mobile record rows.
5. Shared CSS based only on the frozen government-service tokens in `app/globals.css`.
6. A deterministic source guard proving the operator shell remains present, responsive, and free of prohibited visual patterns.
7. Documentation of the protected operator-shell design contract.

## 5. Out of scope and prohibited

- No database, migration, reference-data, fixture, or PostGIS change.
- No API, generated contract, backend, authentication, authorization, session, or audit behavior change.
- No new role, permission, institution, territorial scope, workflow state, status, or metric.
- No publication, certificate, public proof, signage-authority, or address-code semantics change.
- No external font, icon package, analytics system, map source, geocoder, UI framework, or paid service.
- No removal or weakening of English/Spanish localization infrastructure.
- No redesign of public citizen workflows beyond regression-compatible inherited shared styling.
- No changes to NLI-WO-002 PR #7 or NLI-WO-001 maintenance PR #8.
- No deployment, merge, mark-ready, or production action under this work order.

## 6. Acceptance criteria

### AC-01 — Protected workspace structure

Authenticated protected routes use one consistent desktop workspace with a stable navigation rail and a primary content column. Public routes retain their existing public navigation model.

### AC-02 — Authority and orientation

The protected workspace shows the platform identity, current section, signed-in user, and active role without implying additional institutional scope or replacing server-side authorization.

### AC-03 — Mobile navigation

At documented mobile widths, the navigation becomes an accessible off-canvas drawer and existing high-frequency protected routes remain reachable through a compact text-labeled quick navigation. Keyboard focus and reduced-motion behavior remain supported.

### AC-04 — Information density

Protected tables, forms, panels, record lists, disclosures, and status treatments use smaller, consistent spacing and text sizes while retaining legibility, touch targets, semantic headings, table headers, and mobile alternatives.

### AC-05 — Civic visual continuity

The coat of arms and Equatorial Guinea colour scheme remain. Protected surfaces use flat backgrounds, thin dividers, restrained accents, and no decorative gradients, glass effects, pill clouds, heavy shadows, or generic dashboard walls.

### AC-06 — No authority or workflow drift

Existing route access, role visibility, API calls, record states, form behavior, publication locks, and public/protected data boundaries remain unchanged.

### AC-07 — Localization and accessibility

No changed workflow introduces untranslated visible service copy. The implementation preserves semantic navigation, visible focus, keyboard-operable controls, mobile reflow, table/mobile alternatives, and reduced-motion behavior.

### AC-08 — Verification

At the exact implementation head:

- TypeScript compilation passes;
- `npm run test:operator-shell` passes;
- `npm run test:quality` passes;
- `npm run build` passes;
- representative protected routes are checked at desktop and mobile widths for editor, admin, and read-only roles;
- representative public routes are checked for visual and access regression;
- screenshots record role, language, viewport, environment, and exact commit.

If GitHub-hosted CI fails before steps because free minutes or runner infrastructure are unavailable, record that separately from repository test results and do not modify workflows merely to trigger CI.

## 7. Expected changed paths

- `apps/admin-portal/app/layout.tsx`
- `apps/admin-portal/app/operator-shell.css`
- `apps/admin-portal/components/RoleAwareChrome.tsx`
- `apps/admin-portal/scripts/operator-shell-guard.mjs`
- `apps/admin-portal/package.json`
- `apps/admin-portal/DESIGN.md`
- `docs/agent/task-contexts/NLI-WO-003-operator-interface-foundation.md`
- this work order

Any additional application path requires a scope update before modification.

## 8. Evidence and review boundary

The implementation must remain on a separate draft PR from PR #7 and PR #8. Completion means implemented and locally tested at an exact commit. It does not mean SDA acceptance, pilot-ready approval, deployment approval, or national-production readiness.
