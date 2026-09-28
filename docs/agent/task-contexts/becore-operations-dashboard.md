# BeCore-inspired operations dashboard

User-directed Class B presentation follow-up to NLI-WO-003; no SDA acceptance or new work order is claimed. Base: WO-007 draft branch at 94114450399fca2ca8c56c438e1e6fa36f2e6a2f. Reference: bechirobob/tickets main a4670d7289604210e5f5fdae2c3b4e92580f3e6b (workspace chrome, metrics strip, operations directory and view controls).

## Workflow and scope
Authenticated staff inspect current summary counts and pilot gates, then open a role-permitted workspace. Existing APIs and server authorization remain authoritative. Requests use the existing session helper. No writes, new states, publication authority, deployment, backend, dependencies or synced project reference changes. Failures show unavailable values and a retry action. Pilot readiness is separate from queue volume and is not authorization to publish.

## Plan and acceptance
1. Adapt BeCore's restrained hierarchy, metric strip, view controls and actionable rows using EG navy tokens, existing icons, emblem and attribution. Keep responsive content scoped to this dashboard.
2. Read protected summary endpoints only after session resolution; represent loading, partial failure, empty queues and retry honestly. Hide unknown shell attention counts rather than report zero.
3. Validate production build, existing guards, role-filtered destinations, authenticated requests, failure/recovery, keyboard controls and desktop/mobile reflow with explicitly synthetic browser fixtures. Record screenshots and limitations.
4. Submit isolated draft PR against the parent workspaces branch; do not merge or deploy.

Selected repository skills: S01/S03 scope and criteria; S08 session request boundary; S10 UI/a11y; S11 semantic evidence; S12 draft delivery; S16 handoff; S18 frontend; S21/S22/S23/S24 navigation regression; S27 read-only reporting; S29 performance; S30/S31 release handoff. Read the manifest, existing task context, UI standard, design contract and affected source. No data or migration effects.

The repository's active English-only UI guard conflicts with the broader bilingual target in S10. This bounded adaptation retains the existing language policy; bilingual acceptance remains unproven and must be resolved before release. Browser fixtures cannot establish server-side authorization, live production data, institutional acceptance or deployment readiness. Rollback: revert this frontend change. Operators should be told that workload and pilot gates now have separate views and unavailable data no longer appears as zero.
