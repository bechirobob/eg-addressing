from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main


def test_api_lifespan_does_not_call_init_db(monkeypatch) -> None:
    called = False

    def fail_init_db() -> None:
        nonlocal called
        called = True
        raise AssertionError('API startup must not mutate schema or seed data')

    monkeypatch.setattr(main, 'init_db', fail_init_db, raising=False)
    with TestClient(main.app) as client:
        response = client.get('/api/v1/health')

    assert response.status_code == 200
    assert called is False


def test_migration_runner_source_has_sda_controls() -> None:
    source = Path('../../infra/scripts/migrate.py').read_text(encoding='utf-8')
    assert 'pg_advisory_lock' in source
    assert 'checksum' in source
    assert 'execution_context' in source
    assert 'checksum-mismatch' in source
    assert 'transition-pilot' in source
    assert "row['filename'] != migration.filename" in source


def test_initial_schema_migration_precedes_legacy_marker_and_preserves_existing_checksums() -> None:
    migrations = sorted(Path('../../infra/migrations').glob('*.sql'))
    names = [path.name for path in migrations]
    assert names[0] == '000_current_operational_schema.sql'
    assert '001_schema_migration_baseline.sql' in names
    assert Path('../../infra/migrations/001_schema_migration_baseline.sql').read_text(encoding='utf-8') == (
        '-- Baseline marker for the current pilot schema.\n'
        '-- The schema was originally created by application bootstrap code; this migration\n'
        '-- establishes a durable migration ledger before future schema changes.\n'
        'SELECT 1;\n'
    )


def test_reference_and_fixture_lifecycle_files_exist_and_are_separated() -> None:
    assert Path('../../infra/reference-data/manifest.json').exists()
    assert Path('../../infra/reference-data/eg-admin-units-v1.json').exists()
    assert Path('../../infra/fixtures/development-fixtures-v1.json').exists()
    fixture_script = Path('../../infra/scripts/load_development_fixtures.py').read_text(encoding='utf-8')
    reference_script = Path('../../infra/scripts/load_reference_data.py').read_text(encoding='utf-8')
    assert 'APP_ENV' in fixture_script
    assert 'production' in fixture_script
    assert 'DEVELOPMENT_FIXTURE_PASSWORD' in fixture_script
    assert 'admin123' not in fixture_script
    assert 'CREATE TABLE' not in fixture_script
    assert 'CREATE TABLE' not in reference_script
    assert 'missing-migrations' in fixture_script
    assert 'missing-migrations' in reference_script


def test_schema_bridge_is_schema_only_and_data_backfill_is_isolated() -> None:
    bridge = Path('../../infra/migrations/000_current_operational_schema.sql').read_text(encoding='utf-8')
    hardening = Path('../../infra/migrations/007_lifecycle_metadata_hardening.sql').read_text(encoding='utf-8')
    assert 'UPDATE auth_tokens' not in bridge
    assert 'UPDATE auth_tokens' in hardening


def test_run_migrations_shell_delegates_to_controlled_runner() -> None:
    source = Path('../../infra/scripts/run_migrations.sh').read_text(encoding='utf-8')
    assert 'migrate.py' in source
    assert 'schema_migrations' not in source or 'Legacy compatibility wrapper' in source
