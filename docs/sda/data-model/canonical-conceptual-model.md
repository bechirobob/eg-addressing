# Canonical Conceptual Model — National Location Infrastructure

**Status:** Draft for SDA review

## 1. Design principles

1. One canonical location/address registry authority.
2. Candidate intake and evidence are never canonical until an approval event promotes them.
3. Administrative geography, operational areas, physical addressable objects, geometry evidence, and publication projections are separate domains.
4. Public visibility is an explicit release state, not a property inferred from database presence.
5. Every canonical fact carries source, authority, time, classification, and audit lineage.

## 2. Domain areas

| Domain | Entities | Authority |
|---|---|---|
| Administrative geography | `country`, `administrative_unit`, `administrative_unit_name`, `administrative_boundary_version` | Government/GIS reference authority. |
| Operational areas | `operational_area`, `campaign_area`, `routing_assignment` | Programme/operator authority; not legal geography. |
| Addressable objects | `road`, `road_segment`, `road_name`, `parcel_reference`, `building`, `entrance`, `unit`, `landmark`, `non_building_object` | Registry authority after evidence approval. |
| Canonical registry | `location_record`, `location_record_version`, `location_record_event`, `location_record_relationship` | Sole canonical authority for national location/address records. |
| Geometry/provenance | `geometry_observation`, `geometry_version`, `geometry_quality_assessment` | GIS/data authority after validation. |
| Intake/evidence | `intake_case`, `field_observation`, `evidence_object`, `source_package`, `source_record` | Evidence authority, not canonical. |
| Publication/projection | `publication_release`, `publication_release_item`, `public_code_alias`, `partner_projection` | Publication authority after approval. |
| Corrections/disputes | `correction_case`, `dispute_case`, `resolution_event` | Registry/correction authority. |

## 3. Sole canonical authority

`location_record` is the target canonical registry anchor. It covers an addressable location, not only a postal-style address. It may reference a building/unit, entrance, road segment, landmark, parcel reference, or other approved addressable object. It must not duplicate the current `addresses` table as a parallel authority.

## 4. Core relationships

- One `location_record` has one current `location_record_version` and many historical versions.
- One `location_record_version` references zero or more addressable objects depending on context.
- One `location_record` may have many geometry versions, but only one current canonical geometry per geometry role.
- One public code may point to one active `location_record`; reused public codes are prohibited.
- One correction/dispute case targets one canonical record, one candidate, or one source observation.
- One publication release contains explicit release items and projections, not arbitrary table rows.

## 5. Administrative versus operational geography

Administrative units represent legal/reference geography. Operational areas represent service/routing/workflow areas. A territory-like operational area may overlap or cover administrative units but does not define legal hierarchy.

## 6. Addressable object model

The model supports:

- roads and road segments;
- official and candidate road names;
- landmarks and named places;
- optional external parcel references without land-title claims;
- buildings;
- entrances/access points;
- units/sub-addresses;
- non-building addressable objects such as kiosks, utility assets, community sites, and service points.

## 7. Publication model

Publication is an explicit release process. Internal registry readiness does not imply public lookup, certificate, signage, or partner release. `registry-ready` remains internal until a publication release records authority, effective date, scope, and projection.
