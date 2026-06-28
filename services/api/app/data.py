PROVINCES = [
    {'id': 'prov-centro-sur', 'code': 'CS', 'name': 'Centro Sur'},
    {'id': 'prov-djibloho', 'code': 'DJ', 'name': 'Djibloho'},
    {'id': 'prov-kie-ntem', 'code': 'KN', 'name': 'Kié-Ntem'},
    {'id': 'prov-litoral', 'code': 'LI', 'name': 'Litoral'},
    {'id': 'prov-wele-nzas', 'code': 'WN', 'name': 'Wele-Nzas'},
]

DEMO_USERS = [
    {
        'id': 'user-admin',
        'username': 'admin',
        'full_name': 'National Platform Administrator',
        'role': 'admin',
        'password': 'admin123',
    },
    {
        'id': 'user-editor',
        'username': 'editor',
        'full_name': 'Registry Editor',
        'role': 'editor',
        'password': 'editor123',
    },
    {
        'id': 'user-viewer',
        'username': 'viewer',
        'full_name': 'Program Viewer',
        'role': 'viewer',
        'password': 'viewer123',
    },
]

MODULES = [
    'auth',
    'territories',
    'registry',
    'field-workflow',
    'verification',
    'publication',
    'reporting',
    'integrations',
]

TERRITORIES = [
    {
        'id': 'territory-bata-urban-core',
        'name': 'Bata Urban Core',
        'province_code': 'LI',
        'type': 'urban-core',
        'readiness': 'active-mapping',
        'is_archived': False,
    },
    {
        'id': 'territory-oyala-civic-district',
        'name': 'Oyala Civic District',
        'province_code': 'DJ',
        'type': 'government-priority',
        'readiness': 'verification-prep',
        'is_archived': False,
    },
    {
        'id': 'territory-ebebiyin-access-corridor',
        'name': 'Ebebiyin Access Corridor',
        'province_code': 'KN',
        'type': 'cross-border-logistics',
        'readiness': 'survey-queue',
        'is_archived': False,
    },
]

ROADS = [
    {
        'id': 'road-bata-independencia',
        'name': 'Avenida de la Independencia',
        'territory_id': 'territory-bata-urban-core',
        'status': 'verified',
        'length_km': '2.4',
        'is_archived': False,
    },
    {
        'id': 'road-oyala-admin-loop',
        'name': 'Administrative Sector Loop',
        'territory_id': 'territory-oyala-civic-district',
        'status': 'field-review',
        'length_km': '1.1',
        'is_archived': False,
    },
]

BUILDINGS = [
    {
        'id': 'building-bata-block-4',
        'label': 'Block 4 Civic Cluster',
        'territory_id': 'territory-bata-urban-core',
        'road_id': 'road-bata-independencia',
        'status': 'verified',
        'usage': 'mixed-use',
        'is_archived': False,
    },
    {
        'id': 'building-oyala-ministry-annex',
        'label': 'Ministry Annex A',
        'territory_id': 'territory-oyala-civic-district',
        'road_id': 'road-oyala-admin-loop',
        'status': 'field-review',
        'usage': 'government',
        'is_archived': False,
    },
]

ADDRESSES = [
    {
        'id': 'addr-bata-001',
        'formatted': 'Avenida de la Independencia, Block 4, Bata',
        'territory_id': 'territory-bata-urban-core',
        'road_id': 'road-bata-independencia',
        'building_id': 'building-bata-block-4',
        'province_code': 'LI',
        'status': 'verified',
        'publication_state': 'published',
        'is_archived': False,
    },
    {
        'id': 'addr-oyala-002',
        'formatted': 'Sector Administrativo 2, Oyala',
        'territory_id': 'territory-oyala-civic-district',
        'road_id': 'road-oyala-admin-loop',
        'building_id': 'building-oyala-ministry-annex',
        'province_code': 'DJ',
        'status': 'field-review',
        'publication_state': 'draft',
        'is_archived': False,
    },
]

FIELD_ASSIGNMENTS = [
    {
        'assignment_id': 'field-001',
        'territory_id': 'territory-bata-urban-core',
        'territory': 'Bata Urban Core',
        'task': 'Road frontage validation',
        'team': 'Litoral Survey Unit A',
        'priority': 'high',
    },
    {
        'assignment_id': 'field-002',
        'territory_id': 'territory-oyala-civic-district',
        'territory': 'Oyala Civic District',
        'task': 'Government campus building capture',
        'team': 'Djibloho Verification Cell',
        'priority': 'critical',
    },
    {
        'assignment_id': 'field-003',
        'territory_id': 'territory-ebebiyin-access-corridor',
        'territory': 'Ebebiyin Access Corridor',
        'task': 'Access-road naming review',
        'team': 'Northern Boundary Team',
        'priority': 'medium',
    },
]

FIELD_SUBMISSIONS = [
    {
        'id': 'submission-bata-road-001',
        'assignment_id': 'field-001',
        'territory_id': 'territory-bata-urban-core',
        'submission_type': 'road',
        'candidate_name': 'Boulevard del Litoral',
        'candidate_status': 'submitted',
        'notes': 'Frontage confirmed and residents use this corridor name consistently.',
        'submitted_by': 'Litoral Survey Unit A',
        'review_status': 'submitted',
        'registry_entity_id': None,
    },
    {
        'id': 'submission-oyala-address-001',
        'assignment_id': 'field-002',
        'territory_id': 'territory-oyala-civic-district',
        'submission_type': 'address',
        'candidate_name': 'Sector Administrativo 8, Annex B, Oyala',
        'candidate_status': 'submitted',
        'notes': 'Building frontage and municipal confirmation captured.',
        'submitted_by': 'Djibloho Verification Cell',
        'review_status': 'under-review',
        'registry_entity_id': None,
    },
]

IMPORT_JOBS = [
    {
        'id': 'import-bata-legacy-001',
        'name': 'Bata legacy intake',
        'source_name': 'bata_legacy_registry.csv',
        'status': 'draft',
    }
]

IMPORT_ROWS = [
    {
        'job_id': 'import-bata-legacy-001',
        'row_number': 1,
        'submission_type': 'road',
        'territory_id': 'territory-bata-urban-core',
        'candidate_name': 'Paseo Maritimo de Bata',
        'candidate_status': 'ready-for-import',
        'notes': 'Legacy municipal road register',
        'validation_status': 'valid',
        'validation_message': 'Ready to commit',
    },
    {
        'job_id': 'import-bata-legacy-001',
        'row_number': 2,
        'submission_type': 'address',
        'territory_id': 'territory-bata-urban-core',
        'candidate_name': 'Paseo Maritimo de Bata, Parcel 18',
        'candidate_status': 'ready-for-import',
        'notes': 'Legacy parcel sheet',
        'validation_status': 'valid',
        'validation_message': 'Ready to commit',
    },
]

PUBLICATION_PACKS = [
    {
        'id': 'publication-pack-001',
        'name': 'Published addresses — Bata',
        'status': 'published',
        'audience': 'Cabinet / programme steering',
        'address_ids': ['addr-bata-001'],
    }
]
