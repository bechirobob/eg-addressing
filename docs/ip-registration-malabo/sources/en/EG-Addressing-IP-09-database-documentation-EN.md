# Database Documentation

## Document Control

Title: Database Documentation
Product: National Digital Addressing System
Responsible founder: Benjamin Bob Bechiro
Company: BeCorps
Document type: Technical manual
Status: Supporting document for intellectual-property registration preparation in Malabo.

## Purpose

This document summarizes persistent entities, operational relationships, and retention rules supporting the system.

## Identified tables

- address_corrections
- address_points
- address_record_events
- address_records
- addresses
- admin_units
- audit_logs
- auth_tokens
- buildings
- citizen_geotag_submissions
- field_assignments
- field_submissions
- import_jobs
- import_rows
- provinces
- publication_pack_addresses
- publication_packs
- roads
- territories
- users

## Data domains

- Internal users, sessions, and roles.
- Provinces, administrative units, territories, roads, and buildings.
- Candidate addresses and official records.
- Citizen corrections and field evidence.
- Publication packs, certificates, signage, reports, and audit.

## Data rules

- Sensitive data is not exposed on public routes.
- Internal identifiers remain separate from citizen-facing presentation where necessary.
- Official publication requires review and approval lock.
- Audit preserves action, actor, entity, and operational detail events.
