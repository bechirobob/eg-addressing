# PDF Style Guide for Training Manuals

## Purpose

This guide defines the visual and editorial standard for all PDF training manuals in the Equatorial Guinea National Digital Addressing training package.

## Required outputs

Every manual must be produced as a paired bilingual set:

```text
{Manual-Name}-ES.pdf
{Manual-Name}-EN.pdf
```

The Spanish version is the primary government-facing copy. The English version is the review, partner, and coordination copy.

## Page structure

Every manual must include:

1. Cover
2. Document control page
3. Table of contents
4. How to use this manual
5. Audience and responsibilities
6. Training outcomes
7. Key terms
8. Privacy and safety rules
9. Training modules
10. Step-by-step procedures
11. Practice exercises
12. Common mistakes
13. Troubleshooting
14. Assessment checklist
15. Reference index
16. Support/contact page

## Cover standard

The cover should feel like official civic training material.

Include:

- Republic / national addressing identity line;
- manual title;
- language version label: `Versión española` or `English version`;
- controlled-pilot status where appropriate;
- BeCore operational/support contact label where appropriate.

Avoid:

- decorative gradients;
- stock-photo clutter;
- AI/tool/process attribution;
- internal dates, file paths, commit hashes, or task IDs;
- fake government seals unless approved assets are provided.

## Document control page

Use plain labelled lines, not a table or card layout:

```text
Document title: Manual title.
Language: Spanish or English.
Audience: Target audience.
Status: Controlled pilot training material.
Prepared for: Equatorial Guinea National Digital Addressing pilot.
Operational support: BeCore.
```

Do not include automatic generated timestamps or internal file locations.

## Table of contents

Required in every manual.

Rules:

- Use clear numbered sections.
- Keep section titles short.
- Match the section order in the Spanish and English versions.
- Page numbers should be included in final PDF exports when the rendering system supports them cleanly.

## Reference index

Required in every manual.

The index is an alphabetical lookup section for important terms, procedures, and warnings.

Examples:

```text
Address code — sections 3.2, 5.1
Approval lock — sections 6.1, 6.3
Field check — sections 4.2, 8.1
GPS accuracy — sections 4.1, 9.2
Official record — sections 5.4, 7.1
Submitted location — sections 3.1, 4.3
```

If exact page-number indexing is not available at draft stage, use section-number references. Final PDFs may convert these to page references later.

## Typography and layout

Mirror the frozen addressing system document/page style:

- system UI sans-serif typography for labels, headings, and body text;
- heavy deep-navy headings;
- uppercase letter-spaced section labels;
- readable body text;
- wide margins;
- restrained navy/green/gold/red/ivory palette;
- ivory or white background;
- clean pagination that allows short related sections to share a page when they fit, while preventing stranded headings at page foot.

Avoid:

- SaaS cards everywhere;
- pill clutter;
- emoji;
- decorative glass/blur effects;
- cramped tables;
- tables in manual body content unless explicitly approved for a specific manual;
- colored callout containers;
- brown/gold side ticks beside cover labels;
- shadows under the coat of arms or other page elements;
- dense paragraphs without steps or examples.

## Training module pattern

Each module should include:

1. What this module teaches.
2. Why it matters.
3. Step-by-step procedure.
4. Example scenario.
5. Common mistakes.
6. Check your understanding.

## Exercises

Every manual must include practical exercises.

Exercise format:

```text
Exercise title
Goal
Scenario
Steps
Expected result
Trainer notes
```

Exercises must use training examples, not real private records.

## Checklists

Use checklists for operational readiness and assessment.

Examples:

```text
Before submitting a location request:
- Address description is clear.
- GPS accuracy is acceptable or a manual correction was noted.
- Contact details are correct.
- No full private identity number is exposed in public notes.
```

## Screenshots

Screenshots are allowed only when they are safe and useful.

Rules:

- Use staging-safe screenshots.
- Hide or crop private data.
- Do not show temporary usernames, passwords, tokens, cookies, or browser developer tools.
- Prefer annotated screenshots with simple callouts.
- Do not include localhost/private-port URLs.
- If using the preview URL, label it as controlled pilot preview only.

## Approved terminology

Use the simplified operator terms:

1. Use “official record”; avoid “canonical record”.
2. Use “ready for approval”; avoid “registry-ready”.
3. Use “public status”; avoid “publication state”.
4. Use “approval lock” or “public release lock”; avoid “release gate”.
5. Use “submitted location” or “location request”; avoid “geotag submission”.
6. Use “location evidence”; avoid “spatial evidence”.
7. Use “map evidence”; avoid “geometry evidence”.
8. Use “activity log”; avoid “audit log” unless explaining a formal audit term.
9. Use “login session”; avoid “auth token” or “session token”.
10. Use “sign user out everywhere”; avoid “revoke sessions”.
11. Use “test record” or “training example”; avoid “smoke fixture” or “pilot fixture”.

## Language quality

Spanish:

- Use formal but plain government Spanish.
- Prefer `solicitud de ubicación`, `registro oficial`, `listo para aprobación`, and `bloqueo de publicación pública`.
- Avoid literal English technical calques unless they are accepted operational terms.

English:

- Use plain operational English.
- Keep sentences direct.
- Avoid engineering terms unless the admin audience needs them.

## PDF QA checklist

Before a manual is accepted:

- Text extraction finds no placeholders such as `TODO`, `lorem`, `draft-only`, or template notes.
- Visual review finds no overlap, cut-off text, broken tables, or unreadable screenshots.
- Table of contents exists.
- Reference index exists.
- Spanish and English versions have matching section structure.
- No internal URLs, file paths, commit hashes, generated timestamps, AI/tool names, or temporary credentials appear.
- Public-release wording preserves the controlled-pilot boundary.
- BeCore contact/support references are appropriate and not over-branded.
