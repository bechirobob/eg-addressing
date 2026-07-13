# Technical Architecture Manual

## Document Control

Title: Technical Architecture Manual
Product: National Digital Addressing System
Responsible founder: Benjamin Bob Bechiro
Company: BeCorps
Document type: Technical manual
Status: Supporting document for intellectual-property registration preparation in Malabo.

## Purpose

This manual describes the base architecture of the system to demonstrate structure, technical scope, and coordinated operation of its components.

## Overall architecture

- Administration web frontend and public routes.
- Backend API for authentication, registry, review, publication, reporting, and audit.
- PostgreSQL/PostGIS database for territorial entities, addresses, users, and events.
- Redis for runtime support and auxiliary services.
- S3-compatible storage for protected evidence where applicable.

## Functional modules

- Citizen location submission and address tracking
- Field evidence capture and review
- Registry review and official address records
- Road, building, territory, and administrative-unit management
- Publication governance, certificates, signage, and public proof
- Reports, activity review, exports, audit logging, and access administration

## Application routes

- /admin/staff
- /code/[code]
- /exports
- /field
- /geotag
- /issue
- /login
- /operations-runbook
- /
- /proof/[code]
- /records
- /registry
- /reports
- /signage
- /territories
- /track
- /verify

## Design principles

- Modular-first architecture; microservices only when growth justifies them.
- Server-side authorization for protected functions.
- Separation between public routes and internal operator routes.
- Official publication remains locked until institutional approval.
