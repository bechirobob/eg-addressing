# NLI-WO-002 Data Model Design Pack

**Work order:** `NLI-WO-002 — Canonical National Location Data Model`  
**Status:** `Draft for SDA Review`  
**Branch:** `nli/wo-002-canonical-location-model`  
**Date:** `2026-07-13`

This package is the design-authority output for NLI-WO-002. It is documentation only. It does not deploy schema, change API contracts, alter infrastructure, or touch production/pilot data.

## Authority boundary

- Existing runtime authority remains the current PostgreSQL/PostGIS-backed pilot implementation.
- Future schema deployment requires a separate accepted work order, expected as `NLI-WO-002B`.
- `draft-physical-schema.sql` is non-executable and intentionally stored under `docs/sda/data-model/`, not under `infra/migrations/`.
- `docs/source-proposals/schema.sql` was reviewed only as design input and is not copied wholesale.

## Pack contents

| Artifact | Purpose |
|---|---|
| `current-state-inventory.md` | Current operational schema/API behavior inventory. |
| `canonical-conceptual-model.md` | Target entity and authority model. |
| `canonical-logical-erd.mmd` | Mermaid logical ERD source. |
| `data-dictionary.md` | Field definitions, classifications, nullability intent, and projections. |
| `controlled-vocabularies.md` | Target vocabularies and current-string mapping. |
| `lifecycle-state-machines.md` | Candidate, verification, canonical, publication, correction, and retirement state machines. |
| `identifiers-and-codes.md` | Internal IDs, public codes, external IDs, provisional IDs, non-reuse, and supersession. |
| `geometry-provenance-and-quality.md` | CRS, geometry classes, quality model, source authority, and validation. |
| `source-authority-and-classification.md` | Data authority, provenance, evidence, and classification model. |
| `api-projection-map.md` | Current API/public/operator/export projection mapping. |
| `current-to-target-mapping.md` | Current table/field disposition to target model. |
| `schema-convergence-plan.md` | Expand–migrate–contract proposal for later implementation. |
| `draft-physical-schema.sql` | Non-executable physical schema proposal. |
| `representative-records/` | Representative examples covering required cases. |

## AC traceability

| AC-01 | Represented | See data-model pack sections for AC-01; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-02 | Represented | See data-model pack sections for AC-02; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-03 | Represented | See data-model pack sections for AC-03; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-04 | Represented | See data-model pack sections for AC-04; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-05 | Represented | See data-model pack sections for AC-05; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-06 | Represented | See data-model pack sections for AC-06; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-07 | Represented | See data-model pack sections for AC-07; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-08 | Represented | See data-model pack sections for AC-08; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-09 | Represented | See data-model pack sections for AC-09; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-10 | Represented | See data-model pack sections for AC-10; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-11 | Represented | See data-model pack sections for AC-11; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-12 | Represented | See data-model pack sections for AC-12; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-13 | Represented | See data-model pack sections for AC-13; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-14 | Represented | See data-model pack sections for AC-14; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-15 | Represented | See data-model pack sections for AC-15; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-16 | Represented | See data-model pack sections for AC-16; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-17 | Represented | See data-model pack sections for AC-17; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-18 | Represented | See data-model pack sections for AC-18; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-19 | Represented | See data-model pack sections for AC-19; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-20 | Represented | See data-model pack sections for AC-20; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-21 | Represented | See data-model pack sections for AC-21; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |
| AC-22 | Represented | See data-model pack sections for AC-22; no runtime implementation in this phase. | Docs-only review against `git diff --name-only origin/main...HEAD`. | NLI-WO-002B required before deployment. |

## No-runtime-change proof target

The PR evidence must show changed paths limited to `docs/sda/data-model/**`, `docs/sda/adrs/**`, `docs/sda/rfis/**`, `docs/sda/implementation-plans/**`, and `docs/sda/evidence/**`.
