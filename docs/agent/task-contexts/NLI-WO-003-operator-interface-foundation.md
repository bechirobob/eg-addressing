# Agent Task Context Pack — NLI-WO-003 Operator Interface Foundation

**Repository:** `bechirobob/eg-addressing`  
**Base branch/SHA:** `main` / `f10016ed4cea8582ac48de41aa4f80b30c999ba1`  
**Task branch/SHA:** `nli/wo-003-operator-interface-foundation` / created from the exact base  
**PR/issue:** draft PR to be opened after implementation  
**Working tree:** connector-backed controlled change set  
**Prepared at:** 2026-07-21

## 1. Authority

- **Programme:** Equatorial Guinea National Location Infrastructure.
- **Active work order:** `NLI-WO-003 — Operator Interface and Navigation Foundation`.
- **Current SDA outcome/review:** newly issued; no acceptance decision yet.
- **Change class:** Class B frontend/design-system change.
- **Applicable ADRs:** ADR-001 modular monolith; ADR-004 registry-ready is not published.
- **Mandatory standards:** UI/accessibility/workflows, security, documentation/records.
- **Readiness boundary:** presentation/navigation only; no new authority, state, API, data, deployment, or publication behavior.

## 2. Whole-project impact map

- **Repository areas:** `apps/admin-portal`, controlled SDA/agent documentation.
- **NLI bounded domains:** presentation layer across registry, field, verification, publication/signage, reporting, and administration.
- **Product modules/applications:** protected operator portal; public portal is regression-only.
- **User roles/institutions:** editor, admin, viewer, agency viewer; no institution model change.
- **Territorial/data scopes:** existing session and API scopes only.
- **Trust zones:** protected browser UI; public/protected boundary unchanged.
- **Environments:** local, controlled staging/pilot; production not authorized.
- **Lifecycle stages:** navigation and display only across existing states.
- **Partner/external dependencies:** none added.
- **Operational/support/rollout impact:** navigation and training references must be updated before deployment; rollback is a frontend commit revert.

## 3. Selected skills

### Cross-cutting S01–S16

| Skill | Trigger | Required output |
|---|---|---|
| S01 | Every task | Authority, scope, stop conditions |
| S03 | Class B work order | Acceptance-criterion implementation plan |
| S10 | User-visible workflow and design change | Responsive, accessible, bilingual workflow evidence |
| S11 | Required semantic evidence | Type, guard, quality, build, browser and role evidence |
| S12 | GitHub delivery | Separate branch, draft PR, exact-head proof |
| S16 | Completion/handoff | Self-audit, limits, exact next action |

### Whole-project S17–S31

| Skill | Trigger | Required output |
|---|---|---|
| S18 | Next.js shell, responsive behavior and design tokens | Shared operator shell and design-system guard |
| S20 | Shared chrome also surrounds public routes | Public-route regression evidence |
| S21 | Registry operator navigation and record density | Registry workflow usability check |
| S22 | Field/mobile navigation | Mobile drawer, quick navigation, touch/reflow evidence |
| S23 | Verification route orientation | Verification workflow regression check |
| S24 | Signage/publication routes in navigation | Publication authority remains unchanged |
| S27 | Reporting route in role-aware navigation | Read-only role regression check |
| S29 | Responsive/performance effect | No external dependency; CSS-only layout overhead |
| S30 | Staff navigation change | Training/release note requirement |
| S31 | Separate controlled delivery stream | Draft PR and rollout boundary |

### Considered but not applicable

| Skill | Why not applicable |
|---|---|
| S07 | No database, migration, data, or fixture effect |
| S08 | No API/auth/session/authorization behavior change |
| S09 | No geometry, map authority, evidence or publication-state change |
| S19 | No backend/domain logic change |
| S25 | No integration or notification change |
| S26 | No worker/import/export behavior change |
| S28 | No infrastructure or environment configuration change |

## 4. Scope matrix

### In scope

- Shared protected workspace structure and navigation.
- Compact protected masthead and content density.
- Desktop/mobile responsive rules using existing classes and tokens.
- Source guard and design-contract documentation.

### Supporting evidence

- Existing route ownership, role policy, localization dictionary, design guards, density guards, public/staff split, and current protected page components.

### Separate maintenance

- Any pre-existing component defect discovered while applying the shell.
- Any required browser/polyfill support decision for older unsupported browsers.

### Prohibited

- API/backend/data model/migration changes.
- New roles/states/authority/metrics.
- Paid services, external dependencies, workflow-file edits, deployment, PR #7 or PR #8 changes.

## 5. Current-state evidence inspected

| Domain/object/workflow | Source path | What it establishes |
|---|---|---|
| Root layout | `apps/admin-portal/app/layout.tsx` | Shared CSS import boundary |
| Shared chrome | `components/SiteChrome.tsx`, `components/RoleAwareChrome.tsx` | Public/protected wrapper, route/session behavior |
| Route policy | `components/site-data.ts` | Role-visible and route-access rules |
| Localization | `components/i18n.tsx` | Existing English/Spanish labels available to the shell |
| Registry | `app/registry/page.tsx`, `components/RegistryCorePanel.tsx` | Search-first operator workflow and table/mobile alternatives |
| Design contract | `apps/admin-portal/DESIGN.md`, `app/globals.css` | Frozen visual tokens and anti-patterns |
| Quality controls | `scripts/design-system-freeze-guard.mjs`, `scripts/density-guard.mjs` | Existing source-level UI controls |

## 6. Acceptance-criterion plan

| AC | Observable result | Change | Positive evidence | Negative/authority evidence |
|---|---|---|---|---|
| AC-01 | Consistent protected desktop shell | Refactor `RoleAwareChrome` and add stylesheet | Protected routes render sidebar/content grid | Guest route still uses public chrome |
| AC-02 | User, role and current section visible | Add role/location utility regions | Role/session values originate from existing session | No institution/scope or permission invented |
| AC-03 | Mobile navigation usable | Drawer, scrim and quick nav | Reflow and keyboard/touch review | Reduced motion; no icon-only labels |
| AC-04 | Denser operational pages | Protected-only CSS overrides | Tables/forms/panels use compact spacing | Public pages not selected by protected CSS |
| AC-05 | Civic identity retained | Compact staff masthead, existing tokens | Coat of arms and EG accents remain | Guard rejects gradients/glass/pills |
| AC-06 | Workflow behavior unchanged | Presentation-only code | Existing route/auth/data tests | No API/session function modified |
| AC-07 | Accessible/localized shell | Reuse existing translations and semantics | Quality/keyboard/mobile evidence | No new untranslated workflow copy |
| AC-08 | Exact-head verification | Add guard and run full portal gates | Type/quality/build/browser evidence | CI-startup failure classified separately |

## 7. Expected changed paths

### Add

- `apps/admin-portal/app/operator-shell.css`
- `apps/admin-portal/scripts/operator-shell-guard.mjs`
- `docs/sda/work-orders/NLI-WO-003-operator-interface-foundation.md`
- `docs/agent/task-contexts/NLI-WO-003-operator-interface-foundation.md`

### Modify

- `apps/admin-portal/app/layout.tsx`
- `apps/admin-portal/components/RoleAwareChrome.tsx`
- `apps/admin-portal/package.json`
- `apps/admin-portal/DESIGN.md`

### Remove/deprecate

- None.

## 8. Effect assessment

- **Architecture/domain boundaries:** unchanged; presentation layer only.
- **Database/migrations/reference data/fixtures:** none.
- **API/contracts/identity/authorization:** unchanged; session values only displayed.
- **Security/privacy/audit/evidence:** no new fields or logs; full name and role already available in session UI.
- **GIS/geometry/provenance:** map container presentation only.
- **Frontend/design system/accessibility/localization:** primary effect.
- **Backend/domain logic/transactions:** none.
- **Citizen/public services:** regression-only.
- **Registry/operator case management:** navigation and density only.
- **Field/mobile/offline synchronization:** navigation/reflow only; sync behavior unchanged.
- **Verification/quality/recapture:** presentation only.
- **Publication/corrections/certificates/signage:** navigation only; authority unchanged.
- **Agency integrations/notifications/interoperability:** none.
- **Imports/exports/workers/batch jobs:** none.
- **Reporting/analytics/data products:** navigation/display only.
- **Infrastructure/environments/platform:** no configuration change.
- **Performance/scalability/resilience:** one local stylesheet; no dependency or request added.
- **Operations/backup/restore/DR:** not applicable; revert commit for recovery.
- **Support/training/change adoption:** staff navigation guide/screenshots required before rollout.
- **Programme roadmap/release/rollout:** separate draft PR; no deployment authorization.

## 9. Decisions and RFIs

| Decision | Classification | Owner | Blocking? |
|---|---|---|---|
| Retain public home and primary colour/coat-of-arms direction | Programme/design direction | Programme Owner | No |
| Use existing system font stack; add no external font | Supportability/cost | Work order | No |
| Keep existing roles, routes and workflow states | Protected architecture | SDA | No |
| Federated cross-domain search | Deferred Class B/API decision | SDA | Not for this foundation |

## 10. Execution sequence

1. Create exact-base branch and controlled documents.
2. Add protected operator stylesheet and source guard.
3. Refactor shared role-aware chrome without changing route or session authority.
4. Import stylesheet and update design contract/package scripts.
5. Run source guard, TypeScript, full quality and build gates locally when a full checkout is available.
6. Capture desktop/mobile role/language screenshots.
7. Open draft PR and report exact-head evidence and CI limitation.

## 11. Recovery and compatibility

- **Rollback safe:** yes; revert UI commits.
- **Forward recovery:** correct CSS/component behavior in the same work-order branch.
- **Idempotency:** not applicable; no data mutation.
- **Breaking/compatibility effect:** no intended route/API behavior change.
- **External effects:** none.
- **Monitoring/alert changes:** none.
- **Support/training/communication:** updated operator navigation reference before deployment.
- **Rollout/cutover gate:** browser evidence, quality/build gates, SDA acceptance and explicit deployment authorization.

## 12. Submission plan

- **Draft PR target:** `main` from `nli/wo-003-operator-interface-foundation`.
- **Required workflows/jobs:** frontend build/quality plus repository-required checks.
- **Expected exact-head evidence:** changed paths, source guard, typecheck, quality, build, role/language/viewport screenshots.
- **Required artifacts:** protected routes at desktop/mobile; public regression; denied/loading/empty states where available.
- **Review request:** criterion-by-criterion evidence; no production claim.

## 13. Agent declaration

- [x] Authority and scope are explicit.
- [x] Whole-project impact is mapped.
- [x] Applicable skills are selected.
- [x] Not-applicable skills have rationale.
- [x] Every criterion has positive and negative evidence planned.
- [x] Reserved decisions are not silently embedded.
- [x] Out-of-scope defects will use S14.
- [x] Operational, support, rollout, and recovery effects are addressed.
- [x] No prohibited path or behavior is planned.
