from fastapi.testclient import TestClient

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
    assert response.json() == {'status': 'ok', 'service': 'eg-addressing-api', 'version': '0.1.0'}


def test_meta_endpoint_returns_platform_identity() -> None:
    response = client.get('/api/v1/meta')
    assert response.status_code == 200
    payload = response.json()
    assert payload['platform']['name'] == 'Equatorial Guinea National Digital Addressing Platform'
    assert payload['platform']['mode'] == 'operational-readiness'
    assert 'publication' in payload['modules']
    assert 'admin' in payload['roles']


def test_login_returns_token_and_user(monkeypatch) -> None:
    monkeypatch.setattr(main, 'authenticate_user_session', lambda username, password: {'token': 'demo-token', 'user': ADMIN})
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    assert response.status_code == 200
    assert response.json()['user']['role'] == 'admin'


def test_auth_me_requires_token() -> None:
    response = client.get('/api/v1/auth/me')
    assert response.status_code == 401


def test_territories_endpoint_returns_database_rows(monkeypatch) -> None:
    expected = [{'id': 'territory-mongomo-core', 'name': 'Mongomo Core', 'province_code': 'WN', 'province': 'Wele-Nzas', 'type': 'district-core', 'readiness': 'enumeration-ready', 'is_archived': False}]
    monkeypatch.setattr(main, 'fetch_territories', lambda **kwargs: expected)
    response = client.get('/api/v1/territories')
    assert response.status_code == 200
    assert response.json()['items'] == expected


def test_create_territory_requires_editor_role(monkeypatch) -> None:
    payload = {'name': 'Mongomo Core', 'province_code': 'WN', 'type': 'district-core', 'readiness': 'enumeration-ready'}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    response = client.post('/api/v1/territories', json=payload, headers=auth_header())
    assert response.status_code == 403


def test_road_detail_returns_record(monkeypatch) -> None:
    monkeypatch.setattr(main, 'get_road', lambda road_id: {'id': road_id, 'name': 'Avenida', 'territory_id': 'territory-bata', 'territory_name': 'Bata', 'status': 'verified', 'length_km': '2.1', 'is_archived': False})
    response = client.get('/api/v1/roads/road-a')
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


def test_field_assignments_returns_items(monkeypatch) -> None:
    monkeypatch.setattr(main, 'list_field_assignments', lambda: [{'assignment_id': 'field-001', 'territory_id': 'territory-bata', 'territory': 'Bata', 'task': 'Task', 'team': 'Team', 'priority': 'critical'}])
    response = client.get('/api/v1/field/assignments')
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
    monkeypatch.setattr(main, 'verify_address', lambda query: {'query': query, 'match_status': 'verified', 'address_label': 'Bata', 'jurisdiction': 'Bata · Litoral', 'verification_note': 'Published registry record found.'})
    response = client.get('/api/v1/verification/lookup', params={'query': 'Bata'})
    assert response.status_code == 200
    assert response.json()['match_status'] == 'verified'


def test_verification_lookup_handles_not_found(monkeypatch) -> None:
    monkeypatch.setattr(main, 'verify_address', lambda query: None)
    response = client.get('/api/v1/verification/lookup', params={'query': 'missing'})
    assert response.status_code == 200
    assert response.json()['match_status'] == 'not-found'


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


def test_publication_pack_create_returns_pack(monkeypatch) -> None:
    payload = {'name': 'Published Bata Pack', 'audience': 'Cabinet', 'status': 'draft', 'address_ids': ['addr-1']}
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    monkeypatch.setattr(main, 'create_publication_pack', lambda payload, actor=None: {'id': 'publication-pack', 'name': payload['name'], 'status': payload['status'], 'audience': payload['audience'], 'address_count': 1})
    response = client.post('/api/v1/publication/packs', json=payload, headers=auth_header())
    assert response.status_code == 201
    assert response.json()['address_count'] == 1


def test_publish_publication_pack_requires_admin(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: EDITOR)
    response = client.post('/api/v1/publication/packs/pack-1/publish', headers=auth_header())
    assert response.status_code == 403


def test_reporting_summary_returns_totals(monkeypatch) -> None:
    monkeypatch.setattr(main, 'resolve_user_from_token', lambda token: VIEWER)
    monkeypatch.setattr(main, 'reporting_summary', lambda: {'totals': {'territories': 3, 'submissions': 2, 'review_queue': 1, 'published_addresses': 1, 'import_jobs': 1}, 'territories_by_province': [], 'review_breakdown': [], 'publication_breakdown': []})
    response = client.get('/api/v1/reporting/summary', headers=auth_header())
    assert response.status_code == 200
    assert response.json()['totals']['review_queue'] == 1


def test_cors_preflight_allows_admin_origin() -> None:
    response = client.options('/api/v1/territories', headers={'Origin': 'http://localhost:3100', 'Access-Control-Request-Method': 'POST'})
    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == 'http://localhost:3100'
