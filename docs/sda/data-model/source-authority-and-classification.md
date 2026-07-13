# Source Authority and Classification Model

**Status:** Draft for SDA review

## 1. Authority levels

| Authority class | Meaning | Canonical effect |
|---|---|---|
| `official-government` | Official source or decision from competent authority. | May establish canonical reference/certified values. |
| `registry-authority` | SDA/registry operator approval. | May promote candidate to canonical registry. |
| `gis-data-authority` | Approved GIS/boundary/geometry authority. | May approve geometry/boundary version. |
| `field-verified` | Field team observation/evidence. | Supports decisions; not alone publication authority. |
| `citizen-submitted` | Public/citizen intake. | Candidate/evidence only. |
| `external-map-suggestion` | OSM/geocoder/map-derived value. | Suggestion only, requires review. |
| `imported-reference` | Imported package not yet accepted as official. | Reference/evidence until authority status is approved. |
| `test-fixture` | Dev/test fixture. | Never production canonical. |

## 2. Data classification

| Class | Examples | Projection |
|---|---|---|
| Public | approved public code, released label, released location. | Public/partner. |
| Government internal | unpublished registry state, operational routing area, source package status. | Operator/authorized partner only. |
| Restricted | citizen contact, precise unpublished GPS, evidence files, DIP fragments, dispute details. | Protected operator only. |
| Highly restricted | full identity document values, credentials, privileged keys. | Avoid storing unless separately authorized. |

## 3. Provenance chain

Every canonical fact should be traceable to:

- source package/record or intake case;
- actor/system;
- time captured and time recorded;
- validation checks;
- approval event;
- canonical record version;
- publication release if public.

## 4. Public safety rule

A value being present in PostgreSQL does not make it public. Public, partner, signage, certificate, and export projections must use explicit safe projections based on publication release items.
