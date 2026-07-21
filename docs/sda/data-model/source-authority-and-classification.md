# Source, Evidence, Lineage, and Classification

Lineage chain: `source_authority -> source_package -> source_record -> evidence_object/geometry_observation -> decision_event -> location_record_version/location_record_assertion/publication_release_item`. Every field with source significance has field-level assertion support through `location_record_assertion`. Sensitive identity/contact values from current fields are retained as restricted source payload hashes or evidence, not projected publicly.

Projection is allowlisted: public release requires `publication_release_item`; operator case files may include evidence/source/quality according to role; partner projections are scoped by `partner_projection.response_field_set`.
