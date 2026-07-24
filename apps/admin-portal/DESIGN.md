# National Addressing Platform UI Contract

This is the frozen design-system contract for the Equatorial Guinea National Addressing Platform admin portal.

## Status

Phase 0 freeze: the current government-grade direction is the baseline for all future phases.

## Product posture

The platform is a controlled institutional pilot and implementation-planning system, not a final national production service until production hardening and government publication authority are complete.

## Visual direction

Use a calm government-service interface:

- warm off-white page background;
- dark navy headings and readable body text;
- restrained Equatorial Guinea colour accents;
- compact page headers;
- thin borders and row dividers;
- tables or row lists for records and queues;
- practical forms with clear labels;
- secondary technical detail behind disclosures;
- restrained radii from shared tokens only;
- no decorative shadows, glow effects, or generic SaaS gradients.

## Shared tokens

All new surfaces should use the existing shared tokens in `app/globals.css`:

- `--gov-bg`
- `--gov-surface`
- `--gov-surface-raised`
- `--gov-ink`
- `--gov-ink-strong`
- `--gov-muted`
- `--gov-line`
- `--gov-blue`
- `--gov-green`
- `--gov-gold`
- `--gov-red`
- `--gov-radius`
- `--gov-radius-sm`
- `--gov-control-height`
- `--gov-shadow`

Do not introduce a second visual token system for a new module unless this file is intentionally revised.

## Page rule

Every page must have:

1. one clear purpose;
2. one primary action or primary workflow;
3. clear data fields;
4. public/private data boundaries;
5. readable empty/loading/error states.

Do not add a dashboard block unless the user can act on it.

## Language rule

Use plain official service language:

- register;
- check;
- track;
- review;
- verify;
- publish;
- export;
- approve;
- reject;
- return for correction.

Avoid hype and vague automation language. Do not use:

- AI dashboard;
- command center;
- mission control;
- smart civic platform;
- autonomous platform;
- futuristic admin panel.

## Component rule

Prefer these reusable patterns:

- `page-shell` for page bounds;
- section headings with `section-label` only when useful;
- `public-task-panel` for official work panels;
- tables for records and queues;
- compact rows for mobile records;
- `details` / disclosure blocks for advanced or secondary work;
- text-first status with colour as secondary support.

Avoid these anti-patterns:

- decorative card walls;
- pill clouds;
- fake widgets;
- emoji controls;
- raw payload-style UI;
- repeated platform overview grids inside staff pages;
- exposing operator-only fields on public routes.

## Public/staff boundary

Public routes are for citizens and public verification:

- `/`
- `/geotag`
- `/track`
- `/issue`
- `/code/[code]`

Protected routes are for staff/operator workflows:

- `/field`
- `/registry`
- `/signage`
- `/reports`
- `/territories`
- `/exports`
- `/verify`

Public routes must not expose private contact data, raw evidence files, internal reviewer notes, full D.I.P. data, or operator-only status details.

## Protected operator workspace

Protected routes use one shared workspace rather than repeating a generic page navigation block on every screen.

Desktop rules:

- use a stable left navigation rail and one primary content column;
- show the current section, signed-in user, and role context;
- retain the coat of arms and national identity in a compact masthead;
- prioritize tables, record rows, search, and the next valid action over decorative summaries;
- keep advanced or infrequent controls behind clear disclosures;
- use the available desktop width for operational tables without creating empty margins.

Mobile rules:

- replace the desktop rail with a text-labeled navigation drawer;
- keep high-frequency authorized routes reachable through compact quick navigation;
- show record rows instead of shrinking desktop tables below usable widths;
- preserve touch targets, visible focus, reduced-motion behavior, and non-map alternatives;
- do not represent local, queued, provisional, or unpublished work as registry acceptance.

The operator workspace stylesheet is `app/operator-shell.css`. It may override spacing and layout on authenticated protected routes, but it must use the shared `--gov-*` tokens and must not change public/protected authority, route access, API behavior, or workflow states.

## Verification rule

Before reporting a UI phase complete, run:

```bash
npx tsc --noEmit --pretty false
npm run test:quality
npm run build
```

For live/deployed work, also verify representative public and protected routes in the browser, check console output, and clean temporary smoke data.
