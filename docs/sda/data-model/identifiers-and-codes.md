# Identifier and Public-Code Architecture

**Status:** Draft for SDA review

## 1. Identifier classes

| Class | Purpose | Public? | Reuse policy |
|---|---|---|---|
| Internal stable ID | Database identity for entities. | No by default. | Never reused. |
| Public code alias | Human/public lookup code. | Yes after release. | Never reused for a different record. |
| External authority ID | Imported government/cadastre/source identifier. | Depends on source. | Controlled by source; stored with authority. |
| Provisional/offline ID | Temporary field/offline/candidate identity. | No. | May be reconciled but preserved in lineage. |
| Version ID | Immutable version identity. | No. | Never reused. |
| Event ID | Audit/event identity. | No. | Never reused. |

## 2. Current identifiers

Current values include `addresses.id`, `addresses.public_code`, `citizen_geotag_submissions.grid_code`, `address_records.address_code`, `address_records.id`, `address_points.id`, and field/import/publication IDs. `grid_code`, `public_code`, and `address_code` currently overlap in meaning and must be separated.

## 3. Target public-code principles

- Public code grammar is reserved pending authority decision.
- A public code points to a canonical `location_record`, not to an intake row or legacy address row.
- Public codes must support supersession history and non-reuse.
- Public code activation requires publication authority.
- Internal registry-ready records may reserve a public code without exposing details.

## 4. Supersession

When a record is corrected or superseded:

- old internal IDs remain immutable;
- old public codes remain linked to history;
- public lookup may redirect, warn, or hide details based on publication authority;
- the model records successor/predecessor relationships explicitly.

## 5. RFIs

Final national public-code grammar, checksum, province prefix behavior, and offline issuance semantics require SDA/programme authority before executable implementation.
