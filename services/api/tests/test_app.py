from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

import app.db as db
import app.main as main
from app.main import app

client = TestClient(app)

ADMIN = {'id': 'user-admin', 'username': 'admin', 'full_name': 'National Platform Administrator', 'role': 'admin'}
EDITOR = {'id': 'user-editor', 'username': 'editor', 'full_name': 'Registry Editor', 'role': 'editor'}
VIEWER = {'id': 'user-viewer', 'username': 'viewer', 'full_name': 'Program Viewer', 'role': 'viewer'}


def auth_header(token: str = 'demo-token') -> dict[str, str]:
    return {'Authorization': f'Bearer {token}'}


def test_health_endpoint_returns_ok() -> None:
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert response.json()['service'] == 'eg-addressing-api'
    assert response.json()['version'] == '0.1.0'
    assert response.json()['environment']


def test_health_endpoint_sets_request_id_header() -> None:
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.headers['X-Request-ID']


def test_meta_endpoint_returns_platform_identity() -> None:
    response = client.get('/api/v1/meta')
    assert response.status_code == 200
    payload = response.json()
    assert payload['platform']['name'] == 'Equatorial Guinea National Digital Addressing Platform'
    assert payload['platform']['mode'] == 'operational-readiness'
    assert 'publication' in payload['modules']
    assert 'admin' in payload['roles']


def test_login_returns_token_and_user(monkeypatch) -> None:
    monkeypatch.setattr(main, 'authenticate_user_session', lambda username, password: {'token': 'demo-token', 'expires_at': '2026-06-29T00:00:00+00:00', 'user': ADMIN})
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    assert response.status_code == 200
    assert response.json()['user']['role'] == 'admin'
    assert response.json()['expires_at'] == '2026-06-29T00:00:00+00:00'
    assert response.json()['session_ttl_hours'] >= 1


def test_auth_me_requires_token() -> None:
    response = client.get('/api/v1/auth/me')
    assert response.status_code == 401


def test_auth_logout_requires_token() -> None:
    response = client.post('/api/v1/auth/logout')
    assert response.status_code == 401


def test_auth_logout_revokes_current_token(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: ADMIN)
    revoked: dict[str, str | None] = {'token': None}
    monkeypatch.setattr(main, 'revoke_user_session', lambda token, actor=None: revoked.__setitem__('token', token))
    response = client.post('/api/v1/auth/logout', headers=auth_header('logout-token'))
    assert response.status_code == 204
    assert revoked['token'] == 'logout-token'


def test_cookie_mode_protected_mutation_requires_csrf(monkeypatch) -> None:
    monkeypatch.setattr(main, 'SESSION_COOKIE_MODE', 'secure-http-only-cookie')
    monkeypatch.setattr(main, 'SESSION_COOKIE_SECURE', False)
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR if token == 'cookie-token' else ADMIN)

    response = client.post(
        '/api/v1/territories',
        json={'name': 'Mongomo Core', 'province_code': 'WN', 'admin_unit_id': 'admin-unit-wele-nzas', 'type': 'district-core', 'readiness': 'enumeration-ready'},
        cookies={main.SESSION_COOKIE_NAME: 'cookie-token', main.CSRF_COOKIE_NAME: 'csrf-token'},
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'csrf token required'


def test_cookie_mode_protected_mutation_accepts_matching_csrf(monkeypatch) -> None:
    monkeypatch.setattr(main, 'SESSION_COOKIE_MODE', 'secure-http-only-cookie')
    monkeypatch.setattr(main, 'SESSION_COOKIE_SECURE', False)
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR if token == 'cookie-token' else ADMIN)
    monkeypatch.setattr(
        main,
        'create_territory',
        lambda payload, actor=None: {'id': 'territory-mongomo-core', 'name': payload['name'], 'province_code': payload['province_code'], 'readiness': payload['readiness'], 'is_archived': False},
    )

    response = client.post(
        '/api/v1/territories',
        json={'name': 'Mongomo Core', 'province_code': 'WN', 'admin_unit_id': 'admin-unit-wele-nzas', 'type': 'district-core', 'readiness': 'enumeration-ready'},
        headers={'X-CSRF-Token': 'csrf-token'},
        cookies={main.SESSION_COOKIE_NAME: 'cookie-token', main.CSRF_COOKIE_NAME: 'csrf-token'},
    )

    assert response.status_code == 201
    assert response.json()['id'] == 'territory-mongomo-core'


def test_cookie_mode_public_submission_does_not_require_csrf(monkeypatch) -> None:
    monkeypatch.setattr(main, 'SESSION_COOKIE_MODE', 'secure-http-only-cookie')
    monkeypatch.setattr(main, 'preview_citizen_geotag', lambda latitude, longitude, territory_id=None, province_code=None: {'address_code': 'EG-BN-N1-TEST-AA', 'duplicate_hint': 'none'})

    response = client.post(
        '/api/v1/public/geotag/preview',
        json={'latitude': 3.75, 'longitude': 8.77, 'province_code': 'BN'},
        cookies={main.SESSION_COOKIE_NAME: 'cookie-token'},
    )

    assert response.status_code == 200






def test_init_db_keeps_official_municipality_routing_active() -> None:
    source = Path('app/db.py').read_text()
    assert "WHERE type = 'official-municipality'" in source
    assert "AND readiness = 'official-routing'" in source
    assert 'SET is_archived = FALSE' in source
    assert "AND NOT (type = 'official-municipality' AND readiness = 'official-routing')" in source

def test_official_admin_routing_seed_contains_table_backed_units() -> None:
    from app.data import ADMIN_UNITS, TERRITORIES

    districts = [unit for unit in ADMIN_UNITS if unit['level'] == 'district']
    municipalities = [unit for unit in ADMIN_UNITS if unit['level'] == 'municipality']
    official_territories = [territory for territory in TERRITORIES if territory['type'] == 'official-municipality']

    assert len(districts) == 20
    assert len(municipalities) == 38
    assert len(official_territories) == 38
    assert {unit['name_es'] for unit in municipalities} >= {'Malabo', 'Bata', 'Mongomo', 'Ciudad de la Paz', 'San Antonio de Palé'}
    assert next(territory for territory in TERRITORIES if territory['name'] == 'Rebola' and territory['province_code'] == 'BN')['readiness'] == 'official-routing'

def test_provinces_endpoint_returns_database_rows(monkeypatch) -> None:
    expected = [
        {'id': 'admin-unit-annobon', 'code': 'AN', 'name': 'Annobón'},
        {'id': 'admin-unit-bioko-norte', 'code': 'BN', 'name': 'Bioko Norte'},
        {'id': 'admin-unit-bioko-sur', 'code': 'BS', 'name': 'Bioko Sur'},
        {'id': 'admin-unit-centro-sur', 'code': 'CS', 'name': 'Centro Sur'},
        {'id': 'admin-unit-djibloho', 'code': 'DJ', 'name': 'Djibloho'},
        {'id': 'admin-unit-kie-ntem', 'code': 'KN', 'name': 'Kié-Ntem'},
        {'id': 'admin-unit-litoral', 'code': 'LI', 'name': 'Litoral'},
        {'id': 'admin-unit-wele-nzas', 'code': 'WN', 'name': 'Wele-Nzas'},
    ]
    monkeypatch.setattr(main, 'list_provinces_db', lambda: expected)
    response = client.get('/api/v1/territories/provinces')
    assert response.status_code == 200
    assert response.json()['items'] == expected


def test_admin_units_endpoint_supports_level_filter(monkeypatch) -> None:
    expected = [
        {'id': 'admin-unit-litoral', 'level': 'province', 'code': 'LI', 'parent_id': None, 'province_code': 'LI', 'name_es': 'Litoral', 'name_en': 'Litoral', 'status': 'active', 'sort_order': 70}
    ]
    monkeypatch.setattr(main, 'list_admin_units_db', lambda level=None, parent_id=None, province_code=None: expected if level == 'province' and province_code == 'LI' else [])
    response = client.get('/api/v1/admin-units', params={'level': 'province', 'province_code': 'LI'})
    assert response.status_code == 200
    assert response.json()['items'] == expected


def test_territories_endpoint_requires_auth_for_full_registry(monkeypatch) -> None:
    response = client.get('/api/v1/territories')
    assert response.status_code == 401


def test_territories_endpoint_returns_database_rows_for_authorized_viewer(monkeypatch) -> None:
    expected = [{'id': 'territory-mongomo-core', 'name': 'Mongomo Core', 'province_code': 'WN', 'province': 'Wele-Nzas', 'admin_unit_id': 'admin-unit-wele-nzas', 'admin_unit_code': 'WN', 'admin_unit_name': 'Wele-Nzas', 'admin_unit_level': 'province', 'type': 'district-core', 'readiness': 'enumeration-ready', 'is_archived': False}]
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'fetch_territories_page', lambda **kwargs: {'items': expected, 'pagination': {'page': kwargs.get('page', 1), 'per_page': kwargs.get('per_page', 100), 'total_items': len(expected), 'total_pages': 1, 'has_next': False, 'has_previous': False}})
    response = client.get('/api/v1/territories', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['items'] == expected


def test_public_territory_options_returns_minimal_public_fields(monkeypatch) -> None:
    expected = [{'id': 'territory-mongomo-core', 'name': 'Mongomo Core', 'province_code': 'WN', 'province': 'Wele-Nzas', 'admin_unit_id': 'admin-unit-wele-nzas', 'admin_unit_code': 'WN', 'admin_unit_name': 'Wele-Nzas', 'admin_unit_level': 'province', 'type': 'district-core', 'readiness': 'enumeration-ready', 'is_archived': False}]
    monkeypatch.setattr(main, 'fetch_territories', lambda **kwargs: expected)
    response = client.get('/api/v1/public/territory-options')
    assert response.status_code == 200
    assert response.json()['items'] == [{'id': 'territory-mongomo-core', 'name': 'Mongomo Core', 'province': 'Wele-Nzas', 'province_code': 'WN', 'readiness': 'enumeration-ready'}]
    assert 'admin_unit_id' not in response.text


def test_create_territory_requires_editor_role(monkeypatch) -> None:
    payload = {'name': 'Mongomo Core', 'province_code': 'WN', 'admin_unit_id': 'admin-unit-wele-nzas', 'type': 'district-core', 'readiness': 'enumeration-ready'}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    response = client.post('/api/v1/territories', json=payload, headers=auth_header())
    assert response.status_code == 403


def test_create_territory_accepts_admin_unit_id(monkeypatch) -> None:
    payload = {'name': 'Mongomo Core', 'province_code': 'WN', 'admin_unit_id': 'admin-unit-wele-nzas', 'type': 'district-core', 'readiness': 'enumeration-ready'}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(
        main,
        'create_territory',
        lambda payload, actor=None: {
            'id': 'territory-mongomo-core',
            'name': payload['name'],
            'province_code': payload['province_code'],
            'province': 'Wele-Nzas',
            'admin_unit_id': payload['admin_unit_id'],
            'admin_unit_code': 'WN',
            'admin_unit_name': 'Wele-Nzas',
            'admin_unit_level': 'province',
            'type': payload['type'],
            'readiness': payload['readiness'],
            'is_archived': False,
        },
    )
    response = client.post('/api/v1/territories', json=payload, headers=auth_header())
    assert response.status_code == 201
    assert response.json()['admin_unit_id'] == 'admin-unit-wele-nzas'


def test_road_detail_requires_auth(monkeypatch) -> None:
    response = client.get('/api/v1/roads/road-a')
    assert response.status_code == 401


def test_road_detail_returns_record_for_authorized_viewer(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'get_road', lambda road_id: {'id': road_id, 'name': 'Avenida', 'territory_id': 'territory-bata', 'territory_name': 'Bata', 'status': 'verified', 'length_km': '2.1', 'is_archived': False})
    response = client.get('/api/v1/roads/road-a', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['name'] == 'Avenida'


def test_update_road_requires_editor(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    response = client.patch('/api/v1/roads/road-a', json={'name': 'Avenida', 'territory_id': 'territory-bata', 'status': 'verified', 'length_km': '2.1'}, headers=auth_header())
    assert response.status_code == 403


def test_archive_address_requires_admin(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    response = client.delete('/api/v1/addresses/addr-a', headers=auth_header())
    assert response.status_code == 403


def test_field_assignments_requires_auth(monkeypatch) -> None:
    response = client.get('/api/v1/field/assignments')
    assert response.status_code == 401


def test_field_assignments_returns_items_for_authorized_viewer(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'list_field_assignments', lambda: [{'assignment_id': 'field-001', 'territory_id': 'territory-bata', 'territory': 'Bata', 'task': 'Task', 'team': 'Team', 'priority': 'critical'}])
    response = client.get('/api/v1/field/assignments', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['items'][0]['priority'] == 'critical'


def test_create_field_submission_requires_auth(monkeypatch) -> None:
    response = client.post('/api/v1/field/submissions', json={'assignment_id': None, 'territory_id': 'territory-bata', 'submission_type': 'road', 'candidate_name': 'New Road', 'candidate_status': 'submitted', 'notes': 'n', 'submitted_by': 'Team'})
    assert response.status_code == 401


def test_create_field_submission_persists(monkeypatch) -> None:
    payload = {'assignment_id': 'field-001', 'territory_id': 'territory-bata', 'submission_type': 'road', 'candidate_name': 'New Road', 'candidate_status': 'submitted', 'notes': 'n', 'submitted_by': 'Team'}
    expected = {'id': 'submission-new-road', **payload, 'review_status': 'submitted', 'reviewer_note': '', 'registry_entity_id': None, 'territory_name': 'Bata'}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'create_field_submission', lambda payload, actor=None: expected)
    response = client.post('/api/v1/field/submissions', json=payload, headers=auth_header())
    assert response.status_code == 201
    assert response.json()['id'] == 'submission-new-road'


def test_create_field_submission_invalid_assignment_returns_404(monkeypatch) -> None:
    payload = {'assignment_id': 'missing-assignment', 'territory_id': 'territory-bata', 'submission_type': 'road', 'candidate_name': 'New Road', 'candidate_status': 'submitted', 'notes': 'n', 'submitted_by': 'Team'}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'create_field_submission', lambda payload, actor=None: (_ for _ in ()).throw(main.SubmissionNotFoundError('assignment not found')))
    response = client.post('/api/v1/field/submissions', json=payload, headers=auth_header())
    assert response.status_code == 404
    assert response.json()['detail'] == 'assignment not found'


def test_approve_submission_returns_registry_link(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'approve_submission', lambda submission_id, actor=None: {'id': submission_id, 'review_status': 'approved', 'registry_entity_id': 'road-new-road'})
    response = client.post('/api/v1/field/submissions/sub-1/approve', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['registry_entity_id'] == 'road-new-road'


def test_reject_submission_returns_review_state(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'update_submission_review_status', lambda submission_id, review_status, reviewer_note, actor=None: {'id': submission_id, 'review_status': review_status, 'reviewer_note': reviewer_note})
    response = client.post('/api/v1/field/submissions/sub-1/reject', json={'reviewer_note': 'duplicate evidence'}, headers=auth_header())
    assert response.status_code == 200
    assert response.json()['review_status'] == 'rejected'


def test_verification_lookup_returns_result(monkeypatch) -> None:
    monkeypatch.setattr(main, 'verify_address', lambda query: {'query': query, 'match_status': 'verified', 'public_code': 'EG-LI-BATA-123ABC', 'address_label': 'Bata', 'jurisdiction': 'Bata · Litoral', 'verification_status': 'official', 'publication_state': 'published', 'verification_note': 'Published registry record found.'})
    response = client.get('/api/v1/verification/lookup', params={'query': 'Bata'})
    assert response.status_code == 200
    assert response.json()['match_status'] == 'verified'
    assert response.json()['public_code'] == 'EG-LI-BATA-123ABC'


def test_public_verification_alias_returns_result(monkeypatch) -> None:
    monkeypatch.setattr(main, 'verify_address', lambda query: {'query': query, 'match_status': 'verified', 'public_code': 'EG-LI-BATA-123ABC', 'address_label': 'Bata', 'jurisdiction': 'Bata · Litoral', 'verification_status': 'official', 'publication_state': 'published', 'verification_note': 'Published registry record found.'})
    response = client.get('/api/v1/public/verification/EG-LI-BATA-123ABC')
    assert response.status_code == 200
    assert response.json()['public_code'] == 'EG-LI-BATA-123ABC'


def test_public_issuance_alias_returns_extract_metadata(monkeypatch) -> None:
    monkeypatch.setattr(main, 'verify_address', lambda query: {'query': query, 'match_status': 'verified', 'public_code': 'EG-LI-BATA-123ABC', 'address_label': 'Bata', 'jurisdiction': 'Bata · Litoral', 'verification_status': 'official', 'publication_state': 'published', 'verification_note': 'Published registry record found.'})
    response = client.get('/api/v1/public/issuance/EG-LI-BATA-123ABC')
    assert response.status_code == 200
    assert response.json()['extract_status'] == 'ready'
    assert response.json()['document_reference'] == 'EXTRACT-EG-LI-BATA-123ABC'


def test_verification_lookup_handles_not_found(monkeypatch) -> None:
    monkeypatch.setattr(main, 'verify_address', lambda query: None)
    response = client.get('/api/v1/verification/lookup', params={'query': 'missing'})
    assert response.status_code == 200
    assert response.json()['match_status'] == 'not-found'
    assert response.json()['verification_status'] == 'not-found'


def test_public_correction_create_returns_created_record(monkeypatch) -> None:
    payload = {
        'query': 'EG-LI-BATA-123ABC',
        'public_code': 'EG-LI-BATA-123ABC',
        'correction_type': 'location-fix',
        'reason': 'pin-drift',
        'note': 'marker is on the wrong side of the property',
        'reporter_name': 'Citizen One',
        'reporter_contact': '+240****0000',
    }
    monkeypatch.setattr(
        main,
        'create_address_correction',
        lambda body, actor=None: {
            'id': 'correction-1234abcd',
            'status': 'submitted',
            **body,
        },
    )
    response = client.post('/api/v1/public/corrections', json=payload)
    assert response.status_code == 201
    assert response.json()['status'] == 'submitted'
    assert response.json()['public_code'] == 'EG-LI-BATA-123ABC'


def test_public_verification_rate_limit_returns_429(monkeypatch) -> None:
    monkeypatch.setattr(main, 'verify_address', lambda query: {'query': query, 'match_status': 'verified', 'public_code': 'EG-LI-BATA-123ABC', 'address_label': 'Bata', 'jurisdiction': 'Bata · Litoral', 'verification_status': 'official', 'publication_state': 'published', 'verification_note': 'Published registry record found.'})
    monkeypatch.setattr(main, 'PUBLIC_RATE_LIMIT_MAX_REQUESTS', 1)
    monkeypatch.setattr(main, 'PUBLIC_RATE_LIMIT_WINDOW_SECONDS', 60)
    main.PUBLIC_RATE_LIMIT_BUCKETS.clear()
    first = client.get('/api/v1/public/verification/EG-LI-BATA-123ABC')
    second = client.get('/api/v1/public/verification/EG-LI-BATA-123ABC')
    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()['detail'] == 'rate limit exceeded'
    main.PUBLIC_RATE_LIMIT_BUCKETS.clear()


def test_address_corrections_queue_requires_editor_role(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    response = client.get('/api/v1/address-corrections', headers=auth_header())
    assert response.status_code == 403


def test_address_corrections_queue_returns_items(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(
        main,
        'list_address_corrections',
        lambda status=None: [
            {
                'id': 'correction-queue-1',
                'public_code': 'EG-LI-BATA-123ABC',
                'query': 'EG-LI-BATA-123ABC',
                'correction_type': 'record-update',
                'reason': 'household name typo',
                'note': 'front gate marker is correct',
                'status': status or 'submitted',
                'reviewer_note': '',
            }
        ],
    )
    response = client.get('/api/v1/address-corrections', params={'status': 'submitted'}, headers=auth_header())
    assert response.status_code == 200
    assert response.json()['items'][0]['status'] == 'submitted'


def test_resolve_address_correction_returns_updated_state(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(
        main,
        'update_address_correction_status',
        lambda correction_id, next_status, reviewer_note, actor=None: {
            'id': correction_id,
            'status': next_status,
            'reviewer_note': reviewer_note,
        },
    )
    response = client.post(
        '/api/v1/address-corrections/correction-queue-1/resolve',
        json={'reviewer_note': 'registry record corrected and republished'},
        headers=auth_header(),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'resolved'
    assert response.json()['reviewer_note'] == 'registry record corrected and republished'


def test_import_jobs_requires_auth() -> None:
    response = client.get('/api/v1/imports/jobs')
    assert response.status_code == 401


def test_create_import_job_returns_created_job(monkeypatch) -> None:
    payload = {'name': 'Legacy import', 'source_name': 'legacy.csv', 'rows': [{'submission_type': 'road', 'territory_id': 'territory-bata', 'candidate_name': 'Road', 'candidate_status': 'submitted', 'notes': 'ok'}]}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'create_import_job', lambda payload, actor=None: {'id': 'import-legacy', 'name': payload['name'], 'status': 'draft', 'source_name': payload['source_name'], 'imported_count': 0, 'total_rows': 1, 'valid_rows': 1})
    response = client.post('/api/v1/imports/jobs', json=payload, headers=auth_header())
    assert response.status_code == 201
    assert response.json()['id'] == 'import-legacy'


def test_commit_import_job_returns_committed_job(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'commit_import_job', lambda job_id, actor=None: {'id': job_id, 'status': 'committed', 'imported_count': 2})
    response = client.post('/api/v1/imports/jobs/import-1/commit', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['status'] == 'committed'


def test_commit_import_job_rejects_already_committed_job(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'commit_import_job', lambda job_id, actor=None: (_ for _ in ()).throw(main.InvalidSubmissionActionError('import job already committed')))
    response = client.post('/api/v1/imports/jobs/import-1/commit', headers=auth_header())
    assert response.status_code == 409
    assert response.json()['detail'] == 'import job already committed'


def test_create_import_job_duplicate_name_returns_409(monkeypatch) -> None:
    payload = {'name': 'Legacy import', 'source_name': 'legacy.csv', 'rows': [{'submission_type': 'road', 'territory_id': 'territory-bata', 'candidate_name': 'Road', 'candidate_status': 'submitted', 'notes': 'ok'}]}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'create_import_job', lambda payload, actor=None: (_ for _ in ()).throw(main.DuplicateImportJobError('duplicate import job')))
    response = client.post('/api/v1/imports/jobs', json=payload, headers=auth_header())
    assert response.status_code == 409
    assert response.json()['detail'] == 'duplicate import job'


def test_publication_pack_create_returns_pack(monkeypatch) -> None:
    payload = {'name': 'Published Bata Pack', 'audience': 'Cabinet', 'status': 'draft', 'address_ids': ['addr-1']}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'create_publication_pack', lambda payload, actor=None: {'id': 'publication-pack', 'name': payload['name'], 'status': payload['status'], 'audience': payload['audience'], 'address_count': 1})
    response = client.post('/api/v1/publication/packs', json=payload, headers=auth_header())
    assert response.status_code == 201
    assert response.json()['address_count'] == 1


def test_editor_cannot_create_published_publication_pack(monkeypatch) -> None:
    payload = {'name': 'Published Bata Pack', 'audience': 'Cabinet', 'status': 'published', 'address_ids': ['addr-1']}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    response = client.post('/api/v1/publication/packs', json=payload, headers=auth_header())
    assert response.status_code == 403
    assert response.json()['detail'] == 'admin required to create a published pack'


def test_publication_pack_duplicate_name_returns_409(monkeypatch) -> None:
    payload = {'name': 'Published Bata Pack', 'audience': 'Cabinet', 'status': 'draft', 'address_ids': ['addr-1']}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'create_publication_pack', lambda payload, actor=None: (_ for _ in ()).throw(main.DuplicatePublicationPackError('duplicate publication pack')))
    response = client.post('/api/v1/publication/packs', json=payload, headers=auth_header())
    assert response.status_code == 409
    assert response.json()['detail'] == 'duplicate publication pack'


def test_publish_publication_pack_requires_admin(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    response = client.post('/api/v1/publication/packs/pack-1/publish', headers=auth_header())
    assert response.status_code == 403


def test_reporting_summary_returns_totals(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(
        main,
        'reporting_summary',
        lambda: {
            'totals': {
                'territories': 3,
                'submissions': 2,
                'review_queue': 1,
                'published_addresses': 1,
                'import_jobs': 1,
                'public_corrections': 4,
                'correction_queue': 2,
                'citizen_geotags': 5,
                'geotag_queue': 3,
            },
            'territories_by_province': [],
            'review_breakdown': [],
            'publication_breakdown': [],
            'correction_breakdown': [],
            'geotag_breakdown': [],
        },
    )
    response = client.get('/api/v1/reporting/summary', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['totals']['review_queue'] == 1
    assert response.json()['totals']['correction_queue'] == 2
    assert response.json()['totals']['citizen_geotags'] == 5


def test_pilot_readiness_summary_requires_viewer_role(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: {'id': 'public-user', 'username': 'public', 'full_name': 'Public User', 'role': 'public'})
    response = client.get('/api/v1/pilot-readiness/summary', headers=auth_header())
    assert response.status_code == 403


def test_pilot_readiness_summary_returns_gates(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(
        main,
        'pilot_readiness_summary',
        lambda: {
            'readiness_status': 'pilot-ready',
            'passed_gates': 6,
            'total_gates': 6,
            'gates': [{'name': 'Citizen capture intake', 'status': 'passed', 'evidence': '1 record', 'next_step': 'continue'}],
            'totals': {'citizen_geotags': 1},
            'breakdowns': {},
            'recent_audit_events': [],
            'boundaries': ['Government approval still required.'],
        },
    )
    response = client.get('/api/v1/pilot-readiness/summary', headers=auth_header())
    assert response.status_code == 200
    payload = response.json()
    assert payload['readiness_status'] == 'pilot-ready'
    assert payload['gates'][0]['name'] == 'Citizen capture intake'
    assert payload['boundaries'][0] == 'Government approval still required.'


def test_cors_preflight_allows_admin_origin() -> None:
    response = client.options('/api/v1/territories', headers={'Origin': 'http://localhost:3100', 'Access-Control-Request-Method': 'POST'})
    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == 'http://localhost:3100'


def test_public_geotag_preview_returns_grid_code(monkeypatch) -> None:
    monkeypatch.setattr(main, 'preview_citizen_geotag', lambda latitude, longitude, territory_id=None, province_code=None: {
        'grid_code': 'EG-LI-GABCD1234',
        'territory_id': territory_id,
        'territory_name': 'Bata Urban Core',
        'latitude': latitude,
        'longitude': longitude,
        'duplicate_hints': [],
        'signage_label': 'EG-LI-GABCD1234 · provisional citizen point',
    })
    response = client.post('/api/v1/public/geotag/preview', json={'latitude': 1.865, 'longitude': 9.77, 'territory_id': 'territory-bata-urban-core'})
    assert response.status_code == 200
    assert response.json()['grid_code'] == 'EG-LI-GABCD1234'


def test_public_geotag_submission_creates_citizen_record(monkeypatch) -> None:
    payload = {
        'territory_id': 'territory-bata-urban-core',
        'address_label': 'House near civic cluster',
        'citizen_name': 'Citizen Tester',
        'citizen_contact': '+240555000000',
        'landmark': 'Blue gate near pharmacy',
        'latitude': 1.865,
        'longitude': 9.77,
        'accuracy_meters': 18,
        'capture_method': 'browser-gps',
    }
    monkeypatch.setattr(main, 'create_citizen_geotag_submission', lambda body, actor=None: {'id': 'citizen-geotag-1', 'status': 'submitted', **body, 'grid_code': 'EG-LI-GABCD1234', 'duplicate_hints': []})
    response = client.post('/api/v1/public/geotag-submissions', json=payload)
    assert response.status_code == 201
    assert response.json()['grid_code'] == 'EG-LI-GABCD1234'
    assert response.json()['status'] == 'submitted'


def test_geotag_submissions_require_operator(monkeypatch) -> None:
    response = client.get('/api/v1/geotag-submissions')
    assert response.status_code == 401


def test_geotag_submission_can_be_marked_registry_ready(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'update_citizen_geotag_status', lambda submission_id, next_status, reviewer_note, actor=None: {
        'id': submission_id,
        'status': next_status,
        'reviewer_note': reviewer_note,
        'grid_code': 'EG-LI-GABCD1234',
        'address_label': 'Registry ready test address',
        'territory_id': 'territory-bata-core',
        'territory_name': 'Bata Core',
        'latitude': 1.85,
        'longitude': 9.76,
        'accuracy_meters': 8,
        'capture_method': 'manual-map-pin',
        'landmark': 'Test gate',
        'field_submission_id': 'submission-1',
        'signage_batch': None,
    })
    monkeypatch.setattr(main, 'upsert_address_record_from_geotag', lambda geotag, actor=None: {'address_code': geotag['grid_code']})
    response = client.post('/api/v1/geotag-submissions/citizen-geotag-1/registry-ready', json={'reviewer_note': 'verified for official case file'}, headers=auth_header())
    assert response.status_code == 200
    assert response.json()['status'] == 'registry-ready'
    assert response.json()['signage_batch'] is None


def test_signage_export_requires_operator_and_returns_rows(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'signage_export', lambda status='published': {'status': status, 'count': 1, 'items': [{'grid_code': 'EG-LI-GABCD1234', 'signage_text': 'EG-LI-GABCD1234'}]})
    response = client.get('/api/v1/signage/export', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['count'] == 1


def test_national_address_code_generation_and_validation() -> None:
    from app.address_codes import decode_national_address_code, generate_national_address_code, validate_national_address_code

    code = generate_national_address_code(1.865222, 9.770333, 'LI')
    assert code.startswith('EG-LI-N1-')
    assert len(code.split('-')) == 5
    decoded = decode_national_address_code(code)
    assert decoded.is_valid is True
    assert decoded.province_code == 'LI'
    assert decoded.cell_size_meters == 5.0
    assert abs(decoded.latitude - 1.865222) < 0.0001
    assert abs(decoded.longitude - 9.770333) < 0.0001

    invalid = validate_national_address_code(code[:-1] + ('0' if code[-1] != '0' else '1'))
    assert invalid['is_valid'] is False


def test_public_address_code_lookup_validates_checksum(monkeypatch) -> None:
    response = client.get('/api/v1/public/address-code/EG-LI-N1-0000000000-00')
    assert response.status_code == 200
    assert response.json()['is_valid'] is False


def test_geotag_submission_server_recomputes_national_code(monkeypatch) -> None:
    from app.address_codes import generate_national_address_code

    payload = {
        'territory_id': 'territory-bata-urban-core',
        'address_label': 'Server recompute test location',
        'citizen_name': 'Citizen Tester',
        'citizen_contact': '+240****0000',
        'landmark': 'Server-side code test',
        'latitude': 1.865222,
        'longitude': 9.770333,
        'accuracy_meters': 18,
        'capture_method': 'browser-gps',
        'grid_code': 'EG-LI-N1-0000000000-00',
    }
    expected = generate_national_address_code(payload['latitude'], payload['longitude'], 'LI')
    monkeypatch.setattr(main, 'create_citizen_geotag_submission', lambda body, actor=None: {'id': 'citizen-geotag-2', 'status': 'submitted', **body, 'grid_code': expected, 'address_code': {'code': expected, 'is_valid': True}, 'duplicate_hints': []})
    response = client.post('/api/v1/public/geotag-submissions', json=payload)
    assert response.status_code == 201
    assert response.json()['grid_code'] == expected
    assert response.json()['grid_code'] != payload['grid_code']


def test_public_geotag_preview_uses_selected_province_without_territory(monkeypatch) -> None:
    monkeypatch.setattr(main, 'preview_citizen_geotag', lambda latitude, longitude, territory_id=None, province_code=None: {
        'grid_code': f'EG-{province_code}-N1-TEST000001-AA',
        'address_code': {'province_code': province_code, 'is_valid': True},
        'territory_id': territory_id,
        'territory_name': None,
        'latitude': latitude,
        'longitude': longitude,
        'duplicate_hints': [],
        'signage_label': 'province-only preview',
    })
    response = client.post('/api/v1/public/geotag/preview', json={'latitude': 3.7523, 'longitude': 8.7741, 'province_code': 'BN'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['grid_code'].startswith('EG-BN-N1-')
    assert payload['address_code']['province_code'] == 'BN'


def test_public_road_suggestion_returns_review_required_map_candidate(monkeypatch) -> None:
    monkeypatch.setattr(main, 'suggest_nearest_road_name', lambda latitude, longitude: {
        'suggested_road_name': 'Avenida de la Independencia',
        'source': 'openstreetmap-nominatim',
        'source_attribution': '© OpenStreetMap contributors',
        'distance_meters': None,
        'confidence': 'medium',
        'requires_review': True,
        'status': 'suggested',
    })
    response = client.post('/api/v1/public/geotag/road-suggestion', json={'latitude': 3.7523, 'longitude': 8.7741})
    assert response.status_code == 200
    payload = response.json()
    assert payload['suggested_road_name'] == 'Avenida de la Independencia'
    assert payload['requires_review'] is True
    assert payload['source_attribution'] == '© OpenStreetMap contributors'


def test_map_suggestion_can_include_local_area_without_officializing_it() -> None:
    address = {'suburb': 'Santa Isabel', 'city': 'Malabo'}
    assert main._extract_local_area(address) == 'Santa Isabel'

    fallback_address = {'city': 'Malabo'}
    assert main._extract_local_area(fallback_address) == 'Malabo'


def test_public_road_suggestion_fails_softly_when_no_name_found(monkeypatch) -> None:
    monkeypatch.setattr(main, 'suggest_nearest_road_name', lambda latitude, longitude: {
        'suggested_road_name': None,
        'source': 'openstreetmap-nominatim',
        'source_attribution': '© OpenStreetMap contributors',
        'distance_meters': None,
        'confidence': 'none',
        'requires_review': True,
        'status': 'unavailable',
    })
    response = client.post('/api/v1/public/geotag/road-suggestion', json={'latitude': 3.7523, 'longitude': 8.7741})
    assert response.status_code == 200
    payload = response.json()
    assert payload['suggested_road_name'] is None
    assert payload['status'] == 'unavailable'
    assert payload['requires_review'] is True


def test_public_geotag_submission_accepts_dip_last4_only(monkeypatch) -> None:
    captured = {}

    def fake_create(body, actor=None):
        captured.update(body)
        return {
            'id': 'citizen-geotag-identity',
            'status': 'submitted',
            **body,
            'grid_code': 'EG-BN-N1-TEST000001-AA',
            'address_code': {'code': 'EG-BN-N1-TEST000001-AA', 'is_valid': True},
            'duplicate_hints': [],
        }

    monkeypatch.setattr(main, 'create_citizen_geotag_submission', fake_create)
    response = client.post('/api/v1/public/geotag-submissions', json={
        'territory_id': None,
        'province_code': 'BN',
        'address_label': 'Identity pilot test house',
        'citizen_name': 'Citizen Tester',
        'citizen_contact': '+240555000000',
        'dip_last4': '1234',
        'landmark': 'Blue gate',
        'latitude': 3.7523,
        'longitude': 8.7741,
        'capture_method': 'manual-map-pin',
    })
    assert response.status_code == 201
    assert captured['dip_last4'] == '1234'
    assert 'dip_full' not in captured


def test_public_geotag_submission_rejects_invalid_dip_last4() -> None:
    response = client.post('/api/v1/public/geotag-submissions', json={
        'territory_id': None,
        'province_code': 'BN',
        'address_label': 'Identity invalid DIP test',
        'dip_last4': '12AB',
        'landmark': 'Blue gate',
        'latitude': 3.7523,
        'longitude': 8.7741,
        'capture_method': 'manual-map-pin',
    })
    assert response.status_code == 422


def test_operator_can_verify_geotag_identity(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    captured = {}

    def fake_verify(submission_id, dip_full, identity_document_verified, reviewer_note, actor=None):
        captured.update({
            'submission_id': submission_id,
            'dip_full': dip_full,
            'identity_document_verified': identity_document_verified,
            'reviewer_note': reviewer_note,
            'actor': actor,
        })
        return {
            'id': submission_id,
            'dip_last4': dip_full[-4:],
            'dip_masked': f'****{dip_full[-4:]}',
            'identity_verification_status': 'verified',
            'identity_document_verified': True,
        }

    monkeypatch.setattr(main, 'verify_geotag_identity', fake_verify)
    response = client.post('/api/v1/geotag-submissions/geo-identity-1/identity', headers=auth_header(), json={
        'dip_full': '1234567890123',
        'identity_document_verified': True,
        'reviewer_note': 'D.I.P. checked by operator.',
    })
    assert response.status_code == 200
    payload = response.json()
    assert captured['actor']['role'] == 'editor'
    assert captured['dip_full'] == '1234567890123'
    assert payload['dip_masked'] == '****0123'
    assert 'dip_full' not in payload


def test_geotag_public_lookup_does_not_expose_identity_fields(monkeypatch) -> None:
    monkeypatch.setattr(main, 'public_address_code_record_lookup', lambda code: {
        'code': code,
        'is_valid': True,
        'publication_status': 'published',
        'record': {
            'id': 'geo-public',
            'address_label': 'Approved address',
            'grid_code': code,
            'status': 'published',
            'dip_last4': '1234',
            'dip_masked': '****1234',
            'identity_verification_status': 'verified',
        },
    })
    response = client.get('/api/v1/public/address-code/EG-BN-N1-TEST000001-AA/record')
    assert response.status_code == 200
    text = response.text
    assert 'dip_last4' not in text
    assert 'dip_masked' not in text
    assert 'identity_verification_status' not in text


def test_public_geotag_submission_stores_road_suggestion_for_review(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def fake_create(body, actor=None):
        captured.update(body)
        return {
            'id': 'citizen-geotag-road-suggestion',
            'status': 'submitted',
            **body,
            'grid_code': 'EG-BN-N1-TEST000001-AA',
            'address_code': {'code': 'EG-BN-N1-TEST000001-AA', 'is_valid': True},
            'duplicate_hints': [],
        }

    monkeypatch.setattr(main, 'create_citizen_geotag_submission', fake_create)
    response = client.post('/api/v1/public/geotag-submissions', json={
        'territory_id': None,
        'province_code': 'BN',
        'address_label': 'House near airport road',
        'landmark': 'Blue gate',
        'latitude': 3.7523,
        'longitude': 8.7741,
        'capture_method': 'manual-map-pin',
        'suggested_road_name': 'Carretera del Aeropuerto',
        'suggested_local_area': 'Ela Nguema',
        'suggested_place_name': 'Aeropuerto de Malabo',
        'map_display_name': 'Ela Nguema, Malabo, Bioko Norte, Equatorial Guinea',
        'road_suggestion_source': 'openstreetmap-nominatim',
        'road_suggestion_attribution': '© OpenStreetMap contributors',
    })
    assert response.status_code == 201
    assert captured['suggested_road_name'] == 'Carretera del Aeropuerto'
    assert captured['suggested_local_area'] == 'Ela Nguema'
    assert captured['suggested_place_name'] == 'Aeropuerto de Malabo'
    assert str(captured['map_display_name']).startswith('Ela Nguema')
    assert captured['road_suggestion_source'] == 'openstreetmap-nominatim'
    payload = response.json()
    assert payload['automation']['triage_bucket'] in {'field-verification', 'operator-road-review'}
    assert payload['automation']['citizen_tracking']['tracking_code'] == 'citizen-geotag-road-suggestion'
    assert payload['automation']['integration']['api_record_state'] == 'not-public'


def test_routing_area_auto_assignment_uses_only_exact_local_area_matches() -> None:
    rows = [
        {'id': 'territory-malabo-urban-core', 'name': 'Malabo Urban Core', 'province_code': 'BN', 'type': 'district-core'},
        {'id': 'territory-malabo-ela-nguema', 'name': 'Ela Nguema', 'province_code': 'BN', 'type': 'map-referenced-local-area'},
        {'id': 'territory-bata-ela-nguema', 'name': 'Ela Nguema', 'province_code': 'LI', 'type': 'map-referenced-local-area'},
    ]
    assignment = db.resolve_geotag_routing_area(rows, suggested_local_area='ela nguema', province_code='BN')
    assert assignment == {
        'territory_id': 'territory-malabo-ela-nguema',
        'territory_name': 'Ela Nguema',
        'routing_assignment_source': 'map-local-area-exact-match',
        'routing_assignment_confidence': 'high',
    }
    assert db.resolve_geotag_routing_area(rows, suggested_local_area='Malabo', province_code='BN') is None
    assert db.resolve_geotag_routing_area(rows, suggested_local_area='Ela Nguema', province_code='WN') is None


def test_public_geotag_submission_reports_auto_assigned_routing_area(monkeypatch) -> None:
    def fake_create(body, actor=None):
        return {
            'id': 'citizen-geotag-routing-auto',
            **body,
            'territory_id': 'territory-malabo-ela-nguema',
            'territory_name': 'Ela Nguema',
            'status': 'submitted',
            'grid_code': 'EG-BN-N1-TEST000004-AA',
            'address_code': {'code': 'EG-BN-N1-TEST000004-AA', 'is_valid': True},
            'duplicate_hints': [],
            'routing_assignment': {
                'territory_id': 'territory-malabo-ela-nguema',
                'territory_name': 'Ela Nguema',
                'routing_assignment_source': 'map-local-area-exact-match',
                'routing_assignment_confidence': 'high',
            },
        }

    monkeypatch.setattr(main, 'create_citizen_geotag_submission', fake_create)
    response = client.post('/api/v1/public/geotag-submissions', json={
        'territory_id': None,
        'province_code': 'BN',
        'address_label': 'House near Ela Nguema',
        'latitude': 3.7523,
        'longitude': 8.7741,
        'capture_method': 'manual-map-pin',
        'suggested_local_area': 'Ela Nguema',
        'road_suggestion_source': 'openstreetmap-nominatim',
    })
    assert response.status_code == 201
    payload = response.json()
    assert payload['territory_id'] == 'territory-malabo-ela-nguema'
    assert payload['territory_name'] == 'Ela Nguema'
    assert payload['routing_assignment']['routing_assignment_source'] == 'map-local-area-exact-match'
    assert payload['automation']['routing']['assigned'] is True
    assert payload['automation']['routing']['territory_name'] == 'Ela Nguema'


def test_public_geotag_tracking_strips_identity_and_returns_next_step(monkeypatch) -> None:
    monkeypatch.setattr(main, 'list_citizen_geotag_submissions', lambda: [{
        'id': 'citizen-geotag-track-1',
        'territory_id': None,
        'territory_name': None,
        'address_label': 'Trackable house near airport',
        'citizen_name': 'Private Citizen',
        'citizen_contact': '+240555000000',
        'dip_last4': '1234',
        'dip_masked': '****1234',
        'landmark': 'Blue gate',
        'latitude': 3.7523,
        'longitude': 8.7741,
        'accuracy_meters': 55,
        'capture_method': 'browser-gps',
        'grid_code': 'EG-BN-N1-TEST000002-AA',
        'status': 'submitted',
        'duplicate_hint': 'none',
        'reviewer_note': '',
        'road_suggestion_status': 'pending-review',
        'field_status': 'assigned',
        'field_submission_id': None,
        'signage_batch': None,
        'created_at': '2026-07-06T12:00:00Z',
        'updated_at': '2026-07-06T12:00:00Z',
    }])
    response = client.get('/api/v1/public/geotag-submissions/citizen-geotag-track-1/tracking')
    assert response.status_code == 200
    body = response.json()
    assert body['id'] == 'citizen-geotag-track-1'
    assert body['process_stage'] == 'Needs field verification'
    assert body['publication_state'] == 'not-public'
    assert 'dip_last4' not in body
    assert 'dip_masked' not in body
    assert 'citizen_contact' not in body


def test_geotag_automation_summary_requires_auth_and_groups_lanes(monkeypatch) -> None:
    now = datetime(2026, 7, 7, 9, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(main, '_now_utc', lambda: now)
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'list_address_corrections', lambda status=None: [
        {
            'id': 'correction-old-1',
            'status': 'submitted',
            'query': 'EG-BN-N1-CORRECT-AA',
            'created_at': (now - timedelta(hours=50)).isoformat(),
            'updated_at': (now - timedelta(hours=50)).isoformat(),
        }
    ])
    monkeypatch.setattr(main, 'list_citizen_geotag_submissions', lambda: [
        {
            'id': 'citizen-geotag-auto-1',
            'territory_id': None,
            'territory_name': None,
            'address_label': 'Weak GPS house',
            'landmark': '',
            'latitude': 3.7523,
            'longitude': 8.7741,
            'accuracy_meters': 80,
            'capture_method': 'browser-gps',
            'grid_code': 'EG-BN-N1-AUTO000001-AA',
            'status': 'submitted',
            'duplicate_hint': 'none',
            'reviewer_note': '',
            'road_suggestion_status': 'not-suggested',
            'field_status': 'assigned',
            'field_submission_id': None,
            'signage_batch': None,
            'created_at': (now - timedelta(hours=73)).isoformat(),
            'updated_at': (now - timedelta(hours=73)).isoformat(),
        },
        {
            'id': 'citizen-geotag-auto-2',
            'territory_id': 'territory-malabo-urban-core',
            'territory_name': 'Malabo Urban Core',
            'address_label': 'Approved location',
            'landmark': 'Gate',
            'latitude': 3.7524,
            'longitude': 8.7742,
            'accuracy_meters': 6,
            'capture_method': 'browser-gps',
            'grid_code': 'EG-BN-N1-AUTO000002-AA',
            'status': 'registry-ready',
            'duplicate_hint': 'none',
            'reviewer_note': '',
            'road_suggestion_status': 'accepted',
            'field_status': 'verified',
            'field_submission_id': 'submission-auto-2',
            'signage_batch': 'signage-auto',
            'created_at': (now - timedelta(days=7)).isoformat(),
            'updated_at': (now - timedelta(days=7)).isoformat(),
        },
    ])
    response = client.get('/api/v1/geotag-submissions/automation/summary', headers=auth_header())
    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 2
    assert body['field_required'] == 1
    assert body['registry_ready'] == 1
    assert body['partner_api_ready'] == 0
    assert {'bucket': 'field-verification', 'count': 1} in body['triage_buckets']
    assert {'bucket': 'registry-ready', 'count': 1} in body['triage_buckets']
    assert body['sla']['items_tracked'] == 2
    assert body['sla']['overdue'] == 2
    assert body['sla']['by_state']['overdue'] == 2
    assert body['sla']['oldest_overdue']['id'] == 'citizen-geotag-auto-1'
    assert body['publication_hold']['registry_ready'] == 1
    assert body['publication_hold']['oldest_days'] == 7
    assert body['publication_hold']['public_release_locked'] is True


def test_address_record_bundle_is_case_file_and_strips_identity() -> None:
    geotag = {
        'id': 'citizen-geotag-case-1',
        'grid_code': 'EG-BN-N1-CASE000001-AA',
        'address_label': 'House near Ela Nguema clinic',
        'citizen_name': 'Private Citizen',
        'citizen_contact': '+240555000000',
        'dip_last4': '1234',
        'dip_masked': '****1234',
        'province_code': 'BN',
        'territory_id': 'territory-malabo-ela-nguema',
        'territory_name': 'Ela Nguema',
        'latitude': 3.7523,
        'longitude': 8.7741,
        'accuracy_meters': 8,
        'capture_method': 'manual-map-pin',
        'landmark': 'Blue gate',
        'status': 'registry-ready',
        'reviewed_road_name': 'Carretera del Aeropuerto',
        'suggested_road_name': 'Airport Road',
        'suggested_local_area': 'Ela Nguema',
        'field_status': 'verified',
        'signage_batch': None,
        'routing_assignment': {'routing_assignment_source': 'map-local-area-exact-match', 'routing_assignment_confidence': 'high'},
    }
    bundle = db.build_address_record_bundle(geotag)
    bundle_text = str(bundle)
    assert bundle['identity']['address_code'] == 'EG-BN-N1-CASE000001-AA'
    assert bundle['location']['latitude'] == 3.7523
    assert bundle['routing']['territory_name'] == 'Ela Nguema'
    assert bundle['evidence']['gps_capture']['accuracy_meters'] == 8
    assert bundle['outputs']['signage_batch'] is None
    assert bundle['outputs']['physical_rollout_status'] == 'awaiting-full-project-approval'
    assert 'Private Citizen' not in bundle_text
    assert '+240555000000' not in bundle_text
    assert '1234' not in bundle_text


def test_mark_geotag_registry_ready_upserts_canonical_address_record(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    updated = {
        'id': 'citizen-geotag-case-2',
        'grid_code': 'EG-BN-N1-CASE000002-AA',
        'status': 'registry-ready',
        'address_label': 'Case file address',
        'territory_id': 'territory-malabo-ela-nguema',
        'territory_name': 'Ela Nguema',
        'latitude': 3.75,
        'longitude': 8.78,
        'accuracy_meters': 8,
        'capture_method': 'manual-map-pin',
        'landmark': 'Clinic gate',
        'signage_batch': None,
    }
    monkeypatch.setattr(main, 'update_citizen_geotag_status', lambda submission_id, status_value, note, actor=None: updated)
    captured: dict[str, Any] = {}

    def fake_upsert(geotag, actor=None):
        captured['geotag'] = geotag
        captured['actor'] = actor
        return {'address_code': geotag['grid_code'], 'record_bundle': {'identity': {'address_code': geotag['grid_code']}}}

    monkeypatch.setattr(main, 'upsert_address_record_from_geotag', fake_upsert)
    response = client.post('/api/v1/geotag-submissions/citizen-geotag-case-2/registry-ready', json={'reviewer_note': 'approved'}, headers=auth_header())
    assert response.status_code == 200
    assert captured['geotag']['grid_code'] == 'EG-BN-N1-CASE000002-AA'
    assert captured['actor']['role'] == 'editor'
    assert response.json()['address_record']['address_code'] == 'EG-BN-N1-CASE000002-AA'


def test_address_record_search_requires_auth_and_returns_case_files(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'search_address_records', lambda **kwargs: [{
        'address_code': 'EG-BN-N1-CASE000003-AA',
        'status': 'registry-ready',
        'address_label': 'Ela Nguema clinic gate',
        'province_code': 'BN',
        'territory_name': 'Ela Nguema',
        'latitude': 3.75,
        'longitude': 8.78,
        'record_bundle': {'identity': {'address_code': 'EG-BN-N1-CASE000003-AA'}},
    }])
    unauthenticated = client.get('/api/v1/address-records/search', params={'q': 'ela nguema'})
    assert unauthenticated.status_code == 401
    response = client.get('/api/v1/address-records/search', params={'q': 'ela nguema'}, headers=auth_header())
    assert response.status_code == 200
    body = response.json()
    assert body['items'][0]['address_code'] == 'EG-BN-N1-CASE000003-AA'
    assert body['items'][0]['record_bundle']['identity']['address_code'] == 'EG-BN-N1-CASE000003-AA'


def test_address_record_case_file_history_requires_auth(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'get_address_record_case_file', lambda address_code: {
        'address_code': address_code,
        'record_bundle': {'identity': {'address_code': address_code}},
        'timeline': [{'event_type': 'address-record-upserted', 'actor_role': 'editor'}],
    })
    response = client.get('/api/v1/address-records/EG-BN-N1-CASE000004-AA', headers=auth_header())
    assert response.status_code == 200
    body = response.json()
    assert body['address_code'] == 'EG-BN-N1-CASE000004-AA'
    assert body['timeline'][0]['event_type'] == 'address-record-upserted'


def test_signage_pack_returns_batch_metadata_and_csv(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'signage_export', lambda status='published': {'items': [
        {
            'grid_code': 'EG-BN-N1-PACK000001-AA',
            'signage_text': 'EG-BN-N1-PACK000001-AA · Ministry Annex',
            'address_label': 'Ministry Annex',
            'territory_name': 'Malabo Urban Core',
            'latitude': 3.75,
            'longitude': 8.78,
            'accuracy_meters': 8,
            'batch': 'signage-pack-test',
            'status': status,
        },
    ]})
    response = client.get('/api/v1/signage/pack', headers=auth_header())
    assert response.status_code == 200
    body = response.json()
    assert body['batch_id'].startswith('signage-pack-')
    assert body['record_count'] == 1
    assert 'EG-BN-N1-PACK000001-AA' in body['csv']
    assert body['operator_note'].startswith('Physical signage packs include published records only')


def test_operator_can_review_road_suggestion(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    captured = {}

    def fake_review(submission_id, action, reviewed_road_name, reviewer_note, actor=None):
        captured.update({'submission_id': submission_id, 'action': action, 'reviewed_road_name': reviewed_road_name, 'reviewer_note': reviewer_note, 'actor': actor})
        return {'id': submission_id, 'road_suggestion_status': action, 'reviewed_road_name': reviewed_road_name}

    monkeypatch.setattr(main, 'review_geotag_road_suggestion', fake_review)
    response = client.post('/api/v1/geotag-submissions/geo-road-1/road-suggestion', headers=auth_header(), json={
        'action': 'accepted',
        'reviewed_road_name': 'Carretera del Aeropuerto',
        'reviewer_note': 'Accepted after operator review.',
    })
    assert response.status_code == 200
    assert captured['submission_id'] == 'geo-road-1'
    assert captured['action'] == 'accepted'
    assert captured['actor']['role'] == 'editor'


def test_public_geotag_submission_uses_selected_province_without_territory(monkeypatch) -> None:
    monkeypatch.setattr(main, 'create_citizen_geotag_submission', lambda body, actor=None: {
        'id': 'citizen-geotag-bn-1',
        'status': 'submitted',
        **body,
        'grid_code': 'EG-BN-N1-TEST000001-AA',
        'address_code': {'province_code': body['province_code'], 'is_valid': True},
        'duplicate_hints': [],
    })
    response = client.post('/api/v1/public/geotag-submissions', json={
        'province_code': 'BN',
        'territory_id': None,
        'address_label': 'Malabo province-only test location',
        'citizen_name': 'Citizen Tester',
        'citizen_contact': '+240****0000',
        'landmark': 'Province-only code generation test',
        'latitude': 3.7523,
        'longitude': 8.7741,
        'accuracy_meters': 14,
        'capture_method': 'manual-map-pin',
    })
    assert response.status_code == 201
    payload = response.json()
    assert payload['grid_code'].startswith('EG-BN-N1-')
    assert payload['address_code']['province_code'] == 'BN'


def test_provinces_endpoint_lists_all_eight_equatorial_guinea_provinces(monkeypatch) -> None:
    monkeypatch.setattr(main, 'list_provinces_db', lambda: [
        {'code': 'AN', 'name': 'Annobón'},
        {'code': 'BN', 'name': 'Bioko Norte'},
        {'code': 'BS', 'name': 'Bioko Sur'},
        {'code': 'CS', 'name': 'Centro Sur'},
        {'code': 'DJ', 'name': 'Djibloho'},
        {'code': 'KN', 'name': 'Kié-Ntem'},
        {'code': 'LI', 'name': 'Litoral'},
        {'code': 'WN', 'name': 'Wele-Nzas'},
    ])
    response = client.get('/api/v1/provinces')
    assert response.status_code == 200
    names = {item['name'] for item in response.json()['items']}
    assert names == {'Annobón', 'Bioko Norte', 'Bioko Sur', 'Centro Sur', 'Djibloho', 'Kié-Ntem', 'Litoral', 'Wele-Nzas'}


def test_geotag_submission_quality_flags_show_accuracy_and_duplicate(monkeypatch) -> None:
    rows = [
        {
            'id': 'geo-a',
            'territory_id': 'territory-malabo-urban-core',
            'territory_name': 'Malabo Urban Core',
            'address_label': 'Vicatana Police Station',
            'citizen_name': None,
            'citizen_contact': None,
            'landmark': '',
            'latitude': 3.7252425,
            'longitude': 8.7760228,
            'accuracy_meters': 32,
            'capture_method': 'browser-gps',
            'grid_code': 'EG-BN-N1-1ZNSA408CX-MH',
            'status': 'submitted',
            'duplicate_hint': 'possible-duplicate',
            'reviewer_note': '',
            'field_submission_id': None,
            'signage_batch': None,
            'created_at': None,
            'updated_at': None,
        },
        {
            'id': 'geo-b',
            'territory_id': 'territory-malabo-urban-core',
            'territory_name': 'Malabo Urban Core',
            'address_label': 'Vicatana Block 4',
            'citizen_name': None,
            'citizen_contact': None,
            'landmark': '',
            'latitude': 3.7252425,
            'longitude': 8.7760228,
            'accuracy_meters': 32,
            'capture_method': 'browser-gps',
            'grid_code': 'EG-BN-N1-1ZNSA408CX-MH',
            'status': 'submitted',
            'duplicate_hint': 'possible-duplicate',
            'reviewer_note': '',
            'field_submission_id': None,
            'signage_batch': None,
            'created_at': None,
            'updated_at': None,
        },
    ]
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'list_citizen_geotag_submissions', lambda status=None, territory_id=None: rows)
    response = client.get('/api/v1/geotag-submissions', headers=auth_header())
    assert response.status_code == 200
    item = response.json()['items'][0]
    assert item['quality_flags']['accuracy_level'] == 'weak-gps'
    assert item['quality_flags']['requires_field_check'] is True
    assert item['quality_flags']['duplicate_code'] is True
    assert item['duplicate_group']['count'] == 2


def test_duplicate_decision_endpoint_records_reason(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    captured = {}

    def fake_decision(submission_id, duplicate_action, reviewer_note, actor=None):
        captured.update({'submission_id': submission_id, 'duplicate_action': duplicate_action, 'reviewer_note': reviewer_note, 'actor': actor})
        return {'id': submission_id, 'status': 'needs-field-check', 'duplicate_resolution': duplicate_action, 'reviewer_note': reviewer_note}

    monkeypatch.setattr(main, 'record_geotag_duplicate_decision', fake_decision)
    response = client.post(
        '/api/v1/geotag-submissions/geo-a/duplicate-decision',
        json={'duplicate_action': 'gps-error-recapture', 'reviewer_note': 'Same code but different label; request recapture.'},
        headers=auth_header(),
    )
    assert response.status_code == 200
    assert captured['duplicate_action'] == 'gps-error-recapture'
    assert response.json()['status'] == 'needs-field-check'


def test_geotag_submission_history_is_scoped_to_request(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    captured = {}

    def fake_audit_logs(entity_type=None, entity_id=None, limit=50):
        captured.update({'entity_type': entity_type, 'entity_id': entity_id, 'limit': limit})
        return [
            {
                'actor_username': 'editor',
                'action': 'needs-field-check',
                'entity_type': entity_type,
                'entity_id': entity_id,
                'details': {'reviewer_note': 'GPS accuracy needs confirmation'},
            }
        ]

    monkeypatch.setattr(main, 'list_audit_logs', fake_audit_logs)
    response = client.get('/api/v1/geotag-submissions/geo-a/history', headers=auth_header())
    assert response.status_code == 200
    assert captured == {'entity_type': 'citizen_geotag_submission', 'entity_id': 'geo-a', 'limit': 25}
    assert response.json()['items'][0]['action'] == 'needs-field-check'


def test_geotag_submission_history_requires_operator_role(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: {'id': 'public', 'username': 'public', 'display_name': 'Public', 'role': 'public'})
    response = client.get('/api/v1/geotag-submissions/geo-a/history', headers=auth_header())
    assert response.status_code == 403


def test_public_approved_address_code_lookup_hides_unpublished(monkeypatch) -> None:
    monkeypatch.setattr(main, 'public_address_code_record_lookup', lambda code: {
        'code': code,
        'is_valid': True,
        'publication_status': 'not_public',
        'record': None,
    })
    response = client.get('/api/v1/public/address-code/EG-BN-N1-1ZNSA408CX-MH/record')
    assert response.status_code == 200
    assert response.json()['publication_status'] == 'not_public'
    assert response.json()['record'] is None


def test_public_approved_address_code_lookup_returns_published_record(monkeypatch) -> None:
    monkeypatch.setattr(main, 'public_address_code_record_lookup', lambda code: {
        'code': code,
        'is_valid': True,
        'publication_status': 'published',
        'record': {
            'grid_code': code,
            'address_label': 'Abaceria Makeda Torrejon',
            'territory_name': 'Malabo Urban Core',
            'latitude': 3.7245106,
            'longitude': 8.7766097,
            'status': 'published',
        },
    })
    response = client.get('/api/v1/public/address-code/EG-BN-N1-1ZNRT408DA-1X/record')
    assert response.status_code == 200
    assert response.json()['publication_status'] == 'published'
    assert response.json()['record']['address_label'] == 'Abaceria Makeda Torrejon'


def test_geotag_certificate_requires_operator_and_omits_identity(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'build_geotag_certificate', lambda submission_id: {
        'certificate_id': 'CERT-EG-BN-N1-TEST000001-AA',
        'submission_id': submission_id,
        'address_code': 'EG-BN-N1-TEST000001-AA',
        'address_label': 'Abaceria Makeda Torrejon',
        'territory_name': 'Malabo Urban Core',
        'status': 'published',
        'qr_payload': 'http://testserver/code/EG-BN-N1-TEST000001-AA',
        'html': '<html><body>Certificate EG-BN-N1-TEST000001-AA</body></html>',
    })
    response = client.get('/api/v1/geotag-submissions/geo-cert-1/certificate', headers=auth_header())
    assert response.status_code == 200
    payload = response.json()
    assert payload['certificate_id'].startswith('CERT-')
    assert payload['status'] == 'published'
    text = response.text
    assert 'dip_last4' not in text
    assert 'dip_full' not in text
    assert 'citizen_contact' not in text


def test_geotag_certificate_refuses_unapproved_request(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'build_geotag_certificate', lambda submission_id: (_ for _ in ()).throw(main.InvalidSubmissionActionError('certificate requires published status after full project approval')))
    response = client.get('/api/v1/geotag-submissions/geo-pending/certificate', headers=auth_header())
    assert response.status_code == 400


def test_field_geotag_tasks_are_operator_scoped(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'list_field_geotag_tasks', lambda status=None, territory_id=None: [
        {
            'id': 'geo-field-1',
            'address_label': 'Vicatana Block 4',
            'territory_name': 'Malabo Urban Core',
            'grid_code': 'EG-BN-N1-TEST000001-AA',
            'status': 'needs-field-check',
            'field_status': 'assigned',
            'latitude': 3.7252,
            'longitude': 8.7760,
            'quality_flags': {'requires_field_check': True},
        }
    ])
    response = client.get('/api/v1/field/geotag-tasks', headers=auth_header())
    assert response.status_code == 200
    item = response.json()['items'][0]
    assert item['field_status'] == 'assigned'
    assert item['status'] == 'needs-field-check'


def test_field_geotag_task_status_update_requires_editor(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    captured = {}

    def fake_update(submission_id, field_status, field_note, actor=None):
        captured.update({'submission_id': submission_id, 'field_status': field_status, 'field_note': field_note, 'actor': actor})
        return {'id': submission_id, 'field_status': field_status, 'field_note': field_note, 'status': 'under-review'}

    monkeypatch.setattr(main, 'update_geotag_field_status', fake_update)
    response = client.post('/api/v1/field/geotag-tasks/geo-field-1/status', headers=auth_header(), json={
        'field_status': 'verified',
        'field_note': 'Coordinates verified at gate.',
    })
    assert response.status_code == 200
    assert captured['field_status'] == 'verified'
    assert captured['actor']['role'] == 'editor'


def test_geotag_duplicate_summary_groups_by_code_and_status(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'geotag_duplicate_summary', lambda: {
        'groups': [
            {
                'grid_code': 'EG-BN-N1-TEST000001-AA',
                'count': 2,
                'active_count': 2,
                'resolved_count': 0,
                'items': [
                    {'id': 'geo-a', 'address_label': 'House A', 'status': 'submitted'},
                    {'id': 'geo-b', 'address_label': 'House B', 'status': 'under-review'},
                ],
            }
        ]
    })
    response = client.get('/api/v1/geotag-submissions/duplicates/summary', headers=auth_header())
    assert response.status_code == 200
    group = response.json()['groups'][0]
    assert group['count'] == 2
    assert group['active_count'] == 2


def test_geotag_sla_drilldown_filters_overdue_items(monkeypatch) -> None:
    now = datetime(2026, 7, 7, 9, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(main, '_now_utc', lambda: now)
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'list_address_corrections', lambda status=None: [])
    monkeypatch.setattr(main, 'list_citizen_geotag_submissions', lambda status=None, territory_id=None: [
        {
            'id': 'geo-overdue',
            'territory_id': None,
            'territory_name': None,
            'address_label': 'Overdue weak GPS house',
            'landmark': '',
            'latitude': 3.75,
            'longitude': 8.77,
            'accuracy_meters': 80,
            'capture_method': 'browser-gps',
            'grid_code': 'EG-BN-N1-OVERDUE001-AA',
            'status': 'submitted',
            'duplicate_hint': 'none',
            'reviewer_note': '',
            'road_suggestion_status': 'not-suggested',
            'field_status': 'assigned',
            'field_submission_id': None,
            'signage_batch': None,
            'created_at': (now - timedelta(hours=80)).isoformat(),
            'updated_at': (now - timedelta(hours=80)).isoformat(),
        },
        {
            'id': 'geo-on-time',
            'territory_id': 'territory-malabo-ela-nguema',
            'territory_name': 'Ela Nguema',
            'address_label': 'Fresh house',
            'landmark': 'Gate',
            'latitude': 3.751,
            'longitude': 8.771,
            'accuracy_meters': 8,
            'capture_method': 'browser-gps',
            'grid_code': 'EG-BN-N1-ONTIME001-AA',
            'status': 'submitted',
            'duplicate_hint': 'none',
            'reviewer_note': '',
            'road_suggestion_status': 'not-suggested',
            'field_status': 'assigned',
            'field_submission_id': None,
            'signage_batch': None,
            'created_at': (now - timedelta(hours=8)).isoformat(),
            'updated_at': (now - timedelta(hours=8)).isoformat(),
        },
    ])
    response = client.get('/api/v1/geotag-submissions/automation/sla-drilldown', params={'state': 'overdue'}, headers=auth_header())
    assert response.status_code == 200
    body = response.json()
    assert body['state'] == 'overdue'
    assert [item['id'] for item in body['items']] == ['geo-overdue']
    assert body['items'][0]['next_best_action'] == 'send-field-check'


def test_field_evidence_endpoint_records_metadata_without_public_identity(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    captured = {}

    def fake_record(submission_id, evidence_type, evidence_reference, evidence_note, actor=None):
        captured.update({
            'submission_id': submission_id,
            'evidence_type': evidence_type,
            'evidence_reference': evidence_reference,
            'evidence_note': evidence_note,
            'actor': actor,
        })
        return {
            'submission_id': submission_id,
            'evidence_type': evidence_type,
            'evidence_reference': evidence_reference,
            'evidence_note': evidence_note,
            'field_status': 'visited',
            'public_safe': True,
        }

    monkeypatch.setattr(main, 'record_geotag_field_evidence', fake_record)
    response = client.post('/api/v1/field/geotag-tasks/geo-field-1/evidence', headers=auth_header(), json={
        'evidence_type': 'photo-reference',
        'evidence_reference': 'field-photo-001.jpg',
        'evidence_note': 'Front gate and road sign verified by field team.',
    })
    assert response.status_code == 200
    assert captured['actor']['role'] == 'editor'
    assert response.json()['public_safe'] is True
    assert 'citizen_contact' not in response.text
    assert 'dip_full' not in response.text


def test_public_tracking_lookup_accepts_address_code_without_leaking_operator_data(monkeypatch) -> None:
    monkeypatch.setattr(main, 'public_address_code_record_lookup', lambda code: {
        'code': code,
        'is_valid': True,
        'publication_status': 'not_public',
        'record': None,
    })
    monkeypatch.setattr(main, 'list_citizen_geotag_submissions', lambda status=None, territory_id=None: [
        {
            'id': 'geo-track-code',
            'territory_id': 'territory-malabo-ela-nguema',
            'territory_name': 'Ela Nguema',
            'address_label': 'Tracked by address code',
            'citizen_contact': '+240****0000',
            'dip_last4': '1234',
            'latitude': 3.75,
            'longitude': 8.77,
            'accuracy_meters': 8,
            'capture_method': 'browser-gps',
            'grid_code': 'EG-BN-N1-TRACK001-AA',
            'status': 'registry-ready',
            'duplicate_hint': 'none',
            'reviewer_note': 'operator-only note',
            'road_suggestion_status': 'accepted',
            'field_status': 'verified',
            'field_submission_id': None,
            'signage_batch': None,
            'created_at': '2026-07-07T08:00:00Z',
            'updated_at': '2026-07-07T08:00:00Z',
        }
    ])
    response = client.get('/api/v1/public/tracking/EG-BN-N1-TRACK001-AA')
    assert response.status_code == 200
    body = response.json()
    assert body['lookup_type'] == 'address-code'
    assert body['grid_code'] == 'EG-BN-N1-TRACK001-AA'
    assert body['publication_state'] == 'internal-registry'
    assert 'citizen_contact' not in response.text
    assert 'dip_last4' not in response.text
    assert 'operator-only note' not in response.text


def test_publication_simulation_does_not_publish_or_create_signage(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    captured = {}

    def fake_simulate(submission_id, reviewer_note, actor=None):
        captured.update({'submission_id': submission_id, 'reviewer_note': reviewer_note, 'actor': actor})
        return {
            'submission_id': submission_id,
            'simulation_status': 'simulated-publication-path',
            'public_release_locked': True,
            'physical_signage_locked': True,
            'resulting_record_status': 'registry-ready',
            'would_create_public_lookup': True,
            'would_create_certificate': True,
            'would_create_signage_batch': True,
            'operator_note': 'Simulation only. Full project/institutional approval is required before publication, certificates, or physical signage.',
        }

    monkeypatch.setattr(main, 'simulate_geotag_publication_path', fake_simulate)
    response = client.post('/api/v1/geotag-submissions/geo-ready/publication-simulation', headers=auth_header(), json={
        'reviewer_note': 'Dry run for ministry workflow demonstration.',
    })
    assert response.status_code == 200
    body = response.json()
    assert captured['actor']['role'] == 'editor'
    assert body['public_release_locked'] is True
    assert body['physical_signage_locked'] is True
    assert body['resulting_record_status'] == 'registry-ready'
    assert 'Simulation only' in body['operator_note']


def test_operator_command_center_groups_key_operational_lanes(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'reporting_summary', lambda: {
        'totals': {'territories': 8, 'submissions': 4, 'review_queue': 2, 'published_addresses': 1, 'import_jobs': 1, 'public_corrections': 3, 'correction_queue': 2, 'citizen_geotags': 5, 'geotag_queue': 3},
        'correction_breakdown': [],
        'review_breakdown': [],
        'publication_breakdown': [],
        'geotag_breakdown': [],
        'territories_by_province': [],
    })
    monkeypatch.setattr(main, 'pilot_readiness_summary', lambda: {'readiness_status': 'pilot-ready', 'passed_gates': 7, 'total_gates': 8, 'gates': [], 'boundaries': []})
    monkeypatch.setattr(main, 'list_citizen_geotag_submissions', lambda status=None, territory_id=None: [])
    monkeypatch.setattr(main, 'list_address_corrections', lambda status=None: [])
    monkeypatch.setattr(main, 'geotag_duplicate_summary', lambda: {'groups': [{'grid_code': 'EG-BN-N1-TEST', 'active_count': 2}]})
    monkeypatch.setattr(main, 'demo_fixture_status', lambda: {'buckets': [{'bucket': 'roads_smoke', 'count': 0}], 'total': 0, 'clean': True})
    monkeypatch.setattr(main, 'latest_restore_drill_report', lambda: {'status': 'passed', 'backup_file': 'addressing_latest.dump', 'restored_counts': [{'table_name': 'addresses', 'rows': 3}]})
    monkeypatch.setattr(main, 'migration_status', lambda: {'status': 'current', 'applied_count': 4, 'pending_count': 0, 'latest_version': '004'})

    response = client.get('/api/v1/operator/command-center', headers=auth_header())

    assert response.status_code == 200
    body = response.json()
    assert body['readiness']['status'] == 'pilot-ready'
    assert body['queues']['verification_queue'] == 2
    assert body['risk_lanes']['duplicate_groups'] == 1
    assert body['demo_fixtures']['clean'] is True
    assert body['restore_drill']['status'] == 'passed'
    assert body['migrations']['status'] == 'current'
    assert body['migrations']['pending_count'] == 0
    assert body['walkthrough'][0]['route'] == '/geotag'


def test_operator_command_center_requires_authenticated_viewer(monkeypatch) -> None:
    response = client.get('/api/v1/operator/command-center')
    assert response.status_code == 401


def test_demo_fixture_status_and_cleanup_are_admin_scoped(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: ADMIN)
    monkeypatch.setattr(main, 'demo_fixture_status', lambda: {'buckets': [{'bucket': 'roads_smoke', 'count': 2}], 'total': 2, 'clean': False})
    cleanup_called = {}

    def fake_cleanup(actor=None):
        cleanup_called['actor'] = actor
        return {'buckets': [{'bucket': 'roads_smoke', 'count': 0}], 'total': 0, 'clean': True, 'deleted': True}

    monkeypatch.setattr(main, 'cleanup_demo_fixtures', fake_cleanup)

    status_response = client.get('/api/v1/operator/demo-fixtures/status', headers=auth_header())
    cleanup_response = client.post('/api/v1/operator/demo-fixtures/cleanup', headers=auth_header())

    assert status_response.status_code == 200
    assert status_response.json()['total'] == 2
    assert cleanup_response.status_code == 200
    assert cleanup_response.json()['clean'] is True
    assert cleanup_called['actor']['role'] == 'admin'


def test_demo_fixture_cleanup_rejects_non_admin(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    response = client.post('/api/v1/operator/demo-fixtures/cleanup', headers=auth_header())
    assert response.status_code == 403


def test_restore_drill_report_missing_file_has_not_run_status(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'latest_restore_drill_report', lambda: {'status': 'not-run', 'operator_note': 'No restore drill proof has been recorded yet.'})
    response = client.get('/api/v1/operator/restore-drill/latest', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['status'] == 'not-run'


def test_operator_migration_status_requires_authenticated_viewer(monkeypatch) -> None:
    response = client.get('/api/v1/operator/migrations/status')
    assert response.status_code == 401


def test_operator_migration_status_returns_safe_summary(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'migration_status', lambda: {
        'status': 'current',
        'applied_count': 4,
        'pending_count': 0,
        'latest_version': '004',
        'latest_filename': '004_registry_ready_not_signage_ready.sql',
    })

    response = client.get('/api/v1/operator/migrations/status', headers=auth_header())

    assert response.status_code == 200
    body = response.json()
    assert body['status'] == 'current'
    assert body['pending_count'] == 0
    assert 'password' not in str(body).lower()


def test_migration_status_uses_configured_migration_directory(monkeypatch, tmp_path) -> None:
    migrations = tmp_path / 'migrations'
    migrations.mkdir()
    (migrations / '001_schema_migration_baseline.sql').write_text('-- baseline\n', encoding='utf-8')
    monkeypatch.setenv('MIGRATIONS_DIR', str(migrations))
    monkeypatch.delenv('DATABASE_URL', raising=False)
    monkeypatch.delenv('POSTGRES_HOST', raising=False)

    body = main.migration_status()

    assert body['status'] == 'not-configured'
    assert body['expected_count'] == 1
    assert body['pending_count'] == 1
    assert body['latest_filename'] == '001_schema_migration_baseline.sql'


def test_addresses_endpoint_returns_pagination_metadata(monkeypatch) -> None:
    rows = [
        {'id': f'addr-{index}', 'formatted': f'Address {index}', 'status': 'active'}
        for index in range(1, 6)
    ]
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'fetch_addresses_page', lambda **kwargs: {'items': rows[(kwargs.get('page', 1) - 1) * kwargs.get('per_page', 100): kwargs.get('page', 1) * kwargs.get('per_page', 100)], 'pagination': {'page': kwargs.get('page', 1), 'per_page': kwargs.get('per_page', 100), 'total_items': len(rows), 'total_pages': 3, 'has_next': kwargs.get('page', 1) < 3, 'has_previous': kwargs.get('page', 1) > 1}})

    response = client.get('/api/v1/addresses', params={'page': 2, 'per_page': 2}, headers=auth_header())

    assert response.status_code == 200
    body = response.json()
    assert [item['id'] for item in body['items']] == ['addr-3', 'addr-4']
    assert body['pagination'] == {
        'page': 2,
        'per_page': 2,
        'total_items': 5,
        'total_pages': 3,
        'has_next': True,
        'has_previous': True,
    }


def test_list_pagination_clamps_per_page_without_breaking_items(monkeypatch) -> None:
    rows = [{'id': f'road-{index}', 'name': f'Road {index}'} for index in range(1, 4)]
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'fetch_roads_page', lambda **kwargs: {'items': rows, 'pagination': {'page': 1, 'per_page': 100, 'total_items': len(rows), 'total_pages': 1, 'has_next': False, 'has_previous': False}})

    response = client.get('/api/v1/roads', params={'page': 0, 'per_page': 999}, headers=auth_header())

    assert response.status_code == 200
    body = response.json()
    assert len(body['items']) == 3
    assert body['pagination']['page'] == 1
    assert body['pagination']['per_page'] == 100


def test_api_responses_include_security_headers() -> None:
    response = client.get('/api/v1/health')

    assert response.status_code == 200
    assert response.headers['x-content-type-options'] == 'nosniff'
    assert response.headers['referrer-policy'] == 'no-referrer'
    assert response.headers['cache-control'] == 'no-store'


def test_production_readiness_endpoint_is_auth_protected_and_honest(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)

    unauthenticated = client.get('/api/v1/operator/production-readiness')
    assert unauthenticated.status_code == 401

    response = client.get('/api/v1/operator/production-readiness', headers=auth_header())
    assert response.status_code == 200
    body = response.json()
    assert body['status'] in {'ready', 'needs_work'}
    assert 'secure_cookie_sessions' in body['checks']
    assert body['checks']['secure_cookie_sessions']['status'] == 'needs_work'


def test_login_can_issue_secure_session_cookie(monkeypatch) -> None:
    monkeypatch.setattr(main, 'SESSION_COOKIE_MODE', 'secure-http-only-cookie')
    monkeypatch.setattr(main, 'SESSION_COOKIE_SECURE', True)
    monkeypatch.setattr(main, 'authenticate_user_session', lambda username, password: {'token': 'cookie-token', 'user': ADMIN})
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})

    assert response.status_code == 200
    set_cookie = response.headers.get('set-cookie', '')
    assert 'eg_addressing_session=' in set_cookie
    assert 'HttpOnly' in set_cookie
    assert 'Secure' in set_cookie
    assert 'SameSite=lax' in set_cookie


def test_auth_me_accepts_session_cookie(monkeypatch) -> None:
    monkeypatch.setattr(main, 'SESSION_COOKIE_MODE', 'secure-http-only-cookie')
    monkeypatch.setattr(main, 'SESSION_COOKIE_SECURE', False)
    monkeypatch.setattr(main, 'authenticate_user_session', lambda username, password: {'token': 'cookie-token', 'user': ADMIN})
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: ADMIN if token == 'cookie-token' else (_ for _ in ()).throw(main.AuthenticationError('bad token')))
    login_response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    assert login_response.status_code == 200

    response = client.get('/api/v1/auth/me', cookies=login_response.cookies)

    assert response.status_code == 200
    assert response.json()['user']['username'] == 'admin'


def test_data_command_deck_source_guard() -> None:
    registry_source = Path('../../apps/admin-portal/components/RegistryCorePanel.tsx').resolve().read_text()
    reporting_source = Path('../../apps/admin-portal/components/ReportingDashboardPanel.tsx').resolve().read_text()
    assert 'data-command-deck' in registry_source
    assert 'case-lane' in registry_source
    assert 'information scent' in registry_source.lower()
    assert 'data-command-deck' in reporting_source
    assert 'risk lane' in reporting_source.lower()


def test_full_registry_read_endpoints_are_not_public() -> None:
    client.cookies.clear()
    protected_paths = [
        '/api/v1/territories',
        '/api/v1/territories/territory-a',
        '/api/v1/roads',
        '/api/v1/roads/road-a',
        '/api/v1/buildings',
        '/api/v1/buildings/building-a',
        '/api/v1/addresses',
        '/api/v1/addresses/address-a',
        '/api/v1/field/assignments',
    ]
    for path in protected_paths:
        response = client.get(path)
        assert response.status_code == 401, path


def test_route_auth_guard_has_no_unexpected_public_registry_reads() -> None:
    client.cookies.clear()
    allowed_public = {
        '/api/v1/health',
        '/api/v1/meta',
        '/api/v1/auth/login',
        '/api/v1/territories/provinces',
        '/api/v1/provinces',
        '/api/v1/admin-units',
        '/api/v1/verification/lookup',
        '/api/v1/public/territory-options',
    }
    allowed_prefixes = ('/api/v1/public/',)
    leaked = []
    for route in main.app.routes:
        path = getattr(route, 'path', '')
        methods = set(getattr(route, 'methods', set()))
        if not path.startswith('/api/v1') or 'GET' not in methods:
            continue
        if path in allowed_public or path.startswith(allowed_prefixes):
            continue
        source = getattr(route.endpoint, '__name__', '')
        # Exercise likely registry/ops reads without auth; path params are replaced with safe dummy values.
        candidate = path.replace('{territory_id}', 'territory-a').replace('{road_id}', 'road-a').replace('{building_id}', 'building-a').replace('{address_id}', 'address-a').replace('{submission_id}', 'submission-a').replace('{address_code}', 'EG-BN-N1-TEST').replace('{job_id}', 'job-a').replace('{pack_id}', 'pack-a').replace('{correction_id}', 'correction-a')
        response = client.get(candidate)
        if response.status_code != 401:
            leaked.append((source, candidate, response.status_code))
    assert leaked == []

