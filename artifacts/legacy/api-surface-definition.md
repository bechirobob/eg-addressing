# National Digital Addressing Platform — API Surface Definition

**Purpose:** Define the first serious API surface for the national digital addressing platform so frontend, integrations, and backend implementation can align early.

**API Style:** REST-first, versioned, JSON-based, authenticated except for explicitly public endpoints.

Base path recommendation:

```text
/api/v1
```

---

## 1. API Design Principles

- version APIs from day one
- separate internal and external use cases by scope and policy
- paginate all list endpoints
- validate all payloads
- return explicit status codes and error bodies
- audit all privileged and export-like access
- keep write operations behind strong auth and role checks

---

## 2. Authentication & Authorization

## 2.1 Internal users
Use session or token-based auth for web apps.

### Endpoints
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh`

## 2.2 API clients
Use scoped API credentials.

### Endpoints
- `POST /api/v1/integrations/token` (if token exchange is needed)
- credential management should remain admin-only

---

## 3. Territory Endpoints

## 3.1 Read territory structure
- `GET /api/v1/territories/provinces`
- `GET /api/v1/territories/provinces/{provinceId}`
- `GET /api/v1/territories/districts?provinceId=`
- `GET /api/v1/territories/municipalities?districtId=`
- `GET /api/v1/territories/zones?municipalityId=`
- `GET /api/v1/territories/zones/{zoneId}`

## 3.2 Territory admin
- `POST /api/v1/territories/zones`
- `PATCH /api/v1/territories/zones/{zoneId}`
- `POST /api/v1/territories/import-boundaries`

---

## 4. Road Endpoints

## 4.1 Query roads
- `GET /api/v1/roads`
- `GET /api/v1/roads/{roadId}`
- `GET /api/v1/roads?zoneId=`
- `GET /api/v1/roads?name=`

## 4.2 Manage roads
- `POST /api/v1/roads`
- `PATCH /api/v1/roads/{roadId}`
- `POST /api/v1/roads/{roadId}/approve-name`
- `POST /api/v1/roads/{roadId}/retire`

---

## 5. Building Endpoints

## 5.1 Query buildings
- `GET /api/v1/buildings`
- `GET /api/v1/buildings/{buildingId}`
- `GET /api/v1/buildings?zoneId=`
- `GET /api/v1/buildings?roadId=`

## 5.2 Manage buildings
- `POST /api/v1/buildings`
- `PATCH /api/v1/buildings/{buildingId}`
- `POST /api/v1/buildings/{buildingId}/units`

---

## 6. Address Endpoints

## 6.1 Search and lookup
- `GET /api/v1/addresses`
- `GET /api/v1/addresses/{addressId}`
- `GET /api/v1/addresses/search?q=`
- `GET /api/v1/addresses/verify?code=`
- `GET /api/v1/addresses/reverse-geocode?lat=&lng=`

### Suggested filters
- `status`
- `zoneId`
- `municipalityId`
- `roadId`
- `buildingId`
- `isOfficial`

## 6.2 Create and update
- `POST /api/v1/addresses`
- `PATCH /api/v1/addresses/{addressId}`
- `POST /api/v1/addresses/{addressId}/submit`
- `POST /api/v1/addresses/{addressId}/approve`
- `POST /api/v1/addresses/{addressId}/publish`
- `POST /api/v1/addresses/{addressId}/dispute`
- `POST /api/v1/addresses/{addressId}/retire`

## 6.3 History and workflow
- `GET /api/v1/addresses/{addressId}/versions`
- `GET /api/v1/addresses/{addressId}/status-events`
- `GET /api/v1/addresses/{addressId}/verification-events`

---

## 7. Field Operations Endpoints

## 7.1 Assignments
- `GET /api/v1/field/assignments`
- `GET /api/v1/field/assignments/{assignmentId}`
- `POST /api/v1/field/assignments`
- `PATCH /api/v1/field/assignments/{assignmentId}`

## 7.2 Submissions
- `GET /api/v1/field/submissions`
- `GET /api/v1/field/submissions/{submissionId}`
- `POST /api/v1/field/submissions`
- `PATCH /api/v1/field/submissions/{submissionId}`
- `POST /api/v1/field/submissions/{submissionId}/submit`
- `POST /api/v1/field/submissions/{submissionId}/accept`
- `POST /api/v1/field/submissions/{submissionId}/reject`
- `POST /api/v1/field/submissions/{submissionId}/request-correction`

## 7.3 Media upload
- `POST /api/v1/field/submissions/{submissionId}/photos`
- `DELETE /api/v1/field/submissions/{submissionId}/photos/{photoId}`

---

## 8. Correction Request Endpoints

- `GET /api/v1/corrections`
- `GET /api/v1/corrections/{correctionId}`
- `POST /api/v1/corrections`
- `PATCH /api/v1/corrections/{correctionId}`
- `POST /api/v1/corrections/{correctionId}/assign`
- `POST /api/v1/corrections/{correctionId}/resolve`
- `POST /api/v1/corrections/{correctionId}/reject`

---

## 9. Reporting Endpoints

- `GET /api/v1/reports/coverage-summary`
- `GET /api/v1/reports/pending-approvals`
- `GET /api/v1/reports/field-productivity`
- `GET /api/v1/reports/correction-backlog`
- `GET /api/v1/reports/zone-progress`

Optional export endpoints:
- `POST /api/v1/reports/exports/approved-addresses`
- `GET /api/v1/reports/exports/{exportJobId}`

---

## 10. Integration Endpoints

These should be tightly scoped.

### Read-only operational endpoints
- `GET /api/v1/integrations/addresses/verify?code=`
- `GET /api/v1/integrations/addresses/{addressCode}`
- `GET /api/v1/integrations/zones/{zoneId}/approved-addresses`
- `GET /api/v1/integrations/reverse-geocode?lat=&lng=`

### Reconciliation / batch endpoints
- `POST /api/v1/integrations/reconciliation-jobs`
- `GET /api/v1/integrations/reconciliation-jobs/{jobId}`

### Admin endpoints
- `GET /api/v1/integrations/clients`
- `POST /api/v1/integrations/clients`
- `POST /api/v1/integrations/clients/{clientId}/rotate-credential`
- `POST /api/v1/integrations/clients/{clientId}/revoke`

---

## 11. Audit Endpoints

- `GET /api/v1/audits`
- `GET /api/v1/audits/{auditId}`
- `GET /api/v1/audits?entityType=&entityId=`
- `GET /api/v1/audits?actorUserId=`

Audit access should be highly restricted.

---

## 12. Example Payloads

## 12.1 Create address candidate

```json
{
  "buildingId": "uuid",
  "roadId": "uuid",
  "zoneId": "uuid",
  "numberingValue": "12B",
  "addressLine1": "12B Avenida Central, Sector Norte",
  "postalCode": null
}
```

## 12.2 Field submission payload

```json
{
  "assignmentId": "uuid",
  "zoneId": "uuid",
  "gps": { "lat": 3.7523, "lng": 8.7741 },
  "buildingType": "residential",
  "provisionalRoadName": "Avenida Central",
  "notes": "Blue gate, two-storey building",
  "photos": []
}
```

## 12.3 Verification response

```json
{
  "addressCode": "EG-MAL-001-000123",
  "status": "published",
  "isOfficial": true,
  "addressLine1": "12B Avenida Central, Sector Norte",
  "zone": "Sector Norte",
  "municipality": "Malabo",
  "province": "Bioko Norte"
}
```

---

## 13. Error Model

Use a consistent error body.

```json
{
  "error": {
    "code": "ADDRESS_NOT_FOUND",
    "message": "No address record was found for the supplied code.",
    "details": null
  }
}
```

Recommended status codes:
- `200 OK`
- `201 Created`
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `409 Conflict`
- `422 Unprocessable Entity`
- `429 Too Many Requests`

---

## 14. Security Controls for the API Layer

- enforce auth at gateway/backend layer
- scope API clients by allowed endpoints and territory where relevant
- log exports and privileged lookups
- rate limit external clients
- validate uploads and payload size
- reject unsafe file types
- support credential rotation and revocation

---

## 15. MVP API Recommendation

For MVP, implement first:

- auth endpoints
- territory read endpoints
- road/building/address CRUD basics
- field assignments and submissions
- approval/publish workflow endpoints
- address search/verify endpoints
- basic reporting endpoints
- scoped integration verification endpoints

Leave advanced reconciliation and full public APIs for later unless urgently needed.

---

## 16. Plain-English Summary

The first API surface should focus on four things: field capture, record review, official address verification, and safe institutional access. If the API tries to solve every future integration before the pilot even works, the whole thing gets slower and messier.
