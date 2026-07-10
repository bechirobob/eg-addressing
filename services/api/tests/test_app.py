from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

import app.db as db
import app.main as main
from app.security_posture import production_readiness_status
from app.main import app

client = TestClient(app)

ADMIN = {'id': 'user-admin', 'username': 'admin', 'full_name': 'National Platform Administrator', 'role': 'admin'}
EDITOR = {'id': 'user-editor', 'username': 'editor', 'full_name': 'Registry Editor', 'role': 'editor'}
VIEWER = {'id': 'user-viewer', 'username': 'viewer', 'full_name': 'Program Viewer', 'role': 'viewer'}
AGENCY_VIEWER = {'id': 'user-agency-viewer', 'username': 'agency_viewer', 'full_name': 'Agency Review Viewer', 'role': 'agency_viewer'}


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


def test_admin_can_list_staff_users_without_hashes_or_tokens(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: ADMIN)
    monkeypatch.setattr(main, 'list_staff_users', lambda: [
        {
            'id': 'user-editor',
            'username': 'editor',
            'full_name': 'Registry Editor',
            'role': 'editor',
            'is_active': True,
            'created_at': '2026-07-10T00:00:00+00:00',
            'active_sessions': 1,
            'password_hash': 'must-not-leak',
        }
    ])

    response = client.get('/api/v1/admin/users', headers=auth_header())

    assert response.status_code == 200
    body = response.json()
    assert body['items'][0]['username'] == 'editor'
    assert 'password_hash' not in body['items'][0]
    assert 'token' not in json.dumps(body)


def test_non_admin_cannot_manage_staff_users(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)

    response = client.get('/api/v1/admin/users', headers=auth_header())

    assert response.status_code == 403


def test_admin_can_create_update_disable_and_revoke_staff_user(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: ADMIN)
    calls: list[tuple[Any, ...]] = []

    def fake_create(payload, actor=None):
        calls.append(('create', payload, actor))
        return {'id': 'user-field-lead', 'username': payload['username'], 'full_name': payload['full_name'], 'role': payload['role'], 'is_active': True, 'created_at': '2026-07-10T00:00:00+00:00', 'active_sessions': 0}

    def fake_update(user_id, payload, actor=None):
        calls.append(('update', user_id, payload, actor))
        return {'id': user_id, 'username': 'field_lead', 'full_name': payload['full_name'], 'role': payload['role'], 'is_active': payload['is_active'], 'created_at': '2026-07-10T00:00:00+00:00', 'active_sessions': 0}

    def fake_disable(user_id, actor=None):
        calls.append(('disable', user_id, actor))
        return {'id': user_id, 'username': 'field_lead', 'full_name': 'Field Lead', 'role': 'viewer', 'is_active': False, 'created_at': '2026-07-10T00:00:00+00:00', 'active_sessions': 0}

    def fake_revoke(user_id, actor=None):
        calls.append(('revoke', user_id, actor))
        return {'user_id': user_id, 'revoked_sessions': 2}

    monkeypatch.setattr(main, 'create_staff_user', fake_create)
    monkeypatch.setattr(main, 'update_staff_user', fake_update)
    monkeypatch.setattr(main, 'disable_staff_user', fake_disable)
    monkeypatch.setattr(main, 'revoke_staff_user_sessions', fake_revoke)

    created = client.post('/api/v1/admin/users', json={'username': 'field_lead', 'full_name': 'Field Lead', 'role': 'viewer', 'password': 'temporary-strong-pass'}, headers=auth_header())
    updated = client.patch('/api/v1/admin/users/user-field-lead', json={'full_name': 'Field Operations Lead', 'role': 'editor', 'is_active': True}, headers=auth_header())
    disabled = client.post('/api/v1/admin/users/user-field-lead/disable', headers=auth_header())
    revoked = client.post('/api/v1/admin/users/user-field-lead/revoke-sessions', headers=auth_header())

    assert created.status_code == 201
    assert updated.status_code == 200
    assert disabled.json()['is_active'] is False
    assert revoked.json()['revoked_sessions'] == 2
    assert [call[0] for call in calls] == ['create', 'update', 'disable', 'revoke']


def test_admin_cannot_deactivate_or_revoke_own_account(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: ADMIN)

    deactivate = client.patch('/api/v1/admin/users/user-admin', json={'is_active': False}, headers=auth_header())
    disable = client.post('/api/v1/admin/users/user-admin/disable', headers=auth_header())
    revoke = client.post('/api/v1/admin/users/user-admin/revoke-sessions', headers=auth_header())

    assert deactivate.status_code == 400
    assert disable.status_code == 400
    assert revoke.status_code == 400


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


def test_public_territory_options_returns_safe_evidence_fields(monkeypatch) -> None:
    expected = [{'id': 'territory-mongomo-core', 'name': 'Mongomo Core', 'province_code': 'WN', 'province': 'Wele-Nzas', 'admin_unit_id': 'admin-unit-wele-nzas', 'admin_unit_code': 'WN-M-MONGOMO', 'admin_unit_name': 'Mongomo', 'admin_unit_level': 'municipality', 'type': 'official-municipality', 'readiness': 'official-routing', 'is_archived': False}]
    monkeypatch.setattr(main, 'fetch_territories', lambda **kwargs: expected)
    response = client.get('/api/v1/public/territory-options')
    assert response.status_code == 200
    item = response.json()['items'][0]
    assert item['id'] == 'territory-mongomo-core'
    assert item['routing_status_label'] == 'Official administrative route'
    assert item['source_label'] == 'Administrative division table / INEGE-referenced source'
    assert item['confidence_label'] == 'Administrative unit confirmed'
    assert item['geometry_status'] == 'Name-based routing area; surveyed boundary not attached'
    assert item['public_status'] == 'Internal routing only until operator verification and controlled publication'
    assert item['admin_unit_name'] == 'Mongomo'
    assert item['admin_unit_level'] == 'municipality'
    assert 'admin_unit_id' not in response.text
    assert 'admin_unit_code' not in response.text




def test_public_territory_options_can_filter_nationwide_official_routing(monkeypatch) -> None:
    captured = {}
    def fake_fetch_territories(**kwargs):
        captured.update(kwargs)
        return [{'id': 'territory-official-municipality-bata', 'name': 'Bata', 'province_code': 'LI', 'province': 'Litoral', 'admin_unit_name': 'Bata', 'admin_unit_level': 'municipality', 'type': 'official-municipality', 'readiness': 'official-routing', 'is_archived': False}]
    monkeypatch.setattr(main, 'fetch_territories', fake_fetch_territories)
    response = client.get('/api/v1/public/territory-options', params={'province_code': 'LI'})
    assert response.status_code == 200
    assert captured == {'province_code': 'LI', 'include_archived': False}
    assert response.json()['items'][0]['name'] == 'Bata'
    assert response.json()['items'][0]['source_label'].startswith('Administrative division table')

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


def test_create_field_submission_returns_400_for_missing_spatial_evidence(monkeypatch) -> None:
    payload = {'assignment_id': 'field-001', 'territory_id': 'territory-bata', 'submission_type': 'road', 'candidate_name': 'New Road', 'candidate_status': 'submitted', 'notes': 'n', 'submitted_by': 'Team'}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'create_field_submission', lambda payload, actor=None: (_ for _ in ()).throw(main.InvalidSubmissionActionError('road stretch geometry requires captured start and end GPS points')))
    response = client.post('/api/v1/field/submissions', json=payload, headers=auth_header())
    assert response.status_code == 400
    assert 'road stretch geometry' in response.json()['detail']



def test_approve_submission_returns_registry_link(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'approve_submission', lambda submission_id, actor=None: {'id': submission_id, 'review_status': 'approved', 'registry_entity_id': 'road-new-road'})
    response = client.post('/api/v1/field/submissions/sub-1/approve', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['registry_entity_id'] == 'road-new-road'


def test_spatial_evidence_blocks_road_approval_without_polyline() -> None:
    try:
        db.validate_submission_spatial_evidence({'submission_type': 'road', 'spatial_evidence': None})
    except main.InvalidSubmissionActionError as exc:
        assert 'road stretch geometry' in str(exc)
    else:
        raise AssertionError('road approval should require captured stretch geometry')


def test_spatial_evidence_accepts_road_polyline_with_calculated_length() -> None:
    db.validate_submission_spatial_evidence({
        'submission_type': 'road',
        'spatial_evidence': {
            'geometry_type': 'LineString',
            'capture_method': 'browser-gps',
            'calculated_length_km': 0.42,
            'points': [
                {'latitude': 3.7521, 'longitude': 8.7731, 'role': 'start'},
                {'latitude': 3.7536, 'longitude': 8.7762, 'role': 'end'},
            ],
            'evidence_attachments': [
                {
                    'type': 'photo-reference',
                    'reference': 'FIELD-PHOTO-20260709-001',
                    'note': 'Frontage photo stored in protected field drive.',
                    'captured_by': 'Field Team A',
                    'captured_at': '2026-07-09T20:00:00+01:00',
                },
            ],
        },
    })
    normalized = db.normalize_submission_spatial_evidence(
        'road',
        {
            'geometry_type': 'LineString',
            'points': [
                {'latitude': 3.7521, 'longitude': 8.7731, 'role': 'start'},
                {'latitude': 3.7536, 'longitude': 8.7762, 'role': 'end'},
            ],
            'evidence_attachments': [{'type': 'site-note', 'reference': 'NOTE-001', 'note': 'Gate confirmed.'}],
        },
    )
    assert normalized['evidence_attachment_count'] == 1
    assert normalized['evidence_attachments'][0]['reference'] == 'NOTE-001'


def test_spatial_evidence_rejects_sensitive_evidence_references() -> None:
    try:
        db.normalize_submission_spatial_evidence(
            'building',
            {
                'geometry_type': 'Point',
                'latitude': 3.7521,
                'longitude': 8.7731,
                'accuracy_meters': 18,
                'road_reference': 'Avenida principal',
                'evidence_attachments': [{'type': 'photo-reference', 'reference': 'DIP-scan-private'}],
            },
        )
    except main.InvalidSubmissionActionError as exc:
        assert 'private credentials or identity document' in str(exc)
    else:
        raise AssertionError('sensitive evidence references must be rejected')


def test_spatial_evidence_rejects_too_many_evidence_references() -> None:
    try:
        db.normalize_submission_spatial_evidence(
            'road',
            {
                'geometry_type': 'LineString',
                'points': [
                    {'latitude': 3.7521, 'longitude': 8.7731, 'role': 'start'},
                    {'latitude': 3.7536, 'longitude': 8.7762, 'role': 'end'},
                ],
                'evidence_attachments': [{'type': 'site-note', 'reference': f'NOTE-{index:03d}'} for index in range(7)],
            },
        )
    except main.InvalidSubmissionActionError as exc:
        assert 'limited to 6 items' in str(exc)
    else:
        raise AssertionError('too many evidence references must be rejected')


def test_spatial_evidence_blocks_building_approval_without_point() -> None:
    try:
        db.validate_submission_spatial_evidence({'submission_type': 'building', 'spatial_evidence': {}})
    except main.InvalidSubmissionActionError as exc:
        assert 'building point evidence' in str(exc)
    else:
        raise AssertionError('building approval should require captured point geometry')


def test_spatial_evidence_accepts_building_point_with_accuracy() -> None:
    db.validate_submission_spatial_evidence({
        'submission_type': 'building',
        'spatial_evidence': {
            'geometry_type': 'Point',
            'capture_method': 'browser-gps',
            'latitude': 3.7521,
            'longitude': 8.7731,
            'accuracy_meters': 18,
            'road_reference': 'Avenida principal',
        },
    })


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
        'privacy_notice_acknowledged': True,
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


def test_public_correction_requires_privacy_acknowledgement() -> None:
    response = client.post('/api/v1/public/corrections', json={
        'query': 'EG-LI-BATA-123ABC',
        'public_code': 'EG-LI-BATA-123ABC',
        'correction_type': 'location-fix',
        'reason': 'pin-drift',
    })
    assert response.status_code == 400
    assert response.json()['detail'] == 'privacy notice acknowledgement required'


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


def test_publish_publication_pack_requires_release_gate(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: ADMIN)
    monkeypatch.setattr(main, 'PUBLICATION_RELEASE_ENABLED', False)
    response = client.post('/api/v1/publication/packs/pack-1/publish', headers=auth_header())
    assert response.status_code == 403
    assert response.json()['detail'] == 'publication release gate is disabled'


def test_audit_logs_endpoint_returns_pagination_metadata(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: ADMIN)
    captured = {}

    def fake_audit_logs_page(entity_type=None, entity_id=None, page=1, per_page=50):
        captured.update({'entity_type': entity_type, 'entity_id': entity_id, 'page': page, 'per_page': per_page})
        return {
            'items': [{'id': 1, 'action': 'login', 'entity_type': 'session'}],
            'pagination': {'page': page, 'per_page': per_page, 'total_items': 1, 'total_pages': 1, 'has_next': False, 'has_previous': False},
        }

    monkeypatch.setattr(main, 'list_audit_logs_page', fake_audit_logs_page)
    response = client.get('/api/v1/audit-logs?page=2&per_page=25&entity_type=session', headers=auth_header())

    assert response.status_code == 200
    assert captured == {'entity_type': 'session', 'entity_id': None, 'page': 2, 'per_page': 25}
    assert response.json()['pagination']['per_page'] == 25


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


def test_reporting_summary_allows_agency_viewer(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: AGENCY_VIEWER)
    monkeypatch.setattr(
        main,
        'reporting_summary',
        lambda: {
            'totals': {'territories': 3, 'submissions': 2, 'review_queue': 1, 'published_addresses': 1, 'import_jobs': 1, 'public_corrections': 4, 'correction_queue': 2, 'citizen_geotags': 5, 'geotag_queue': 3},
            'territories_by_province': [],
            'review_breakdown': [],
            'publication_breakdown': [],
            'correction_breakdown': [],
            'geotag_breakdown': [],
        },
    )
    response = client.get('/api/v1/reporting/summary', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['totals']['territories'] == 3


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


def test_agency_viewer_can_read_readiness_and_signage_but_not_protected_operations(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: AGENCY_VIEWER)
    monkeypatch.setattr(
        main,
        'pilot_readiness_summary',
        lambda: {
            'readiness_status': 'pilot-ready',
            'passed_gates': 6,
            'total_gates': 6,
            'gates': [],
            'recent_audit_events': [{'action': 'login', 'entity_type': 'session', 'entity_id': 'session-secret-token', 'actor_username': 'agency_viewer'}],
            'boundaries': ['Government approval still required.'],
        },
    )
    monkeypatch.setattr(main, 'signage_export', lambda status='published': {'status': status, 'count': 0, 'items': []})

    readiness = client.get('/api/v1/pilot-readiness/summary', headers=auth_header())
    signage = client.get('/api/v1/signage/export', headers=auth_header())
    registry = client.get('/api/v1/geotag-submissions', headers=auth_header())
    mutation = client.post('/api/v1/imports/jobs', json={'name': 'Agency blocked', 'source_name': 'phase-6', 'rows': [{'submission_type': 'road', 'territory_id': 'territory-malabo-urban-core', 'candidate_name': 'Agency blocked road', 'candidate_status': 'submitted', 'notes': 'agency role negative test'}]}, headers=auth_header())
    audit = client.get('/api/v1/audit-logs', headers=auth_header())

    assert readiness.status_code == 200
    assert signage.status_code == 200
    assert registry.status_code == 403
    assert mutation.status_code == 403
    assert audit.status_code == 403


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
        'privacy_notice_acknowledged': True,
    }
    monkeypatch.setattr(main, 'create_citizen_geotag_submission', lambda body, actor=None: {'id': 'citizen-geotag-1', 'status': 'submitted', **body, 'grid_code': 'EG-LI-GABCD1234', 'duplicate_hints': []})
    response = client.post('/api/v1/public/geotag-submissions', json=payload)
    assert response.status_code == 201
    assert response.json()['grid_code'] == 'EG-LI-GABCD1234'
    assert response.json()['status'] == 'submitted'


def test_public_geotag_submission_requires_privacy_acknowledgement() -> None:
    response = client.post('/api/v1/public/geotag-submissions', json={
        'territory_id': 'territory-bata-urban-core',
        'address_label': 'House near civic cluster',
        'landmark': 'Blue gate near pharmacy',
        'latitude': 1.865,
        'longitude': 9.77,
        'capture_method': 'browser-gps',
    })
    assert response.status_code == 400
    assert response.json()['detail'] == 'privacy notice acknowledgement required'


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
        'privacy_notice_acknowledged': True,
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
        'privacy_notice_acknowledged': True,
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
        'privacy_notice_acknowledged': True,
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
        'privacy_notice_acknowledged': True,
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
        'privacy_notice_acknowledged': True,
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


def test_address_record_case_file_includes_masked_timeline(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'get_address_record_case_file', lambda code: {
        'id': 'address-record-1',
        'address_code': code,
        'status': 'registry-ready',
        'timeline': [
            {
                'event_type': 'registry-ready',
                'action': 'registry-ready',
                'entity_type': 'citizen_geotag_submission',
                'entity_id': 'citizen-geotag-1',
                'actor_username': 'editor',
                'details': {'session_token': 'private-session-placeholder', 'reviewer_note': 'approved'},
            }
        ],
    })

    response = client.get('/api/v1/address-records/EG-BN-N1-CASE000003-AA', headers=auth_header())

    assert response.status_code == 200
    body = response.json()
    assert body['timeline'][0]['event_type'] == 'registry-ready'
    assert 'private-session-placeholder' not in json.dumps(body)
    assert body['timeline'][0]['details']['session_token'] == '[protected]'



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
        'privacy_notice_acknowledged': True,
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


def test_public_address_code_record_accepts_published_legacy_registry_code(monkeypatch) -> None:
    legacy_code = 'EG-BN-MALABO-001A'
    monkeypatch.setattr(db, 'search_address_records', lambda q, limit=5, **kwargs: [
        {
            'id': 'addr-malabo-001',
            'address_code': legacy_code,
            'address_label': 'Avenida de la Independencia, Malabo',
            'record_bundle': {'routing': {'territory_name': 'Malabo Urban Core'}},
            'territory_id': 'territory-malabo-core',
            'latitude': 3.7528,
            'longitude': 8.7832,
            'accuracy_meters': 4.8,
            'status': 'published',
            'updated_at': '2026-07-09T00:00:00Z',
        }
    ])

    payload = db.public_address_code_record_lookup(legacy_code)

    assert payload['is_valid'] is True
    assert payload['schema'] == 'registry-public-code'
    assert payload['province_code'] == 'BN'
    assert 'error' not in payload
    assert payload['publication_status'] == 'published'
    assert payload['registry_identifier_type'] == 'published-registry-code'
    assert payload['record']['address_label'] == 'Avenida de la Independencia, Malabo'


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


def test_restore_drill_report_sanitizes_local_backup_paths(monkeypatch, tmp_path) -> None:
    report = tmp_path / 'restore_drill_latest.json'
    report.write_text(json.dumps({
        'status': 'passed',
        'backup_path': 'private_storage/backups/postgres/addressing_20260710T002016Z.dump',
        'backup_bytes': 123,
        'backup_sha256': 'abc123',
        'restored_counts': {'users': 3},
    }), encoding='utf-8')
    monkeypatch.setenv('RESTORE_DRILL_REPORT_PATH', str(report))

    body = main.latest_restore_drill_report()

    assert body['backup_file'] == 'addressing_20260710T002016Z.dump'
    assert 'backup_path' not in body
    assert 'private_storage' not in json.dumps(body)


def test_restore_drill_script_writes_operator_latest_digest() -> None:
    source = Path('../../infra/scripts/restore_drill.sh').read_text()
    assert 'LATEST_REPORT_FILE' in source
    assert 'artifacts/operator-digests/restore_drill_latest.json' in source


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


def test_migration_runner_rejects_malformed_filenames_before_sql_execution() -> None:
    source = Path('../../infra/scripts/run_migrations.sh').read_text()
    assert 'validate_migration_name()' in source
    assert "^[0-9]{3}_[A-Za-z0-9_]+\\.sql$" in source
    assert 'Invalid migration filename' in source


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
    monkeypatch.setenv('SESSION_COOKIE_MODE', 'bearer-local-storage')
    monkeypatch.setenv('ALLOW_DEFAULT_DEMO_PASSWORDS', 'true')

    unauthenticated = client.get('/api/v1/operator/production-readiness')
    assert unauthenticated.status_code == 401

    response = client.get('/api/v1/operator/production-readiness', headers=auth_header())
    assert response.status_code == 200
    body = response.json()
    assert body['status'] in {'ready', 'needs_work'}
    assert 'secure_cookie_sessions' in body['checks']
    assert body['checks']['secure_cookie_sessions']['status'] == 'needs_work'
    assert 'default_demo_passwords_disabled' in body['checks']
    assert body['checks']['default_demo_passwords_disabled']['status'] == 'needs_work'


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


def test_government_service_source_guard() -> None:
    registry_source = Path('../../apps/admin-portal/components/RegistryCorePanel.tsx').resolve().read_text()
    reporting_source = Path('../../apps/admin-portal/components/ReportingPanel.tsx').resolve().read_text()
    chrome_source = Path('../../apps/admin-portal/components/SiteChrome.tsx').resolve().read_text()
    role_chrome_source = Path('../../apps/admin-portal/components/RoleAwareChrome.tsx').resolve().read_text()

    assert 'Address registry' in registry_source or 'Address register' in registry_source
    assert 'Search, update, and manage official address records' in registry_source
    assert 'Reports are read-only' in reporting_source
    assert 'Export report' in reporting_source
    forbidden = ['command center', 'risk lane', 'information scent', 'LanguageSwitcher', 'SpanishUiTextPatcher', 'Dashboard label']
    combined = '\n'.join([reporting_source, chrome_source, role_chrome_source])
    for term in forbidden:
        assert term.lower() not in combined.lower()


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




def test_enrich_field_spatial_evidence_adds_grid_cells_and_map_suggestion(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'get_territory', lambda territory_id: {'id': territory_id, 'province_code': 'BN'})
    monkeypatch.setattr(main, 'suggest_nearest_road_name', lambda latitude, longitude: {
        'suggested_road_name': 'Airport Road',
        'suggested_local_area': 'Malabo',
        'suggested_place_name': None,
        'display_name': 'Airport Road, Malabo',
        'source': 'openstreetmap-nominatim',
        'source_attribution': '© OpenStreetMap contributors',
        'distance_meters': None,
        'confidence': 'medium',
        'requires_review': True,
        'status': 'suggested',
    })
    response = client.post('/api/v1/field/spatial-evidence/enrich', json={
        'territory_id': 'territory-malabo-urban-core',
        'submission_type': 'road',
        'spatial_evidence': {
            'points': [
                {'role': 'start', 'latitude': 3.7521, 'longitude': 8.7731},
                {'role': 'end', 'latitude': 3.7534, 'longitude': 8.7759},
            ],
        },
    }, headers=auth_header())
    assert response.status_code == 200
    evidence = response.json()['spatial_evidence']
    assert evidence['map_suggestion']['suggested_road_name'] == 'Airport Road'
    assert evidence['map_suggestion']['requires_review'] is True
    assert evidence['grid_cells'][0]['grid_code'].startswith('EG-BN-N1-')
    assert evidence['calculated_length_km'] == 0.343
    assert evidence['review_required'] is True


def test_enrich_field_spatial_evidence_fails_soft_when_map_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'get_territory', lambda territory_id: {'id': territory_id, 'province_code': 'BN'})
    monkeypatch.setattr(main, 'suggest_nearest_road_name', lambda latitude, longitude: main._road_suggestion_unavailable())
    response = client.post('/api/v1/field/spatial-evidence/enrich', json={
        'territory_id': 'territory-malabo-urban-core',
        'submission_type': 'road',
        'spatial_evidence': {
            'points': [
                {'role': 'start', 'latitude': 3.7521, 'longitude': 8.7731},
                {'role': 'end', 'latitude': 3.7534, 'longitude': 8.7759},
            ],
        },
    }, headers=auth_header())
    assert response.status_code == 200
    evidence = response.json()['spatial_evidence']
    assert evidence['map_suggestion']['status'] == 'unavailable'
    assert evidence['grid_cells']
    assert evidence['review_required'] is True



def test_spatial_evidence_preserves_map_grid_enrichment() -> None:
    evidence = db.normalize_submission_spatial_evidence('road', {
        'points': [
            {'role': 'start', 'latitude': 3.7521, 'longitude': 8.7731},
            {'role': 'end', 'latitude': 3.7534, 'longitude': 8.7759},
        ],
        'grid_cells': [{'grid_code': 'EG-BN-N1-TEST'}],
        'map_suggestion': {'suggested_road_name': 'Airport Road', 'requires_review': True},
        'review_confidence': 'high',
    })
    assert evidence['grid_cells'][0]['grid_code'] == 'EG-BN-N1-TEST'
    assert evidence['map_suggestion']['suggested_road_name'] == 'Airport Road'
    assert evidence['review_required'] is True

def test_evidence_file_upload_requires_authenticated_editor(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    response = client.post(
        '/api/v1/field/submissions/submission-a/evidence-files?attachment_index=0&file_name=frontage.txt',
        content=b'field evidence note',
        headers={'Content-Type': 'text/plain'},
    )
    assert response.status_code == 401


def test_evidence_file_upload_rejects_executable_extension(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    response = client.post(
        '/api/v1/field/submissions/submission-a/evidence-files?attachment_index=0&file_name=malware.sh',
        content=b'echo bad',
        headers={**auth_header(), 'Content-Type': 'text/plain'},
    )
    assert response.status_code == 400
    assert 'not allowed' in response.json()['detail']


def test_evidence_file_upload_attaches_private_metadata(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    stored: dict[str, Any] = {}

    def fake_store(object_key: str, content: bytes, content_type: str) -> dict[str, Any]:
        stored.update({'object_key': object_key, 'content': content, 'content_type': content_type})
        return {'bucket': 'eg-field-evidence', 'object_key': object_key, 'size_bytes': len(content), 'sha256': 'hash123', 'content_type': content_type, 'etag': 'etag123'}

    def fake_attach(submission_id: str, attachment_index: int, file_metadata: dict[str, Any], actor=None) -> dict[str, Any]:
        assert submission_id == 'submission-a'
        assert attachment_index == 0
        assert actor == EDITOR
        assert file_metadata['file_name'] == 'frontage.txt'
        assert file_metadata['object_key'].startswith('field-submissions/submission-a/evidence-')
        return {'id': submission_id, 'spatial_evidence': {'evidence_attachments': [{'reference': 'FIELD-REF-1', 'files': [file_metadata]}]}}

    monkeypatch.setattr(main, 'store_evidence_object', fake_store)
    monkeypatch.setattr(main, 'attach_field_submission_evidence_file', fake_attach)
    response = client.post(
        '/api/v1/field/submissions/submission-a/evidence-files?attachment_index=0&file_name=frontage.txt',
        content=b'field evidence note',
        headers={**auth_header(), 'Content-Type': 'text/plain'},
    )
    assert response.status_code == 201
    body = response.json()
    assert body['file']['access'] == 'protected'
    assert body['file']['file_name'] == 'frontage.txt'
    assert stored['content'] == b'field evidence note'


def test_evidence_file_download_requires_auth_and_streams_private_object(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'get_field_submission_evidence_file', lambda submission_id, file_id, actor=None: {'file_id': file_id, 'file_name': 'frontage.txt', 'content_type': 'text/plain', 'object_key': 'field-submissions/submission-a/evidence-1/frontage.txt'})
    monkeypatch.setattr(main, 'read_evidence_object', lambda object_key: b'field evidence note')

    blocked = client.get('/api/v1/field/submissions/submission-a/evidence-files/evidence-1')
    assert blocked.status_code == 401

    response = client.get('/api/v1/field/submissions/submission-a/evidence-files/evidence-1', headers=auth_header())
    assert response.status_code == 200
    assert response.content == b'field evidence note'
    assert response.headers['content-type'].startswith('text/plain')

def test_evidence_review_requires_editor_or_admin(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    response = client.post(
        '/api/v1/field/submissions/submission-a/evidence-review',
        json={'attachment_index': 0, 'file_id': 'evidence-1', 'decision': 'accepted', 'reviewer_note': 'ok'},
        headers=auth_header(),
    )
    assert response.status_code == 403


def test_evidence_review_updates_protected_file_metadata(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    captured: dict[str, Any] = {}

    def fake_review(submission_id, attachment_index, decision, reviewer_note, file_id=None, actor=None):
        captured.update({
            'submission_id': submission_id,
            'attachment_index': attachment_index,
            'decision': decision,
            'reviewer_note': reviewer_note,
            'file_id': file_id,
            'actor': actor,
        })
        return {
            'id': submission_id,
            'review_status': 'under-review',
            'spatial_evidence': {
                'evidence_review_status': 'accepted',
                'evidence_attachments': [{'files': [{'file_id': file_id, 'review_status': decision}]}],
            },
        }

    monkeypatch.setattr(main, 'review_field_submission_evidence', fake_review)
    response = client.post(
        '/api/v1/field/submissions/submission-a/evidence-review',
        json={'attachment_index': 0, 'file_id': 'evidence-1', 'decision': 'accepted', 'reviewer_note': 'frontage confirmed'},
        headers=auth_header(),
    )
    assert response.status_code == 200
    assert response.json()['spatial_evidence']['evidence_review_status'] == 'accepted'
    assert captured['file_id'] == 'evidence-1'
    assert captured['actor']['username'] == 'editor'


def test_evidence_history_requires_auth_and_returns_audit_entries(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    captured: dict[str, Any] = {}

    def fake_history(submission_id, limit=50):
        captured.update({'submission_id': submission_id, 'limit': limit})
        return [{'id': 1, 'action': 'download-evidence-file', 'entity_id': submission_id, 'details': {'file_id': 'evidence-1'}}]

    monkeypatch.setattr(main, 'list_field_submission_evidence_history', fake_history)
    unauth = client.get('/api/v1/field/submissions/submission-a/evidence-history')
    assert unauth.status_code == 401
    response = client.get('/api/v1/field/submissions/submission-a/evidence-history?limit=7', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['items'][0]['action'] == 'download-evidence-file'
    assert captured == {'submission_id': 'submission-a', 'limit': 7}


def test_field_evidence_review_status_blocks_unaccepted_files() -> None:
    pending = {'evidence_attachments': [{'files': [{'file_id': 'evidence-1'}]}]}
    accepted = {'evidence_attachments': [{'files': [{'file_id': 'evidence-1', 'review_status': 'accepted'}]}]}
    recapture = {'evidence_attachments': [{'files': [{'file_id': 'evidence-1', 'review_status': 'needs-recapture'}]}]}
    assert db._field_evidence_review_status(pending) == 'pending'
    assert db._field_evidence_review_status(accepted) == 'accepted'
    assert db._field_evidence_review_status(recapture) == 'blocked'
    assert db._field_evidence_approval_ready(pending) is False
    assert db._field_evidence_approval_ready(accepted) is True

def test_cookie_mode_login_sets_cookies_without_exposing_bearer_token(monkeypatch) -> None:
    monkeypatch.setattr(main, 'SESSION_COOKIE_MODE', 'secure-http-only-cookie')
    monkeypatch.setattr(main, 'SESSION_COOKIE_SECURE', False)
    monkeypatch.setattr(main, 'authenticate_user_session', lambda username, password: {'token': 'cookie-only-token', 'expires_at': '2026-07-09T00:00:00+00:00', 'user': ADMIN})

    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})

    assert response.status_code == 200
    payload = response.json()
    assert payload['auth_mode'] == 'cookie_session'
    assert 'token' not in payload
    assert 'csrf_token' not in payload
    set_cookie = response.headers.get('set-cookie', '')
    assert main.SESSION_COOKIE_NAME in set_cookie
    assert main.CSRF_COOKIE_NAME in set_cookie
    assert 'HttpOnly' in set_cookie


def test_auth_me_reports_auth_mode_for_cookie_session(monkeypatch) -> None:
    monkeypatch.setattr(main, 'SESSION_COOKIE_MODE', 'secure-http-only-cookie')
    monkeypatch.setattr(main, 'SESSION_COOKIE_SECURE', False)
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: ADMIN)

    response = client.get('/api/v1/auth/me', cookies={main.SESSION_COOKIE_NAME: 'cookie-only-token'})

    assert response.status_code == 200
    assert response.json()['auth_mode'] == 'cookie_session'
    assert response.json()['user']['role'] == 'admin'


def test_default_demo_password_policy_can_reject_seeded_passwords(monkeypatch) -> None:
    monkeypatch.setattr(db, 'ALLOW_DEFAULT_DEMO_PASSWORDS', False, raising=False)

    assert db.default_demo_password_rejected('admin', 'admin123') is True
    assert db.default_demo_password_rejected('admin', 'not-the-default') is False
    assert db.default_demo_password_rejected('unknown', 'admin123') is False


def test_user_seed_preserves_existing_password_hash_and_active_state() -> None:
    source = Path(db.__file__).read_text()
    seed_section = source[source.index('for user in DEMO_USERS:'):source.index('for territory in TERRITORIES:')]

    assert 'password_hash = users.password_hash' in seed_section
    assert 'is_active = users.is_active' in seed_section
    assert 'password_hash = EXCLUDED.password_hash' not in seed_section
    assert 'is_active = TRUE' not in seed_section


def test_admin_smoke_uses_environment_supplied_credentials() -> None:
    source = Path('/home/ubuntu/projects/eg-addressing/apps/admin-portal/scripts/admin-flow-smoke.mjs').read_text()

    assert 'SMOKE_ADMIN_USERNAME' in source
    assert 'SMOKE_ADMIN_PASSWORD' in source
    assert "password: 'admin123'" not in source
    assert "username: 'admin'" not in source


def test_production_readiness_reports_strict_phase3_auth_ready(monkeypatch) -> None:
    monkeypatch.setenv('SESSION_COOKIE_MODE', 'secure-http-only-cookie')
    monkeypatch.setenv('ALLOW_DEFAULT_DEMO_PASSWORDS', 'false')

    body = production_readiness_status()

    assert body['checks']['secure_cookie_sessions']['status'] == 'ready'
    assert body['checks']['default_demo_passwords_disabled']['status'] == 'ready'


def test_production_readiness_blocks_staging_label_in_production(monkeypatch) -> None:
    monkeypatch.setenv('APP_ENV', 'production')
    monkeypatch.setenv('NEXT_PUBLIC_DEPLOYMENT_LABEL', 'STAGING / NOT OFFICIAL PRODUCTION RECORD')

    body = production_readiness_status()

    assert body['checks']['deployment_identity']['status'] == 'needs_work'
    assert body['status'] == 'needs_work'


def test_publish_geotag_submission_requires_admin(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    response = client.post('/api/v1/geotag-submissions/geo-ready/publish', json={'reviewer_note': 'Approved by institutional release authority.'}, headers=auth_header())
    assert response.status_code == 403


def test_publish_geotag_submission_requires_release_gate(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: ADMIN)
    monkeypatch.setattr(main, 'PUBLICATION_RELEASE_ENABLED', False)

    response = client.post('/api/v1/geotag-submissions/geo-ready/publish', json={'reviewer_note': 'Approved by institutional release authority.'}, headers=auth_header())

    assert response.status_code == 403
    assert response.json()['detail'] == 'publication release gate is disabled'


def test_admin_can_publish_registry_ready_geotag_and_gets_public_record(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: ADMIN)
    monkeypatch.setattr(main, 'PUBLICATION_RELEASE_ENABLED', True)
    captured = {}

    def fake_publish(submission_id, reviewer_note, actor=None):
        captured.update({'submission_id': submission_id, 'reviewer_note': reviewer_note, 'actor': actor})
        return {
            'id': submission_id,
            'status': 'published',
            'signage_batch': 'publication-batch-20260710',
            'grid_code': 'EG-BN-N1-PUB000001-AA',
            'address_record': {
                'address_code': 'EG-BN-N1-PUB000001-AA',
                'status': 'published',
                'publication_state': 'published',
            },
            'publication': {
                'public_release': 'published',
                'signage_export_status': 'ready-for-export',
                'certificate_status': 'ready',
            },
        }

    monkeypatch.setattr(main, 'publish_geotag_submission', fake_publish)
    response = client.post('/api/v1/geotag-submissions/geo-ready/publish', json={'reviewer_note': 'Approved by institutional release authority.'}, headers=auth_header())

    assert response.status_code == 200
    body = response.json()
    assert captured['submission_id'] == 'geo-ready'
    assert captured['actor']['role'] == 'admin'
    assert body['status'] == 'published'
    assert body['address_record']['publication_state'] == 'published'
    assert body['publication']['certificate_status'] == 'ready'


def test_publication_ui_has_admin_publish_action_separate_from_simulation() -> None:
    source = Path('/home/ubuntu/projects/eg-addressing/apps/admin-portal/components/PublicationOperationsPanel.tsx').read_text()

    assert '/api/v1/geotag-submissions/${encodeURIComponent(publishSubmissionId)}/publish' in source
    assert 'Publish registry-ready case file' in source
    assert 'Admin required' in source
    assert 'simulation only' in source.lower()
