# Next controlled slice

Reviewed predecessor: `58925f94c9f42623a0b49afb8c3913e7d98e06aa`

Authorized group: `WO002-R06-identity-crosswalk-address_records`

Required implementation: `transform_address_records_identity_crosswalk`

Use the reviewer control at `docs/sda/acceptance/NLI-WO-002-phase-a-address-records-identity-expected.json`.

Identity derives from `address_records.id`. Other source fields are context only. Create only the reviewed location record, registry subject and crosswalk. Stop after exact-head CI. No other group is authorized.
