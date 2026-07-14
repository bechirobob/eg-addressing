# S20 — Citizen Portal and Public Services

## Invoke when

- changing public lookup, submission, geotagging, tracking, correction reporting, or proof;
- collecting citizen identity, contact, evidence, or precise coordinates;
- changing public statuses, privacy notices, rate limits, or accessible public workflows.

## Required inputs

- approved public-service purpose and data-classification rules;
- public API/OpenAPI and projection contracts;
- publication/correction authority rules;
- privacy, accessibility, localization, GIS, and abuse-control standards;
- current citizen workflow and support evidence.

## Procedure

1. Define the citizen task, public value, collected data, purpose, and public/protected boundary.
2. Minimize fields and explain sensitive identity/contact/evidence/coordinate collection.
3. Provide privacy notice, acknowledgement where required, retention/contact expectations, and a citizen-safe tracking reference.
4. Use explicit public-safe request and response models.
5. Distinguish submitted, under review, field check, registry-ready, published, corrected, disputed, rejected, and retired states.
6. Prevent enumeration of restricted/unpublished records and apply distributed abuse/rate controls.
7. Preserve citizen coordinates/photos/map choices as evidence, not canonical truth.
8. Provide recoverable validation, duplicate-submit handling, low-bandwidth behavior, and map alternatives.
9. Tie public proof and certificates to an exact authorized release with correction/revocation history.
10. Test privacy, mobile, keyboard, language, bot/abuse, network failure, duplicate, tracking, and public projection behavior.
11. Measure completion, abandonment, errors, abuse, accessibility, and support demand without invasive analytics.

## Outputs

- citizen journey and data-purpose inventory;
- public-safe API contracts;
- privacy and retention impact;
- accessible bilingual workflows;
- tracking/correction/publication behavior;
- abuse controls and support metrics.

## Stop or RFI conditions

Stop when:

- a public field or precision has no publication rule;
- identity/contact collection lacks necessity or authority;
- a submission would auto-create official state;
- tracking would reveal protected workflow details;
- a proof/certificate would be issued without publication authority.

## Evidence gate

Before review:

- public projection and privacy tests pass;
- evidence cannot auto-promote to canonical state;
- mobile/accessibility/language evidence exists;
- abuse/rate-limit and duplicate behavior execute;
- public proof and revocation/correction paths are verified.

## Anti-patterns

- Treating a citizen pin as official geometry.
- Asking for identity documents by default.
- Returning internal IDs, evidence keys, reviewer notes, or operator states publicly.
- Calling submitted or registry-ready records verified/published.
- Blocking capture because an external geocoder is unavailable.
- Requiring a map with no non-map alternative.
