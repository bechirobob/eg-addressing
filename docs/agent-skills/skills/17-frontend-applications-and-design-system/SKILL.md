# Skill 17 — Frontend Applications and Design System

## Use when

Use for Next.js/TypeScript public, operator, administrative, field, report, certificate, signage, or shared-UI work.

## Objective

Build maintainable, accessible, bilingual frontend applications that accurately reflect authority, record state, API contracts, and constrained-network conditions.

## Procedure

1. Identify application surface, route, role, scope, task, and data classification.
2. Confirm server component/client component boundaries and data-fetching strategy.
3. Use generated/shared API contracts; do not hand-invent response types when authoritative contracts exist.
4. Separate public and protected route ownership, layouts, navigation, and session behavior.
5. Define browser state, cache, retry, optimistic behavior, duplicate-submit prevention, and error recovery.
6. Keep authorization server-side; client guards may improve usability but never grant access.
7. Use shared design tokens/components and preserve the restrained interface direction.
8. Implement complete Spanish and English content, including errors, help, empty states, confirmation, reports, and official artifacts.
9. Meet accessibility requirements and provide non-map alternatives for essential spatial tasks.
10. Handle responsive, mobile, low-bandwidth, loading, offline/queued, conflict, and denied states honestly.
11. Avoid leaking tokens, internal IDs, evidence object keys, or restricted fields into client bundles, URLs, logs, analytics, or screenshots.
12. Test rendering, forms, navigation, role visibility, API errors, keyboard use, accessibility, localization, browser history, and printing/export where affected.
13. Capture workflow evidence by role, language, viewport, state, environment, and exact commit.

## Design-system responsibilities

- Tokens for typography, spacing, contrast, focus, status, and print.
- Reusable form, table, disclosure, timeline, map, evidence, status, and confirmation patterns.
- Stable component APIs and deprecation path.
- Accessible defaults rather than per-screen repair.
- No decorative pattern that obscures information or increases clicks.

## Required evidence

- Route/component inventory
- API contract/type result
- Role/state workflow map
- Spanish/English proof
- Keyboard and accessibility checks
- Responsive screenshots
- Loading/error/denied/conflict/offline states
- Design-system and browser tests
- Performance/bundle impact where material

## Stop and escalate when

- The UI needs a new workflow state or permission.
- A public page would expose internal/restricted data.
- An official label/certificate/signage claim lacks authority.
- A map is the only way to complete an essential task.
- The API response is dynamic and cannot be safely typed/projected.

## Anti-patterns

- Generic SaaS dashboards or excessive cards/modals.
- Fetching protected data and hiding it client-side.
- Hardcoded untranslated strings in changed workflows.
- Optimistic success before authoritative commit.
- Treating local/offline save as registry acceptance.
- Copying API types manually into components.
- Using color or icons as the only state signal.
