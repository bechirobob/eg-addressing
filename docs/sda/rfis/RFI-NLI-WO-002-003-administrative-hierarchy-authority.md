# NLI Request for Information — RFI-NLI-WO-002-003-administrative-hierarchy-authority

**Related work order:** `NLI-WO-002`  
**Raised by:** `Implementation Agent`  
**Date:** `2026-07-13`  
**Required by:** `Before executable NLI-WO-002B implementation for affected area`  
**Status:** `OPEN`

## 1. Decision question

Administrative hierarchy authority

## 2. Concrete options and consequences

Options: A) current province/admin_units package as provisional; B) official government gazette hierarchy; C) GIS boundary package with legal source. Recommendation: model generic hierarchy now, require official source before publication.

## 3. Agent recommendation

Use the recommendation above for design constraints, but do not implement runtime behavior until the named authority decides.

## 4. Consequence of no decision

WO-002 design can preserve the placeholder and safety boundary. WO-002B executable migration/API/publication work must stop for this decision area.

## 5. Requested decision authority

`SDA | Programme Owner | Registry Authority | GIS/Data Authority | Legal/Privacy Authority | Publication Authority`
