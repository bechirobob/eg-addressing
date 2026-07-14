# NLI Request for Information — RFI-NLI-WO-002-005-parcel-reference-authority

**Related work order:** `NLI-WO-002`  
**Raised by:** `Implementation Agent`  
**Date:** `2026-07-13`  
**Required by:** `Before executable NLI-WO-002B implementation for affected area`  
**Status:** `OPEN`

## 1. Decision question

Parcel/cadastre reference authority

## 2. Concrete options and consequences

Options: A) no parcels; B) external parcel references restricted; C) official cadastre integration. Recommendation: allow restricted external references only, no title/cadastre claims until authority named.

## 3. Agent recommendation

Use the recommendation above for design constraints, but do not implement runtime behavior until the named authority decides.

## 4. Consequence of no decision

WO-002 design can preserve the placeholder and safety boundary. WO-002B executable migration/API/publication work must stop for this decision area.

## 5. Requested decision authority

`SDA | Programme Owner | Registry Authority | GIS/Data Authority | Legal/Privacy Authority | Publication Authority`
