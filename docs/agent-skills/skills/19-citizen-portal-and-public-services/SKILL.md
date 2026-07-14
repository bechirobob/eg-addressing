# Skill 19 — Citizen Portal and Public Services

## Use when

Use for anonymous or low-assurance public lookup, address/location submission, geotagging, tracking, correction reporting, public proof, privacy notices, or citizen-facing status communication.

## Objective

Deliver simple, accessible, bilingual public services that collect only necessary data, resist abuse, preserve evidence, and never imply official status before authorized publication.

## Procedure

1. Define the citizen task, public value, approved purpose, data collected, and public/protected boundary.
2. Minimize fields and explain why sensitive identity, contact, evidence, or precise coordinates are requested.
3. Provide clear privacy notice, acknowledgement/consent behavior where required, retention/contact expectations, and citizen-safe tracking reference.
4. Use explicit public-safe request and response models.
5. Separate:
   - submission received;
   - queued or under review;
   - needs more evidence/field verification;
   - registry-ready;
   - published;
   - corrected, disputed, rejected, or retired.
6. Prevent public enumeration of restricted/unpublished records and apply distributed abuse/rate controls.
7. Preserve submitted coordinates/photos/map selections as evidence, not canonical truth.
8. Provide recoverable validation, duplicate-submit handling, low-bandwidth behavior, and accessible map alternatives.
9. Keep public proof/certificates tied to an exact authorized publication release and revocation/correction path.
10. Ensure correction/reporting status reveals only public-safe information.
11. Test Spanish/English, mobile, keyboard, assistive technology, bot/abuse, privacy, network failure, duplicate, and public-projection cases.
12. Monitor completion, abandonment, error, abuse, accessibility, and support demand without collecting unnecessary analytics data.

## Required evidence

- Citizen journey and interaction count
- Data-purpose/classification inventory
- Privacy notice and retention implications
- Public-safe API projection tests
- Abuse/rate-limit tests
- Mobile/accessibility/localization evidence
- Evidence-versus-canonical separation proof
- Tracking/correction/publication-state tests
- Public proof/revocation behavior
- Support and adoption metrics

## Stop and escalate when

- A public field or precise coordinate has no approved publication rule.
- Identity/contact collection is not necessary or authorized.
- A submission would auto-create official state.
- Public tracking would disclose protected workflow details.
- A certificate/proof would be issued without publication authority.

## Anti-patterns

- Treating a citizen pin as official geometry.
- Asking for identity documents by default.
- Returning internal IDs, evidence keys, reviewer notes, or operator states publicly.
- Saying “verified” when the record is only submitted or registry-ready.
- Blocking capture because an external geocoder is unavailable.
- Requiring a map interaction with no text/list alternative.
- Using opaque errors that force citizens to contact support for ordinary correction.
