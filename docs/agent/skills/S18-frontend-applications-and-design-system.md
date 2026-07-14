# S18 — Frontend Applications and Design System

## Invoke when

- changing the Next.js public/operator portal or future field application;
- adding routes, forms, tables, maps, reports, certificates, or shared components;
- changing browser state, client data access, responsive behavior, or design tokens.

## Required inputs

- actual OpenAPI/generated client types;
- UI/accessibility/localization standard;
- route ownership and role policy;
- shared design-system conventions;
- affected workflow and data-classification rules.

## Procedure

1. Identify application surface, route, role, scope, task, and record state.
2. Define server/client component and data-fetching boundaries.
3. Use authoritative generated/shared contracts; do not hand-copy API types.
4. Separate public and protected layouts, navigation, session, and error behavior.
5. Define loading, validation, denied, empty, conflict, retry, offline/queued, and completion states.
6. Keep authorization server-side; client guards improve usability only.
7. Use shared tokens/components and preserve the restrained human-designed interface direction.
8. Implement complete Spanish and English content, including errors, help, reports, and artifacts.
9. Meet accessibility requirements and provide non-map alternatives for essential spatial tasks.
10. Prevent tokens, evidence keys, internal identifiers, and restricted fields from entering URLs, client bundles, logs, analytics, or screenshots.
11. Test forms, navigation, history, API failures, keyboard use, reflow, localization, printing, and role/state behavior.
12. Capture exact-head workflow evidence by role, language, viewport, state, and environment.

## Outputs

- route/component and workflow map;
- generated-contract/type result;
- accessible bilingual implementation;
- responsive/browser evidence pack;
- design-system changes and tests;
- client security/performance impact.

## Stop or RFI conditions

Stop when:

- the UI requires a new workflow state, role, or permission;
- a public screen would expose internal/restricted data;
- an official label, proof, certificate, or signage claim lacks authority;
- a map is the only usable path for an essential task;
- a dynamic backend response cannot be enumerated safely.

## Evidence gate

Before review:

- server authorization and public-safe projection are verified;
- Spanish/English and accessibility checks pass;
- mobile/desktop and failure states are evidenced;
- generated contracts match the backend;
- screenshots identify exact commit, role, language, viewport, and fixture boundary.

## Anti-patterns

- Generic SaaS dashboards, unnecessary cards, modals, gradients, or glass effects.
- Fetching protected data and hiding it client-side.
- Hardcoded untranslated strings in changed workflows.
- Optimistic success before authoritative commit.
- Treating local/offline save as registry acceptance.
- Using color or icons as the only state signal.
