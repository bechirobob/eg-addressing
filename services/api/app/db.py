from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row

from app.data import (
    ADDRESSES,
    BUILDINGS,
    DEMO_USERS,
    FIELD_ASSIGNMENTS,
    FIELD_SUBMISSIONS,
    IMPORT_JOBS,
    IMPORT_ROWS,
    PROVINCES,
    PUBLICATION_PACKS,
    ROADS,
    TERRITORIES,
)

PASSWORD_SALT = 'eg-addressing-demo-salt'


class UnknownProvinceError(ValueError):
    pass


class DuplicateTerritoryError(ValueError):
    pass


class TerritoryNotFoundError(ValueError):
    pass


class UnknownTerritoryError(ValueError):
    pass


class DuplicateRoadError(ValueError):
    pass


class RoadNotFoundError(ValueError):
    pass


class UnknownRoadError(ValueError):
    pass


class DuplicateBuildingError(ValueError):
    pass


class BuildingNotFoundError(ValueError):
    pass


class UnknownBuildingError(ValueError):
    pass


class DuplicateAddressError(ValueError):
    pass


class AddressNotFoundError(ValueError):
    pass


class AuthenticationError(ValueError):
    pass


class ImportJobNotFoundError(ValueError):
    pass


class SubmissionNotFoundError(ValueError):
    pass


class InvalidSubmissionActionError(ValueError):
    pass


class PublicationPackNotFoundError(ValueError):
    pass


def _normalize_database_url(url: str) -> str:
    return url.replace('postgresql+psycopg://', 'postgresql://', 1)


def get_database_url() -> str | None:
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return _normalize_database_url(database_url)

    host = os.getenv('POSTGRES_HOST')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    database = os.getenv('POSTGRES_DB')
    port = os.getenv('POSTGRES_PORT', '5432')

    if not all([host, user, password, database]):
        return None

    return f'postgresql://{user}:{password}@{host}:{port}/{database}'


@contextmanager
def db_connection() -> Iterator[psycopg.Connection]:
    database_url = get_database_url()
    if not database_url:
        raise RuntimeError('DATABASE_URL is not configured')
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        yield connection


def _hash_password(password: str) -> str:
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), PASSWORD_SALT.encode('utf-8'), 120000)
    return digest.hex()


def _slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r'[^a-z0-9]+', '-', lowered)
    lowered = re.sub(r'-+', '-', lowered).strip('-')
    return lowered


def _log_action(
    cursor: psycopg.Cursor,
    *,
    actor: dict[str, str] | None,
    action: str,
    entity_type: str,
    entity_id: str,
    details: dict[str, Any] | None = None,
) -> None:
    cursor.execute(
        '''
        INSERT INTO audit_logs (actor_user_id, actor_username, actor_role, action, entity_type, entity_id, details)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''',
        (
            actor['id'] if actor else None,
            actor['username'] if actor else None,
            actor['role'] if actor else None,
            action,
            entity_type,
            entity_id,
            json.dumps(details or {}),
        ),
    )


def _ensure_schema(cursor: psycopg.Cursor) -> None:
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS provinces (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS auth_tokens (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id BIGSERIAL PRIMARY KEY,
            actor_user_id TEXT,
            actor_username TEXT,
            actor_role TEXT,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '{}',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS territories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            province_code TEXT NOT NULL REFERENCES provinces(code),
            type TEXT NOT NULL,
            readiness TEXT NOT NULL,
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE territories ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE")
    cursor.execute("ALTER TABLE territories ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS roads (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            territory_id TEXT NOT NULL REFERENCES territories(id),
            status TEXT NOT NULL,
            length_km TEXT NOT NULL,
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE roads ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE")
    cursor.execute("ALTER TABLE roads ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS buildings (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL UNIQUE,
            territory_id TEXT NOT NULL REFERENCES territories(id),
            road_id TEXT NOT NULL REFERENCES roads(id),
            status TEXT NOT NULL,
            usage TEXT NOT NULL,
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE buildings ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE")
    cursor.execute("ALTER TABLE buildings ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS addresses (
            id TEXT PRIMARY KEY,
            formatted TEXT NOT NULL UNIQUE,
            territory_id TEXT NOT NULL REFERENCES territories(id),
            road_id TEXT NOT NULL REFERENCES roads(id),
            building_id TEXT NOT NULL REFERENCES buildings(id),
            province_code TEXT NOT NULL REFERENCES provinces(code),
            status TEXT NOT NULL,
            publication_state TEXT NOT NULL DEFAULT 'draft',
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE addresses ADD COLUMN IF NOT EXISTS publication_state TEXT NOT NULL DEFAULT 'draft'")
    cursor.execute("ALTER TABLE addresses ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE")
    cursor.execute("ALTER TABLE addresses ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS field_assignments (
            assignment_id TEXT PRIMARY KEY,
            territory_id TEXT NOT NULL REFERENCES territories(id),
            territory TEXT NOT NULL,
            task TEXT NOT NULL,
            team TEXT NOT NULL,
            priority TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS field_submissions (
            id TEXT PRIMARY KEY,
            assignment_id TEXT REFERENCES field_assignments(assignment_id),
            territory_id TEXT NOT NULL REFERENCES territories(id),
            submission_type TEXT NOT NULL,
            candidate_name TEXT NOT NULL,
            candidate_status TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            submitted_by TEXT NOT NULL,
            review_status TEXT NOT NULL DEFAULT 'submitted',
            reviewer_note TEXT NOT NULL DEFAULT '',
            registry_entity_id TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE field_submissions ADD COLUMN IF NOT EXISTS reviewer_note TEXT NOT NULL DEFAULT ''")
    cursor.execute("ALTER TABLE field_submissions ADD COLUMN IF NOT EXISTS registry_entity_id TEXT")
    cursor.execute("ALTER TABLE field_submissions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS import_jobs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            imported_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE import_jobs ADD COLUMN IF NOT EXISTS imported_count INTEGER NOT NULL DEFAULT 0")
    cursor.execute("ALTER TABLE import_jobs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS import_rows (
            job_id TEXT NOT NULL REFERENCES import_jobs(id) ON DELETE CASCADE,
            row_number INTEGER NOT NULL,
            submission_type TEXT NOT NULL,
            territory_id TEXT NOT NULL REFERENCES territories(id),
            candidate_name TEXT NOT NULL,
            candidate_status TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            validation_status TEXT NOT NULL,
            validation_message TEXT NOT NULL,
            committed_submission_id TEXT,
            PRIMARY KEY (job_id, row_number)
        )
        '''
    )
    cursor.execute("ALTER TABLE import_rows ADD COLUMN IF NOT EXISTS committed_submission_id TEXT")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS publication_packs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            audience TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE publication_packs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS publication_pack_addresses (
            publication_pack_id TEXT NOT NULL REFERENCES publication_packs(id) ON DELETE CASCADE,
            address_id TEXT NOT NULL REFERENCES addresses(id),
            PRIMARY KEY (publication_pack_id, address_id)
        )
        '''
    )


def init_db() -> None:
    database_url = get_database_url()
    if not database_url:
        return

    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            _ensure_schema(cursor)

            for province in PROVINCES:
                cursor.execute(
                    '''
                    INSERT INTO provinces (code, name)
                    VALUES (%s, %s)
                    ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
                    ''',
                    (province['code'], province['name']),
                )

            for user in DEMO_USERS:
                cursor.execute(
                    '''
                    INSERT INTO users (id, username, full_name, role, password_hash, is_active)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                    ON CONFLICT (id) DO UPDATE SET
                        username = EXCLUDED.username,
                        full_name = EXCLUDED.full_name,
                        role = EXCLUDED.role,
                        password_hash = EXCLUDED.password_hash,
                        is_active = TRUE
                    ''',
                    (user['id'], user['username'], user['full_name'], user['role'], _hash_password(user['password'])),
                )

            for territory in TERRITORIES:
                cursor.execute(
                    '''
                    INSERT INTO territories (id, name, province_code, type, readiness, is_archived)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        province_code = EXCLUDED.province_code,
                        type = EXCLUDED.type,
                        readiness = EXCLUDED.readiness,
                        is_archived = EXCLUDED.is_archived,
                        updated_at = NOW()
                    ''',
                    (
                        territory['id'],
                        territory['name'],
                        territory['province_code'],
                        territory['type'],
                        territory['readiness'],
                        territory['is_archived'],
                    ),
                )

            for road in ROADS:
                cursor.execute(
                    '''
                    INSERT INTO roads (id, name, territory_id, status, length_km, is_archived)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        territory_id = EXCLUDED.territory_id,
                        status = EXCLUDED.status,
                        length_km = EXCLUDED.length_km,
                        is_archived = EXCLUDED.is_archived,
                        updated_at = NOW()
                    ''',
                    (road['id'], road['name'], road['territory_id'], road['status'], road['length_km'], road.get('is_archived', False)),
                )

            for building in BUILDINGS:
                cursor.execute(
                    '''
                    INSERT INTO buildings (id, label, territory_id, road_id, status, usage, is_archived)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        label = EXCLUDED.label,
                        territory_id = EXCLUDED.territory_id,
                        road_id = EXCLUDED.road_id,
                        status = EXCLUDED.status,
                        usage = EXCLUDED.usage,
                        is_archived = EXCLUDED.is_archived,
                        updated_at = NOW()
                    ''',
                    (
                        building['id'],
                        building['label'],
                        building['territory_id'],
                        building['road_id'],
                        building['status'],
                        building['usage'],
                        building.get('is_archived', False),
                    ),
                )

            for address in ADDRESSES:
                cursor.execute(
                    '''
                    INSERT INTO addresses (id, formatted, territory_id, road_id, building_id, province_code, status, publication_state, is_archived)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        formatted = EXCLUDED.formatted,
                        territory_id = EXCLUDED.territory_id,
                        road_id = EXCLUDED.road_id,
                        building_id = EXCLUDED.building_id,
                        province_code = EXCLUDED.province_code,
                        status = EXCLUDED.status,
                        publication_state = EXCLUDED.publication_state,
                        is_archived = EXCLUDED.is_archived,
                        updated_at = NOW()
                    ''',
                    (
                        address['id'],
                        address['formatted'],
                        address['territory_id'],
                        address['road_id'],
                        address['building_id'],
                        address['province_code'],
                        address['status'],
                        address.get('publication_state', 'draft'),
                        address.get('is_archived', False),
                    ),
                )

            for assignment in FIELD_ASSIGNMENTS:
                cursor.execute(
                    '''
                    INSERT INTO field_assignments (assignment_id, territory_id, territory, task, team, priority)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (assignment_id) DO UPDATE SET
                        territory_id = EXCLUDED.territory_id,
                        territory = EXCLUDED.territory,
                        task = EXCLUDED.task,
                        team = EXCLUDED.team,
                        priority = EXCLUDED.priority
                    ''',
                    (
                        assignment['assignment_id'],
                        assignment['territory_id'],
                        assignment['territory'],
                        assignment['task'],
                        assignment['team'],
                        assignment['priority'],
                    ),
                )

            for submissions in FIELD_SUBMISSIONS:
                cursor.execute(
                    '''
                    INSERT INTO field_submissions (
                        id, assignment_id, territory_id, submission_type, candidate_name,
                        candidate_status, notes, submitted_by, review_status, registry_entity_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        assignment_id = EXCLUDED.assignment_id,
                        territory_id = EXCLUDED.territory_id,
                        submission_type = EXCLUDED.submission_type,
                        candidate_name = EXCLUDED.candidate_name,
                        candidate_status = EXCLUDED.candidate_status,
                        notes = EXCLUDED.notes,
                        submitted_by = EXCLUDED.submitted_by,
                        review_status = EXCLUDED.review_status,
                        registry_entity_id = COALESCE(field_submissions.registry_entity_id, EXCLUDED.registry_entity_id),
                        updated_at = NOW()
                    ''',
                    (
                        submission['id'],
                        submission['assignment_id'],
                        submission['territory_id'],
                        submission['submission_type'],
                        submission['candidate_name'],
                        submission['candidate_status'],
                        submission['notes'],
                        submission['submitted_by'],
                        submission['review_status'],
                        submission.get('registry_entity_id'),
                    ),
                )

            for job in IMPORT_JOBS:
                cursor.execute(
                    '''
                    INSERT INTO import_jobs (id, name, source_name, status)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        source_name = EXCLUDED.source_name,
                        status = EXCLUDED.status,
                        updated_at = NOW()
                    ''',
                    (job['id'], job['name'], job['source_name'], job['status']),
                )

            for row in IMPORT_ROWS:
                cursor.execute(
                    '''
                    INSERT INTO import_rows (
                        job_id, row_number, submission_type, territory_id, candidate_name,
                        candidate_status, notes, validation_status, validation_message
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_id, row_number) DO UPDATE SET
                        submission_type = EXCLUDED.submission_type,
                        territory_id = EXCLUDED.territory_id,
                        candidate_name = EXCLUDED.candidate_name,
                        candidate_status = EXCLUDED.candidate_status,
                        notes = EXCLUDED.notes,
                        validation_status = EXCLUDED.validation_status,
                        validation_message = EXCLUDED.validation_message
                    ''',
                    (
                        row['job_id'],
                        row['row_number'],
                        row['submission_type'],
                        row['territory_id'],
                        row['candidate_name'],
                        row['candidate_status'],
                        row['notes'],
                        row['validation_status'],
                        row['validation_message'],
                    ),
                )

            for pack in PUBLICATION_PACKS:
                cursor.execute(
                    '''
                    INSERT INTO publication_packs (id, name, status, audience)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        status = EXCLUDED.status,
                        audience = EXCLUDED.audience,
                        updated_at = NOW()
                    ''',
                    (pack['id'], pack['name'], pack['status'], pack['audience']),
                )
                for address_id in pack.get('address_ids', []):
                    cursor.execute(
                        '''
                        INSERT INTO publication_pack_addresses (publication_pack_id, address_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                        ''',
                        (pack['id'], address_id),
                    )
        connection.commit()


def authenticate_user_session(username: str, password: str) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT id, username, full_name, role, password_hash, is_active FROM users WHERE username = %s',
                (username,),
            )
            user = cursor.fetchone()
            if not user or not user['is_active']:
                raise AuthenticationError('invalid credentials')
            if user['password_hash'] != _hash_password(password):
                raise AuthenticationError('invalid credentials')

            token = secrets.token_urlsafe(24)
            cursor.execute('INSERT INTO auth_tokens (token, user_id) VALUES (%s, %s)', (token, user['id']))
            _log_action(cursor, actor=user, action='login', entity_type='session', entity_id=token, details={'username': username})
        connection.commit()

    return {
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'full_name': user['full_name'],
            'role': user['role'],
        },
    }


def resolve_user_from_token(token: str) -> dict[str, str]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT u.id, u.username, u.full_name, u.role
                FROM auth_tokens t
                JOIN users u ON u.id = t.user_id
                WHERE t.token = %s AND u.is_active = TRUE
                ''',
                (token,),
            )
            user = cursor.fetchone()
            if not user:
                raise AuthenticationError('invalid token')
            return {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role'],
            }


def _territory_projection() -> str:
    return '''
        SELECT t.id, t.name, t.province_code, p.name AS province, t.type, t.readiness, t.is_archived
        FROM territories t
        JOIN provinces p ON p.code = t.province_code
    '''


def fetch_territories(*, q: str | None = None, province_code: str | None = None, readiness: str | None = None, include_archived: bool = False) -> list[dict[str, Any]]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if q:
        like = f'%{q.lower()}%'
        where_clauses.append('(LOWER(t.name) LIKE %s OR LOWER(p.name) LIKE %s OR LOWER(t.type) LIKE %s OR LOWER(t.readiness) LIKE %s)')
        params.extend([like, like, like, like])
    if province_code:
        where_clauses.append('t.province_code = %s')
        params.append(province_code)
    if readiness:
        where_clauses.append('t.readiness = %s')
        params.append(readiness)
    if not include_archived:
        where_clauses.append('t.is_archived = FALSE')
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(_territory_projection() + where_sql + ' ORDER BY t.name ASC', params)
            return list(cursor.fetchall())


def get_territory(territory_id: str) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(_territory_projection() + ' WHERE t.id = %s', (territory_id,))
            territory = cursor.fetchone()
            if not territory:
                raise TerritoryNotFoundError('territory not found')
            return dict(territory)


def create_territory(payload: dict[str, str], actor: dict[str, str] | None = None) -> dict[str, Any]:
    territory_id = f"territory-{_slugify(payload['name'])}"
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT name FROM provinces WHERE code = %s', (payload['province_code'],))
            province = cursor.fetchone()
            if not province:
                raise UnknownProvinceError(f"Unknown province code: {payload['province_code']}")
            cursor.execute('SELECT 1 FROM territories WHERE LOWER(name) = LOWER(%s)', (payload['name'],))
            if cursor.fetchone():
                raise DuplicateTerritoryError('duplicate territory')
            cursor.execute(
                '''
                INSERT INTO territories (id, name, province_code, type, readiness, is_archived)
                VALUES (%s, %s, %s, %s, %s, FALSE)
                RETURNING id, name, province_code, type, readiness, is_archived
                ''',
                (territory_id, payload['name'], payload['province_code'], payload['type'], payload['readiness']),
            )
            created = cursor.fetchone()
            _log_action(cursor, actor=actor, action='create', entity_type='territory', entity_id=territory_id, details=payload)
        connection.commit()
    return {**created, 'province': province['name']}


def update_territory(territory_id: str, payload: dict[str, str], actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT name FROM provinces WHERE code = %s', (payload['province_code'],))
            province = cursor.fetchone()
            if not province:
                raise UnknownProvinceError(f"Unknown province code: {payload['province_code']}")
            cursor.execute('SELECT id FROM territories WHERE id = %s', (territory_id,))
            if not cursor.fetchone():
                raise TerritoryNotFoundError('territory not found')
            cursor.execute('SELECT id FROM territories WHERE LOWER(name) = LOWER(%s) AND id <> %s', (payload['name'], territory_id))
            if cursor.fetchone():
                raise DuplicateTerritoryError('duplicate territory')
            cursor.execute(
                '''
                UPDATE territories
                SET name = %s, province_code = %s, type = %s, readiness = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING id, name, province_code, type, readiness, is_archived
                ''',
                (payload['name'], payload['province_code'], payload['type'], payload['readiness'], territory_id),
            )
            updated = cursor.fetchone()
            _log_action(cursor, actor=actor, action='update', entity_type='territory', entity_id=territory_id, details=payload)
        connection.commit()
    return {**updated, 'province': province['name']}


def archive_territory(territory_id: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE territories SET is_archived = TRUE, updated_at = NOW() WHERE id = %s RETURNING id', (territory_id,))
            updated = cursor.fetchone()
            if not updated:
                raise TerritoryNotFoundError('territory not found')
            _log_action(cursor, actor=actor, action='archive', entity_type='territory', entity_id=territory_id)
        connection.commit()
    return get_territory(territory_id)


def list_audit_logs(entity_type: str | None = None, entity_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if entity_type:
        where_clauses.append('entity_type = %s')
        params.append(entity_type)
    if entity_id:
        where_clauses.append('entity_id = %s')
        params.append(entity_id)
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT id, actor_username, actor_role, action, entity_type, entity_id, details, created_at FROM audit_logs' + where_sql + ' ORDER BY created_at DESC LIMIT %s',
                [*params, limit],
            )
            return list(cursor.fetchall())


def _entity_exists(cursor: psycopg.Cursor, table: str, entity_id: str) -> bool:
    cursor.execute(f'SELECT 1 FROM {table} WHERE id = %s', (entity_id,))
    return cursor.fetchone() is not None


def fetch_roads(q: str | None = None, territory_id: str | None = None, include_archived: bool = False) -> list[dict[str, Any]]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if q:
        like = f'%{q.lower()}%'
        where_clauses.append('(LOWER(r.name) LIKE %s OR LOWER(r.status) LIKE %s OR LOWER(t.name) LIKE %s)')
        params.extend([like, like, like])
    if territory_id:
        where_clauses.append('r.territory_id = %s')
        params.append(territory_id)
    if not include_archived:
        where_clauses.append('r.is_archived = FALSE')
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT r.id, r.name, r.territory_id, t.name AS territory_name, r.status, r.length_km, r.is_archived
                FROM roads r
                JOIN territories t ON t.id = r.territory_id
                ''' + where_sql + ' ORDER BY r.name ASC',
                params,
            )
            return list(cursor.fetchall())


def get_road(road_id: str) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT r.id, r.name, r.territory_id, t.name AS territory_name, r.status, r.length_km, r.is_archived
                FROM roads r JOIN territories t ON t.id = r.territory_id WHERE r.id = %s
                ''',
                (road_id,),
            )
            road = cursor.fetchone()
            if not road:
                raise RoadNotFoundError('road not found')
            return dict(road)


def create_road(payload: dict[str, str], actor: dict[str, str] | None = None) -> dict[str, Any]:
    road_id = f"road-{_slugify(payload['name'])}"
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT name FROM territories WHERE id = %s', (payload['territory_id'],))
            territory = cursor.fetchone()
            if not territory:
                raise UnknownTerritoryError('unknown territory')
            cursor.execute('SELECT 1 FROM roads WHERE LOWER(name) = LOWER(%s)', (payload['name'],))
            if cursor.fetchone():
                raise DuplicateRoadError('duplicate road')
            cursor.execute(
                '''
                INSERT INTO roads (id, name, territory_id, status, length_km, is_archived)
                VALUES (%s, %s, %s, %s, %s, FALSE)
                RETURNING id, name, territory_id, status, length_km, is_archived
                ''',
                (road_id, payload['name'], payload['territory_id'], payload['status'], payload['length_km']),
            )
            created = cursor.fetchone()
            _log_action(cursor, actor=actor, action='create', entity_type='road', entity_id=road_id, details=payload)
        connection.commit()
    return {**created, 'territory_name': territory['name']}


def update_road(road_id: str, payload: dict[str, str], actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT name FROM territories WHERE id = %s', (payload['territory_id'],))
            territory = cursor.fetchone()
            if not territory:
                raise UnknownTerritoryError('unknown territory')
            cursor.execute('SELECT id FROM roads WHERE id = %s', (road_id,))
            if not cursor.fetchone():
                raise RoadNotFoundError('road not found')
            cursor.execute('SELECT id FROM roads WHERE LOWER(name) = LOWER(%s) AND id <> %s', (payload['name'], road_id))
            if cursor.fetchone():
                raise DuplicateRoadError('duplicate road')
            cursor.execute(
                '''
                UPDATE roads SET name = %s, territory_id = %s, status = %s, length_km = %s, updated_at = NOW()
                WHERE id = %s RETURNING id, name, territory_id, status, length_km, is_archived
                ''',
                (payload['name'], payload['territory_id'], payload['status'], payload['length_km'], road_id),
            )
            updated = cursor.fetchone()
            _log_action(cursor, actor=actor, action='update', entity_type='road', entity_id=road_id, details=payload)
        connection.commit()
    return {**updated, 'territory_name': territory['name']}


def archive_road(road_id: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE roads SET is_archived = TRUE, updated_at = NOW() WHERE id = %s RETURNING id', (road_id,))
            if not cursor.fetchone():
                raise RoadNotFoundError('road not found')
            _log_action(cursor, actor=actor, action='archive', entity_type='road', entity_id=road_id)
        connection.commit()
    return get_road(road_id)


def fetch_buildings(q: str | None = None, territory_id: str | None = None, include_archived: bool = False) -> list[dict[str, Any]]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if q:
        like = f'%{q.lower()}%'
        where_clauses.append('(LOWER(b.label) LIKE %s OR LOWER(b.status) LIKE %s OR LOWER(b.usage) LIKE %s OR LOWER(r.name) LIKE %s)')
        params.extend([like, like, like, like])
    if territory_id:
        where_clauses.append('b.territory_id = %s')
        params.append(territory_id)
    if not include_archived:
        where_clauses.append('b.is_archived = FALSE')
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT b.id, b.label, b.territory_id, t.name AS territory_name, b.road_id, r.name AS road_name, b.status, b.usage, b.is_archived
                FROM buildings b
                JOIN territories t ON t.id = b.territory_id
                JOIN roads r ON r.id = b.road_id
                ''' + where_sql + ' ORDER BY b.label ASC',
                params,
            )
            return list(cursor.fetchall())


def get_building(building_id: str) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT b.id, b.label, b.territory_id, t.name AS territory_name, b.road_id, r.name AS road_name, b.status, b.usage, b.is_archived
                FROM buildings b
                JOIN territories t ON t.id = b.territory_id
                JOIN roads r ON r.id = b.road_id
                WHERE b.id = %s
                ''',
                (building_id,),
            )
            building = cursor.fetchone()
            if not building:
                raise BuildingNotFoundError('building not found')
            return dict(building)


def create_building(payload: dict[str, str], actor: dict[str, str] | None = None) -> dict[str, Any]:
    building_id = f"building-{_slugify(payload['label'])}"
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT name FROM territories WHERE id = %s', (payload['territory_id'],))
            territory = cursor.fetchone()
            if not territory:
                raise UnknownTerritoryError('unknown territory')
            cursor.execute('SELECT name, territory_id FROM roads WHERE id = %s', (payload['road_id'],))
            road = cursor.fetchone()
            if not road:
                raise UnknownRoadError('unknown road')
            if road['territory_id'] != payload['territory_id']:
                raise UnknownRoadError('road does not belong to selected territory')
            cursor.execute('SELECT 1 FROM buildings WHERE LOWER(label) = LOWER(%s)', (payload['label'],))
            if cursor.fetchone():
                raise DuplicateBuildingError('duplicate building')
            cursor.execute(
                '''
                INSERT INTO buildings (id, label, territory_id, road_id, status, usage, is_archived)
                VALUES (%s, %s, %s, %s, %s, %s, FALSE)
                RETURNING id, label, territory_id, road_id, status, usage, is_archived
                ''',
                (building_id, payload['label'], payload['territory_id'], payload['road_id'], payload['status'], payload['usage']),
            )
            created = cursor.fetchone()
            _log_action(cursor, actor=actor, action='create', entity_type='building', entity_id=building_id, details=payload)
        connection.commit()
    return {**created, 'territory_name': territory['name'], 'road_name': road['name']}


def update_building(building_id: str, payload: dict[str, str], actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT name FROM territories WHERE id = %s', (payload['territory_id'],))
            territory = cursor.fetchone()
            if not territory:
                raise UnknownTerritoryError('unknown territory')
            cursor.execute('SELECT name, territory_id FROM roads WHERE id = %s', (payload['road_id'],))
            road = cursor.fetchone()
            if not road:
                raise UnknownRoadError('unknown road')
            if road['territory_id'] != payload['territory_id']:
                raise UnknownRoadError('road does not belong to selected territory')
            cursor.execute('SELECT id FROM buildings WHERE id = %s', (building_id,))
            if not cursor.fetchone():
                raise BuildingNotFoundError('building not found')
            cursor.execute('SELECT id FROM buildings WHERE LOWER(label) = LOWER(%s) AND id <> %s', (payload['label'], building_id))
            if cursor.fetchone():
                raise DuplicateBuildingError('duplicate building')
            cursor.execute(
                '''
                UPDATE buildings SET label = %s, territory_id = %s, road_id = %s, status = %s, usage = %s, updated_at = NOW()
                WHERE id = %s RETURNING id, label, territory_id, road_id, status, usage, is_archived
                ''',
                (payload['label'], payload['territory_id'], payload['road_id'], payload['status'], payload['usage'], building_id),
            )
            updated = cursor.fetchone()
            _log_action(cursor, actor=actor, action='update', entity_type='building', entity_id=building_id, details=payload)
        connection.commit()
    return {**updated, 'territory_name': territory['name'], 'road_name': road['name']}


def archive_building(building_id: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE buildings SET is_archived = TRUE, updated_at = NOW() WHERE id = %s RETURNING id', (building_id,))
            if not cursor.fetchone():
                raise BuildingNotFoundError('building not found')
            _log_action(cursor, actor=actor, action='archive', entity_type='building', entity_id=building_id)
        connection.commit()
    return get_building(building_id)


def fetch_addresses(q: str | None = None, territory_id: str | None = None, status: str | None = None, include_archived: bool = False) -> list[dict[str, Any]]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if q:
        like = f'%{q.lower()}%'
        where_clauses.append('(LOWER(a.formatted) LIKE %s OR LOWER(a.status) LIKE %s OR LOWER(t.name) LIKE %s OR LOWER(b.label) LIKE %s)')
        params.extend([like, like, like, like])
    if territory_id:
        where_clauses.append('a.territory_id = %s')
        params.append(territory_id)
    if status:
        where_clauses.append('a.status = %s')
        params.append(status)
    if not include_archived:
        where_clauses.append('a.is_archived = FALSE')
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT a.id, a.formatted, a.territory_id, t.name AS territory_name, a.road_id, r.name AS road_name,
                       a.building_id, b.label AS building_label, a.province_code, a.status, a.publication_state, a.is_archived
                FROM addresses a
                JOIN territories t ON t.id = a.territory_id
                JOIN roads r ON r.id = a.road_id
                JOIN buildings b ON b.id = a.building_id
                ''' + where_sql + ' ORDER BY a.formatted ASC',
                params,
            )
            return list(cursor.fetchall())


def get_address(address_id: str) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT a.id, a.formatted, a.territory_id, t.name AS territory_name, a.road_id, r.name AS road_name,
                       a.building_id, b.label AS building_label, a.province_code, a.status, a.publication_state, a.is_archived
                FROM addresses a
                JOIN territories t ON t.id = a.territory_id
                JOIN roads r ON r.id = a.road_id
                JOIN buildings b ON b.id = a.building_id
                WHERE a.id = %s
                ''',
                (address_id,),
            )
            address = cursor.fetchone()
            if not address:
                raise AddressNotFoundError('address not found')
            return dict(address)


def create_address(payload: dict[str, str], actor: dict[str, str] | None = None) -> dict[str, Any]:
    address_id = f"addr-{_slugify(payload['formatted'])}"
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT name, province_code FROM territories WHERE id = %s', (payload['territory_id'],))
            territory = cursor.fetchone()
            if not territory:
                raise UnknownTerritoryError('unknown territory')
            cursor.execute('SELECT name, territory_id FROM roads WHERE id = %s', (payload['road_id'],))
            road = cursor.fetchone()
            if not road:
                raise UnknownRoadError('unknown road')
            cursor.execute('SELECT label, territory_id, road_id FROM buildings WHERE id = %s', (payload['building_id'],))
            building = cursor.fetchone()
            if not building:
                raise UnknownBuildingError('unknown building')
            if road['territory_id'] != payload['territory_id'] or building['territory_id'] != payload['territory_id'] or building['road_id'] != payload['road_id']:
                raise UnknownBuildingError('building or road does not belong to selected territory chain')
            cursor.execute('SELECT 1 FROM addresses WHERE LOWER(formatted) = LOWER(%s)', (payload['formatted'],))
            if cursor.fetchone():
                raise DuplicateAddressError('duplicate address')
            cursor.execute(
                '''
                INSERT INTO addresses (id, formatted, territory_id, road_id, building_id, province_code, status, publication_state, is_archived)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'draft', FALSE)
                RETURNING id, formatted, territory_id, road_id, building_id, province_code, status, publication_state, is_archived
                ''',
                (address_id, payload['formatted'], payload['territory_id'], payload['road_id'], payload['building_id'], territory['province_code'], payload['status']),
            )
            created = cursor.fetchone()
            _log_action(cursor, actor=actor, action='create', entity_type='address', entity_id=address_id, details=payload)
        connection.commit()
    return {**created, 'territory_name': territory['name'], 'road_name': road['name'], 'building_label': building['label']}


def update_address(address_id: str, payload: dict[str, str], actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT name, province_code FROM territories WHERE id = %s', (payload['territory_id'],))
            territory = cursor.fetchone()
            if not territory:
                raise UnknownTerritoryError('unknown territory')
            cursor.execute('SELECT name, territory_id FROM roads WHERE id = %s', (payload['road_id'],))
            road = cursor.fetchone()
            if not road:
                raise UnknownRoadError('unknown road')
            cursor.execute('SELECT label, territory_id, road_id FROM buildings WHERE id = %s', (payload['building_id'],))
            building = cursor.fetchone()
            if not building:
                raise UnknownBuildingError('unknown building')
            if road['territory_id'] != payload['territory_id'] or building['territory_id'] != payload['territory_id'] or building['road_id'] != payload['road_id']:
                raise UnknownBuildingError('building or road does not belong to selected territory chain')
            cursor.execute('SELECT id, publication_state FROM addresses WHERE id = %s', (address_id,))
            current = cursor.fetchone()
            if not current:
                raise AddressNotFoundError('address not found')
            cursor.execute('SELECT id FROM addresses WHERE LOWER(formatted) = LOWER(%s) AND id <> %s', (payload['formatted'], address_id))
            if cursor.fetchone():
                raise DuplicateAddressError('duplicate address')
            cursor.execute(
                '''
                UPDATE addresses
                SET formatted = %s, territory_id = %s, road_id = %s, building_id = %s, province_code = %s, status = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING id, formatted, territory_id, road_id, building_id, province_code, status, publication_state, is_archived
                ''',
                (payload['formatted'], payload['territory_id'], payload['road_id'], payload['building_id'], territory['province_code'], payload['status'], address_id),
            )
            updated = cursor.fetchone()
            _log_action(cursor, actor=actor, action='update', entity_type='address', entity_id=address_id, details=payload)
        connection.commit()
    return {**updated, 'territory_name': territory['name'], 'road_name': road['name'], 'building_label': building['label']}


def archive_address(address_id: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE addresses SET is_archived = TRUE, updated_at = NOW() WHERE id = %s RETURNING id', (address_id,))
            if not cursor.fetchone():
                raise AddressNotFoundError('address not found')
            _log_action(cursor, actor=actor, action='archive', entity_type='address', entity_id=address_id)
        connection.commit()
    return get_address(address_id)


def list_field_assignments() -> list[dict[str, Any]]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT assignment_id, territory_id, territory, task, team, priority FROM field_assignments ORDER BY priority DESC, territory ASC')
            return list(cursor.fetchall())


def list_field_submissions(review_status: str | None = None, territory_id: str | None = None) -> list[dict[str, Any]]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if review_status:
        where_clauses.append('s.review_status = %s')
        params.append(review_status)
    if territory_id:
        where_clauses.append('s.territory_id = %s')
        params.append(territory_id)
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT s.id, s.assignment_id, s.territory_id, t.name AS territory_name, s.submission_type, s.candidate_name,
                       s.candidate_status, s.notes, s.submitted_by, s.review_status, s.reviewer_note, s.registry_entity_id, s.created_at
                FROM field_submissions s
                JOIN territories t ON t.id = s.territory_id
                ''' + where_sql + ' ORDER BY s.created_at DESC',
                params,
            )
            return list(cursor.fetchall())


def create_field_submission(payload: dict[str, str], actor: dict[str, str] | None = None) -> dict[str, Any]:
    submission_id = f"submission-{_slugify(payload['candidate_name'])}-{secrets.token_hex(3)}"
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT task FROM field_assignments WHERE assignment_id = %s', (payload.get('assignment_id'),))
            if payload.get('assignment_id') and not cursor.fetchone():
                raise SubmissionNotFoundError('assignment not found')
            cursor.execute('SELECT name FROM territories WHERE id = %s', (payload['territory_id'],))
            territory = cursor.fetchone()
            if not territory:
                raise UnknownTerritoryError('unknown territory')
            cursor.execute(
                '''
                INSERT INTO field_submissions (
                    id, assignment_id, territory_id, submission_type, candidate_name,
                    candidate_status, notes, submitted_by, review_status, reviewer_note, registry_entity_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'submitted', '', NULL)
                RETURNING id, assignment_id, territory_id, submission_type, candidate_name, candidate_status, notes,
                          submitted_by, review_status, reviewer_note, registry_entity_id, created_at
                ''',
                (
                    submission_id,
                    payload.get('assignment_id'),
                    payload['territory_id'],
                    payload['submission_type'],
                    payload['candidate_name'],
                    payload['candidate_status'],
                    payload.get('notes', ''),
                    payload['submitted_by'],
                ),
            )
            created = cursor.fetchone()
            _log_action(cursor, actor=actor, action='create', entity_type='field_submission', entity_id=submission_id, details=payload)
        connection.commit()
    return {**created, 'territory_name': territory['name']}


def update_submission_review_status(submission_id: str, review_status: str, reviewer_note: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    if review_status not in {'under-review', 'rejected', 'needs-rework'}:
        raise InvalidSubmissionActionError('unsupported review status')
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE field_submissions
                SET review_status = %s, reviewer_note = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING id
                ''',
                (review_status, reviewer_note, submission_id),
            )
            updated = cursor.fetchone()
            if not updated:
                raise SubmissionNotFoundError('submission not found')
            _log_action(cursor, actor=actor, action=review_status, entity_type='field_submission', entity_id=submission_id, details={'reviewer_note': reviewer_note})
        connection.commit()
    return get_submission(submission_id)


def get_submission(submission_id: str) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT s.id, s.assignment_id, s.territory_id, t.name AS territory_name, s.submission_type, s.candidate_name,
                       s.candidate_status, s.notes, s.submitted_by, s.review_status, s.reviewer_note, s.registry_entity_id, s.created_at
                FROM field_submissions s JOIN territories t ON t.id = s.territory_id WHERE s.id = %s
                ''',
                (submission_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise SubmissionNotFoundError('submission not found')
            return dict(row)


def approve_submission(submission_id: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM field_submissions WHERE id = %s', (submission_id,))
            submission = cursor.fetchone()
            if not submission:
                raise SubmissionNotFoundError('submission not found')

            registry_entity_id = submission['registry_entity_id']
            candidate_payload = {
                'territory_id': submission['territory_id'],
                'status': submission['candidate_status'],
                'notes': submission['notes'],
            }

            if submission['submission_type'] == 'road':
                payload = {'name': submission['candidate_name'], 'territory_id': submission['territory_id'], 'status': submission['candidate_status'], 'length_km': '1.0'}
                if registry_entity_id and _entity_exists(cursor, 'roads', registry_entity_id):
                    cursor.execute('UPDATE roads SET status = %s, updated_at = NOW() WHERE id = %s', (payload['status'], registry_entity_id))
                else:
                    created = create_road(payload, actor=actor)
                    registry_entity_id = created['id']
            elif submission['submission_type'] == 'building':
                cursor.execute('SELECT id, name FROM roads WHERE territory_id = %s AND is_archived = FALSE ORDER BY name ASC LIMIT 1', (submission['territory_id'],))
                road = cursor.fetchone()
                if not road:
                    road = create_road({'name': f"Support Road for {submission['candidate_name']}", 'territory_id': submission['territory_id'], 'status': 'verified', 'length_km': '0.5'}, actor=actor)
                road_id = road['id'] if isinstance(road, dict) else road['id']
                payload = {'label': submission['candidate_name'], 'territory_id': submission['territory_id'], 'road_id': road_id, 'status': submission['candidate_status'], 'usage': 'field-captured'}
                if registry_entity_id and _entity_exists(cursor, 'buildings', registry_entity_id):
                    cursor.execute('UPDATE buildings SET status = %s, updated_at = NOW() WHERE id = %s', (payload['status'], registry_entity_id))
                else:
                    created = create_building(payload, actor=actor)
                    registry_entity_id = created['id']
            elif submission['submission_type'] == 'address':
                cursor.execute('SELECT id, name FROM roads WHERE territory_id = %s AND is_archived = FALSE ORDER BY name ASC LIMIT 1', (submission['territory_id'],))
                road = cursor.fetchone()
                if not road:
                    road = create_road({'name': f"Support Road for {submission['candidate_name']}", 'territory_id': submission['territory_id'], 'status': 'verified', 'length_km': '0.5'}, actor=actor)
                road_id = road['id'] if isinstance(road, dict) else road['id']
                cursor.execute('SELECT id, label FROM buildings WHERE territory_id = %s AND road_id = %s AND is_archived = FALSE ORDER BY label ASC LIMIT 1', (submission['territory_id'], road_id))
                building = cursor.fetchone()
                if not building:
                    building = create_building({'label': f"Support Building for {submission['candidate_name']}", 'territory_id': submission['territory_id'], 'road_id': road_id, 'status': 'verified', 'usage': 'field-captured'}, actor=actor)
                building_id = building['id'] if isinstance(building, dict) else building['id']
                payload = {'formatted': submission['candidate_name'], 'territory_id': submission['territory_id'], 'road_id': road_id, 'building_id': building_id, 'status': submission['candidate_status']}
                if registry_entity_id and _entity_exists(cursor, 'addresses', registry_entity_id):
                    cursor.execute('UPDATE addresses SET status = %s, updated_at = NOW() WHERE id = %s', (payload['status'], registry_entity_id))
                else:
                    created = create_address(payload, actor=actor)
                    registry_entity_id = created['id']
            else:
                raise InvalidSubmissionActionError('unsupported submission type')

            cursor.execute(
                '''
                UPDATE field_submissions
                SET review_status = 'approved', reviewer_note = 'Approved into registry', registry_entity_id = %s, updated_at = NOW()
                WHERE id = %s
                ''',
                (registry_entity_id, submission_id),
            )
            _log_action(cursor, actor=actor, action='approve', entity_type='field_submission', entity_id=submission_id, details={'registry_entity_id': registry_entity_id, **candidate_payload})
        connection.commit()
    return get_submission(submission_id)


def verify_address(query: str) -> dict[str, Any] | None:
    like = f'%{query.lower()}%'
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT a.id, a.formatted, a.status, a.publication_state, t.name AS territory_name, p.name AS province_name
                FROM addresses a
                JOIN territories t ON t.id = a.territory_id
                JOIN provinces p ON p.code = a.province_code
                WHERE a.is_archived = FALSE AND a.publication_state = 'published' AND (LOWER(a.id) = LOWER(%s) OR LOWER(a.formatted) LIKE %s)
                ORDER BY a.updated_at DESC
                LIMIT 1
                ''',
                (query, like),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                'query': query,
                'match_status': 'verified',
                'address_label': row['formatted'],
                'jurisdiction': f"{row['territory_name']} · {row['province_name']}",
                'verification_note': f"Published registry record found with status {row['status']}.",
                'address_id': row['id'],
            }


def list_import_jobs() -> list[dict[str, Any]]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT j.id, j.name, j.source_name, j.status, j.imported_count,
                       COUNT(r.row_number) AS total_rows,
                       SUM(CASE WHEN r.validation_status = 'valid' THEN 1 ELSE 0 END) AS valid_rows
                FROM import_jobs j
                LEFT JOIN import_rows r ON r.job_id = j.id
                GROUP BY j.id
                ORDER BY j.created_at DESC
                '''
            )
            return list(cursor.fetchall())


def get_import_rows(job_id: str) -> list[dict[str, Any]]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id FROM import_jobs WHERE id = %s', (job_id,))
            if not cursor.fetchone():
                raise ImportJobNotFoundError('import job not found')
            cursor.execute(
                '''
                SELECT job_id, row_number, submission_type, territory_id, candidate_name, candidate_status,
                       notes, validation_status, validation_message, committed_submission_id
                FROM import_rows WHERE job_id = %s ORDER BY row_number ASC
                ''',
                (job_id,),
            )
            return list(cursor.fetchall())


def create_import_job(payload: dict[str, Any], actor: dict[str, str] | None = None) -> dict[str, Any]:
    job_id = f"import-{_slugify(payload['name'])}"
    rows = payload.get('rows', [])
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO import_jobs (id, name, source_name, status) VALUES (%s, %s, %s, %s)', (job_id, payload['name'], payload['source_name'], 'draft'))
            for index, row in enumerate(rows, start=1):
                cursor.execute('SELECT name FROM territories WHERE id = %s', (row['territory_id'],))
                territory = cursor.fetchone()
                validation_status = 'valid' if territory else 'invalid'
                validation_message = 'Ready to commit' if territory else 'Unknown territory'
                cursor.execute(
                    '''
                    INSERT INTO import_rows (
                        job_id, row_number, submission_type, territory_id, candidate_name,
                        candidate_status, notes, validation_status, validation_message
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''',
                    (job_id, index, row['submission_type'], row['territory_id'], row['candidate_name'], row['candidate_status'], row.get('notes', ''), validation_status, validation_message),
                )
            _log_action(cursor, actor=actor, action='create', entity_type='import_job', entity_id=job_id, details={'row_count': len(rows)})
        connection.commit()
    return next(item for item in list_import_jobs() if item['id'] == job_id)


def commit_import_job(job_id: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id, status FROM import_jobs WHERE id = %s', (job_id,))
            job = cursor.fetchone()
            if not job:
                raise ImportJobNotFoundError('import job not found')
            cursor.execute(
                '''
                SELECT row_number, submission_type, territory_id, candidate_name, candidate_status, notes, validation_status
                FROM import_rows WHERE job_id = %s ORDER BY row_number ASC
                ''',
                (job_id,),
            )
            rows = list(cursor.fetchall())

        valid_count = 0
        for row in rows:
            if row['validation_status'] != 'valid':
                continue
            submission = create_field_submission(
                {
                    'assignment_id': None,
                    'territory_id': row['territory_id'],
                    'submission_type': row['submission_type'],
                    'candidate_name': row['candidate_name'],
                    'candidate_status': row['candidate_status'],
                    'notes': row['notes'],
                    'submitted_by': f'import:{job_id}',
                },
                actor=actor,
            )
            valid_count += 1
            with db_connection() as connection2:
                with connection2.cursor() as cursor2:
                    cursor2.execute('UPDATE import_rows SET committed_submission_id = %s WHERE job_id = %s AND row_number = %s', (submission['id'], job_id, row['row_number']))
                    connection2.commit()

    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE import_jobs SET status = %s, imported_count = imported_count + %s, updated_at = NOW() WHERE id = %s', ('committed', valid_count, job_id))
            _log_action(cursor, actor=actor, action='commit', entity_type='import_job', entity_id=job_id, details={'imported_count': valid_count})
        connection.commit()
    return next(item for item in list_import_jobs() if item['id'] == job_id)


def list_publication_packs() -> list[dict[str, Any]]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT p.id, p.name, p.status, p.audience, COUNT(pa.address_id) AS address_count
                FROM publication_packs p
                LEFT JOIN publication_pack_addresses pa ON pa.publication_pack_id = p.id
                GROUP BY p.id
                ORDER BY p.created_at DESC
                '''
            )
            return list(cursor.fetchall())


def create_publication_pack(payload: dict[str, Any], actor: dict[str, str] | None = None) -> dict[str, Any]:
    pack_id = f"publication-{_slugify(payload['name'])}"
    address_ids = payload.get('address_ids', [])
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO publication_packs (id, name, status, audience) VALUES (%s, %s, %s, %s)', (pack_id, payload['name'], payload.get('status', 'draft'), payload['audience']))
            for address_id in address_ids:
                cursor.execute('SELECT id FROM addresses WHERE id = %s', (address_id,))
                if not cursor.fetchone():
                    raise AddressNotFoundError('address not found')
                cursor.execute('INSERT INTO publication_pack_addresses (publication_pack_id, address_id) VALUES (%s, %s)', (pack_id, address_id))
                if payload.get('status', 'draft') == 'published':
                    cursor.execute("UPDATE addresses SET publication_state = 'published', updated_at = NOW() WHERE id = %s", (address_id,))
            _log_action(cursor, actor=actor, action='create', entity_type='publication_pack', entity_id=pack_id, details={'address_ids': address_ids})
        connection.commit()
    return next(item for item in list_publication_packs() if item['id'] == pack_id)


def publish_publication_pack(pack_id: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id FROM publication_packs WHERE id = %s', (pack_id,))
            if not cursor.fetchone():
                raise PublicationPackNotFoundError('publication pack not found')
            cursor.execute("UPDATE publication_packs SET status = 'published', updated_at = NOW() WHERE id = %s", (pack_id,))
            cursor.execute(
                '''
                UPDATE addresses
                SET publication_state = 'published', updated_at = NOW()
                WHERE id IN (SELECT address_id FROM publication_pack_addresses WHERE publication_pack_id = %s)
                ''',
                (pack_id,),
            )
            _log_action(cursor, actor=actor, action='publish', entity_type='publication_pack', entity_id=pack_id)
        connection.commit()
    return next(item for item in list_publication_packs() if item['id'] == pack_id)


def reporting_summary() -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) AS count FROM territories WHERE is_archived = FALSE')
            territories = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) AS count FROM field_submissions')
            submissions = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) AS count FROM field_submissions WHERE review_status IN ('submitted', 'under-review')")
            review_queue = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) AS count FROM addresses WHERE publication_state = 'published' AND is_archived = FALSE")
            published_addresses = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) AS count FROM import_jobs')
            import_jobs = cursor.fetchone()['count']
            cursor.execute('SELECT province_code, COUNT(*) AS territory_count FROM territories WHERE is_archived = FALSE GROUP BY province_code ORDER BY province_code ASC')
            territories_by_province = list(cursor.fetchall())
            cursor.execute("SELECT review_status, COUNT(*) AS count FROM field_submissions GROUP BY review_status ORDER BY review_status ASC")
            review_breakdown = list(cursor.fetchall())
            cursor.execute("SELECT status, COUNT(*) AS count FROM publication_packs GROUP BY status ORDER BY status ASC")
            publication_breakdown = list(cursor.fetchall())
            return {
                'totals': {
                    'territories': territories,
                    'submissions': submissions,
                    'review_queue': review_queue,
                    'published_addresses': published_addresses,
                    'import_jobs': import_jobs,
                },
                'territories_by_province': territories_by_province,
                'review_breakdown': review_breakdown,
                'publication_breakdown': publication_breakdown,
            }
