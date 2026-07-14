# Skill 11 — UI Workflows, Accessibility, and Localization

## Use when

Use for public, operator, administrative, field, report, certificate, signage, or training interfaces.

## Objective

Deliver clear, role-appropriate, accessible, bilingual workflows with minimal unnecessary interaction and truthful state/authority communication.

## Procedure

1. Identify the user role, institution/scope, task, decision, prerequisite, record state, and expected audit/evidence result.
2. Map the current and proposed workflow step by step.
3. Keep capture, review, approval, publication, audit, and platform operations visually and conceptually separate.
4. Confirm server-side authorization for every protected action; UI visibility is only usability.
5. Design loading, empty, validation, denied, conflict, offline, retry, and completion states.
6. Minimize repeated entry, modal chains, navigation, and confirmations while preserving segregation of duties.
7. Implement complete Spanish and English coverage for labels, validation, errors, help, confirmation, reports, and official outputs.
8. Test WCAG 2.2 AA expectations:
   - keyboard operation;
   - focus order/visibility;
   - semantic labels/headings/landmarks;
   - contrast and reflow;
   - error association;
   - status announcements;
   - target size;
   - non-color meaning;
   - reduced motion;
   - accessible tables/maps.
9. For maps, provide source/confidence/official-state labels and a text/list alternative.
10. For field/offline workflows, distinguish local, queued, synchronized, accepted, and rejected states.
11. Capture exact-head browser evidence by role, language, viewport, state, environment, and fixture classification.
12. Run existing design-system, route-ownership, accessibility, localization, and browser smoke checks.

## Required evidence

- Role/task/authority statement
- Before/after workflow steps
- Desktop/mobile screenshots
- Spanish/English coverage result
- Keyboard/accessibility result
- Loading/error/denied/recovery states
- Server allow/deny tests
- Audit/state-transition effect
- Design-system guard result

## Stop and escalate when

- The UI would imply official authority that does not exist.
- A high-impact action lacks confirmation/approval policy.
- A sensitive field has no purpose or projection rule.
- Offline conflict behavior is undefined.
- Translation could alter legal or official meaning.

## Anti-patterns

- Generic SaaS dashboards, unnecessary cards, decorative gradients, or glass effects.
- Hiding a button and calling the feature authorized.
- Mixing pilot, registry-ready, approved, verified, and published language.
- Capturing only a happy-path desktop screenshot.
- Translating navigation but leaving workflow errors/help in one language.
- Showing a map pin as official without source/quality/status.
