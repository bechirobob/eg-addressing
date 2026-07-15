# SDA Authorization — Address-Points Observation Crosswalk

**Control:** `NLI-WO-002-PA-ID-02-AUTHORIZATION`  
**Addresses acceptance head:** `715ec287543c330c6e060a45b4a27affd9f812e5`  
**Oracle head:** `b98ae0fafffddadcef120eed34d1c16332708de2`  
**Outcome:** `ONE ADDRESS_POINTS OBSERVATION-CROSSWALK SLICE AUTHORIZED`

## Decision

`address_points.id` is an observation identity, not a location identity.

Authorized path:

```text
current_source.address_points.id
→ transform_address_points_observation_crosswalk
→ proposed_legacy_crosswalk
→ existing proposed_geometry_observation
```

Required binding:

```text
impl_wo002_r06_identity_crosswalk_address_points
→ transform_address_points_observation_crosswalk
```

The crosswalk target is:

```text
target_entity = geometry_observation
target_id = phase-a-geometry-address-points-phase-a-address-points-id
```

The target geometry observation must already exist and must remain tied to the queried source record, evidence object, restricted classification and resolved address subject.

The slice creates exactly one legacy crosswalk. It creates no location record, registry subject, geometry observation, migration exception, version, public-code alias or publication row.

## Reviewer control

Implement against and do not modify:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-address-points-observation-crosswalk-expected.json
```

## Boundary

Only `WO002-R06-identity-crosswalk-address_points` is authorized. The `address_records` and citizen-geotag identity groups remain deferred. The accepted addresses identity and geometry controls, frozen broad specification, broad expected fixture, runtime, migrations, deployment and PR #8 remain unchanged.

Obtain exact-head CI and stop for SDA assessment before any additional identity group.
