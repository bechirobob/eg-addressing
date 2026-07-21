# NLI-WO-002 Phase A administrative units convergence-extension mapping

**Status:** planning evidence only; reviewer-controlled extension control not created.  
**Reviewer-controlled base head:** `ee37c4e203bdab25339063672a5eccee24f2aa6f`  
**Accepted administrative implementation:** `d8e98f681fa06404dd1fc2a097c3091645b9f0d4`  
**Accepted marker:** `docs/sda/reviews/NLI-WO-002-admin-shell-acceptance.json`  
**Current instructed action:** prepare one accepted-family convergence-extension mapping only.  
**Allowed changed path:** `docs/agent/tasks/NLI-WO-002-phase-a-admin-units-convergence-extension-mapping.md`

## 0. Authority and scope boundary

This mapping is a design/planning artifact only. It does **not**:

- integrate `transform_admin_units_identity_crosswalk` into accepted-family convergence;
- alter the existing accepted-family sequence, command, control, report, implementation, or CI step;
- create a reviewer control, oracle, authorization, generated report, harness command, transform, fixture, migration, runtime feature, or CI invocation;
- modify PR #8;
- authorize administrative versions, codes, names, hierarchy, geometry, publication, province identity, territory identity, or administrative-context integration;
- accept broad Phase A, close F02/F14, authorize Review 12 or Phase B, or authorize publication, deployment, merge, or another transform group.

Expected future SDA step: a reviewer-owned extension control or authorization must be created before any implementation/harness/CI integration.

## 1. Controlling artifact pins

Every artifact below was pinned at `ee37c4e203bdab25339063672a5eccee24f2aa6f` using Git blob hash and file SHA-256.

| Artifact | Path | Git blob | SHA-256 |
| --- | --- | --- | --- |
| administrative identity-shell acceptance marker | `docs/sda/reviews/NLI-WO-002-admin-shell-acceptance.json` | `6ef3d332429205c9422d6e278bae1fb5eb3a134b` | `4c13e31cec1f7f52060a6f6a1a9fb1e56732ecb581b4ce57d2b2169d7873bb79` |
| administrative reviewer oracle | `docs/sda/acceptance/NLI-WO-002-phase-a-admin-units-identity-shell-expected.json` | `ef31fc1426b27427ed4ce01a4b89a7605ce280ec` | `96d3c8a70ce995e26e1fa85ed38013c091a56e819a451a8daac257acb9347f84` |
| administrative identity-shell report | `docs/sda/data-model/phase-a-admin-units-identity-shell-report.json` | `03327183562bc89e410d8320faf1f22eddec7c4b` | `a91505c2feb85134835d24a0d7b2924ef2743c9bba7f84b1062272f7cecf6a17` |
| administrative live transform specification | `docs/sda/data-model/fixtures/transform-specs/phase-a-transform-specs.json` | `763cad920cb398771c983adbbe5d653f332bf6c1` | `8e39fbc84108064e2c008cac3468f7a5d82a287baeac5483ac82a8d6b4508dce` |
| administrative authority control | `docs/sda/reviews/NLI-WO-002-admin-shell-authority.json` | `51a83b459b477bdf588dab96cc028ac6cbdc4a6e` | `afee3006b9da042365de8d1d35a895e5632c69fb26f479ca2242a15f7a986a19` |
| administrative implementation authorization | `docs/sda/reviews/NLI-WO-002-admin-impl-auth.json` | `24051827d182be32a7c182e338fe811789eb04b0` | `187dae38c3f0f389f093de662c6242d63db0a8722374c71498bb1bb145e2ece1` |
| administrative specification authorization | `docs/sda/reviews/NLI-WO-002-admin-spec-auth.json` | `e88a7061e6be7b274d25af9c44c75a9c74e5c0a5` | `f8ef3656327097281f4c4e0df0df052076ea7e13ac16e8e638c2471bec9b690b` |
| administrative specification assessment | `docs/sda/reviews/NLI-WO-002-admin-spec-assessment.json` | `7f3ded1c5ddc48b767986ba7534148f7673d28bf` | `3cf5b6e146e30d3e62111d3e8d940d6b242653ea8317809efe95b7ee37ae6a01` |
| administrative shell assessment | `docs/sda/reviews/NLI-WO-002-admin-shell-assessment.json` | `b00319eeb2cf139d7523c3a4180717e2eac29e97` | `9f04e0447779b458f31a09928bef455f5584e2924e5144e69417d8f4f04eed1c` |
| administrative shell final assessment | `docs/sda/reviews/NLI-WO-002-admin-shell-final-assessment.json` | `158145ca013a0db597c84aa5b9827b017ae3dd91` | `aa9ee16a931add4be17bbbdaaad0482e9edfba0ccdc63055450cab4476c49054` |
| existing accepted-family convergence mapping | `docs/agent/tasks/NLI-WO-002-phase-a-accepted-family-convergence-mapping.md` | `c984a16f352417b9fde0f8cb9e0536a5e0ab6eb1` | `382c1ccd0de2b90ecb08241d8cf3f6788ae7166ef93f9122bb6ed3b6ed3669ce` |
| existing accepted-family convergence control | `docs/sda/acceptance/NLI-WO-002-phase-a-accepted-family-convergence-control.json` | `3c4c59fa5eeb004cfb8ef2520241d74c130fa926` | `d714b32ea170e05b5feef240d587d860ed0c712812036f384e357381a60b3b8a` |
| existing convergence authorization | `docs/sda/reviews/NLI-WO-002-phase-a-accepted-family-convergence-authorization.md` | `2fcbf3fc540ea3c4664314532dce418999856fd5` | `e9ff53940004e3bad4a73379eea5246ffec8827ca4de615fbce1c8f9526b285b` |
| existing accepted-family convergence report | `docs/sda/data-model/phase-a-accepted-family-convergence-report.json` | `bc0346d30eb49f1d2956b81e6cffa5e3e9933d65` | `f28cd006d27cf0d764db1863956d39dc97aa13b11df0d063d8c3b8ad2698a304` |
| existing authoritative harness | `docs/sda/data-model/scripts/authoritative_harness.py` | `f697a9ca4d37a5bec042c63b9cfd997bd5b33303` | `455f94081723faf04db3dc20d8320c8c1dd1d3352bd6c694a77044cd027ebd2a` |
| frozen broad specification | `docs/sda/data-model/fixtures/transform-specs/phase-a-broad-generic-transform-specs-frozen.json` | `443de54b6bacf6a12106fdbba5dba1a07955eec4` | `b601f4fe1c5676511010d10d5b9e819e83fc50a2bbedce11c324e2f4a05099cf` |
| broad expected-target fixture | `docs/sda/data-model/fixtures/expected-target/phase-a-expected-target-records.json` | `7df5326902315123ebb8bc4970899dd293f30c58` | `4b98cc1b580b2513cd0f1eee3a53af87376a1d6efa7c8792ab1211e38a22ea76` |
| parent oracle: addresses identity | `docs/sda/acceptance/NLI-WO-002-phase-a-addresses-identity-expected.json` | `4c1d6068bc39da7a8fef7ed3dbaa1454f27282c8` | `518af277e96c94c55808f9ac1e7992059c371bd225d906cf77156c478b0497cd` |
| parent control: addresses identity acceptance | `docs/sda/reviews/NLI-WO-002-phase-a-addresses-identity-pattern-acceptance.md` | `0da2827293ebdf38c8e72ce2813b14ab267d798f` | `705c7af05888cdd8b68820e999f9bddcef72c05acf48d136c76173028401c783` |
| parent control: addresses identity CI correction | `docs/sda/acceptance/NLI-WO-002-addresses-identity-ci-correction.json` | `aa7c5ea8241319d10fff7197d1b03a5c11951f06` | `22d06863e6aacc31379812b965aa5e34e0c5fee6b8537474498c691dc218b497` |
| parent oracle: address-points geometry | `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-expected.json` | `691d08f09bfd12e227207cd5913b6b54caf59536` | `cf699de04e0ca500c3a7826f257e190d24835356ef96db1650160d7d438edaea` |
| parent correction oracle: address-points geometry | `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-correction-oracle.json` | `68b7c844864d18d9f11f9e26d3f022620439e840` | `12214d3967c6561eaa30c4577d9ab445a9b90d14b6d5c3374a842868e4e62bea` |
| parent final correction oracle: address-points geometry | `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-final-correction-oracle.json` | `8ee505bcce885401b20cedcdda2fb54daac44be0` | `187d940235cdf1ef0976c423151f11ab5a378f1761e30b0007942d9aa4bd9278` |
| parent control: address-points geometry checkpoint | `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-checkpoint.md` | `1fd37c390a2652c50e8b3c62a22ab7bc34b55fb1` | `b35411a45578c499c98eff96da6ac3ae8b828aa7d55725288e4716392cd866a1` |
| parent control: address-points geometry acceptance | `docs/sda/reviews/NLI-WO-002-phase-a-address-points-geometry-pattern-acceptance.md` | `9b53b5fe423d3a0931206d22f9aaac85e76964fe` | `2dfa4b05441dc687e03af7b6c64630e344edf46bcbb8a4f0c7f241fde9d3ee25` |
| parent oracle: address-points observation crosswalk | `docs/sda/acceptance/NLI-WO-002-phase-a-address-points-observation-crosswalk-expected.json` | `7d964599a5500aa5430da208aefdc940c3c0af1b` | `d1b695994ae774a6c54cc99c1e79a0bce023fd5a9a20ec2aee779cfeb10bfa82` |
| parent control: address-points observation authorization | `docs/sda/reviews/NLI-WO-002-phase-a-address-points-observation-crosswalk-authorization.md` | `b9b7809b5c79ccde5ce9f6596c1ffeb277bb51d7` | `50d06db1146bfd35d630cf04f71119f543a295d95251174ac09bf53ac6302a52` |
| parent control: address-points observation acceptance | `docs/sda/reviews/NLI-WO-002-phase-a-address-points-observation-crosswalk-acceptance.md` | `9c017bb8cca1ea89c70af0e915c426fbb7758a4b` | `ffebd7121d3558e614cafc1bc6fab88f185c0dfc71564d3b32fcdb62832372a6` |
| parent oracle: address-records identity | `docs/sda/acceptance/NLI-WO-002-phase-a-address-records-identity-expected.json` | `79e3ee0ccccbfad318a61d58ae036ed8170e0a77` | `16d1034b786a77d31b6863774807e66d87a337fa78c1a4202e401fbcddecd06e` |
| parent control: address-records identity authorization | `docs/sda/reviews/NLI-WO-002-address-records-identity-next.md` | `caf9ddbd0c6ca1898d6ed9ca6d703018656f9cc7` | `192216b00b2e5169787238ce1214466ab335de9ebf8a45d3458bbea077f0ccb6` |
| parent control: address-records identity acceptance | `docs/sda/reviews/NLI-WO-002-phase-a-address-records-identity-pattern-acceptance.md` | `0356abb830fba129b997d52cee17b8f9bb2b5232` | `6678efa72a7e90a64052fae593244e8e05204cb0f979be417356566ab303e4eb` |
| parent oracle: address-records geometry | `docs/sda/acceptance/NLI-WO-002-phase-a-address-records-geometry-expected.json` | `bd3e821f07e0a1d3968e3dd6f76e6201ea7229fd` | `7a5e68c4639fe290fd46c38d41c754ae25737bee8b260278817970e7758d20e2` |
| parent correction oracle: address-records geometry | `docs/sda/acceptance/NLI-WO-002-phase-a-address-records-geometry-correction-oracle.json` | `2efd13161fb17e31ad08f7aabb700dcc6bf6d358` | `ed5afa99495234a609762117c102793644529b5b1dfcdf784528a67a3c2ddee2` |
| parent control: address-records geometry assessment | `docs/sda/reviews/NLI-WO-002-phase-a-address-records-geometry-assessment.md` | `f376dae87e30f6a38f7330437f187e6177269b3f` | `b89d7d4ff7f8341d2534686c30cc6bc83d680d8bdc12101eb14bbe0e209ec28d` |
| parent control: address-records geometry acceptance | `docs/sda/reviews/NLI-WO-002-phase-a-address-records-geometry-pattern-acceptance.md` | `7bed98d817a3d173171c313903993f28c5c60ab9` | `c1aa8f68f611643c81d42cb15cb2ac71c7384ece5acab143b3da25d8aa67d214` |
| parent oracle: citizen-geotag identity | `docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-identity-expected.json` | `61fb777a2af5a917b4ea7bbff0d6c7dff09241ba` | `65e4f2511f70ed1e94562f4973fbbb1ab072592d3b27b94f2a459843647af45e` |
| parent control: citizen-geotag identity authorization | `docs/sda/reviews/NLI-WO-002-phase-a-citizen-geotag-identity-authorization.md` | `7e505dbfc850c4dd0b8686f945d73c90755b959c` | `821b2b5280e25da8928a6791b8ae6a67379f80d5b8292d3f9784286a44336034` |
| parent control: citizen-geotag identity final assessment | `docs/sda/reviews/NLI-WO-002-PA-ID-04-final-assessment.json` | `ed297d756835ee60d9d0ae93c14e7654174664f8` | `6e83b8b73b7c378593a662fa66b47c0812dc1c0e24a049f0ca3028ef6825cfdc` |
| parent oracle: citizen-geotag geometry | `docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-geometry-expected.json` | `d5ae8a9a859ec466b68365ee006c310a85955504` | `5a09abd8a017dcbf8210040e9311bc4118be82e24c245cafa485987eb5932a46` |
| parent correction oracle: citizen-geotag geometry | `docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-geometry-correction-oracle.json` | `40fd53c8ae810bc17f031556f634244b5930b2c1` | `f2cbb6689154616955b330c068b4bdfcdaac4b18642799fcca1f94270fe0d7f2` |
| parent control: citizen-geotag geometry authorization | `docs/sda/reviews/NLI-WO-002-phase-a-citizen-geotag-geometry-authorization.md` | `038a5baf74bf3fe601eaf139de7b7d3ea29d315d` | `8dc23e6395c2a6319c1c62bd2a3e422a19d4910a801bf167f62c94a181b808a8` |
| parent control: citizen-geotag geometry acceptance | `docs/sda/reviews/NLI-WO-002-phase-a-citizen-geotag-geometry-pattern-acceptance.md` | `1c117058bdf7b810285ab25d4dc83192bfd5e3c0` | `6762539f9021f8c95d3e23d6f6fbf4855e538549bde0a41a548328679cc71e70` |

## 2. Parent and extension boundaries

### Parent accepted family

Parent accepted-family convergence remains immutable:

- **Callables:**
  1. `transform_addresses_identity_crosswalk`
  2. `transform_address_points_geometry`
  3. `transform_address_points_observation_crosswalk`
  4. `transform_address_records_identity_crosswalk`
  5. `transform_address_records_geometry`
  6. `transform_citizen_geotag_identity_crosswalk`
  7. `transform_citizen_geotag_geometry`
- **Parent row count:** 16
- **Parent hash:** `df921407d51d97559db64f380bd7a5d112e9d3823ea985944bef94b31924c5a6`

| Owner callable | Table | Primary key |
| --- | --- | --- |
| transform_address_points_geometry | proposed_geometry_observation | `phase-a-geometry-address-points-phase-a-address-points-id` |
| transform_address_records_geometry | proposed_geometry_observation | `phase-a-geometry-address-records-phase-a-address-records-id` |
| transform_citizen_geotag_geometry | proposed_geometry_observation | `phase-a-geometry-citizen-geotag-submissions-phase-a-geotag-001` |
| transform_address_points_observation_crosswalk | proposed_legacy_crosswalk | `phase-a-crosswalk-address-points-id-to-geometry-observation` |
| transform_address_records_identity_crosswalk | proposed_legacy_crosswalk | `phase-a-crosswalk-address-records-id-to-location-record` |
| transform_addresses_identity_crosswalk | proposed_legacy_crosswalk | `phase-a-crosswalk-addresses-id-to-location-record` |
| transform_citizen_geotag_identity_crosswalk | proposed_legacy_crosswalk | `phase-a-crosswalk-citizen-geotag-id-to-location-record` |
| transform_address_records_identity_crosswalk | proposed_location_record | `phase-a-location-address-records-id` |
| transform_addresses_identity_crosswalk | proposed_location_record | `phase-a-location-address-reference` |
| transform_citizen_geotag_identity_crosswalk | proposed_location_record | `phase-a-location-citizen-geotag-001` |
| transform_address_points_geometry | proposed_migration_exception | `phase-a-exception-geometry-authority-address-points-phase-a-address-points-id` |
| transform_address_records_geometry | proposed_migration_exception | `phase-a-exception-geometry-authority-address-records-phase-a-address-records-id` |
| transform_citizen_geotag_geometry | proposed_migration_exception | `phase-a-exception-geometry-authority-citizen-geotag-submissions-phase-a-geotag-001` |
| transform_address_records_identity_crosswalk | proposed_registry_subject | `phase-a-subject-phase-a-location-address-records-id` |
| transform_addresses_identity_crosswalk | proposed_registry_subject | `phase-a-subject-phase-a-location-address-reference` |
| transform_citizen_geotag_identity_crosswalk | proposed_registry_subject | `phase-a-subject-phase-a-location-citizen-geotag-001` |

### Proposed administrative extension boundary

- **Proposed extension callable:** `transform_admin_units_identity_crosswalk`
- **Transform group:** `WO002-R06-identity-crosswalk-admin_units`
- **Owned rows:** exactly 3

| Owner callable | Table | Primary key |
| --- | --- | --- |
| transform_admin_units_identity_crosswalk | proposed_administrative_unit | `administrative-unit:admin_units:phase-a-admin-units-id` |
| transform_admin_units_identity_crosswalk | proposed_legacy_crosswalk | `crosswalk:admin_units:id:phase-a-admin-units-id:to:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id` |
| transform_admin_units_identity_crosswalk | proposed_registry_subject | `subject:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id` |

The administrative extension must **not** own or create:

- `proposed_country`
- source authority
- source package
- source record
- evidence object
- administrative version
- code history
- name record
- geometry observation/version
- migration exception
- decision event
- public alias
- publication output
- province identity
- territory identity

## 3. Convergence architecture evaluation

### Option A — Modify the existing accepted convergence directly

Rejected. Risks:

- mutates the already accepted 16-row parent control and report evidence;
- changes the semantics of the existing `accepted-family-convergence` command;
- replaces the six accepted three-chain order proofs with a new proof domain;
- invalidates the existing parent hash `df921407d51d97559db64f380bd7a5d112e9d3823ea985944bef94b31924c5a6` as a standalone immutable acceptance artifact;
- blurs whether future failures belong to the parent accepted family or to the administrative extension.

### Option B — Add a reviewer-controlled extension layer

Recommended. It preserves the existing parent convergence unchanged. A future reviewer-owned extension control can reference the immutable parent control/report and add Chain D without editing the parent artifact set.

Proposed future command, not created here:

```text
accepted-family-admin-extension-convergence
```

Proposed future report, not created here:

```text
docs/sda/data-model/phase-a-accepted-family-admin-extension-report.json
```

### Option C — Keep the administrative slice standalone

Possible but weaker. Costs:

- no order-invariance evidence between parent family and administrative shell;
- no unified ownership/collision proof across the 19-row candidate family;
- future reviewers must mentally combine two separate proof domains;
- prerequisite sharing, especially `phase-a-country-gq`, remains unproven at convergence level.

### Recommendation

**Option B — reviewer-controlled extension layer.** Do not create the control, command, report, authorization, or CI integration in this checkpoint.

## 4. Proposed four-chain model

Retain:

- **Chain A:** addresses identity → address-points geometry → address-points observation crosswalk
- **Chain B:** address-records identity → address-records geometry
- **Chain C:** citizen-geotag identity → citizen-geotag geometry

Add:

- **Chain D:** administrative-unit identity shell

### Chain D independence assessment

Current expected assessment:

- Chain D requires only reviewed country and source-lineage prerequisites.
- Chain D does not require an accepted address, address-record, or citizen identity.
- Chains A–C do not require Chain D because province and territory fields remain context-only in the currently accepted slices.
- Administrative-context integration remains a separate blocked slice.

Contradicting evidence found: `none`.

## 5. Candidate 19-row union

The candidate expected union is built from:

1. independently reviewed 16-row parent expected union; and
2. three rows from `docs/sda/acceptance/NLI-WO-002-phase-a-admin-units-identity-shell-expected.json`.

It is **not** derived from observed report rows.

### Candidate table counts

| Table | Count |
| --- | --- |
| proposed_administrative_unit | 1 |
| proposed_geometry_observation | 3 |
| proposed_legacy_crosswalk | 5 |
| proposed_location_record | 3 |
| proposed_migration_exception | 3 |
| proposed_registry_subject | 4 |

### Exact candidate row keys and owners

| # | Owner callable | Table | Primary key |
| --- | --- | --- | --- |
| 1 | transform_admin_units_identity_crosswalk | proposed_administrative_unit | `administrative-unit:admin_units:phase-a-admin-units-id` |
| 2 | transform_address_points_geometry | proposed_geometry_observation | `phase-a-geometry-address-points-phase-a-address-points-id` |
| 3 | transform_address_records_geometry | proposed_geometry_observation | `phase-a-geometry-address-records-phase-a-address-records-id` |
| 4 | transform_citizen_geotag_geometry | proposed_geometry_observation | `phase-a-geometry-citizen-geotag-submissions-phase-a-geotag-001` |
| 5 | transform_admin_units_identity_crosswalk | proposed_legacy_crosswalk | `crosswalk:admin_units:id:phase-a-admin-units-id:to:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id` |
| 6 | transform_address_points_observation_crosswalk | proposed_legacy_crosswalk | `phase-a-crosswalk-address-points-id-to-geometry-observation` |
| 7 | transform_address_records_identity_crosswalk | proposed_legacy_crosswalk | `phase-a-crosswalk-address-records-id-to-location-record` |
| 8 | transform_addresses_identity_crosswalk | proposed_legacy_crosswalk | `phase-a-crosswalk-addresses-id-to-location-record` |
| 9 | transform_citizen_geotag_identity_crosswalk | proposed_legacy_crosswalk | `phase-a-crosswalk-citizen-geotag-id-to-location-record` |
| 10 | transform_address_records_identity_crosswalk | proposed_location_record | `phase-a-location-address-records-id` |
| 11 | transform_addresses_identity_crosswalk | proposed_location_record | `phase-a-location-address-reference` |
| 12 | transform_citizen_geotag_identity_crosswalk | proposed_location_record | `phase-a-location-citizen-geotag-001` |
| 13 | transform_address_points_geometry | proposed_migration_exception | `phase-a-exception-geometry-authority-address-points-phase-a-address-points-id` |
| 14 | transform_address_records_geometry | proposed_migration_exception | `phase-a-exception-geometry-authority-address-records-phase-a-address-records-id` |
| 15 | transform_citizen_geotag_geometry | proposed_migration_exception | `phase-a-exception-geometry-authority-citizen-geotag-submissions-phase-a-geotag-001` |
| 16 | transform_address_records_identity_crosswalk | proposed_registry_subject | `phase-a-subject-phase-a-location-address-records-id` |
| 17 | transform_addresses_identity_crosswalk | proposed_registry_subject | `phase-a-subject-phase-a-location-address-reference` |
| 18 | transform_citizen_geotag_identity_crosswalk | proposed_registry_subject | `phase-a-subject-phase-a-location-citizen-geotag-001` |
| 19 | transform_admin_units_identity_crosswalk | proposed_registry_subject | `subject:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id` |

### Hashes and derivation

- **Parent union hash:** `df921407d51d97559db64f380bd7a5d112e9d3823ea985944bef94b31924c5a6`
- **Accepted administrative slice hash:** `7748ba9691b8d287b76383402959a5c8c2deb0be71c3502bad0bcfb1d080f27c`
- **Administrative rows hash under proposed extension envelope:** `7afecb457d108d2fd4d7a3d632675b613de4885433d6260b45842cd130769886`
- **Candidate 19-row hash:** `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41`

Derivation procedure:

1. Load parent expected rows through the existing `accepted_family_expected_union()` path, which reads accepted reviewer-owned parent oracles under guarded oracle access.
2. Load administrative expected rows from the administrative reviewer oracle under guarded oracle access.
3. Wrap the administrative rows with the proposed extension ownership metadata: `owning_callable`, `source_identity`, `classification`.
4. Normalize values with the same canonical helpers currently used by accepted-family convergence: `normalize_json`, `norm_row`, deterministic sorting by `(table, primary_key JSON)` and `sha(rows)` using JSON sort keys and compact separators.
5. Hash the resulting 19-row array.

The candidate hash is planning evidence only. It is not reviewer authority.

## 6. Proposed row ownership declarations

Exactly three proposed declarations are added by this mapping:

| Table | Primary key | Owner |
| --- | --- | --- |
| proposed_administrative_unit | `administrative-unit:admin_units:phase-a-admin-units-id` | transform_admin_units_identity_crosswalk |
| proposed_legacy_crosswalk | `crosswalk:admin_units:id:phase-a-admin-units-id:to:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id` | transform_admin_units_identity_crosswalk |
| proposed_registry_subject | `subject:administrative_unit:administrative-unit:admin_units:phase-a-admin-units-id` | transform_admin_units_identity_crosswalk |

Expected ownership total after extension: **19**.

Ownership audit:

- primary-key collisions: `0`
- semantic crosswalk collisions: `0`
- native-ID subject collisions: `0`
- owner collisions: `0`
- target-entity collisions: `0`
- accepted address/geotag subject reuse: `0`
- generic subject reuse: `0`

## 7. Prerequisite convergence audit

| Prerequisite | Table | Parent current value | Proposed extension value | Identical | Future action | Cross-owner update possible | Expected failure if conflict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| phase-a-country-gq | proposed_country | country_id=`phase-a-country-gq`<br>created_at=`2026-07-15T00:00:00Z`<br>iso2_code=`GQ`<br>lifecycle_state=`active`<br>official_name_en=<redacted/context><br>official_name_es=<redacted/context><br>source_authority_id=`phase-a-authority-conditional-admin-reference` | country_id=`phase-a-country-gq`<br>created_at=`2026-07-15T00:00:00Z`<br>iso2_code=`GQ`<br>lifecycle_state=`active`<br>official_name_en=<redacted/context><br>official_name_es=<redacted/context><br>source_authority_id=`phase-a-authority-conditional-admin-reference` | true | reuse existing parent country row; extension must not touch | false | prerequisite row changed / lineage validation failure before transform output |
| phase-a-authority-conditional-admin-reference | proposed_source_authority | authority_class=`registry-authority`<br>authority_name=<redacted/context><br>legal_basis=<redacted/context><br>source_authority_id=`phase-a-authority-conditional-admin-reference`<br>status=`candidate` | authority_class=`registry-authority`<br>authority_name=<redacted/context><br>legal_basis=<redacted/context><br>source_authority_id=`phase-a-authority-conditional-admin-reference`<br>status=`candidate` | true | reuse if present | false | prerequisite row changed / lineage validation failure before transform output |
| phase-a-source-package-admin-units | proposed_source_package | `absent` | licence_id=`None`<br>load_context=`{'phase': 'A', 'source_table': 'admin_units'}`<br>loaded_at=`2026-07-15T00:00:00Z`<br>package_checksum=`135f036e3f7c0f621fe5e90e48557a178d413d7b034f2c320eb3742263df7276`<br>package_name=`Phase A source package admin_units`<br>source_authority_id=`phase-a-authority-conditional-admin-reference`<br>source_package_id=`phase-a-source-package-admin-units` | false | insert by extension setup prerequisite helper; not owned by callable | false | prerequisite row changed / lineage validation failure before transform output |
| phase-a-source-record-admin-units-001 | proposed_source_record | `absent` | raw_payload_classification=`government-internal`<br>raw_payload_hash=`135f036e3f7c0f621fe5e90e48557a178d413d7b034f2c320eb3742263df7276`<br>recorded_at=`2026-07-15T00:00:00Z`<br>source_key=`admin_units:phase-a-admin-units-id`<br>source_package_id=`phase-a-source-package-admin-units`<br>source_record_id=`phase-a-source-record-admin-units-001` | false | insert by extension setup prerequisite helper; not owned by callable | false | prerequisite row changed / lineage validation failure before transform output |
| phase-a-evidence-admin-units | proposed_evidence_object | `absent` | captured_at=`2026-07-15T00:00:00Z`<br>classification=`government-internal`<br>content_hash=`135f036e3f7c0f621fe5e90e48557a178d413d7b034f2c320eb3742263df7276`<br>evidence_object_id=`phase-a-evidence-admin-units`<br>media_type=`application/json`<br>retention_state=`active`<br>source_record_id=`phase-a-source-record-admin-units-001`<br>storage_uri=<redacted/context> | false | insert by extension setup prerequisite helper; not owned by callable | false | prerequisite row changed / lineage validation failure before transform output |

### Current-source fixture context

Raw administrative names, codes, parent IDs, province codes, lifecycle/status, sort order, and timestamps remain redacted in this planning artifact. The extension may use their hashes and field-presence evidence for control purposes, but must not leak raw context values in future reports.

| Source context | Source key | Field names | Normalized value hash | Raw values redacted | Future action |
| --- | --- | --- | --- | --- | --- |
| current_source.provinces fixture context | `provinces:phase-a-provinces-001` | `code`, `created_at`, `name` | `b97c22f82fa5231aefa59dc9010724c502d70c3bd812d0bf627eb1cbf1103f37` | true | load current_source fixture only; not owned by extension callable |
| current_source.admin_units fixture row | `admin_units:phase-a-admin-units-001` | `code`, `created_at`, `id`, `level`, `name_en`, `name_es`, `parent_id`, `province_code`, `sort_order`, `status`, `updated_at` | `9eaf7f3c59593dcec1fba87d252a51ab7e379d26747c1eb01e6fb2746495eb6a` | true | load current_source fixture only; callable consumes id and context; no context-owned target rows |

### Future prerequisite setup ownership

- `setup_accepted_family_convergence_database()` remains owner of parent A–C prerequisites and must remain unchanged.
- A future extension setup helper should own only administrative source-lineage prerequisites not already present in the parent setup.
- `phase-a-country-gq` is reused from parent/base target prerequisites; the administrative callable must consume it and must not own, change, or reinsert it.
- The administrative callable must not own source authority/package/record/evidence rows; those are setup prerequisites, not accepted-family owned rows.

## 8. Execution and idempotency expectations

Fresh extension database:

- parent callables insert 16 accepted rows;
- administrative callable inserts 3 accepted rows;
- total inserts = 19;
- total updates = 0;
- total deletes = 0.

Second complete execution:

- inserts = 0;
- updates = 0;
- deletes = 0;
- union row count = 19;
- union hash unchanged: `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41`.

Delta expectations:

| Order | Parent delta | Administrative delta | Updates | Deletes |
|---|---:|---:|---:|---:|
| Parent first, administrative second | 16 | 3 | 0 | 0 |
| Administrative first, parent second | 16 | 3 | 0 | 0 |

No callable may update, delete, or replace another callable’s owned row or prerequisite row.

## 9. Order invariance plan

The parent command must continue proving the original six A/B/C permutations and 16-row hash. A future extension command must add separate four-chain order evidence without replacing the parent proof.

| # | Chain order | Expected rows | Expected hash | Ownership collisions | Prerequisite mutations | Semantic crosswalk duplicates | Multiple-target resolutions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | A → B → C → D | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 2 | A → B → D → C | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 3 | A → C → B → D | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 4 | A → C → D → B | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 5 | A → D → B → C | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 6 | A → D → C → B | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 7 | B → A → C → D | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 8 | B → A → D → C | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 9 | B → C → A → D | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 10 | B → C → D → A | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 11 | B → D → A → C | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 12 | B → D → C → A | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 13 | C → A → B → D | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 14 | C → A → D → B | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 15 | C → B → A → D | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 16 | C → B → D → A | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 17 | C → D → A → B | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 18 | C → D → B → A | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 19 | D → A → B → C | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 20 | D → A → C → B | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 21 | D → B → A → C | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 22 | D → B → C → A | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 23 | D → C → A → B | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |
| 24 | D → C → B → A | 19 | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` | 0 | 0 | 0 | 0 |

## 10. Future read-only comparator design

A future separate read-only comparator must:

1. verify the immutable parent convergence control;
2. verify the future extension control;
3. open all reviewer-owned oracles only inside guarded comparator access;
4. compare expected to actual;
5. compare actual to expected;
6. compare all normalized values;
7. verify candidate 19-row hash `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41`;
8. execute scoped expected absences;
9. execute ownership and semantic controls;
10. prove target writes are blocked in the comparator transaction.

Transform callables must not receive expected rows or oracle values.

## 11. Future prerequisite, dependency, and conflict tests

Every future database failure must record same-database pre/post rows, counts, hashes, and equality before reset.

### Administrative prerequisite tests

- missing country
- changed country
- missing source record
- wrong source package
- wrong source authority
- wrong evidence object
- classification drift
- lineage-hash mismatch

### Ownership conflict tests

- existing conflicting administrative unit
- existing conflicting administrative subject
- existing conflicting administrative crosswalk
- duplicate administrative owner declaration
- administrative row assigned to another callable
- accepted parent row assigned to administrative callable

### Cross-family isolation tests

- admin shell must not create a location record
- admin shell must not create an address subject
- parent callables must not create an administrative unit
- parent callables must not create an administrative subject
- administrative source fields must not alter parent identities
- parent source fields must not alter administrative identity

### Unexpected extended-union tests

- administrative version
- code-history row
- name record
- geometry observation
- geometry version
- migration exception
- public alias
- decision event
- publication output
- province identity
- territory identity

## 12. Future report and privacy boundaries

The future extension report must not expose raw:

- admin unit names;
- codes;
- parent IDs;
- province codes;
- status;
- sort order;
- citizen data;
- precise restricted geometry values.

Future report schema updates must be path-aware and must include:

- new allowed table domains: `proposed_administrative_unit`, `proposed_registry_subject`, `proposed_legacy_crosswalk`;
- new allowed owner domain: `transform_admin_units_identity_crosswalk`;
- administrative redaction requirements;
- unknown-key mutation tests;
- nested-structure mutation tests;
- citizen privacy regression tests;
- administrative context-value leakage tests.

The original 16-row convergence report schema must remain unchanged.

## 13. Future artifact boundaries

Proposed, not created here:

| Artifact | Proposed path / ID |
|---|---|
| Extension mapping | `docs/agent/tasks/NLI-WO-002-phase-a-admin-units-convergence-extension-mapping.md` |
| Reviewer-owned extension control | `docs/sda/acceptance/NLI-WO-002-phase-a-admin-units-convergence-extension-control.json` |
| Extension authorization | `docs/sda/reviews/NLI-WO-002-phase-a-admin-units-convergence-extension-authorization.md` |
| Extension convergence report | `docs/sda/data-model/phase-a-accepted-family-admin-extension-report.json` |
| Extension harness command | `accepted-family-admin-extension-convergence` |
| CI invocation | add the future command only after reviewer-owned extension control exists |

Do not modify the existing parent control in place.

## 14. Closed gates preserved

This mapping does not:

- integrate the administrative callable into convergence;
- alter the existing accepted-family sequence;
- change the parent 16-row union or hash;
- create an extension control or authorization;
- authorize administrative versions, codes, names, hierarchy, geometry, publication, province identity, territory identity, or context integration;
- authorize another transform group;
- accept broad Phase A;
- close F02 or F14;
- authorize Review 12 or Phase B;
- authorize publication, deployment, or merge;
- modify PR #8.

## 15. Mapping return fields

| Field | Value |
|---|---|
| Recommended architecture | Option B — reviewer-controlled extension layer |
| Parent convergence changed | false |
| Parent command changed | false |
| Parent control changed | false |
| Parent report changed | false |
| Parent callables | 7 |
| Extension callable | `transform_admin_units_identity_crosswalk` |
| Proposed chain count | 4 |
| Proposed chain permutations | 24 |
| Parent row count | 16 |
| Administrative extension rows | 3 |
| Candidate union row count | 19 |
| Candidate table counts | `{"proposed_administrative_unit": 1, "proposed_geometry_observation": 3, "proposed_legacy_crosswalk": 5, "proposed_location_record": 3, "proposed_migration_exception": 3, "proposed_registry_subject": 4}` |
| Parent union hash | `df921407d51d97559db64f380bd7a5d112e9d3823ea985944bef94b31924c5a6` |
| Administrative accepted slice hash | `7748ba9691b8d287b76383402959a5c8c2deb0be71c3502bad0bcfb1d080f27c` |
| Administrative extension-envelope hash | `7afecb457d108d2fd4d7a3d632675b613de4885433d6260b45842cd130769886` |
| Candidate 19-row hash | `1f9a472978313f3ebdc6f82869a2e0af4eb7786c08f4537ba8629b5dc3ddbb41` |
| Candidate hash derivation | reviewer-owned expected rows only; no observed report rows as truth |
| Ownership entries added | 3 |
| Proposed ownership total | 19 |
| Ownership collisions | 0 |
| Semantic crosswalk collisions | 0 |
| Subject/native-ID collisions | 0 |
| Country prerequisite state | existing parent/base prerequisite reused; extension must not own/change |
| Authority prerequisite state | extension setup prerequisite, not owned by callable |
| Package prerequisite state | extension setup prerequisite, not owned by callable |
| Source-record prerequisite state | extension setup prerequisite, not owned by callable |
| Evidence prerequisite state | extension setup prerequisite, not owned by callable |
| Prerequisite conflicts | fail before accepted output; same-database rollback required |
| Cross-owner prerequisite updates | prohibited; expected 0 |
| Chain D dependencies | reviewed country and source-lineage prerequisites only |
| Parent dependencies on Chain D | none in current accepted slices |
| Administrative-context integration included | false |
| First-run total inserts | 19 |
| First-run updates | 0 |
| Second-run inserts | 0 |
| Second-run updates | 0 |
| Dependency tests mapped | yes |
| Conflict tests mapped | yes |
| Unexpected-union tests mapped | yes |
| Rollback contracts mapped | yes |
| Privacy/report tests mapped | yes |
| Proposed extension control path | `docs/sda/acceptance/NLI-WO-002-phase-a-admin-units-convergence-extension-control.json` |
| Proposed extension command | `accepted-family-admin-extension-convergence` |
| Proposed extension report | `docs/sda/data-model/phase-a-accepted-family-admin-extension-report.json` |
| Recommended next reviewer artifact | reviewer-owned extension control and authorization |
| F02 status | open / not closed by this mapping |
| F14 status | open / not closed by this mapping |
| Remaining closed gates | broad Phase A, Review 12, Phase B, publication, deployment, merge, PR #8 modification, additional administrative slices |
| Current instructed action | prepare the administrative accepted-family convergence-extension mapping only |
| Next instruction required from SDA | YES — before creating an extension control, changing the convergence harness, integrating the administrative callable, modifying CI, authorizing another administrative slice, broad Phase A reassessment, F02/F14 closure, Review 12, Phase B, publication, deployment, or merge |
