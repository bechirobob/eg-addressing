# API Documentation

## Document Control

Title: API Documentation
Product: National Digital Addressing System
Responsible founder: Benjamin Bob Bechiro
Company: BeCoreOps
Document type: Technical manual
Status: Supporting document for intellectual-property registration preparation in Malabo.

## Purpose

This document summarizes the API surface as evidence of integration, access control, and functional scope.

## API families

- Authentication and session.
- Users and staff administration.
- Provinces, administrative units, and territories.
- Roads, buildings, addresses, and official records.
- Citizen geotagging, corrections, and tracking.
- Field evidence, review, publication, reports, exports, and audit.

## Representative endpoints

- GET /
- GET /api/v1/health
- GET /api/v1/meta
- POST /api/v1/auth/login
- GET /api/v1/auth/me
- POST /api/v1/auth/logout
- GET /api/v1/admin/users
- POST /api/v1/admin/users
- PATCH /api/v1/admin/users/{user_id}
- POST /api/v1/admin/users/{user_id}/disable
- POST /api/v1/admin/users/{user_id}/revoke-sessions
- GET /api/v1/territories/provinces
- GET /api/v1/provinces
- GET /api/v1/admin-units
- GET /api/v1/public/territory-options
- GET /api/v1/territories
- GET /api/v1/territories/{territory_id}
- POST /api/v1/territories
- PATCH /api/v1/territories/{territory_id}
- DELETE /api/v1/territories/{territory_id}
- GET /api/v1/audit-logs
- GET /api/v1/roads
- GET /api/v1/roads/{road_id}
- POST /api/v1/roads
- PATCH /api/v1/roads/{road_id}
- DELETE /api/v1/roads/{road_id}
- GET /api/v1/buildings
- GET /api/v1/buildings/{building_id}
- POST /api/v1/buildings
- PATCH /api/v1/buildings/{building_id}
- DELETE /api/v1/buildings/{building_id}
- GET /api/v1/addresses
- GET /api/v1/addresses/{address_id}
- POST /api/v1/addresses
- PATCH /api/v1/addresses/{address_id}
- DELETE /api/v1/addresses/{address_id}
- GET /api/v1/field/assignments
- GET /api/v1/field/geotag-tasks

## Controls

- Authentication for internal routes.
- Administration, editing, viewing, and institutional-review roles.
- Input validation and separation of public/protected data.
- Publication limits controlled by approval.
