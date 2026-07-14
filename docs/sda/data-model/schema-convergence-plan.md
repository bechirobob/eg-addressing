# Expand–Migrate–Contract Convergence Plan

Built from the validated field map. NLI-WO-002B remains unauthorized. All batches create `migration_exception` records for unmapped, invalid, conflicting, or authority-blocked records rather than dropping data.

| Batch | Purpose | Dependencies | Field ownership/write behavior | Idempotency key | Validation query/tolerance | Compatible app versions | Recovery boundary | Owner | Cutover/abort gate |
|---|---|---|---|---|---|---|---|---|---|
| B0 | backup/readiness | none | No target writes; freeze release baseline | migration ledger + backup manifest | 0 unresolved readiness errors | current app only | restore backup before expansion | SDA/Ops | stop if backup/restore unproven |
| B1 | source/authority foundations | B0 | source_authority/source_package/source_record/evidence/licence | source checksum + source key | source package counts/checksums exact | current + expand app | drop added empty target tables before data backfill | Data Authority | all source packages loaded or exceptioned |
| B2 | admin/names/operational geography | B1 | administrative_unit/version/name/locality/operational_area/coverage | stable code + effective interval | no cycles; one recorded current; root rows allowed | dual-read admin adapters | forward recovery from source packages | GIS/Data Authority | admin parity and exception queue clear |
| B3 | objects and geometry observations | B1/B2 | roads/segments/buildings/entrances/units/landmarks/non-building objects/observations | source object key | geometry SRID/type/validity; no required circular inserts | dual-write evidence + object adapters | replay source observations | Registry/GIS | object counts and geometry exceptions within tolerance 0 unless RFI |
| B4 | canonical location records | B2/B3 | location_record/version/object links/assertions | address_records.id then legacy addresses.id | record count/hash parity; one current recorded version | canonical-first read with legacy fallback | rebuild from source/evidence | Registry Authority | no unmapped current fields |
| B5 | corrections/disputes/events | B4 | correction_case/dispute_case/decision_event/relationships | source event/case id | event timeline parity and no orphan decisions | dual event writes | replay events | Registry Authority | case queues reconciled |
| B6 | publication aliases/releases | B4/B5 | public_code_alias/publication_release/item/partner_projection | release manifest hash | public release items target exact version+alias; no internal-only leaks | public endpoint reads release items | withdraw/reissue release only | Publication Authority | public proof parity |
| B7 | dual read/write monitoring | B1-B6 | canonical target + legacy projection | idempotency key per command | API parity green; exception SLA met | supported current and canonical-aware app versions | forward fix and replay | Backend/Ops | monitoring window green |
| B8 | cutover | B7 | canonical-first writes/reads | command idempotency | error budget, latency, parity thresholds | canonical app version only | forward recovery preferred; rollback before irreversible contract | SDA/Ops | SDA cutover approval |
| B9 | contract/deprecate | B8 | retire legacy mutable paths | deprecation evidence | no supported app reads legacy authority | post-contract app | restore archive/read-only legacy if needed | SDA | contract acceptance |

## Conflict precedence

1. `address_records` controls canonical backfill over legacy `addresses`; legacy remains compatibility/source evidence.
2. Citizen/geotag and field submissions are evidence until promoted by `decision_event`.
3. GIS/field validated geometry wins over citizen/browser geometry; weaker geometry remains observation.
4. Publication release snapshots win for historical public proof over mutable current state.
5. Conflicts produce `migration_exception`; zero silent overwrite.

## National-scale assumptions

| Area | Planning volume | Access paths | Indexes | Partition candidate |
|---|---|---|---|---|
| location_record/version | 1.5M records / 4.5M versions initial national planning | public code lookup, operator search, history | unique public alias; record version current; search normalized label | versions by recorded_at after 10M |
| geometry_observation/version | 5M observations / 2M approved geometries | nearest/containment/bbox, quality review | GiST geom; subject+role current unique | observations by recorded month/source package after 20M |
| source_record/evidence | 10M source/evidence metadata rows | lineage and audit lookup | source package/key; hash | source_record by package/time after 20M |
| decision_event/assertion | 20M assertion/event rows | case timeline, audit, reconstruction | record version; decision type/time | time partition after 30M |
| publication_release_item | 1M public items per full national release | public proof and export | release id; public code alias; version | release-id partition for national bulk releases |
