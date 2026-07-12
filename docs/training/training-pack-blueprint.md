# Government Training Pack Blueprint

## Objective

Create a formal bilingual PDF training package for the Equatorial Guinea National Digital Addressing platform. The manuals must be deep enough for training, simple enough for non-technical users, and official enough for government review.

## Audience model

The package is role-based. Each manual teaches one audience what they need to do, what they must avoid, and how to confirm their work.

| Manual | Spanish title | English title | Primary audience | Main outcome |
|---|---|---|---|---|
| 1 | Guía pública para ciudadanos, residentes y empresas | Public User Guide for Citizens, Residents, and Businesses | Public users | Submit, check, and track a location request safely. |
| 2 | Manual del personal de campo | Field Officer Manual | Field teams and survey officers | Capture reliable location evidence and field notes. |
| 3 | Manual del oficial de registro | Registry Officer Manual | Registry operators | Review submitted locations and prepare official records. |
| 4 | Manual del revisor institucional | Institutional Reviewer Manual | Ministry, municipal, and delegated reviewers | Review evidence, readiness, and governance status. |
| 5 | Manual del administrador del sistema | System Administrator Manual | System admins and appointed operators | Manage access, login sessions, and safe administration. |
| 6 | Guía de publicación y emisión oficial | Publication and Official Issuance Guide | Approval authorities and admins | Understand public release locks, certificates, signage, and exports. |
| 7 | Guía de informes, actividad y auditoría | Reports, Activity, and Audit Guide | Supervisors, reviewers, BeCore operations | Read reports, activity logs, readiness checks, and exports. |
| 8 | Manual de capacitación para el piloto | Pilot Training Manual | Trainers and supervisors | Run a structured pilot training session with exercises and assessment. |

## Required bilingual deliverables

Each manual must be produced in two matching versions:

```text
EG-Addressing-{Manual-Name}-ES.pdf
EG-Addressing-{Manual-Name}-EN.pdf
```

The Spanish and English versions must match in:

- section order;
- training modules;
- numbering;
- exercises;
- checklists;
- reference index topics;
- page design system.

The wording may adapt naturally per language, but the training structure must stay aligned.

## Required index system

Every manual must include both:

| Section | Required? | Purpose |
|---|---:|---|
| Table of Contents | Yes | Shows the manual structure and page flow. |
| Reference Index | Yes | Alphabetical lookup for topics, procedures, warnings, and terms. |

The reference index should include operational topics such as:

- approval lock;
- address code;
- field check;
- GPS accuracy;
- location evidence;
- official record;
- public release lock;
- public status;
- ready for approval;
- record history;
- submitted location;
- training example.

## Standard manual structure

Every manual should follow this structure unless the audience requires a small adaptation:

1. Cover
2. Document control page
3. Table of contents
4. How to use this manual
5. Audience and responsibilities
6. Training outcomes
7. Key terms
8. Privacy and safety rules
9. Module 1: system overview for this role
10. Module 2: daily workflow
11. Module 3: step-by-step procedures
12. Module 4: review and correction process
13. Module 5: common problems and what to do
14. Practice exercises
15. Common mistakes
16. Troubleshooting
17. Assessment checklist
18. Reference index
19. Support/contact page

## Writing standard

Use official but simple language.

- Prefer short sentences.
- Define technical terms before use.
- Use step numbers for procedures.
- Use warnings only when a mistake affects privacy, public release, or official records.
- Avoid sales language.
- Avoid engineering jargon in user-facing text.
- Explain consequences plainly.

## Government and ownership framing

Training materials must frame the system as controlled pilot infrastructure until formal adoption.

Use:

- Government ownership and approval framing.
- BeCore as operational/support contact where appropriate.
- Controlled pilot and training context.
- Clear distinction between submitted locations, ready-for-approval records, and published official records.

Avoid:

- claims that pilot records are legally final;
- publication/signage promises before approval;
- fake legal authority;
- internal project logs or implementation process notes.

## Privacy and safety baseline

All manuals must include safety notes appropriate to their audience:

- Full D.I.P. details are never placed in public examples.
- Public users should see only public-safe status and proof information.
- Operators must handle identity and location evidence only inside protected staff workflows.
- Screenshots must not show real private people, real full D.I.P. numbers, temp credentials, or internal secrets.
- Training examples must be clearly labeled as training examples.

## Sequencing plan

### Lane 1 — Blueprint and shared standards

Deliver:

- this blueprint;
- bilingual glossary;
- PDF style guide.

### Lane 2 — First paired manual

Create:

- `EG-Addressing-Public-User-Guide-ES.pdf`
- `EG-Addressing-Public-User-Guide-EN.pdf`

This first manual becomes the template for page structure, title treatment, table of contents, exercises, and reference index.

### Lane 3 — Core operations manuals

Create:

- Field Officer Manual, ES and EN;
- Registry Officer Manual, ES and EN;
- Institutional Reviewer Manual, ES and EN.

### Lane 4 — Governance and administration manuals

Create:

- System Administrator Manual, ES and EN;
- Publication and Official Issuance Guide, ES and EN;
- Reports, Activity, and Audit Guide, ES and EN.

### Lane 5 — Trainer pack

Create:

- Pilot Training Manual, ES and EN;
- quick-reference checklists;
- exercises and assessment sheets.

## Acceptance criteria for every PDF

A manual is complete only when:

- Spanish and English versions exist.
- Table of contents is present.
- Reference index is present.
- Glossary terms match the approved bilingual glossary.
- Screenshots, if used, are staging-safe and privacy-safe.
- No internal paths, tool names, generated timestamps, commits, or temporary credentials appear.
- All public-release language preserves the controlled-pilot boundary.
- The PDF has been visually checked after export.
- Text extraction confirms there is no placeholder text or draft-only wording.

## First-manual recommendation

Start with the Public User Guide because it sets the simplest shared language and helps reviewers understand the public value of the platform before deeper staff manuals.
