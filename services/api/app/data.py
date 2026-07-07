PROVINCES = [
    {'id': 'prov-annobon', 'code': 'AN', 'name': 'Annobón'},
    {'id': 'prov-bioko-norte', 'code': 'BN', 'name': 'Bioko Norte'},
    {'id': 'prov-bioko-sur', 'code': 'BS', 'name': 'Bioko Sur'},
    {'id': 'prov-centro-sur', 'code': 'CS', 'name': 'Centro Sur'},
    {'id': 'prov-djibloho', 'code': 'DJ', 'name': 'Djibloho'},
    {'id': 'prov-kie-ntem', 'code': 'KN', 'name': 'Kié-Ntem'},
    {'id': 'prov-litoral', 'code': 'LI', 'name': 'Litoral'},
    {'id': 'prov-wele-nzas', 'code': 'WN', 'name': 'Wele-Nzas'},
]

ADMIN_UNITS = [
    {'id': 'admin-unit-annobon', 'level': 'province', 'code': 'AN', 'parent_id': None, 'name_es': 'Annobón', 'name_en': 'Annobón', 'status': 'active', 'sort_order': 10},
    {'id': 'admin-unit-bioko-norte', 'level': 'province', 'code': 'BN', 'parent_id': None, 'name_es': 'Bioko Norte', 'name_en': 'Bioko Norte', 'status': 'active', 'sort_order': 20},
    {'id': 'admin-unit-bioko-sur', 'level': 'province', 'code': 'BS', 'parent_id': None, 'name_es': 'Bioko Sur', 'name_en': 'Bioko Sur', 'status': 'active', 'sort_order': 30},
    {'id': 'admin-unit-centro-sur', 'level': 'province', 'code': 'CS', 'parent_id': None, 'name_es': 'Centro Sur', 'name_en': 'Centro Sur', 'status': 'active', 'sort_order': 40},
    {'id': 'admin-unit-djibloho', 'level': 'province', 'code': 'DJ', 'parent_id': None, 'name_es': 'Djibloho', 'name_en': 'Djibloho', 'status': 'active', 'sort_order': 50},
    {'id': 'admin-unit-kie-ntem', 'level': 'province', 'code': 'KN', 'parent_id': None, 'name_es': 'Kié-Ntem', 'name_en': 'Kié-Ntem', 'status': 'active', 'sort_order': 60},
    {'id': 'admin-unit-litoral', 'level': 'province', 'code': 'LI', 'parent_id': None, 'name_es': 'Litoral', 'name_en': 'Litoral', 'status': 'active', 'sort_order': 70},
    {'id': 'admin-unit-wele-nzas', 'level': 'province', 'code': 'WN', 'parent_id': None, 'name_es': 'Wele-Nzas', 'name_en': 'Wele-Nzas', 'status': 'active', 'sort_order': 80},
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
    'citizen-geotagging',
    'signage-export',
    'integrations',
]

TERRITORIES = [
    {
        'id': 'territory-malabo-urban-core',
        'name': 'Malabo Urban Core',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'capital-urban-core',
        'readiness': 'active-mapping',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-santa-isabel',
        'name': 'Santa Isabel',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-los-angeles',
        'name': 'Los Ángeles',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-alcaide',
        'name': 'Alcaide',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-santa-maria',
        'name': 'Santa María',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-semu',
        'name': 'Semu',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-area-presidencial',
        'name': 'Área Presidencial',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-sacriba',
        'name': 'Sacriba',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-ela-nguema',
        'name': 'Ela Nguema',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-paraiso',
        'name': 'Paraíso',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-sampaka',
        'name': 'Sampaka',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-buena-esperanza',
        'name': 'Buena Esperanza',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-malabo-ii',
        'name': 'Malabo II',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-caribe',
        'name': 'Caribe',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-la-begona-1',
        'name': 'La Begoña 1',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-basile',
        'name': 'Basilé',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-basupu',
        'name': 'Basupú',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-basupu-fishtown',
        'name': 'Basupú Fishtown',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-rebola',
        'name': 'Rebola',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-sipopo',
        'name': 'Sipopo',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-caracolas',
        'name': 'Caracolas',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-aeropuerto-corridor',
        'name': 'Carretera del Aeropuerto',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
    {
        'id': 'territory-malabo-paseo-maritimo',
        'name': 'Paseo Marítimo',
        'province_code': 'BN',
        'admin_unit_id': 'admin-unit-bioko-norte',
        'type': 'map-referenced-local-area',
        'readiness': 'intake-routing',
        'is_archived': False,
    },
]

ROADS = [
    {
        'id': 'road-malabo-independence-avenue',
        'name': 'Avenida de la Independencia, Malabo',
        'territory_id': 'territory-malabo-urban-core',
        'status': 'active-mapping',
        'length_km': '1.8',
        'is_archived': False,
    },
]

BUILDINGS = [
    {
        'id': 'building-malabo-civic-reference',
        'label': 'Malabo Civic Reference Point',
        'territory_id': 'territory-malabo-urban-core',
        'road_id': 'road-malabo-independence-avenue',
        'status': 'active-mapping',
        'usage': 'civic-reference',
        'is_archived': False,
    },
]

ADDRESSES = [
    {
        'id': 'addr-malabo-001',
        'formatted': 'Avenida de la Independencia, Malabo',
        'territory_id': 'territory-malabo-urban-core',
        'road_id': 'road-malabo-independence-avenue',
        'building_id': 'building-malabo-civic-reference',
        'province_code': 'BN',
        'public_code': 'EG-BN-MALABO-001A',
        'issuance_method': 'registry-publication',
        'source': 'seed-registry',
        'verification_status': 'official',
        'status': 'verified',
        'publication_state': 'published',
        'is_archived': False,
    },
]

FIELD_ASSIGNMENTS = [
    {
        'assignment_id': 'field-malabo-001',
        'territory_id': 'territory-malabo-urban-core',
        'territory': 'Malabo Urban Core',
        'task': 'Capital citizen geotag verification',
        'team': 'Bioko Norte Verification Cell',
        'priority': 'critical',
    },
]

FIELD_SUBMISSIONS = [
    {
        'id': 'submission-malabo-road-001',
        'assignment_id': 'field-malabo-001',
        'territory_id': 'territory-malabo-urban-core',
        'submission_type': 'road',
        'candidate_name': 'Carretera del Aeropuerto routing confirmation',
        'candidate_status': 'submitted',
        'notes': 'Pilot verification row for Bioko Norte routing review.',
        'submitted_by': 'Bioko Norte Verification Cell',
        'review_status': 'submitted',
        'registry_entity_id': None,
    },
]

IMPORT_JOBS = [
    {
        'id': 'import-malabo-pilot-001',
        'name': 'Malabo pilot intake',
        'source_name': 'bioko_norte_pilot_registry.csv',
        'status': 'draft',
    }
]

IMPORT_ROWS = [
    {
        'job_id': 'import-malabo-pilot-001',
        'row_number': 1,
        'submission_type': 'road',
        'territory_id': 'territory-malabo-urban-core',
        'candidate_name': 'Carretera del Aeropuerto routing confirmation',
        'candidate_status': 'ready-for-import',
        'notes': 'Bioko Norte pilot road register',
        'validation_status': 'valid',
        'validation_message': 'Ready to commit',
    },
    {
        'job_id': 'import-malabo-pilot-001',
        'row_number': 2,
        'submission_type': 'address',
        'territory_id': 'territory-malabo-urban-core',
        'candidate_name': 'Avenida de la Independencia, Malabo',
        'candidate_status': 'ready-for-import',
        'notes': 'Bioko Norte pilot address sheet',
        'validation_status': 'valid',
        'validation_message': 'Ready to commit',
    },
]

PUBLICATION_PACKS = [
    {
        'id': 'publication-pack-bioko-norte-001',
        'name': 'Published addresses — Bioko Norte pilot',
        'status': 'published',
        'audience': 'Pilot review / programme steering',
        'address_ids': ['addr-malabo-001'],
    }
]
