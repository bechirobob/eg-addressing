# National Digital Addressing Platform — Pilot MVP Scope

**Purpose:** Define exactly what the first serious pilot version of the national digital addressing platform should include, what success looks like, and what is intentionally out of scope.

---

## 1. Pilot Intent

The pilot is not a throwaway demo.

Its purpose is to prove that government can:

1. define one usable address standard
2. capture roads/buildings/coordinates in the territory
3. review and approve official records
4. search and verify those records reliably
5. support at least a small number of real institutional workflows

The pilot should establish the operating model, not merely showcase a map.

---

## 2. Pilot Geography

Recommended pilot geography:

- priority zones in Malabo
- one government-service-heavy district
- one fast-growing urban area
- one controlled zone in Oyala / Ciudad de la Paz

This provides a useful mix of:
- dense urban patterns
- operational government use
- expansion reality
- future-city planning relevance

---

## 3. MVP Objectives

The pilot MVP must prove these things:

### 3.1 Data objectives
- capture roads and buildings in pilot zones
- assign official address candidates
- attach geographic coordinates to records
- maintain administrative hierarchy for each record

### 3.2 Workflow objectives
- assign field work by zone
- collect field data with evidence
- review and approve records through workflow
- process corrections and disputes in a controlled way

### 3.3 Operational objectives
- allow authorized users to search addresses
- provide map-based visibility
- track coverage and approval backlog
- expose limited approved data to institutional users or APIs

---

## 4. In-Scope Modules for MVP

## 4.1 Must-have modules

### A. Authentication & RBAC
Users can log in and operate by role/scope.

### B. Territory Hierarchy Management
Store provinces, districts, municipalities, and pilot zones.

### C. Road / Building / Address Registry
Create and manage the core addressable entities.

### D. Field Capture Workflow
Enumerators capture structured records and evidence.

### E. Supervisor / Validator Review Workflow
Submissions can be reviewed, corrected, approved, or rejected.

### F. Search & Verification
Users can search and verify official or in-review address records.

### G. Map View
Users can see records geographically in pilot zones.

### H. Audit Logging
System records critical actions.

### I. Basic Reporting Dashboard
Coverage, submission counts, pending approvals, and exceptions.

### J. Limited Integration Access
Approved API or export access for one or two pilot institutional use cases.

---

## 5. MVP Functional Requirements

## 5.1 User and access
- create users and roles
- assign users to geographic scope
- control privileged actions by role

## 5.2 Territory setup
- load pilot administrative boundaries
- define pilot zones
- assign field tasks by zone

## 5.3 Field capture
- create building/road capture records
- store GPS coordinates
- upload field photos
- save drafts and sync submissions
- resubmit corrected records

## 5.4 Review and approval
- route submissions to review queues
- approve/reject/correct submissions
- convert approved records into official address candidates
- publish official pilot records

## 5.5 Search and verification
- search by text
- search by code
- search by administrative area
- verify record status
- show linked map position

## 5.6 Reporting
- total captured buildings
- total approved addresses
- pending review backlog
- rejected/corrected records
- zone progress tracking

## 5.7 Integration
- export approved address set for pilot use
- provide scoped API for lookup and verification

---

## 6. MVP Non-Functional Requirements

### Performance
- responsive search on pilot dataset
- dashboard load times acceptable for office use

### Reliability
- nightly backups
- sync retry support
- no silent submission loss

### Security
- role-based access
- audit logs
- secure credential handling
- protected exports

### Usability
- simple admin workflow
- mobile-friendly field interface
- clear status labels and validation feedback

---

## 7. Out of Scope for MVP

These should **not** be treated as first-release requirements unless political direction changes:

- nationwide rollout coverage
- full public self-service portal
- complete postal transformation stack
- full utility integration across all providers
- advanced citizen proof-of-address issuance at scale
- exhaustive signage lifecycle automation
- large-scale multi-agency workflow orchestration
- deep analytics / BI warehouse
- microservices architecture
- advanced SSO/MFA ecosystem beyond pilot necessity

These are later-phase items, not MVP blockers.

---

## 8. Pilot Success Criteria

The MVP should be considered successful if it proves:

- at least one agreed pilot standard is being used consistently
- field teams can capture and submit structured records
- reviewers can approve or reject records cleanly
- official records can be searched and verified reliably
- coverage and backlog metrics are visible to leadership
- at least one ministry workflow and one external operational use case can consume pilot data

---

## 9. MVP Release Breakdown

### Release 1 — Core platform
- auth
- roles
- territory hierarchy
- road/building/address schema
- admin UI foundation

### Release 2 — Field workflow
- field assignments
- field submission forms
- photo uploads
- sync support
- supervisor review queue

### Release 3 — Approval and publication
- approval workflow
- official address publication
- status history
- search and verification

### Release 4 — Reporting and limited integration
- operational dashboard
- export tooling
- scoped verification API

---

## 10. Dependencies Before MVP Build

These decisions must be settled early:

- address format standard
- numbering policy
- pilot geography
- naming authority model
- minimum required data fields
- who has publication authority
- what counts as official approval

If these rules are vague, the software will reflect the vagueness and become a headache.

---

## 11. Recommended MVP Team Shape

Minimum serious team:

- product/solution lead
- backend engineer
- frontend engineer
- GIS/data engineer
- QA / workflow tester
- field operations counterpart
- government decision owner

A one-person hero build for a system like this is cursed.

---

## 12. Plain-English Summary

The pilot MVP should be the smallest version of the system that can actually run field capture, approvals, and trusted address lookup in real pilot zones. If it cannot support real operational decisions, it is too small. If it tries to solve the whole country on day one, it is too big.
