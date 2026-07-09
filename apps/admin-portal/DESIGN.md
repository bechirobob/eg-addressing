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

## Verification rule

Before reporting a UI phase complete, run:

```bash
npx tsc --noEmit --pretty false
npm run test:quality
npm run build
```

For live/deployed work, also verify representative public and protected routes in the browser, check console output, and clean temporary smoke data.
