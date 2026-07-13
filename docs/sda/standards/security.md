# SDA Standard — Platform Security

**Version:** 0.1  
**Status:** Mandatory  
**Applies to:** source, infrastructure, data, dependencies, operations, and incident handling

## 1. Security posture

Security is a system property, not a final penetration-test phase. Every work order MUST identify affected assets, trust boundaries, actors, abuse cases, data classes, and operational controls.

The platform MUST fail closed for authority and sensitive data. Availability fallbacks MUST NOT promote unverified evidence, bypass approval, or expose protected records.

## 2. Data classification

Every persistent or exported data element MUST belong to a governed class. The initial classes are:

- **Public:** explicitly approved for unrestricted publication.
- **Government internal:** operational data not approved for public release.
- **Restricted:** personal, precise-location, evidentiary, security, or institutionally sensitive data.
- **Highly restricted:** identity-document content, privileged credentials, security keys, break-glass data, or data requiring exceptional access.

Classification determines collection, access, encryption, logging, export, retention, redaction, and incident response. “Available in the database” never means “public.”

## 3. Data minimization and privacy

- Collect only data required for an approved purpose.
- Record the purpose and authority for sensitive data collection.
- Avoid storing full identity-document values when a verified assertion or limited reference is sufficient.
- Public and partner responses MUST use explicit safe projections rather than removing a few known sensitive fields from internal objects.
- Logs, traces, screenshots, test fixtures, and support exports MUST be treated as possible data-disclosure paths.
- Production data MUST NOT be copied into development or general test environments without approved de-identification and control.

## 4. Secrets and keys

- Secrets MUST be generated, stored, distributed, rotated, and revoked through an approved secrets-management process.
- Secrets MUST NOT appear in source control, images, build logs, issue text, screenshots, environment templates, or client-side bundles.
- Production, pilot, staging, test, and development secrets MUST be separate.
- Access keys MUST be scoped to the minimum bucket, operation, environment, and lifetime.
- Cryptographic keys require named ownership, rotation, backup/recovery, and compromise procedures.
- Default/fallback credentials MUST cause controlled-environment startup or readiness failure.

## 5. Encryption

- External traffic MUST use current approved TLS configuration.
- Internal service traffic carrying restricted data SHOULD be encrypted and authenticated; production exceptions require documented network and threat controls.
- Database, object storage, backups, and portable exports containing restricted data MUST be encrypted at rest.
- Cryptographic algorithms and libraries MUST be maintained, standard implementations; custom cryptography is prohibited.
- Hashes used for integrity MUST use a collision-resistant algorithm. Password hashing follows the identity standard, not general-purpose hashing.

## 6. Application security

- Validate input at the API boundary and enforce invariants in domain and database layers.
- Use parameterized database access. Dynamic SQL identifiers or clauses require allowlists and review.
- Output encoding, content-type controls, and safe file delivery are mandatory.
- File uploads require size limits, media verification, extension and content checks, malware scanning in controlled environments, safe object names, and non-executable storage/delivery.
- Server-side request forgery, path traversal, injection, insecure deserialization, mass assignment, and broken object authorization MUST be considered for affected changes.
- Error responses MUST be useful without exposing stack traces, credentials, internal topology, query details, or personal data.
- Security headers and CSRF protections MUST be tested, not only configured.

## 7. API and abuse protection

- Public and partner endpoints require distributed rate and abuse controls suitable for multiple application instances.
- Rate limits MUST distinguish anonymous sources, authenticated subjects, institutions, and clients where appropriate.
- Resource-intensive lookup, export, upload, and geospatial operations require stricter quotas and timeouts.
- Idempotency and replay controls are required for retriable sensitive writes.
- Automated enumeration of personal, restricted, or unpublished records MUST be prevented.

## 8. Infrastructure and network security

Production architecture MUST provide:

- network separation between public ingress, applications, data services, and operations;
- no public database, Redis, object-storage administration, or container-engine interfaces;
- least-privilege runtime identities and read-only filesystems where practical;
- pinned immutable images and explicit base-image lifecycle;
- hardened hosts or managed services with patch ownership;
- controlled administrative entry points with MFA and audit;
- denial-by-default firewall/security-group policy;
- encrypted, access-controlled backups isolated from ordinary application credentials.

Local Docker Compose is not a production security boundary.

## 9. Dependency and supply-chain security

- Dependencies and container images MUST be version controlled and reproducible.
- CI MUST perform dependency review, secret scanning, static analysis, and container/image vulnerability scanning appropriate to the change.
- Release artefacts SHOULD include an SBOM and provenance; production artefacts MUST be immutable and verifiably produced by the controlled pipeline.
- Critical or known-exploited vulnerabilities require documented disposition before release.
- New dependencies require purpose, maintenance status, licensing, data-flow, and operational-impact review.
- Unpinned `latest` images are prohibited in controlled deployment manifests.

## 10. Audit and detection

Security-relevant events MUST be centralized and correlated using request, actor, institution, client, and target identifiers. Events include:

- authentication and MFA activity;
- authorization failures;
- role, scope, credential, and configuration changes;
- sensitive reads and evidence access;
- imports, exports, publication, correction, retirement, and deletion;
- administrative and break-glass actions;
- malware, integrity, rate-limit, and anomaly detections;
- backup, restore, and recovery operations.

Logs MUST have access control, retention, clock synchronization, integrity protection, and alert ownership. Do not log secrets or unnecessary sensitive payloads.

## 11. Threat modeling

Class A changes and material Class B changes MUST include a concise threat model covering:

- assets and data classes;
- trust boundaries and external dependencies;
- legitimate actors and possible attackers;
- abuse/misuse cases;
- prevention, detection, response, and recovery controls;
- residual risk.

Threat modeling is mandatory for identity, publication, partner integration, evidence, field synchronization, public lookup, bulk import/export, and infrastructure changes.

## 12. Vulnerability handling

The programme MUST maintain a controlled process to:

- receive and triage reports;
- assign severity and owner;
- protect reporter and sensitive technical details;
- fix and test safely;
- rotate credentials and investigate exposure where needed;
- communicate operational action;
- document lessons and control improvements.

Security defects are not closed until deployment and exposure implications are addressed.

## 13. Incident response

Security incidents require:

- named incident lead and timeline;
- containment that preserves evidence;
- affected systems, records, institutions, and data classes;
- credential/key decisions;
- recovery validation;
- notification and authority escalation according to policy;
- post-incident review and corrective work orders.

Do not destroy logs, evidence, or compromised state before required forensic preservation.

## 14. Required evidence

Security-sensitive pull requests MUST include:

- threat analysis;
- allow/deny and abuse-case tests;
- dependency and image scan results;
- secret-scan result;
- configuration and environment effects;
- data-classification and privacy impact;
- audit and alert evidence;
- credential/key lifecycle effects;
- operational rollback/containment procedure;
- residual risk and accountable owner.

A passing unit-test suite alone does not satisfy this standard.
