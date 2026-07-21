# SDA Authorization — Final Identity Foundation

**Control:** `NLI-WO-002-PA-ID-04-AUTHORIZATION`  
**Reviewed proposal:** `36e0fcc5f370612c6d263e836989b7e6d46d5ec2`  
**Outcome:** `ONE FINAL IDENTITY SLICE AUTHORIZED`

Authorized group:

```text
WO002-R06-identity-crosswalk-citizen_geotag_submissions
```

Required binding:

```text
impl_wo002_r06_identity_crosswalk_citizen_geotag_submissions
→ transform_citizen_geotag_identity_crosswalk
```

Implement against and do not modify:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-identity-expected.json
```

Oracle Git blob:

```text
61fb777a2af5a917b4ea7bbff0d6c7dff09241ba
```

The detailed exclusion, evidence, test and compatibility requirements are normative in:

```text
docs/agent/tasks/NLI-WO-002-phase-a-citizen-geotag-identity-control-proposal.md
```

Proposal Git blob:

```text
0eaf7a8bc4c479d2d0b3efc8fe6c24c35b819a7d
```

Create exactly the reviewed restricted location row, active subject and ID crosswalk. First run inserts three; second run inserts zero and updates zero. Every source field other than `id` is excluded from identity.

The committed report may contain query text, synthetic IDs, field names, classifications, checks, hashes and redaction flags only. It must not emit excluded source values. The command is fixture-only.

Create no exception, version, geometry, code alias, publication item or external effect. Run the separate unchanged-geometry compatibility test required by the oracle.

Add the slice to exact-head SDA CI after a fresh database reset. Do not implement another group or change broad, runtime, migration, deployment, publication or PR #8 scope.

Stop after exact-head evidence and request final identity-family assessment.