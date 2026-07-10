from __future__ import annotations

import hashlib
import html
import json
import math
import os
import re
import secrets
import unicodedata
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row

from app.address_codes import generate_national_address_code, validate_national_address_code
from app.data import (
    ADDRESSES,
    ADMIN_UNITS,
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
SESSION_TTL_HOURS = max(1, int(os.getenv('SESSION_TTL_HOURS', '12')))
ALLOW_DEFAULT_DEMO_PASSWORDS = os.getenv('ALLOW_DEFAULT_DEMO_PASSWORDS', 'true').strip().lower() not in {'0', 'false', 'no'}


def default_demo_password_rejected(username: str, password: str) -> bool:
    if ALLOW_DEFAULT_DEMO_PASSWORDS:
        return False
    return any(user['username'] == username and user['password'] == password for user in DEMO_USERS)


class UnknownProvinceError(ValueError):
    pass


class UnknownAdminUnitError(ValueError):
    pass


class AdminUnitProvinceMismatchError(ValueError):
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


class DuplicateImportJobError(ValueError):
    pass


class DuplicatePublicationPackError(ValueError):
    pass


class SubmissionNotFoundError(ValueError):
    pass


class EvidenceAttachmentNotFoundError(ValueError):
    pass


class InvalidSubmissionActionError(ValueError):
    pass


class PublicationPackNotFoundError(ValueError):
    pass


class AddressCorrectionNotFoundError(ValueError):
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


def _generate_public_code(province_code: str, formatted: str) -> str:
    digest = hashlib.sha1(f'{province_code}:{formatted.strip().lower()}'.encode('utf-8')).hexdigest()[:6].upper()
    prefix = _slugify(formatted).replace('-', '').upper()[:4] or 'ADDR'
    return f'EG-{province_code}-{prefix}-{digest}'


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
        CREATE TABLE IF NOT EXISTS admin_units (
            id TEXT PRIMARY KEY,
            level TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            parent_id TEXT REFERENCES admin_units(id),
            province_code TEXT REFERENCES provinces(code),
            name_es TEXT NOT NULL,
            name_en TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE admin_units ADD COLUMN IF NOT EXISTS province_code TEXT REFERENCES provinces(code)")
    cursor.execute("ALTER TABLE admin_units ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active'")
    cursor.execute("ALTER TABLE admin_units ADD COLUMN IF NOT EXISTS sort_order INTEGER NOT NULL DEFAULT 0")
    cursor.execute("ALTER TABLE admin_units ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
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
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            revoked_at TIMESTAMPTZ,
            last_seen_at TIMESTAMPTZ
        )
        '''
    )
    cursor.execute("ALTER TABLE auth_tokens ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
    cursor.execute("ALTER TABLE auth_tokens ADD COLUMN IF NOT EXISTS revoked_at TIMESTAMPTZ")
    cursor.execute("ALTER TABLE auth_tokens ADD COLUMN IF NOT EXISTS last_seen_at TIMESTAMPTZ")
    cursor.execute("UPDATE auth_tokens SET expires_at = COALESCE(expires_at, created_at + INTERVAL '12 hours') WHERE expires_at IS NULL OR expires_at <= created_at")
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
            admin_unit_id TEXT REFERENCES admin_units(id),
            type TEXT NOT NULL,
            readiness TEXT NOT NULL,
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE territories ADD COLUMN IF NOT EXISTS admin_unit_id TEXT REFERENCES admin_units(id)")
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
            spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE roads ADD COLUMN IF NOT EXISTS spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb")
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
            spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE buildings ADD COLUMN IF NOT EXISTS spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb")
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
            public_code TEXT,
            issuance_method TEXT NOT NULL DEFAULT 'manual',
            source TEXT NOT NULL DEFAULT 'admin-portal',
            verification_status TEXT NOT NULL DEFAULT 'provisional',
            superseded_by_address_id TEXT REFERENCES addresses(id),
            status TEXT NOT NULL,
            publication_state TEXT NOT NULL DEFAULT 'draft',
            is_archived BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE addresses ADD COLUMN IF NOT EXISTS public_code TEXT")
    cursor.execute("ALTER TABLE addresses ADD COLUMN IF NOT EXISTS issuance_method TEXT NOT NULL DEFAULT 'manual'")
    cursor.execute("ALTER TABLE addresses ADD COLUMN IF NOT EXISTS source TEXT NOT NULL DEFAULT 'admin-portal'")
    cursor.execute("ALTER TABLE addresses ADD COLUMN IF NOT EXISTS verification_status TEXT NOT NULL DEFAULT 'provisional'")
    cursor.execute("ALTER TABLE addresses ADD COLUMN IF NOT EXISTS superseded_by_address_id TEXT REFERENCES addresses(id)")
    cursor.execute("ALTER TABLE addresses ADD COLUMN IF NOT EXISTS publication_state TEXT NOT NULL DEFAULT 'draft'")
    cursor.execute("ALTER TABLE addresses ADD COLUMN IF NOT EXISTS is_archived BOOLEAN NOT NULL DEFAULT FALSE")
    cursor.execute("ALTER TABLE addresses ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_addresses_public_code_unique ON addresses (public_code) WHERE public_code IS NOT NULL")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS address_points (
            id TEXT PRIMARY KEY,
            address_id TEXT NOT NULL REFERENCES addresses(id) ON DELETE CASCADE,
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            accuracy_meters DOUBLE PRECISION,
            source_method TEXT NOT NULL DEFAULT 'manual',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_address_points_address_id_active ON address_points (address_id, is_active)")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS address_corrections (
            id TEXT PRIMARY KEY,
            address_id TEXT REFERENCES addresses(id),
            public_code TEXT,
            query TEXT NOT NULL,
            correction_type TEXT NOT NULL,
            reason TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            reporter_name TEXT,
            reporter_contact TEXT,
            status TEXT NOT NULL DEFAULT 'submitted',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE address_corrections ADD COLUMN IF NOT EXISTS reviewer_note TEXT NOT NULL DEFAULT ''")
    cursor.execute("ALTER TABLE address_corrections ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_address_corrections_status_created_at ON address_corrections (status, created_at DESC)")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS citizen_geotag_submissions (
            id TEXT PRIMARY KEY,
            territory_id TEXT REFERENCES territories(id),
            address_label TEXT NOT NULL,
            citizen_name TEXT,
            citizen_contact TEXT,
            dip_last4 TEXT,
            identity_verification_status TEXT NOT NULL DEFAULT 'unverified',
            identity_document_verified BOOLEAN NOT NULL DEFAULT FALSE,
            identity_verified_at TIMESTAMPTZ,
            landmark TEXT NOT NULL DEFAULT '',
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            accuracy_meters DOUBLE PRECISION,
            capture_method TEXT NOT NULL DEFAULT 'browser-gps',
            grid_code TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'submitted',
            duplicate_hint TEXT NOT NULL DEFAULT 'none',
            reviewer_note TEXT NOT NULL DEFAULT '',
            suggested_road_name TEXT,
            suggested_local_area TEXT,
            suggested_place_name TEXT,
            map_display_name TEXT,
            road_suggestion_source TEXT,
            road_suggestion_attribution TEXT,
            road_suggestion_status TEXT NOT NULL DEFAULT 'not-suggested',
            reviewed_road_name TEXT,
            field_submission_id TEXT,
            field_status TEXT NOT NULL DEFAULT 'assigned',
            field_note TEXT NOT NULL DEFAULT '',
            field_verified_at TIMESTAMPTZ,
            signage_batch TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS citizen_name TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS citizen_contact TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS dip_last4 TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS identity_verification_status TEXT NOT NULL DEFAULT 'unverified'")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS identity_document_verified BOOLEAN NOT NULL DEFAULT FALSE")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS identity_verified_at TIMESTAMPTZ")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS landmark TEXT NOT NULL DEFAULT ''")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS capture_method TEXT NOT NULL DEFAULT 'browser-gps'")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS duplicate_hint TEXT NOT NULL DEFAULT 'none'")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS reviewer_note TEXT NOT NULL DEFAULT ''")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS suggested_road_name TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS suggested_local_area TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS suggested_place_name TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS map_display_name TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS road_suggestion_source TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS road_suggestion_attribution TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS road_suggestion_status TEXT NOT NULL DEFAULT 'not-suggested'")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS reviewed_road_name TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS field_submission_id TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS field_status TEXT NOT NULL DEFAULT 'assigned'")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS field_note TEXT NOT NULL DEFAULT ''")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS field_verified_at TIMESTAMPTZ")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS signage_batch TEXT")
    cursor.execute("ALTER TABLE citizen_geotag_submissions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_citizen_geotag_status_created_at ON citizen_geotag_submissions (status, created_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_citizen_geotag_grid_code ON citizen_geotag_submissions (grid_code)")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS address_records (
            id TEXT PRIMARY KEY,
            address_code TEXT NOT NULL UNIQUE,
            source_submission_id TEXT REFERENCES citizen_geotag_submissions(id),
            province_code TEXT REFERENCES provinces(code),
            territory_id TEXT REFERENCES territories(id),
            address_label TEXT NOT NULL,
            status TEXT NOT NULL,
            publication_state TEXT NOT NULL DEFAULT 'not-public',
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            accuracy_meters DOUBLE PRECISION,
            search_text TEXT NOT NULL DEFAULT '',
            record_bundle JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE address_records ADD COLUMN IF NOT EXISTS source_submission_id TEXT REFERENCES citizen_geotag_submissions(id)")
    cursor.execute("ALTER TABLE address_records ADD COLUMN IF NOT EXISTS province_code TEXT REFERENCES provinces(code)")
    cursor.execute("ALTER TABLE address_records ADD COLUMN IF NOT EXISTS territory_id TEXT REFERENCES territories(id)")
    cursor.execute("ALTER TABLE address_records ADD COLUMN IF NOT EXISTS publication_state TEXT NOT NULL DEFAULT 'not-public'")
    cursor.execute("ALTER TABLE address_records ADD COLUMN IF NOT EXISTS accuracy_meters DOUBLE PRECISION")
    cursor.execute("ALTER TABLE address_records ADD COLUMN IF NOT EXISTS search_text TEXT NOT NULL DEFAULT ''")
    cursor.execute("ALTER TABLE address_records ADD COLUMN IF NOT EXISTS record_bundle JSONB NOT NULL DEFAULT '{}'::jsonb")
    cursor.execute("ALTER TABLE address_records ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_address_records_code ON address_records (address_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_address_records_status_updated ON address_records (status, updated_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_address_records_province_status ON address_records (province_code, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_address_records_territory_status ON address_records (territory_id, status)")

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS address_record_events (
            id TEXT PRIMARY KEY,
            address_record_id TEXT NOT NULL REFERENCES address_records(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            actor_id TEXT,
            actor_username TEXT,
            actor_role TEXT,
            details JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_address_record_events_record_created ON address_record_events (address_record_id, created_at DESC)")

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
            spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        '''
    )
    cursor.execute("ALTER TABLE field_submissions ADD COLUMN IF NOT EXISTS reviewer_note TEXT NOT NULL DEFAULT ''")
    cursor.execute("ALTER TABLE field_submissions ADD COLUMN IF NOT EXISTS registry_entity_id TEXT")
    cursor.execute("ALTER TABLE field_submissions ADD COLUMN IF NOT EXISTS spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb")
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

            for admin_unit in ADMIN_UNITS:
                cursor.execute(
                    '''
                    INSERT INTO admin_units (id, level, code, parent_id, province_code, name_es, name_en, status, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        level = EXCLUDED.level,
                        code = EXCLUDED.code,
                        parent_id = EXCLUDED.parent_id,
                        province_code = EXCLUDED.province_code,
                        name_es = EXCLUDED.name_es,
                        name_en = EXCLUDED.name_en,
                        status = EXCLUDED.status,
                        sort_order = EXCLUDED.sort_order,
                        updated_at = NOW()
                    ''',
                    (
                        admin_unit['id'],
                        admin_unit['level'],
                        admin_unit['code'],
                        admin_unit['parent_id'],
                        admin_unit.get('province_code') or admin_unit['code'],
                        admin_unit['name_es'],
                        admin_unit['name_en'],
                        admin_unit.get('status', 'active'),
                        admin_unit.get('sort_order', 0),
                    ),
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
                        password_hash = users.password_hash,
                        is_active = users.is_active
                    ''',
                    (user['id'], user['username'], user['full_name'], user['role'], _hash_password(user['password'])),
                )

            for territory in TERRITORIES:
                cursor.execute(
                    '''
                    INSERT INTO territories (id, name, province_code, admin_unit_id, type, readiness, is_archived)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        province_code = EXCLUDED.province_code,
                        admin_unit_id = EXCLUDED.admin_unit_id,
                        type = EXCLUDED.type,
                        readiness = EXCLUDED.readiness,
                        is_archived = EXCLUDED.is_archived,
                        updated_at = NOW()
                    ''',
                    (
                        territory['id'],
                        territory['name'],
                        territory['province_code'],
                        territory.get('admin_unit_id'),
                        territory['type'],
                        territory['readiness'],
                        territory['is_archived'],
                    ),
                )

            cursor.execute(
                '''
                UPDATE territories
                SET is_archived = FALSE,
                    updated_at = NOW()
                WHERE type = 'official-municipality'
                  AND readiness = 'official-routing'
                '''
            )

            cursor.execute(
                '''
                UPDATE territories t
                SET admin_unit_id = au.id,
                    updated_at = NOW()
                FROM admin_units au
                WHERE t.admin_unit_id IS NULL
                  AND au.level = 'province'
                  AND au.code = t.province_code
                '''
            )

            for road in ROADS:
                cursor.execute(
                    '''
                    INSERT INTO roads (id, name, territory_id, status, length_km, spatial_evidence, is_archived)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        territory_id = EXCLUDED.territory_id,
                        status = EXCLUDED.status,
                        length_km = EXCLUDED.length_km,
                        spatial_evidence = COALESCE(NULLIF(roads.spatial_evidence, '{}'::jsonb), EXCLUDED.spatial_evidence),
                        is_archived = EXCLUDED.is_archived,
                        updated_at = NOW()
                    ''',
                    (road['id'], road['name'], road['territory_id'], road['status'], road['length_km'], json.dumps(road.get('spatial_evidence') or {}), road.get('is_archived', False)),
                )

            for building in BUILDINGS:
                cursor.execute(
                    '''
                    INSERT INTO buildings (id, label, territory_id, road_id, status, usage, spatial_evidence, is_archived)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        label = EXCLUDED.label,
                        territory_id = EXCLUDED.territory_id,
                        road_id = EXCLUDED.road_id,
                        status = EXCLUDED.status,
                        usage = EXCLUDED.usage,
                        spatial_evidence = COALESCE(NULLIF(buildings.spatial_evidence, '{}'::jsonb), EXCLUDED.spatial_evidence),
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
                        json.dumps(building.get('spatial_evidence') or {}),
                        building.get('is_archived', False),
                    ),
                )

            for address in ADDRESSES:
                cursor.execute(
                    '''
                    INSERT INTO addresses (
                        id, formatted, territory_id, road_id, building_id, province_code,
                        public_code, issuance_method, source, verification_status,
                        status, publication_state, is_archived
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        formatted = EXCLUDED.formatted,
                        territory_id = EXCLUDED.territory_id,
                        road_id = EXCLUDED.road_id,
                        building_id = EXCLUDED.building_id,
                        province_code = EXCLUDED.province_code,
                        public_code = COALESCE(addresses.public_code, EXCLUDED.public_code),
                        issuance_method = EXCLUDED.issuance_method,
                        source = EXCLUDED.source,
                        verification_status = EXCLUDED.verification_status,
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
                        address.get('public_code') or _generate_public_code(address['province_code'], address['formatted']),
                        address.get('issuance_method', 'manual'),
                        address.get('source', 'seed-registry'),
                        address.get('verification_status', 'provisional'),
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

            for submission in FIELD_SUBMISSIONS:
                cursor.execute(
                    '''
                    INSERT INTO field_submissions (
                        id, assignment_id, territory_id, submission_type, candidate_name,
                        candidate_status, notes, submitted_by, review_status, registry_entity_id, spatial_evidence
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
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
                        spatial_evidence = COALESCE(NULLIF(field_submissions.spatial_evidence, '{}'::jsonb), EXCLUDED.spatial_evidence),
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
                        json.dumps(submission.get('spatial_evidence') or {}),
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

            retired_address_ids = ('addr-bata-001', 'addr-oyala-002')
            retired_public_codes = ('EG-LI-BATA-001A', 'EG-DJ-OYAL-002A')
            retired_building_ids = ('building-bata-block-4', 'building-oyala-ministry-annex')
            retired_road_ids = ('road-bata-independencia', 'road-oyala-admin-loop')
            retired_territory_ids = ('territory-bata-urban-core', 'territory-oyala-civic-district', 'territory-ebebiyin-access-corridor')
            retired_assignment_ids = ('field-001', 'field-002', 'field-003')
            retired_submission_ids = ('submission-bata-road-001', 'submission-oyala-address-001')
            retired_import_job_ids = ('import-bata-legacy-001',)
            retired_pack_ids = ('publication-pack-001',)

            cursor.execute('DELETE FROM address_corrections WHERE address_id = ANY(%s) OR public_code = ANY(%s)', (list(retired_address_ids), list(retired_public_codes)))
            cursor.execute('DELETE FROM publication_pack_addresses WHERE publication_pack_id = ANY(%s) OR address_id = ANY(%s)', (list(retired_pack_ids), list(retired_address_ids)))
            cursor.execute('DELETE FROM publication_packs WHERE id = ANY(%s)', (list(retired_pack_ids),))
            cursor.execute('DELETE FROM import_rows WHERE job_id = ANY(%s) OR territory_id = ANY(%s)', (list(retired_import_job_ids), list(retired_territory_ids)))
            cursor.execute('DELETE FROM import_jobs WHERE id = ANY(%s)', (list(retired_import_job_ids),))
            cursor.execute('DELETE FROM field_submissions WHERE id = ANY(%s) OR assignment_id = ANY(%s) OR territory_id = ANY(%s)', (list(retired_submission_ids), list(retired_assignment_ids), list(retired_territory_ids)))
            cursor.execute('DELETE FROM field_assignments WHERE assignment_id = ANY(%s) OR territory_id = ANY(%s)', (list(retired_assignment_ids), list(retired_territory_ids)))
            cursor.execute("UPDATE addresses SET is_archived = TRUE, publication_state = 'retired-pilot-fixture', updated_at = NOW() WHERE id = ANY(%s) OR public_code = ANY(%s)", (list(retired_address_ids), list(retired_public_codes)))
            cursor.execute('UPDATE buildings SET is_archived = TRUE, updated_at = NOW() WHERE id = ANY(%s) OR territory_id = ANY(%s) OR road_id = ANY(%s)', (list(retired_building_ids), list(retired_territory_ids), list(retired_road_ids)))
            cursor.execute('UPDATE roads SET is_archived = TRUE, updated_at = NOW() WHERE id = ANY(%s) OR territory_id = ANY(%s)', (list(retired_road_ids), list(retired_territory_ids)))
            cursor.execute('UPDATE territories SET is_archived = TRUE, updated_at = NOW() WHERE id = ANY(%s)', (list(retired_territory_ids),))
            cursor.execute("UPDATE addresses SET is_archived = TRUE, publication_state = 'retired-outside-bioko-norte-pilot', updated_at = NOW() WHERE province_code <> 'BN'")
            cursor.execute("""
                UPDATE buildings b
                SET is_archived = TRUE, updated_at = NOW()
                FROM territories t
                WHERE b.territory_id = t.id AND t.province_code <> 'BN'
            """)
            cursor.execute("""
                UPDATE roads r
                SET is_archived = TRUE, updated_at = NOW()
                FROM territories t
                WHERE r.territory_id = t.id AND t.province_code <> 'BN'
            """)
            cursor.execute("""
                UPDATE territories
                SET is_archived = TRUE, updated_at = NOW()
                WHERE province_code <> 'BN'
                  AND NOT (type = 'official-municipality' AND readiness = 'official-routing')
            """)
        connection.commit()


def authenticate_user_session(username: str, password: str) -> dict[str, Any]:
    if default_demo_password_rejected(username, password):
        raise AuthenticationError('default demo password disabled')
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_TTL_HOURS)
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
            cursor.execute('DELETE FROM auth_tokens WHERE user_id = %s AND (revoked_at IS NOT NULL OR expires_at <= NOW())', (user['id'],))
            cursor.execute('INSERT INTO auth_tokens (token, user_id, expires_at, last_seen_at) VALUES (%s, %s, %s, NOW())', (token, user['id'], expires_at))
            _log_action(cursor, actor=user, action='login', entity_type='session', entity_id=token, details={'username': username, 'expires_at': expires_at.isoformat()})
        connection.commit()

    return {
        'token': token,
        'expires_at': expires_at.isoformat(),
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
                WHERE t.token = %s AND u.is_active = TRUE AND t.revoked_at IS NULL AND t.expires_at > NOW()
                ''',
                (token,),
            )
            user = cursor.fetchone()
            if not user:
                cursor.execute('DELETE FROM auth_tokens WHERE token = %s AND (revoked_at IS NOT NULL OR expires_at <= NOW())', (token,))
                connection.commit()
                raise AuthenticationError('invalid token')
            cursor.execute('UPDATE auth_tokens SET last_seen_at = NOW() WHERE token = %s', (token,))
            connection.commit()
            return {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role'],
            }


def revoke_user_session(token: str, actor: dict[str, str] | None = None) -> None:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE auth_tokens SET revoked_at = NOW() WHERE token = %s AND revoked_at IS NULL', (token,))
            if actor:
                _log_action(cursor, actor=actor, action='logout', entity_type='session', entity_id=token, details={'revoked': True})
        connection.commit()


def list_provinces() -> list[dict[str, str]]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT COALESCE(au.id, 'prov-' || LOWER(REPLACE(REPLACE(p.name, ' ', '-'), 'é', 'e'))) AS id, p.code, p.name
                FROM provinces p
                LEFT JOIN admin_units au ON au.level = 'province' AND au.code = p.code
                ORDER BY p.name ASC
                '''
            )
            return list(cursor.fetchall())


def list_admin_units(*, level: str | None = None, parent_id: str | None = None, province_code: str | None = None) -> list[dict[str, Any]]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if level:
        where_clauses.append('au.level = %s')
        params.append(level)
    if parent_id:
        where_clauses.append('au.parent_id = %s')
        params.append(parent_id)
    if province_code:
        where_clauses.append('au.province_code = %s')
        params.append(province_code)
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT au.id, au.level, au.code, au.parent_id, au.province_code, au.name_es, au.name_en, au.status, au.sort_order
                FROM admin_units au
                ''' + where_sql + ' ORDER BY au.sort_order ASC, au.name_es ASC',
                params,
            )
            return list(cursor.fetchall())


def _resolve_admin_unit(cursor: psycopg.Cursor, province_code: str, admin_unit_id: str | None) -> dict[str, Any]:
    if admin_unit_id:
        cursor.execute(
            '''
            SELECT id, level, code, province_code, name_es, name_en, status
            FROM admin_units
            WHERE id = %s
            ''',
            (admin_unit_id,),
        )
        admin_unit = cursor.fetchone()
        if not admin_unit:
            raise UnknownAdminUnitError(f'Unknown admin unit id: {admin_unit_id}')
        if admin_unit['province_code'] != province_code:
            raise AdminUnitProvinceMismatchError('admin unit does not belong to the selected province')
        return dict(admin_unit)

    cursor.execute(
        '''
        SELECT id, level, code, province_code, name_es, name_en, status
        FROM admin_units
        WHERE level = 'province' AND code = %s
        ''',
        (province_code,),
    )
    admin_unit = cursor.fetchone()
    if not admin_unit:
        raise UnknownAdminUnitError(f'No default admin unit found for province code: {province_code}')
    return dict(admin_unit)


def _territory_projection() -> str:
    return '''
        SELECT t.id, t.name, t.province_code, p.name AS province, t.admin_unit_id, au.code AS admin_unit_code, au.name_es AS admin_unit_name, au.level AS admin_unit_level, t.type, t.readiness, t.is_archived
        FROM territories t
        JOIN provinces p ON p.code = t.province_code
        LEFT JOIN admin_units au ON au.id = t.admin_unit_id
    '''




def _paginated_query(
    *,
    select_sql: str,
    count_sql: str,
    where_sql: str,
    params: list[Any],
    order_sql: str,
    page: int,
    per_page: int,
    max_per_page: int = 100,
) -> dict[str, Any]:
    safe_page = max(1, int(page or 1))
    safe_per_page = max(1, min(int(per_page or 25), max_per_page))
    offset = (safe_page - 1) * safe_per_page
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(count_sql + where_sql, params)
            total_items = int(cursor.fetchone()['count'])
            cursor.execute(
                select_sql + where_sql + order_sql + ' LIMIT %s OFFSET %s',
                [*params, safe_per_page, offset],
            )
            items = list(cursor.fetchall())
    total_pages = max(1, math.ceil(total_items / safe_per_page)) if total_items else 0
    return {
        'items': items,
        'pagination': {
            'page': safe_page,
            'per_page': safe_per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': safe_page < total_pages,
            'has_previous': safe_page > 1 and total_items > 0,
        },
    }

def fetch_territories(*, q: str | None = None, province_code: str | None = None, readiness: str | None = None, include_archived: bool = False) -> list[dict[str, Any]]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if q:
        like = f'%{q.lower()}%'
        where_clauses.append('(LOWER(t.name) LIKE %s OR LOWER(p.name) LIKE %s OR LOWER(COALESCE(au.name_es, \'\')) LIKE %s OR LOWER(t.type) LIKE %s OR LOWER(t.readiness) LIKE %s)')
        params.extend([like, like, like, like, like])
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



def fetch_territories_page(*, q: str | None = None, province_code: str | None = None, readiness: str | None = None, include_archived: bool = False, page: int = 1, per_page: int = 100) -> dict[str, Any]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if q:
        like = f'%{q.lower()}%'
        where_clauses.append('(LOWER(t.name) LIKE %s OR LOWER(p.name) LIKE %s OR LOWER(COALESCE(au.name_es, '')) LIKE %s OR LOWER(t.type) LIKE %s OR LOWER(t.readiness) LIKE %s)')
        params.extend([like, like, like, like, like])
    if province_code:
        where_clauses.append('t.province_code = %s')
        params.append(province_code)
    if readiness:
        where_clauses.append('t.readiness = %s')
        params.append(readiness)
    if not include_archived:
        where_clauses.append('t.is_archived = FALSE')
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
    return _paginated_query(
        select_sql=_territory_projection(),
        count_sql='SELECT COUNT(*) AS count FROM territories t JOIN provinces p ON p.code = t.province_code LEFT JOIN admin_units au ON au.id = t.admin_unit_id',
        where_sql=where_sql,
        params=params,
        order_sql=' ORDER BY t.name ASC',
        page=page,
        per_page=per_page,
    )


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
            admin_unit = _resolve_admin_unit(cursor, payload['province_code'], payload.get('admin_unit_id'))
            cursor.execute('SELECT 1 FROM territories WHERE LOWER(name) = LOWER(%s)', (payload['name'],))
            if cursor.fetchone():
                raise DuplicateTerritoryError('duplicate territory')
            cursor.execute(
                '''
                INSERT INTO territories (id, name, province_code, admin_unit_id, type, readiness, is_archived)
                VALUES (%s, %s, %s, %s, %s, %s, FALSE)
                RETURNING id, name, province_code, admin_unit_id, type, readiness, is_archived
                ''',
                (territory_id, payload['name'], payload['province_code'], admin_unit['id'], payload['type'], payload['readiness']),
            )
            created = cursor.fetchone()
            _log_action(cursor, actor=actor, action='create', entity_type='territory', entity_id=territory_id, details={**payload, 'admin_unit_id': admin_unit['id']})
        connection.commit()
    return {
        **created,
        'province': province['name'],
        'admin_unit_code': admin_unit['code'],
        'admin_unit_name': admin_unit['name_es'],
        'admin_unit_level': admin_unit['level'],
    }


def update_territory(territory_id: str, payload: dict[str, str], actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT name FROM provinces WHERE code = %s', (payload['province_code'],))
            province = cursor.fetchone()
            if not province:
                raise UnknownProvinceError(f"Unknown province code: {payload['province_code']}")
            admin_unit = _resolve_admin_unit(cursor, payload['province_code'], payload.get('admin_unit_id'))
            cursor.execute('SELECT id FROM territories WHERE id = %s', (territory_id,))
            if not cursor.fetchone():
                raise TerritoryNotFoundError('territory not found')
            cursor.execute('SELECT id FROM territories WHERE LOWER(name) = LOWER(%s) AND id <> %s', (payload['name'], territory_id))
            if cursor.fetchone():
                raise DuplicateTerritoryError('duplicate territory')
            cursor.execute(
                '''
                UPDATE territories
                SET name = %s, province_code = %s, admin_unit_id = %s, type = %s, readiness = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING id, name, province_code, admin_unit_id, type, readiness, is_archived
                ''',
                (payload['name'], payload['province_code'], admin_unit['id'], payload['type'], payload['readiness'], territory_id),
            )
            updated = cursor.fetchone()
            _log_action(cursor, actor=actor, action='update', entity_type='territory', entity_id=territory_id, details={**payload, 'admin_unit_id': admin_unit['id']})
        connection.commit()
    return {
        **updated,
        'province': province['name'],
        'admin_unit_code': admin_unit['code'],
        'admin_unit_name': admin_unit['name_es'],
        'admin_unit_level': admin_unit['level'],
    }


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



def fetch_roads_page(q: str | None = None, territory_id: str | None = None, include_archived: bool = False, page: int = 1, per_page: int = 100) -> dict[str, Any]:
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
    return _paginated_query(
        select_sql='''
                SELECT r.id, r.name, r.territory_id, t.name AS territory_name, r.status, r.length_km, r.is_archived
                FROM roads r
                JOIN territories t ON t.id = r.territory_id
                ''',
        count_sql='SELECT COUNT(*) AS count FROM roads r JOIN territories t ON t.id = r.territory_id',
        where_sql=where_sql,
        params=params,
        order_sql=' ORDER BY r.name ASC',
        page=page,
        per_page=per_page,
    )


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
                INSERT INTO roads (id, name, territory_id, status, length_km, spatial_evidence, is_archived)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, FALSE)
                RETURNING id, name, territory_id, status, length_km, spatial_evidence, is_archived
                ''',
                (road_id, payload['name'], payload['territory_id'], payload['status'], payload['length_km'], json.dumps(payload.get('spatial_evidence') or {})),
            )
            created = cursor.fetchone()
            _log_action(cursor, actor=actor, action='create', entity_type='road', entity_id=road_id, details=payload)
        connection.commit()
    return {**_decode_spatial_evidence(dict(created)), 'territory_name': territory['name']}


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



def fetch_buildings_page(q: str | None = None, territory_id: str | None = None, include_archived: bool = False, page: int = 1, per_page: int = 100) -> dict[str, Any]:
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
    return _paginated_query(
        select_sql='''
                SELECT b.id, b.label, b.territory_id, t.name AS territory_name, b.road_id, r.name AS road_name, b.status, b.usage, b.is_archived
                FROM buildings b
                JOIN territories t ON t.id = b.territory_id
                JOIN roads r ON r.id = b.road_id
                ''',
        count_sql='SELECT COUNT(*) AS count FROM buildings b JOIN territories t ON t.id = b.territory_id JOIN roads r ON r.id = b.road_id',
        where_sql=where_sql,
        params=params,
        order_sql=' ORDER BY b.label ASC',
        page=page,
        per_page=per_page,
    )


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
                INSERT INTO buildings (id, label, territory_id, road_id, status, usage, spatial_evidence, is_archived)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, FALSE)
                RETURNING id, label, territory_id, road_id, status, usage, spatial_evidence, is_archived
                ''',
                (building_id, payload['label'], payload['territory_id'], payload['road_id'], payload['status'], payload['usage'], json.dumps(payload.get('spatial_evidence') or {})),
            )
            created = cursor.fetchone()
            _log_action(cursor, actor=actor, action='create', entity_type='building', entity_id=building_id, details=payload)
        connection.commit()
    return {**_decode_spatial_evidence(dict(created)), 'territory_name': territory['name'], 'road_name': road['name']}


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


def _address_select_sql(where_sql: str) -> str:
    return (
        '''
        SELECT a.id, a.formatted, a.territory_id, t.name AS territory_name, a.road_id, r.name AS road_name,
               a.building_id, b.label AS building_label, a.province_code, a.public_code, a.issuance_method,
               a.source, a.verification_status, a.superseded_by_address_id, a.status, a.publication_state,
               a.is_archived, ap.latitude, ap.longitude, ap.accuracy_meters, ap.source_method AS point_source_method
        FROM addresses a
        JOIN territories t ON t.id = a.territory_id
        JOIN roads r ON r.id = a.road_id
        JOIN buildings b ON b.id = a.building_id
        LEFT JOIN address_points ap ON ap.address_id = a.id AND ap.is_active = TRUE
        '''
        + where_sql
    )


def _upsert_address_point(cursor: psycopg.Cursor, address_id: str, payload: dict[str, Any]) -> None:
    latitude = payload.get('latitude')
    longitude = payload.get('longitude')
    if latitude is None or longitude is None:
        return

    point_id = f'point-{address_id}'
    cursor.execute('UPDATE address_points SET is_active = FALSE, updated_at = NOW() WHERE address_id = %s', (address_id,))
    cursor.execute(
        '''
        INSERT INTO address_points (id, address_id, latitude, longitude, accuracy_meters, source_method, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        ON CONFLICT (id) DO UPDATE SET
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            accuracy_meters = EXCLUDED.accuracy_meters,
            source_method = EXCLUDED.source_method,
            is_active = TRUE,
            updated_at = NOW()
        ''',
        (
            point_id,
            address_id,
            latitude,
            longitude,
            payload.get('accuracy_meters'),
            payload.get('point_source_method') or payload.get('issuance_method') or 'manual',
        ),
    )


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
                _address_select_sql(where_sql) + ' ORDER BY a.formatted ASC',
                params,
            )
            return list(cursor.fetchall())



def fetch_addresses_page(q: str | None = None, territory_id: str | None = None, status: str | None = None, include_archived: bool = False, page: int = 1, per_page: int = 100) -> dict[str, Any]:
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
    return _paginated_query(
        select_sql=_address_select_sql(''),
        count_sql='''
        SELECT COUNT(*) AS count
        FROM addresses a
        JOIN territories t ON t.id = a.territory_id
        JOIN roads r ON r.id = a.road_id
        JOIN buildings b ON b.id = a.building_id
        LEFT JOIN address_points ap ON ap.address_id = a.id AND ap.is_active = TRUE
        ''',
        where_sql=where_sql,
        params=params,
        order_sql=' ORDER BY a.formatted ASC',
        page=page,
        per_page=per_page,
    )


def get_address(address_id: str) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(_address_select_sql(' WHERE a.id = %s'), (address_id,))
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

            public_code = payload.get('public_code') or _generate_public_code(territory['province_code'], payload['formatted'])
            verification_status = payload.get('verification_status') or ('official' if payload.get('publication_state') == 'published' else 'provisional')
            cursor.execute(
                '''
                INSERT INTO addresses (
                    id, formatted, territory_id, road_id, building_id, province_code,
                    public_code, issuance_method, source, verification_status,
                    superseded_by_address_id, status, publication_state, is_archived
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)
                RETURNING id
                ''',
                (
                    address_id,
                    payload['formatted'],
                    payload['territory_id'],
                    payload['road_id'],
                    payload['building_id'],
                    territory['province_code'],
                    public_code,
                    payload.get('issuance_method', 'manual'),
                    payload.get('source', 'admin-portal'),
                    verification_status,
                    payload.get('superseded_by_address_id'),
                    payload['status'],
                    payload.get('publication_state', 'draft'),
                ),
            )
            created = cursor.fetchone()
            _upsert_address_point(cursor, address_id, payload)
            _log_action(cursor, actor=actor, action='create', entity_type='address', entity_id=address_id, details=payload)
        connection.commit()
    return get_address(created['id'])


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
            current = get_address(address_id)
            cursor.execute('SELECT id FROM addresses WHERE LOWER(formatted) = LOWER(%s) AND id <> %s', (payload['formatted'], address_id))
            if cursor.fetchone():
                raise DuplicateAddressError('duplicate address')
            public_code = payload.get('public_code') or current.get('public_code') or _generate_public_code(territory['province_code'], payload['formatted'])
            verification_status = payload.get('verification_status') or current.get('verification_status') or 'provisional'
            cursor.execute(
                '''
                UPDATE addresses
                SET formatted = %s,
                    territory_id = %s,
                    road_id = %s,
                    building_id = %s,
                    province_code = %s,
                    public_code = %s,
                    issuance_method = %s,
                    source = %s,
                    verification_status = %s,
                    superseded_by_address_id = %s,
                    status = %s,
                    publication_state = %s,
                    updated_at = NOW()
                WHERE id = %s
                RETURNING id
                ''',
                (
                    payload['formatted'],
                    payload['territory_id'],
                    payload['road_id'],
                    payload['building_id'],
                    territory['province_code'],
                    public_code,
                    payload.get('issuance_method', current.get('issuance_method') or 'manual'),
                    payload.get('source', current.get('source') or 'admin-portal'),
                    verification_status,
                    payload.get('superseded_by_address_id', current.get('superseded_by_address_id')),
                    payload['status'],
                    payload.get('publication_state', current['publication_state']),
                    address_id,
                ),
            )
            updated = cursor.fetchone()
            if not updated:
                raise AddressNotFoundError('address not found')
            _upsert_address_point(cursor, address_id, payload)
            _log_action(cursor, actor=actor, action='update', entity_type='address', entity_id=address_id, details=payload)
        connection.commit()
    return get_address(updated['id'])


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



def _coerce_json_object(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, str):
        if not value.strip():
            return {}
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    return value if isinstance(value, dict) else {}


def _coordinate_value(point: dict[str, Any], key: str) -> float | None:
    try:
        value = float(point.get(key))
    except (TypeError, ValueError):
        return None
    if key == 'latitude' and -90 <= value <= 90:
        return value
    if key == 'longitude' and -180 <= value <= 180:
        return value
    return None


def _haversine_km(a: dict[str, Any], b: dict[str, Any]) -> float:
    lat1 = math.radians(float(a['latitude']))
    lon1 = math.radians(float(a['longitude']))
    lat2 = math.radians(float(b['latitude']))
    lon2 = math.radians(float(b['longitude']))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371.0088 * 2 * math.asin(min(1, math.sqrt(h)))


FIELD_EVIDENCE_ATTACHMENT_TYPES = {
    'photo-reference',
    'site-note',
    'landmark-confirmation',
    'coordinate-confirmation',
}

SENSITIVE_EVIDENCE_REFERENCE_PATTERN = re.compile(r'(password|secret|token|api[_-]?key|private[_-]?key|dip|passport|credential)', re.IGNORECASE)


def normalize_field_evidence_attachments(value: Any) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise InvalidSubmissionActionError('field evidence attachments must be a list')
    if len(value) > 6:
        raise InvalidSubmissionActionError('field evidence attachments are limited to 6 items')

    normalized: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            raise InvalidSubmissionActionError('field evidence attachment must be an object')
        evidence_type = str(item.get('type') or item.get('evidence_type') or '').strip()
        if evidence_type not in FIELD_EVIDENCE_ATTACHMENT_TYPES:
            raise InvalidSubmissionActionError('field evidence attachment type is not supported')
        reference = str(item.get('reference') or item.get('evidence_reference') or '').strip()
        if len(reference) < 3 or len(reference) > 120:
            raise InvalidSubmissionActionError('field evidence reference must be 3-120 characters')
        if SENSITIVE_EVIDENCE_REFERENCE_PATTERN.search(reference):
            raise InvalidSubmissionActionError('field evidence reference must not include private credentials or identity document labels')
        note = str(item.get('note') or item.get('evidence_note') or '').strip()
        if len(note) > 300:
            raise InvalidSubmissionActionError('field evidence note is too long')
        captured_by = str(item.get('captured_by') or '').strip()[:120]
        captured_at = str(item.get('captured_at') or '').strip()[:80]
        normalized.append({
            'type': evidence_type,
            'reference': reference,
            'note': note,
            'captured_by': captured_by,
            'captured_at': captured_at,
        })
    return normalized


def _attach_field_evidence_metadata(normalized: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    attachments = normalize_field_evidence_attachments(payload.get('evidence_attachments'))
    if attachments:
        normalized['evidence_attachments'] = attachments
        normalized['evidence_attachment_count'] = len(attachments)
    return normalized


def normalize_submission_spatial_evidence(submission_type: str, evidence: Any) -> dict[str, Any]:
    payload = _coerce_json_object(evidence)
    if submission_type == 'road':
        raw_points = payload.get('points')
        if not isinstance(raw_points, list):
            raise InvalidSubmissionActionError('road stretch geometry requires captured start and end GPS points')
        points: list[dict[str, Any]] = []
        for index, raw_point in enumerate(raw_points):
            if not isinstance(raw_point, dict):
                continue
            latitude = _coordinate_value(raw_point, 'latitude')
            longitude = _coordinate_value(raw_point, 'longitude')
            if latitude is None or longitude is None:
                continue
            role = str(raw_point.get('role') or ('start' if index == 0 else 'end' if index == len(raw_points) - 1 else 'midpoint'))
            points.append({'latitude': latitude, 'longitude': longitude, 'role': role})
        roles = {point['role'] for point in points}
        if len(points) < 2 or 'start' not in roles or 'end' not in roles:
            raise InvalidSubmissionActionError('road stretch geometry requires captured start and end GPS points')
        length_km = sum(_haversine_km(points[i - 1], points[i]) for i in range(1, len(points)))
        if length_km <= 0:
            raise InvalidSubmissionActionError('road stretch geometry must calculate a positive length')
        normalized = {
            'geometry_type': 'LineString',
            'capture_method': str(payload.get('capture_method') or 'operator-gps'),
            'points': points,
            'calculated_length_km': round(length_km, 3),
            'evidence_source': str(payload.get('evidence_source') or 'field-intake'),
            'accuracy_note': str(payload.get('accuracy_note') or ''),
        }
        for optional_key in ('grid_cells', 'map_suggestion', 'stretch_midpoint', 'review_confidence', 'review_required'):
            if optional_key in payload:
                normalized[optional_key] = payload[optional_key]
        if 'map_suggestion' in normalized:
            normalized['review_required'] = True
        return _attach_field_evidence_metadata(normalized, payload)
    if submission_type == 'building':
        latitude = _coordinate_value(payload, 'latitude')
        longitude = _coordinate_value(payload, 'longitude')
        try:
            accuracy_meters = float(payload.get('accuracy_meters'))
        except (TypeError, ValueError):
            accuracy_meters = None
        if latitude is None or longitude is None or accuracy_meters is None:
            raise InvalidSubmissionActionError('building point evidence requires captured GPS point and accuracy')
        if accuracy_meters < 0 or accuracy_meters > 5000:
            raise InvalidSubmissionActionError('building point evidence has invalid accuracy')
        road_reference = str(payload.get('road_reference') or '').strip()
        if len(road_reference) < 2:
            raise InvalidSubmissionActionError('building point evidence requires a road or frontage reference')
        normalized = {
            'geometry_type': 'Point',
            'capture_method': str(payload.get('capture_method') or 'operator-gps'),
            'latitude': latitude,
            'longitude': longitude,
            'accuracy_meters': round(accuracy_meters, 2),
            'road_reference': road_reference,
            'evidence_source': str(payload.get('evidence_source') or 'field-intake'),
            'accuracy_note': str(payload.get('accuracy_note') or ''),
        }
        for optional_key in ('grid_cells', 'review_confidence', 'review_required'):
            if optional_key in payload:
                normalized[optional_key] = payload[optional_key]
        return _attach_field_evidence_metadata(normalized, payload)
    return payload


def validate_submission_spatial_evidence(submission: dict[str, Any]) -> None:
    submission_type = str(submission.get('submission_type') or '')
    if submission_type in {'road', 'building'}:
        normalize_submission_spatial_evidence(submission_type, submission.get('spatial_evidence'))


def _decode_spatial_evidence(item: dict[str, Any]) -> dict[str, Any]:
    item['spatial_evidence'] = _coerce_json_object(item.get('spatial_evidence'))
    return item


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
                       s.candidate_status, s.notes, s.submitted_by, s.review_status, s.reviewer_note, s.registry_entity_id, s.spatial_evidence, s.created_at
                FROM field_submissions s
                JOIN territories t ON t.id = s.territory_id
                ''' + where_sql + ' ORDER BY s.created_at DESC',
                params,
            )
            return [_decode_spatial_evidence(dict(row)) for row in cursor.fetchall()]


def create_field_submission(payload: dict[str, Any], actor: dict[str, str] | None = None) -> dict[str, Any]:
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
            spatial_evidence = normalize_submission_spatial_evidence(payload['submission_type'], payload.get('spatial_evidence'))
            cursor.execute(
                '''
                INSERT INTO field_submissions (
                    id, assignment_id, territory_id, submission_type, candidate_name,
                    candidate_status, notes, submitted_by, review_status, reviewer_note, registry_entity_id, spatial_evidence
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'submitted', '', NULL, %s::jsonb)
                RETURNING id, assignment_id, territory_id, submission_type, candidate_name, candidate_status, notes,
                          submitted_by, review_status, reviewer_note, registry_entity_id, spatial_evidence, created_at
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
                    json.dumps(spatial_evidence),
                ),
            )
            created = _decode_spatial_evidence(dict(cursor.fetchone()))
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
                       s.candidate_status, s.notes, s.submitted_by, s.review_status, s.reviewer_note, s.registry_entity_id, s.spatial_evidence, s.created_at
                FROM field_submissions s JOIN territories t ON t.id = s.territory_id WHERE s.id = %s
                ''',
                (submission_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise SubmissionNotFoundError('submission not found')
            return _decode_spatial_evidence(dict(row))


def attach_field_submission_evidence_file(submission_id: str, attachment_index: int, file_metadata: dict[str, Any], actor: dict[str, str] | None = None) -> dict[str, Any]:
    if attachment_index < 0:
        raise EvidenceAttachmentNotFoundError('evidence attachment not found')
    public_metadata = {
        'file_id': file_metadata['file_id'],
        'file_name': file_metadata['file_name'],
        'content_type': file_metadata['content_type'],
        'size_bytes': file_metadata['size_bytes'],
        'sha256': file_metadata['sha256'],
        'object_key': file_metadata['object_key'],
        'uploaded_by': actor['username'] if actor else file_metadata.get('uploaded_by', 'system'),
        'uploaded_at': file_metadata.get('uploaded_at') or datetime.now(timezone.utc).isoformat(),
        'access': 'protected',
    }
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT spatial_evidence FROM field_submissions WHERE id = %s FOR UPDATE', (submission_id,))
            row = cursor.fetchone()
            if not row:
                raise SubmissionNotFoundError('submission not found')
            spatial_evidence = _coerce_json_object(row.get('spatial_evidence'))
            attachments = spatial_evidence.get('evidence_attachments')
            if not isinstance(attachments, list) or attachment_index >= len(attachments):
                raise EvidenceAttachmentNotFoundError('evidence attachment not found')
            attachment = attachments[attachment_index]
            if not isinstance(attachment, dict):
                raise EvidenceAttachmentNotFoundError('evidence attachment not found')
            files = attachment.get('files')
            if not isinstance(files, list):
                files = []
            if len(files) >= 4:
                raise InvalidSubmissionActionError('evidence attachment file limit reached')
            files.append(public_metadata)
            attachment['files'] = files
            attachment['file_count'] = len(files)
            attachments[attachment_index] = attachment
            spatial_evidence['evidence_attachments'] = attachments
            spatial_evidence['evidence_file_count'] = sum(len(item.get('files', [])) for item in attachments if isinstance(item, dict))
            cursor.execute(
                'UPDATE field_submissions SET spatial_evidence = %s::jsonb, updated_at = NOW() WHERE id = %s',
                (json.dumps(spatial_evidence), submission_id),
            )
            _log_action(
                cursor,
                actor=actor,
                action='upload-evidence-file',
                entity_type='field_submission',
                entity_id=submission_id,
                details={
                    'file_id': public_metadata['file_id'],
                    'file_name': public_metadata['file_name'],
                    'content_type': public_metadata['content_type'],
                    'size_bytes': public_metadata['size_bytes'],
                    'attachment_index': attachment_index,
                    'access': 'protected',
                },
            )
        connection.commit()
    return get_submission(submission_id)


def _field_evidence_review_status(spatial_evidence: dict[str, Any]) -> str:
    attachments = spatial_evidence.get('evidence_attachments')
    if not isinstance(attachments, list) or not attachments:
        return 'not-required'
    decisions: list[str] = []
    for attachment in attachments:
        if not isinstance(attachment, dict):
            continue
        files = attachment.get('files')
        if isinstance(files, list) and files:
            decisions.extend(str(file_metadata.get('review_status') or 'pending') for file_metadata in files if isinstance(file_metadata, dict))
        else:
            decisions.append(str(attachment.get('review_status') or 'pending'))
    if not decisions:
        return 'not-required'
    if any(decision in {'rejected', 'needs-recapture'} for decision in decisions):
        return 'blocked'
    if any(decision == 'escalated' for decision in decisions):
        return 'escalated'
    if all(decision == 'accepted' for decision in decisions):
        return 'accepted'
    return 'pending'


def _field_evidence_approval_ready(spatial_evidence: dict[str, Any]) -> bool:
    return _field_evidence_review_status(spatial_evidence) in {'accepted', 'not-required'}


def review_field_submission_evidence(
    submission_id: str,
    attachment_index: int,
    decision: str,
    reviewer_note: str,
    file_id: str | None = None,
    actor: dict[str, str] | None = None,
) -> dict[str, Any]:
    if attachment_index < 0:
        raise EvidenceAttachmentNotFoundError('evidence attachment not found')
    if decision not in {'accepted', 'needs-recapture', 'rejected', 'escalated'}:
        raise InvalidSubmissionActionError('unsupported evidence review decision')
    reviewed_at = datetime.now(timezone.utc).isoformat()
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT spatial_evidence FROM field_submissions WHERE id = %s FOR UPDATE', (submission_id,))
            row = cursor.fetchone()
            if not row:
                raise SubmissionNotFoundError('submission not found')
            spatial_evidence = _coerce_json_object(row.get('spatial_evidence'))
            attachments = spatial_evidence.get('evidence_attachments')
            if not isinstance(attachments, list) or attachment_index >= len(attachments):
                raise EvidenceAttachmentNotFoundError('evidence attachment not found')
            attachment = attachments[attachment_index]
            if not isinstance(attachment, dict):
                raise EvidenceAttachmentNotFoundError('evidence attachment not found')
            reviewed_file_name = None
            if file_id:
                files = attachment.get('files')
                if not isinstance(files, list):
                    raise EvidenceAttachmentNotFoundError('evidence file not found')
                matched = False
                for file_metadata in files:
                    if isinstance(file_metadata, dict) and file_metadata.get('file_id') == file_id:
                        file_metadata['review_status'] = decision
                        file_metadata['reviewer_note'] = reviewer_note
                        file_metadata['reviewed_by'] = actor['username'] if actor else 'system'
                        file_metadata['reviewed_at'] = reviewed_at
                        reviewed_file_name = file_metadata.get('file_name')
                        matched = True
                        break
                if not matched:
                    raise EvidenceAttachmentNotFoundError('evidence file not found')
                attachment['files'] = files
            else:
                attachment['review_status'] = decision
                attachment['reviewer_note'] = reviewer_note
                attachment['reviewed_by'] = actor['username'] if actor else 'system'
                attachment['reviewed_at'] = reviewed_at
            attachments[attachment_index] = attachment
            spatial_evidence['evidence_attachments'] = attachments
            spatial_evidence['evidence_review_status'] = _field_evidence_review_status(spatial_evidence)
            cursor.execute(
                '''
                UPDATE field_submissions
                SET spatial_evidence = %s::jsonb,
                    reviewer_note = COALESCE(NULLIF(%s, ''), reviewer_note),
                    updated_at = NOW()
                WHERE id = %s
                ''',
                (json.dumps(spatial_evidence), reviewer_note, submission_id),
            )
            _log_action(
                cursor,
                actor=actor,
                action=f'evidence-{decision}',
                entity_type='field_submission',
                entity_id=submission_id,
                details={
                    'attachment_index': attachment_index,
                    'file_id': file_id,
                    'file_name': reviewed_file_name,
                    'decision': decision,
                    'reviewer_note': reviewer_note,
                    'access': 'protected',
                },
            )
        connection.commit()
    return get_submission(submission_id)


def list_field_submission_evidence_history(submission_id: str, limit: int = 50) -> list[dict[str, Any]]:
    get_submission(submission_id)
    evidence_actions = {'upload-evidence-file', 'download-evidence-file', 'evidence-accepted', 'evidence-needs-recapture', 'evidence-rejected', 'evidence-escalated'}
    return [
        item for item in list_audit_logs(entity_type='field_submission', entity_id=submission_id, limit=limit)
        if item.get('action') in evidence_actions
    ]


def get_field_submission_evidence_file(submission_id: str, file_id: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT spatial_evidence FROM field_submissions WHERE id = %s', (submission_id,))
            row = cursor.fetchone()
            if not row:
                raise SubmissionNotFoundError('submission not found')
            spatial_evidence = _coerce_json_object(row.get('spatial_evidence'))
            for attachment in spatial_evidence.get('evidence_attachments', []):
                if not isinstance(attachment, dict):
                    continue
                for file_metadata in attachment.get('files', []):
                    if isinstance(file_metadata, dict) and file_metadata.get('file_id') == file_id:
                        _log_action(
                            cursor,
                            actor=actor,
                            action='download-evidence-file',
                            entity_type='field_submission',
                            entity_id=submission_id,
                            details={'file_id': file_id, 'file_name': file_metadata.get('file_name'), 'access': 'protected'},
                        )
                        connection.commit()
                        return file_metadata
            raise EvidenceAttachmentNotFoundError('evidence file not found')


def approve_submission(submission_id: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM field_submissions WHERE id = %s', (submission_id,))
            submission = cursor.fetchone()
            if not submission:
                raise SubmissionNotFoundError('submission not found')

            submission = _decode_spatial_evidence(dict(submission))
            stored_spatial_evidence = _coerce_json_object(submission.get('spatial_evidence'))
            if not _field_evidence_approval_ready(stored_spatial_evidence):
                raise InvalidSubmissionActionError('protected evidence review must be accepted before approval')
            spatial_evidence = normalize_submission_spatial_evidence(submission['submission_type'], stored_spatial_evidence)
            spatial_evidence['evidence_review_status'] = _field_evidence_review_status(stored_spatial_evidence)
            registry_entity_id = submission['registry_entity_id']
            candidate_payload = {
                'territory_id': submission['territory_id'],
                'status': submission['candidate_status'],
                'notes': submission['notes'],
                'spatial_evidence': spatial_evidence,
            }

            if submission['submission_type'] == 'road':
                payload = {'name': submission['candidate_name'], 'territory_id': submission['territory_id'], 'status': submission['candidate_status'], 'length_km': str(spatial_evidence.get('calculated_length_km', '0')), 'spatial_evidence': spatial_evidence}
                if registry_entity_id and _entity_exists(cursor, 'roads', registry_entity_id):
                    cursor.execute('UPDATE roads SET status = %s, length_km = %s, spatial_evidence = %s::jsonb, updated_at = NOW() WHERE id = %s', (payload['status'], payload['length_km'], json.dumps(spatial_evidence), registry_entity_id))
                else:
                    created = create_road(payload, actor=actor)
                    registry_entity_id = created['id']
            elif submission['submission_type'] == 'building':
                cursor.execute('SELECT id, name FROM roads WHERE territory_id = %s AND is_archived = FALSE ORDER BY name ASC LIMIT 1', (submission['territory_id'],))
                road = cursor.fetchone()
                if not road:
                    road = create_road({'name': f"Support Road for {submission['candidate_name']}", 'territory_id': submission['territory_id'], 'status': 'verified', 'length_km': '0.5'}, actor=actor)
                road_id = road['id'] if isinstance(road, dict) else road['id']
                payload = {'label': submission['candidate_name'], 'territory_id': submission['territory_id'], 'road_id': road_id, 'status': submission['candidate_status'], 'usage': 'field-captured', 'spatial_evidence': spatial_evidence}
                if registry_entity_id and _entity_exists(cursor, 'buildings', registry_entity_id):
                    cursor.execute('UPDATE buildings SET status = %s, spatial_evidence = %s::jsonb, updated_at = NOW() WHERE id = %s', (payload['status'], json.dumps(spatial_evidence), registry_entity_id))
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
                SELECT a.id, a.formatted, a.public_code, a.status, a.publication_state, a.verification_status,
                       a.issuance_method, a.source, t.name AS territory_name, p.name AS province_name,
                       ap.latitude, ap.longitude, ap.accuracy_meters
                FROM addresses a
                JOIN territories t ON t.id = a.territory_id
                JOIN provinces p ON p.code = a.province_code
                LEFT JOIN address_points ap ON ap.address_id = a.id AND ap.is_active = TRUE
                WHERE a.is_archived = FALSE AND a.publication_state = 'published'
                  AND (LOWER(a.id) = LOWER(%s) OR LOWER(COALESCE(a.public_code, '')) = LOWER(%s) OR LOWER(a.formatted) LIKE %s)
                ORDER BY a.updated_at DESC
                LIMIT 1
                ''',
                (query, query, like),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                'query': query,
                'match_status': 'verified',
                'public_code': row['public_code'],
                'address_label': row['formatted'],
                'jurisdiction': f"{row['territory_name']} · {row['province_name']}",
                'verification_status': row['verification_status'],
                'publication_state': row['publication_state'],
                'issuance_method': row['issuance_method'],
                'source': row['source'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'accuracy_meters': row['accuracy_meters'],
                'verification_note': f"Published registry record found with status {row['status']} and verification level {row['verification_status']}.",
                'address_id': row['id'],
            }


def create_address_correction(payload: dict[str, Any], actor: dict[str, str] | None = None) -> dict[str, Any]:
    correction_id = f"correction-{secrets.token_hex(4)}"
    with db_connection() as connection:
        with connection.cursor() as cursor:
            address_id = payload.get('address_id')
            public_code = payload.get('public_code')
            if address_id:
                cursor.execute('SELECT id, public_code FROM addresses WHERE id = %s', (address_id,))
                address = cursor.fetchone()
                if not address:
                    raise AddressNotFoundError('address not found')
                public_code = public_code or address['public_code']
            cursor.execute(
                '''
                INSERT INTO address_corrections (
                    id, address_id, public_code, query, correction_type, reason,
                    note, reporter_name, reporter_contact, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'submitted')
                RETURNING id, address_id, public_code, query, correction_type, reason, note,
                          reporter_name, reporter_contact, status, created_at
                ''',
                (
                    correction_id,
                    address_id,
                    public_code,
                    payload['query'],
                    payload['correction_type'],
                    payload['reason'],
                    payload.get('note', ''),
                    payload.get('reporter_name'),
                    payload.get('reporter_contact'),
                ),
            )
            created = cursor.fetchone()
            _log_action(cursor, actor=actor, action='create', entity_type='address_correction', entity_id=correction_id, details=payload)
        connection.commit()
    return dict(created)


def list_address_corrections(status: str | None = None) -> list[dict[str, Any]]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if status:
        where_clauses.append('c.status = %s')
        params.append(status)
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT c.id, c.address_id, c.public_code, c.query, c.correction_type, c.reason, c.note,
                       c.reporter_name, c.reporter_contact, c.status, c.reviewer_note, c.created_at, c.updated_at,
                       a.formatted AS address_label, t.name AS territory_name, p.name AS province_name
                FROM address_corrections c
                LEFT JOIN addresses a ON a.id = c.address_id
                LEFT JOIN territories t ON t.id = a.territory_id
                LEFT JOIN provinces p ON p.code = a.province_code
                ''' + where_sql + ' ORDER BY c.created_at DESC',
                params,
            )
            items = list(cursor.fetchall())
    for item in items:
        territory = item.pop('territory_name', None)
        province = item.pop('province_name', None)
        item['jurisdiction'] = f'{territory} · {province}' if territory and province else None
    return items


def get_address_correction(correction_id: str) -> dict[str, Any]:
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT c.id, c.address_id, c.public_code, c.query, c.correction_type, c.reason, c.note,
                       c.reporter_name, c.reporter_contact, c.status, c.reviewer_note, c.created_at, c.updated_at,
                       a.formatted AS address_label, t.name AS territory_name, p.name AS province_name
                FROM address_corrections c
                LEFT JOIN addresses a ON a.id = c.address_id
                LEFT JOIN territories t ON t.id = a.territory_id
                LEFT JOIN provinces p ON p.code = a.province_code
                WHERE c.id = %s
                ''',
                (correction_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise AddressCorrectionNotFoundError('address correction not found')
            item = dict(row)
    territory = item.pop('territory_name', None)
    province = item.pop('province_name', None)
    item['jurisdiction'] = f'{territory} · {province}' if territory and province else None
    return item


def update_address_correction_status(correction_id: str, next_status: str, reviewer_note: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    if next_status not in {'under-review', 'resolved', 'rejected'}:
        raise InvalidSubmissionActionError('unsupported correction status')
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE address_corrections
                SET status = %s, reviewer_note = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING id
                ''',
                (next_status, reviewer_note, correction_id),
            )
            updated = cursor.fetchone()
            if not updated:
                raise AddressCorrectionNotFoundError('address correction not found')
            _log_action(cursor, actor=actor, action=next_status, entity_type='address_correction', entity_id=correction_id, details={'reviewer_note': reviewer_note})
        connection.commit()
    return get_address_correction(correction_id)



def generate_grid_code(latitude: float, longitude: float, province_code: str | None = None) -> str:
    return generate_national_address_code(latitude, longitude, province_code)


def describe_address_code(code: str) -> dict[str, Any]:
    return validate_national_address_code(code)


def _haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_geotag_duplicate_hints(latitude: float, longitude: float, max_distance_meters: float = 75) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT a.id, a.formatted AS label, a.public_code AS code, ap.latitude, ap.longitude, 'published-address' AS source
                FROM address_points ap
                JOIN addresses a ON a.id = ap.address_id
                WHERE ap.is_active = TRUE AND a.is_archived = FALSE
                '''
            )
            rows = list(cursor.fetchall())
            cursor.execute(
                '''
                SELECT id, address_label AS label, grid_code AS code, latitude, longitude, 'citizen-submission' AS source
                FROM citizen_geotag_submissions
                WHERE status NOT IN ('rejected')
                ORDER BY created_at DESC
                LIMIT 500
                '''
            )
            rows.extend(list(cursor.fetchall()))
    for row in rows:
        distance = _haversine_meters(latitude, longitude, row['latitude'], row['longitude'])
        if distance <= max_distance_meters:
            hints.append({'source': row['source'], 'id': row['id'], 'label': row['label'], 'code': row['code'], 'distance_meters': round(distance, 1)})
    return sorted(hints, key=lambda item: item['distance_meters'])[:8]


def _normalise_routing_area_name(value: str | None) -> str:
    if not value:
        return ''
    decomposed = unicodedata.normalize('NFKD', value)
    ascii_text = ''.join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r'[^a-z0-9]+', ' ', ascii_text.lower()).strip()


def resolve_geotag_routing_area(
    territory_rows: list[dict[str, Any]],
    *,
    suggested_local_area: str | None,
    province_code: str | None,
) -> dict[str, str] | None:
    """Resolve an official routing area only from exact registry-backed local-area matches.

    This intentionally avoids assigning broad district/core areas from coordinates alone. Map labels
    become official routing only when their normalized local-area name exactly matches a registered
    map-referenced local area in the same province.
    """
    normalised_suggestion = _normalise_routing_area_name(suggested_local_area)
    if not normalised_suggestion or not province_code:
        return None
    candidates = [
        row for row in territory_rows
        if row.get('province_code') == province_code
        and row.get('type') == 'map-referenced-local-area'
        and _normalise_routing_area_name(row.get('name')) == normalised_suggestion
    ]
    if len(candidates) != 1:
        return None
    territory = candidates[0]
    return {
        'territory_id': territory['id'],
        'territory_name': territory['name'],
        'routing_assignment_source': 'map-local-area-exact-match',
        'routing_assignment_confidence': 'high',
    }


def preview_citizen_geotag(latitude: float, longitude: float, territory_id: str | None = None, province_code: str | None = None) -> dict[str, Any]:
    territory_name = None
    if territory_id:
        with db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT name, province_code FROM territories WHERE id = %s AND is_archived = FALSE', (territory_id,))
                territory = cursor.fetchone()
                if not territory:
                    raise UnknownTerritoryError('unknown territory')
                province_code = territory['province_code']
                territory_name = territory['name']
    grid_code = generate_grid_code(latitude, longitude, province_code)
    address_code = describe_address_code(grid_code)
    duplicate_hints = find_geotag_duplicate_hints(latitude, longitude, max_distance_meters=75)
    return {
        'grid_code': grid_code,
        'address_code': address_code,
        'territory_id': territory_id,
        'territory_name': territory_name,
        'latitude': latitude,
        'longitude': longitude,
        'duplicate_hints': duplicate_hints,
        'signage_label': f'{grid_code} · national address point',
    }


def create_citizen_geotag_submission(payload: dict[str, Any], actor: dict[str, str] | None = None) -> dict[str, Any]:
    latitude = float(payload['latitude'])
    longitude = float(payload['longitude'])
    territory_id = payload.get('territory_id')
    province_code = payload.get('province_code')
    territory_name = None
    routing_assignment: dict[str, str] | None = None
    with db_connection() as connection:
        with connection.cursor() as cursor:
            if territory_id:
                cursor.execute('SELECT name, province_code FROM territories WHERE id = %s AND is_archived = FALSE', (territory_id,))
                territory = cursor.fetchone()
                if not territory:
                    raise UnknownTerritoryError('unknown territory')
                province_code = territory['province_code']
                territory_name = territory['name']
            else:
                cursor.execute('SELECT id, name, province_code, type FROM territories WHERE is_archived = FALSE')
                routing_assignment = resolve_geotag_routing_area(
                    list(cursor.fetchall()),
                    suggested_local_area=payload.get('suggested_local_area'),
                    province_code=province_code,
                )
                if routing_assignment:
                    territory_id = routing_assignment['territory_id']
                    territory_name = routing_assignment['territory_name']
            grid_code = generate_grid_code(latitude, longitude, province_code)
            address_code = describe_address_code(grid_code)
            duplicate_hints = find_geotag_duplicate_hints(latitude, longitude, max_distance_meters=75)
            duplicate_hint = 'possible-duplicate' if duplicate_hints else 'none'
            submission_id = f"citizen-geotag-{_slugify(grid_code)}-{secrets.token_hex(3)}"
            cursor.execute(
                '''
                INSERT INTO citizen_geotag_submissions (
                    id, territory_id, address_label, citizen_name, citizen_contact, dip_last4, landmark,
                    latitude, longitude, accuracy_meters, capture_method, grid_code, status, duplicate_hint,
                    suggested_road_name, suggested_local_area, suggested_place_name, map_display_name,
                    road_suggestion_source, road_suggestion_attribution, road_suggestion_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'submitted', %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, territory_id, address_label, citizen_name, citizen_contact, dip_last4,
                          identity_verification_status, identity_document_verified, identity_verified_at, landmark,
                          latitude, longitude, accuracy_meters, capture_method, grid_code, status,
                          duplicate_hint, reviewer_note, suggested_road_name, suggested_local_area,
                          suggested_place_name, map_display_name, road_suggestion_source,
                          road_suggestion_attribution, road_suggestion_status, reviewed_road_name,
                          field_submission_id, signage_batch, created_at, updated_at
                ''',
                (
                    submission_id,
                    territory_id,
                    payload['address_label'],
                    payload.get('citizen_name'),
                    payload.get('citizen_contact'),
                    payload.get('dip_last4'),
                    payload.get('landmark', ''),
                    latitude,
                    longitude,
                    payload.get('accuracy_meters'),
                    payload.get('capture_method', 'browser-gps'),
                    grid_code,
                    duplicate_hint,
                    payload.get('suggested_road_name'),
                    payload.get('suggested_local_area'),
                    payload.get('suggested_place_name'),
                    payload.get('map_display_name'),
                    payload.get('road_suggestion_source'),
                    payload.get('road_suggestion_attribution'),
                    'pending-review' if any(payload.get(key) for key in ('suggested_road_name', 'suggested_local_area', 'suggested_place_name')) else 'not-suggested',
                ),
            )
            created = dict(cursor.fetchone())
            _log_action(cursor, actor=actor, action='create', entity_type='citizen_geotag_submission', entity_id=submission_id, details={'grid_code': grid_code, 'address_code': address_code, 'duplicate_hint': duplicate_hint, 'routing_assignment': routing_assignment})
        connection.commit()
    return {**created, 'address_code': address_code, 'territory_name': territory_name, 'duplicate_hints': duplicate_hints, 'routing_assignment': routing_assignment, 'signage_label': f"{created['grid_code']} · {created['address_label']}"}


def list_citizen_geotag_submissions(status: str | None = None, territory_id: str | None = None) -> list[dict[str, Any]]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if status:
        where_clauses.append('g.status = %s')
        params.append(status)
    if territory_id:
        where_clauses.append('g.territory_id = %s')
        params.append(territory_id)
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT g.id, g.territory_id, t.name AS territory_name, g.address_label, g.citizen_name,
                       g.citizen_contact, g.dip_last4, g.identity_verification_status,
                       g.identity_document_verified, g.identity_verified_at,
                       g.landmark, g.latitude, g.longitude, g.accuracy_meters,
                       g.capture_method, g.grid_code, g.status, g.duplicate_hint, g.reviewer_note,
                       g.suggested_road_name, g.suggested_local_area, g.suggested_place_name,
                       g.map_display_name, g.road_suggestion_source, g.road_suggestion_attribution,
                       g.road_suggestion_status, g.reviewed_road_name,
                       g.field_submission_id, g.field_status, g.field_note, g.field_verified_at,
                       g.signage_batch, g.created_at, g.updated_at
                FROM citizen_geotag_submissions g
                LEFT JOIN territories t ON t.id = g.territory_id
                ''' + where_sql + ' ORDER BY g.created_at DESC',
                params,
            )
            rows = list(cursor.fetchall())
            for row in rows:
                row['address_code'] = describe_address_code(row['grid_code'])
                row['dip_masked'] = f"****{row['dip_last4']}" if row.get('dip_last4') else None
            return rows


def update_citizen_geotag_status(submission_id: str, next_status: str, reviewer_note: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    if next_status not in {'under-review', 'needs-field-check', 'rejected', 'registry-ready', 'published'}:
        raise InvalidSubmissionActionError('unsupported geotag status')
    field_submission_id = None
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM citizen_geotag_submissions WHERE id = %s', (submission_id,))
            existing = cursor.fetchone()
            if not existing:
                raise SubmissionNotFoundError('citizen geotag submission not found')
            if next_status in {'needs-field-check', 'registry-ready'} and not existing['field_submission_id'] and existing['territory_id']:
                field_payload = {
                    'assignment_id': None,
                    'territory_id': existing['territory_id'],
                    'submission_type': 'address',
                    'candidate_name': existing['address_label'],
                    'candidate_status': 'submitted' if next_status == 'needs-field-check' else 'registry-ready',
                    'notes': f"Citizen geotag {existing['grid_code']} at {existing['latitude']}, {existing['longitude']}. Landmark: {existing['landmark']}. Accuracy: {existing['accuracy_meters'] or 'not recorded'} m.",
                    'submitted_by': 'citizen-geotag-intake',
                }
                field_submission = create_field_submission(field_payload, actor=actor)
                field_submission_id = field_submission['id']
            else:
                field_submission_id = existing['field_submission_id']
            signage_batch = existing['signage_batch'] or (f"signage-{secrets.token_hex(3)}" if next_status == 'published' else None)
            cursor.execute(
                '''
                UPDATE citizen_geotag_submissions
                SET status = %s, reviewer_note = %s, field_submission_id = COALESCE(%s, field_submission_id),
                    signage_batch = COALESCE(%s, signage_batch), updated_at = NOW()
                WHERE id = %s
                ''',
                (next_status, reviewer_note, field_submission_id, signage_batch, submission_id),
            )
            _log_action(cursor, actor=actor, action=next_status, entity_type='citizen_geotag_submission', entity_id=submission_id, details={'reviewer_note': reviewer_note, 'field_submission_id': field_submission_id})
        connection.commit()
    return next(item for item in list_citizen_geotag_submissions() if item['id'] == submission_id)


def record_geotag_duplicate_decision(submission_id: str, duplicate_action: str, reviewer_note: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    allowed_actions = {
        'same-property-merge': 'under-review',
        'different-property-same-cell': 'under-review',
        'gps-error-recapture': 'needs-field-check',
        'send-field-verification': 'needs-field-check',
    }
    if duplicate_action not in allowed_actions:
        raise InvalidSubmissionActionError('unsupported duplicate decision')
    note = f'Duplicate decision: {duplicate_action}. {reviewer_note}'.strip()
    updated = update_citizen_geotag_status(submission_id, allowed_actions[duplicate_action], note, actor=actor)
    updated['duplicate_resolution'] = duplicate_action
    return updated


def verify_geotag_identity(submission_id: str, dip_full: str, identity_document_verified: bool, reviewer_note: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    if not dip_full.isdigit() or not (6 <= len(dip_full) <= 20):
        raise InvalidSubmissionActionError('D.I.P. must be 6 to 20 digits')
    dip_last4 = dip_full[-4:]
    status_value = 'verified' if identity_document_verified else 'recorded-unverified'
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE citizen_geotag_submissions
                SET dip_last4 = %s,
                    identity_verification_status = %s,
                    identity_document_verified = %s,
                    identity_verified_at = NOW(),
                    reviewer_note = COALESCE(NULLIF(%s, ''), reviewer_note),
                    updated_at = NOW()
                WHERE id = %s
                RETURNING id
                ''',
                (dip_last4, status_value, identity_document_verified, reviewer_note, submission_id),
            )
            if not cursor.fetchone():
                raise SubmissionNotFoundError('citizen geotag submission not found')
            _log_action(
                cursor,
                actor=actor,
                action='identity-verified' if identity_document_verified else 'identity-recorded-unverified',
                entity_type='citizen_geotag_submission',
                entity_id=submission_id,
                details={'dip_masked': f'****{dip_last4}', 'identity_document_verified': identity_document_verified, 'reviewer_note': reviewer_note},
            )
        connection.commit()
    return next(item for item in list_citizen_geotag_submissions() if item['id'] == submission_id)


def review_geotag_road_suggestion(submission_id: str, action: str, reviewed_road_name: str | None, reviewer_note: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    if action not in {'accepted', 'edited', 'rejected'}:
        raise InvalidSubmissionActionError('unsupported road suggestion action')
    if action in {'accepted', 'edited'} and not reviewed_road_name:
        raise InvalidSubmissionActionError('reviewed road name is required')
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE citizen_geotag_submissions
                SET road_suggestion_status = %s,
                    reviewed_road_name = %s,
                    reviewer_note = COALESCE(NULLIF(%s, ''), reviewer_note),
                    updated_at = NOW()
                WHERE id = %s
                RETURNING id
                ''',
                (action, reviewed_road_name if action != 'rejected' else None, reviewer_note, submission_id),
            )
            if not cursor.fetchone():
                raise SubmissionNotFoundError('citizen geotag submission not found')
            _log_action(
                cursor,
                actor=actor,
                action=f'road-suggestion-{action}',
                entity_type='citizen_geotag_submission',
                entity_id=submission_id,
                details={'reviewed_road_name': reviewed_road_name, 'reviewer_note': reviewer_note},
            )
        connection.commit()
    return next(item for item in list_citizen_geotag_submissions() if item['id'] == submission_id)


def list_geotag_field_tasks(status: str | None = None, territory_id: str | None = None) -> list[dict[str, Any]]:
    task_statuses = {'needs-field-check'}
    rows = list_citizen_geotag_submissions(status=status, territory_id=territory_id) if status else [
        item for item in list_citizen_geotag_submissions(territory_id=territory_id) if item['status'] in task_statuses or item.get('field_status') in {'visited', 'verified', 'needs-recapture', 'blocked'}
    ]
    return rows


def update_geotag_field_status(submission_id: str, field_status: str, field_note: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    if field_status not in {'assigned', 'visited', 'verified', 'needs-recapture', 'blocked'}:
        raise InvalidSubmissionActionError('unsupported field task status')
    next_status = 'under-review' if field_status == 'verified' else 'needs-field-check'
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE citizen_geotag_submissions
                SET field_status = %s,
                    field_note = COALESCE(NULLIF(%s, ''), field_note),
                    field_verified_at = CASE WHEN %s = 'verified' THEN NOW() ELSE field_verified_at END,
                    status = %s,
                    reviewer_note = COALESCE(NULLIF(%s, ''), reviewer_note),
                    updated_at = NOW()
                WHERE id = %s
                RETURNING id
                ''',
                (field_status, field_note, field_status, next_status, field_note, submission_id),
            )
            if not cursor.fetchone():
                raise SubmissionNotFoundError('citizen geotag submission not found')
            _log_action(
                cursor,
                actor=actor,
                action=f'field-{field_status}',
                entity_type='citizen_geotag_submission',
                entity_id=submission_id,
                details={'field_status': field_status, 'field_note': field_note},
            )
        connection.commit()
    return next(item for item in list_citizen_geotag_submissions() if item['id'] == submission_id)


def record_geotag_field_evidence(
    submission_id: str,
    evidence_type: str,
    evidence_reference: str,
    evidence_note: str,
    actor: dict[str, str] | None = None,
) -> dict[str, Any]:
    if evidence_type not in {'photo-reference', 'site-note', 'landmark-confirmation', 'coordinate-confirmation'}:
        raise InvalidSubmissionActionError('unsupported field evidence type')
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id, field_status FROM citizen_geotag_submissions WHERE id = %s', (submission_id,))
            existing = cursor.fetchone()
            if not existing:
                raise SubmissionNotFoundError('citizen geotag submission not found')
            next_field_status = existing.get('field_status') or 'visited'
            if next_field_status == 'assigned':
                next_field_status = 'visited'
            cursor.execute(
                '''
                UPDATE citizen_geotag_submissions
                SET field_status = %s,
                    field_note = COALESCE(NULLIF(%s, ''), field_note),
                    updated_at = NOW()
                WHERE id = %s
                ''',
                (next_field_status, evidence_note, submission_id),
            )
            _log_action(
                cursor,
                actor=actor,
                action='field-evidence-recorded',
                entity_type='citizen_geotag_submission',
                entity_id=submission_id,
                details={
                    'evidence_type': evidence_type,
                    'evidence_reference': evidence_reference,
                    'evidence_note': evidence_note,
                    'public_safe': True,
                },
            )
        connection.commit()
    return {
        'submission_id': submission_id,
        'evidence_type': evidence_type,
        'evidence_reference': evidence_reference,
        'evidence_note': evidence_note,
        'field_status': next_field_status,
        'public_safe': True,
    }


def simulate_geotag_publication_path(submission_id: str, reviewer_note: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    items = [item for item in list_citizen_geotag_submissions() if item['id'] == submission_id]
    if not items:
        raise SubmissionNotFoundError('citizen geotag submission not found')
    item = items[0]
    if item.get('status') not in {'registry-ready', 'published'}:
        raise InvalidSubmissionActionError('publication simulation requires a registry-ready case file')
    with db_connection() as connection:
        with connection.cursor() as cursor:
            _log_action(
                cursor,
                actor=actor,
                action='publication-simulation',
                entity_type='citizen_geotag_submission',
                entity_id=submission_id,
                details={'reviewer_note': reviewer_note, 'resulting_record_status': item.get('status')},
            )
        connection.commit()
    return {
        'submission_id': submission_id,
        'address_code': item.get('grid_code'),
        'simulation_status': 'simulated-publication-path',
        'public_release_locked': True,
        'physical_signage_locked': True,
        'resulting_record_status': item.get('status'),
        'would_create_public_lookup': True,
        'would_create_certificate': True,
        'would_create_signage_batch': True,
        'operator_note': 'Simulation only. Full project/institutional approval is required before publication, certificates, or physical signage.',
    }


def publish_geotag_submission(submission_id: str, reviewer_note: str, actor: dict[str, str] | None = None) -> dict[str, Any]:
    items = [item for item in list_citizen_geotag_submissions() if item['id'] == submission_id]
    if not items:
        raise SubmissionNotFoundError('citizen geotag submission not found')
    current = items[0]
    if current.get('status') not in {'registry-ready', 'published'}:
        raise InvalidSubmissionActionError('publication requires a registry-ready case file')

    published = update_citizen_geotag_status(submission_id, 'published', reviewer_note, actor=actor)
    address_record = upsert_address_record_from_geotag(published, actor=actor)

    with db_connection() as connection:
        with connection.cursor() as cursor:
            _log_action(
                cursor,
                actor=actor,
                action='publication-approved',
                entity_type='citizen_geotag_submission',
                entity_id=submission_id,
                details={
                    'reviewer_note': reviewer_note,
                    'address_code': published.get('grid_code'),
                    'signage_batch': published.get('signage_batch'),
                    'address_record_id': address_record.get('id'),
                },
            )
            cursor.execute(
                '''
                INSERT INTO address_record_events (
                    id, address_record_id, event_type, actor_id, actor_username, actor_role, details
                ) VALUES (%s, %s, 'publication-approved', %s, %s, %s, %s::jsonb)
                ''',
                (
                    f"address-record-event-{secrets.token_hex(8)}",
                    address_record['id'],
                    actor.get('id') if actor else None,
                    actor.get('username') if actor else None,
                    actor.get('role') if actor else None,
                    json.dumps({'reviewer_note': reviewer_note, 'source_submission_id': submission_id}),
                ),
            )
        connection.commit()

    return {
        **published,
        'address_record': address_record,
        'publication': {
            'public_release': 'published',
            'signage_export_status': 'ready-for-export',
            'certificate_status': 'ready',
            'proof_status': 'public-proof-ready',
            'operator_note': 'Published after explicit institutional release approval.',
        },
    }


def geotag_duplicate_summary() -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in list_citizen_geotag_submissions():
        groups.setdefault(item['grid_code'], []).append(item)
    active_statuses = {'submitted', 'under-review', 'needs-field-check'}
    duplicate_groups = []
    for grid_code, items in groups.items():
        if len(items) < 2:
            continue
        duplicate_groups.append({
            'grid_code': grid_code,
            'count': len(items),
            'active_count': sum(1 for item in items if item['status'] in active_statuses),
            'resolved_count': sum(1 for item in items if item['status'] not in active_statuses),
            'items': [
                {
                    'id': item['id'],
                    'address_label': item['address_label'],
                    'status': item['status'],
                    'territory_name': item.get('territory_name'),
                    'field_status': item.get('field_status'),
                }
                for item in items
            ],
        })
    duplicate_groups.sort(key=lambda group: (-group['active_count'], -group['count'], group['grid_code']))
    return {'groups': duplicate_groups}


def build_address_record_bundle(geotag: dict[str, Any]) -> dict[str, Any]:
    address_code = geotag['grid_code']
    province_code = geotag.get('province_code') or (address_code.split('-')[1] if '-' in address_code else None)
    raw_routing_assignment = geotag.get('routing_assignment')
    routing_assignment: dict[str, Any] = raw_routing_assignment if isinstance(raw_routing_assignment, dict) else {}
    reviewed_road = geotag.get('reviewed_road_name') or geotag.get('suggested_road_name')
    return {
        'identity': {
            'address_code': address_code,
            'source_submission_id': geotag.get('id'),
            'schema': (geotag.get('address_code') or {}).get('schema') if isinstance(geotag.get('address_code'), dict) else None,
            'status': geotag.get('status'),
            'publication_state': 'published' if geotag.get('status') == 'published' else 'internal-registry',
        },
        'location': {
            'latitude': geotag.get('latitude'),
            'longitude': geotag.get('longitude'),
            'accuracy_meters': geotag.get('accuracy_meters'),
            'capture_method': geotag.get('capture_method'),
            'crs': 'EPSG:4326',
        },
        'jurisdiction': {
            'province_code': province_code,
            'routing_area_id': geotag.get('territory_id'),
            'routing_area_name': geotag.get('territory_name'),
        },
        'routing': {
            'territory_id': geotag.get('territory_id'),
            'territory_name': geotag.get('territory_name'),
            'assignment_source': routing_assignment.get('routing_assignment_source') or ('operator-confirmed' if geotag.get('territory_id') else None),
            'assignment_confidence': routing_assignment.get('routing_assignment_confidence') or ('confirmed' if geotag.get('territory_id') else None),
        },
        'search': {
            'address_label': geotag.get('address_label'),
            'landmark': geotag.get('landmark'),
            'road_name': reviewed_road,
            'suggested_local_area': geotag.get('suggested_local_area'),
            'map_display_name': geotag.get('map_display_name'),
        },
        'workflow': {
            'current_stage': geotag.get('status'),
            'field_status': geotag.get('field_status'),
            'road_suggestion_status': geotag.get('road_suggestion_status'),
            'reviewer_note': geotag.get('reviewer_note'),
        },
        'evidence': {
            'gps_capture': {
                'present': geotag.get('latitude') is not None and geotag.get('longitude') is not None,
                'accuracy_meters': geotag.get('accuracy_meters'),
                'capture_method': geotag.get('capture_method'),
            },
            'field_verification': {
                'status': geotag.get('field_status'),
                'verified_at': geotag.get('field_verified_at'),
            },
            'road_review': {
                'suggested_road_name': geotag.get('suggested_road_name'),
                'reviewed_road_name': geotag.get('reviewed_road_name'),
                'source': geotag.get('road_suggestion_source'),
                'status': geotag.get('road_suggestion_status'),
            },
        },
        'outputs': {
            'signage_batch': geotag.get('signage_batch') if geotag.get('status') == 'published' else None,
            'public_lookup_url': f"/code/{address_code}",
            'certificate_id': f"CERT-{address_code}" if geotag.get('status') == 'published' else None,
            'physical_rollout_status': 'approved-for-rollout' if geotag.get('status') == 'published' else 'awaiting-full-project-approval',
        },
    }


def _address_record_search_text(geotag: dict[str, Any], bundle: dict[str, Any]) -> str:
    parts = [
        geotag.get('grid_code'),
        geotag.get('address_label'),
        geotag.get('landmark'),
        geotag.get('territory_name'),
        geotag.get('reviewed_road_name'),
        geotag.get('suggested_road_name'),
        geotag.get('suggested_local_area'),
        geotag.get('suggested_place_name'),
        geotag.get('map_display_name'),
        bundle.get('jurisdiction', {}).get('province_code'),
    ]
    return ' '.join(str(part) for part in parts if part)


def _address_record_row(row: dict[str, Any]) -> dict[str, Any]:
    item = dict(row)
    bundle = item.get('record_bundle')
    if isinstance(bundle, str):
        item['record_bundle'] = json.loads(bundle)
    return item


def upsert_address_record_from_geotag(geotag: dict[str, Any], actor: dict[str, str] | None = None) -> dict[str, Any]:
    if geotag.get('status') not in {'registry-ready', 'published'}:
        raise InvalidSubmissionActionError('canonical address record requires registry-ready geotag')
    bundle = build_address_record_bundle(geotag)
    address_code = geotag['grid_code']
    record_id = f"address-record-{_slugify(address_code)}"
    province_code = bundle['jurisdiction']['province_code']
    publication_state = bundle['identity']['publication_state']
    search_text = _address_record_search_text(geotag, bundle)
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO address_records (
                    id, address_code, source_submission_id, province_code, territory_id, address_label,
                    status, publication_state, latitude, longitude, accuracy_meters, search_text, record_bundle
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (address_code) DO UPDATE SET
                    source_submission_id = EXCLUDED.source_submission_id,
                    province_code = EXCLUDED.province_code,
                    territory_id = EXCLUDED.territory_id,
                    address_label = EXCLUDED.address_label,
                    status = EXCLUDED.status,
                    publication_state = EXCLUDED.publication_state,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    accuracy_meters = EXCLUDED.accuracy_meters,
                    search_text = EXCLUDED.search_text,
                    record_bundle = EXCLUDED.record_bundle,
                    updated_at = NOW()
                RETURNING *
                ''',
                (
                    record_id,
                    address_code,
                    geotag.get('id'),
                    province_code,
                    geotag.get('territory_id'),
                    geotag.get('address_label'),
                    geotag.get('status'),
                    publication_state,
                    geotag.get('latitude'),
                    geotag.get('longitude'),
                    geotag.get('accuracy_meters'),
                    search_text,
                    json.dumps(bundle),
                ),
            )
            record = _address_record_row(cursor.fetchone())
            event_id = f"address-record-event-{secrets.token_hex(8)}"
            cursor.execute(
                '''
                INSERT INTO address_record_events (
                    id, address_record_id, event_type, actor_id, actor_username, actor_role, details
                ) VALUES (%s, %s, 'address-record-upserted', %s, %s, %s, %s::jsonb)
                ''',
                (
                    event_id,
                    record['id'],
                    actor.get('id') if actor else None,
                    actor.get('username') if actor else None,
                    actor.get('role') if actor else None,
                    json.dumps({'source_submission_id': geotag.get('id'), 'address_code': address_code}),
                ),
            )
        connection.commit()
    return record


def search_address_records(q: str | None = None, status: str | None = None, province_code: str | None = None, limit: int = 25) -> list[dict[str, Any]]:
    where_clauses: list[str] = []
    params: list[Any] = []
    if q:
        where_clauses.append('(address_code ILIKE %s OR search_text ILIKE %s)')
        like = f"%{q}%"
        params.extend([like, like])
    if status:
        where_clauses.append('status = %s')
        params.append(status)
    if province_code:
        where_clauses.append('province_code = %s')
        params.append(province_code)
    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
    params.append(max(1, min(limit, 100)))
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT id, address_code, source_submission_id, province_code, territory_id, address_label,
                       status, publication_state, latitude, longitude, accuracy_meters, search_text,
                       record_bundle, created_at, updated_at
                FROM address_records
                ''' + where_sql + ' ORDER BY updated_at DESC LIMIT %s',
                params,
            )
            return [_address_record_row(row) for row in cursor.fetchall()]


def get_address_record_case_file(address_code: str) -> dict[str, Any]:
    records = search_address_records(q=address_code, limit=5)
    exact = next((record for record in records if record['address_code'].lower() == address_code.lower()), None)
    if not exact:
        raise AddressNotFoundError('address record not found')
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT event_type, actor_id, actor_username, actor_role, details, created_at
                FROM address_record_events
                WHERE address_record_id = %s
                ORDER BY created_at ASC
                ''',
                (exact['id'],),
            )
            timeline = []
            for row in cursor.fetchall():
                event = dict(row)
                if isinstance(event.get('details'), str):
                    event['details'] = json.loads(event['details'])
                timeline.append(event)
    exact['timeline'] = timeline
    return exact


def build_geotag_certificate(submission_id: str) -> dict[str, Any]:
    items = [item for item in list_citizen_geotag_submissions() if item['id'] == submission_id]
    if not items:
        raise SubmissionNotFoundError('citizen geotag submission not found')
    item = items[0]
    if item['status'] != 'published':
        raise InvalidSubmissionActionError('certificate requires published status after full project approval')
    address_code = describe_address_code(item['grid_code'])
    certificate_id = f"CERT-{item['grid_code']}"
    verification_url = f"/code/{item['grid_code']}"
    issued_at = datetime.now(timezone.utc).isoformat()
    safe_label = html.escape(item['address_label'])
    safe_territory = html.escape(item.get('territory_name') or 'Area pending')
    safe_code = html.escape(item['grid_code'])
    html_body = f"""<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><title>{html.escape(certificate_id)}</title></head>
<body>
  <main class=\"official-certificate\">
    <p>Republic of Equatorial Guinea</p>
    <h1>National Digital Address Certificate</h1>
    <p><strong>Certificate reference:</strong> {html.escape(certificate_id)}</p>
    <p><strong>Address code:</strong> {safe_code}</p>
    <p><strong>Location:</strong> {safe_label}</p>
    <p><strong>Territory:</strong> {safe_territory}</p>
    <p><strong>Coordinates:</strong> {item['latitude']}, {item['longitude']}</p>
    <p><strong>Status:</strong> Published after full project approval</p>
    <p><strong>Verify:</strong> {html.escape(verification_url)}</p>
  </main>
</body>
</html>"""
    return {
        'certificate_id': certificate_id,
        'submission_id': submission_id,
        'address_code': item['grid_code'],
        'address_code_metadata': address_code,
        'address_label': item['address_label'],
        'territory_name': item.get('territory_name'),
        'latitude': item['latitude'],
        'longitude': item['longitude'],
        'accuracy_meters': item.get('accuracy_meters'),
        'status': item['status'],
        'issued_at': issued_at,
        'qr_payload': verification_url,
        'prepared_by': 'BeCoreOps Guinea Ecuatorial',
        'html': html_body,
    }


def _province_code_from_public_code(code: str) -> str | None:
    parts = code.upper().strip().split('-')
    if len(parts) >= 2 and parts[0] == 'EG' and re.fullmatch(r'[A-Z]{2}', parts[1]):
        return parts[1]
    return None


def public_address_code_record_lookup(code: str) -> dict[str, Any]:
    address_code = describe_address_code(code)
    result: dict[str, Any] = {
        **address_code,
        'province_code': address_code.get('province_code') or _province_code_from_public_code(code),
        'publication_status': 'invalid' if not address_code.get('is_valid') else 'not_found',
        'record': None,
    }
    canonical = search_address_records(q=code, limit=5)
    exact_record = next((record for record in canonical if record['address_code'].lower() == code.lower()), None)
    if exact_record and not address_code.get('is_valid'):
        result.update({
            'is_valid': True,
            'schema': 'registry-public-code',
            'publication_status': 'not_found',
            'registry_identifier_type': 'published-registry-code',
        })
        result.pop('error', None)
    if exact_record:
        if exact_record['status'] == 'published':
            result['publication_status'] = 'published'
            result['record'] = {
                'id': exact_record['id'],
                'address_label': exact_record['address_label'],
                'territory_id': exact_record.get('territory_id'),
                'territory_name': exact_record.get('record_bundle', {}).get('routing', {}).get('territory_name') if isinstance(exact_record.get('record_bundle'), dict) else None,
                'latitude': exact_record['latitude'],
                'longitude': exact_record['longitude'],
                'accuracy_meters': exact_record.get('accuracy_meters'),
                'grid_code': exact_record['address_code'],
                'status': exact_record['status'],
                'updated_at': exact_record.get('updated_at'),
            }
        else:
            result['publication_status'] = 'internal_registry' if exact_record['status'] == 'registry-ready' else 'not_public'
        return result
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT g.id, g.address_label, g.territory_id, t.name AS territory_name, g.latitude,
                       g.longitude, g.accuracy_meters, g.grid_code, g.status, g.signage_batch, g.updated_at
                FROM citizen_geotag_submissions g
                LEFT JOIN territories t ON t.id = g.territory_id
                WHERE g.grid_code = %s
                ORDER BY CASE WHEN g.status = 'published' THEN 0 WHEN g.status = 'registry-ready' THEN 1 ELSE 2 END, g.updated_at DESC
                LIMIT 1
                ''',
                (code,),
            )
            geotag = cursor.fetchone()
            if geotag:
                if not result.get('is_valid'):
                    result.update({
                        'is_valid': True,
                        'schema': 'registry-public-code',
                        'registry_identifier_type': 'published-registry-code',
                    })
                    result.pop('error', None)
                if geotag['status'] == 'published':
                    result['publication_status'] = 'published'
                    result['record'] = dict(geotag)
                elif geotag['status'] == 'registry-ready':
                    result['publication_status'] = 'internal_registry'
                else:
                    result['publication_status'] = 'not_public'
                return result
            cursor.execute(
                '''
                SELECT a.id, a.formatted AS address_label, a.public_code AS grid_code, t.name AS territory_name,
                       ap.latitude, ap.longitude, ap.accuracy_meters, a.publication_state AS status, a.updated_at
                FROM addresses a
                LEFT JOIN territories t ON t.id = a.territory_id
                LEFT JOIN address_points ap ON ap.address_id = a.id AND ap.is_active = TRUE
                WHERE a.public_code = %s AND a.is_archived = FALSE
                LIMIT 1
                ''',
                (code,),
            )
            address = cursor.fetchone()
            if address:
                if not result.get('is_valid'):
                    result.update({
                        'is_valid': True,
                        'schema': 'registry-public-code',
                        'registry_identifier_type': 'published-registry-code',
                    })
                    result.pop('error', None)
                if address['status'] == 'published':
                    result['publication_status'] = 'published'
                    result['record'] = dict(address)
                else:
                    result['publication_status'] = 'not_public'
    return result


def signage_export(status: str = 'published') -> dict[str, Any]:
    rows = []
    for item in list_citizen_geotag_submissions(status=status):
        rows.append({
            'grid_code': item['grid_code'],
            'address_code': item.get('address_code'),
            'signage_text': item['grid_code'],
            'address_label': item['address_label'],
            'territory_name': item['territory_name'],
            'latitude': item['latitude'],
            'longitude': item['longitude'],
            'accuracy_meters': item['accuracy_meters'],
            'batch': item['signage_batch'],
            'status': item['status'],
        })
    return {'status': status, 'count': len(rows), 'items': rows}


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
            cursor.execute('SELECT id FROM import_jobs WHERE id = %s OR LOWER(name) = LOWER(%s)', (job_id, payload['name']))
            if cursor.fetchone():
                raise DuplicateImportJobError('duplicate import job')
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
            if job['status'] == 'committed':
                raise InvalidSubmissionActionError('import job already committed')
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
            cursor.execute('SELECT id FROM publication_packs WHERE id = %s OR LOWER(name) = LOWER(%s)', (pack_id, payload['name']))
            if cursor.fetchone():
                raise DuplicatePublicationPackError('duplicate publication pack')
            cursor.execute('INSERT INTO publication_packs (id, name, status, audience) VALUES (%s, %s, %s, %s)', (pack_id, payload['name'], payload.get('status', 'draft'), payload['audience']))
            for address_id in address_ids:
                cursor.execute('SELECT id FROM addresses WHERE id = %s', (address_id,))
                if not cursor.fetchone():
                    raise AddressNotFoundError('address not found')
                cursor.execute('INSERT INTO publication_pack_addresses (publication_pack_id, address_id) VALUES (%s, %s)', (pack_id, address_id))
                if payload.get('status', 'draft') == 'published':
                    cursor.execute("UPDATE addresses SET publication_state = 'published', verification_status = 'official', updated_at = NOW() WHERE id = %s", (address_id,))
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
                SET publication_state = 'published', verification_status = 'official', updated_at = NOW()
                WHERE id IN (SELECT address_id FROM publication_pack_addresses WHERE publication_pack_id = %s)
                ''',
                (pack_id,),
            )
            _log_action(cursor, actor=actor, action='publish', entity_type='publication_pack', entity_id=pack_id)
        connection.commit()
    return next(item for item in list_publication_packs() if item['id'] == pack_id)


def _readiness_gate(name: str, passed: bool, evidence: str, next_step: str) -> dict[str, Any]:
    return {
        'name': name,
        'status': 'passed' if passed else 'needs-work',
        'evidence': evidence,
        'next_step': next_step,
    }


def demo_fixture_status() -> dict[str, Any]:
    sql = '''
    SELECT 'address_corrections_smoke' AS bucket, count(*)::int AS count FROM address_corrections WHERE reporter_contact='smoke@example.invalid' OR reason='smoke-test-review'
    UNION ALL SELECT 'field_submissions_smoke', count(*)::int FROM field_submissions WHERE submitted_by='Smoke automation' OR candidate_name ILIKE 'Smoke Flow Road%'
    UNION ALL SELECT 'roads_smoke', count(*)::int FROM roads WHERE name ILIKE 'Smoke Flow Road%'
    UNION ALL SELECT 'audit_smoke', count(*)::int FROM audit_logs WHERE entity_id IN (SELECT id FROM field_submissions WHERE submitted_by='Smoke automation' OR candidate_name ILIKE 'Smoke Flow Road%') OR entity_id IN (SELECT id FROM address_corrections WHERE reporter_contact='smoke@example.invalid' OR reason='smoke-test-review') OR entity_id IN (SELECT id FROM roads WHERE name ILIKE 'Smoke Flow Road%')
    ORDER BY bucket
    '''
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            buckets = list(cursor.fetchall())
    total = sum(int(row['count']) for row in buckets)
    return {'buckets': buckets, 'total': total, 'clean': total == 0}


def cleanup_demo_fixtures(actor: dict[str, str] | None = None) -> dict[str, Any]:
    before = demo_fixture_status()
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                CREATE TEMP TABLE cleanup_smoke_entities(entity_type TEXT, entity_id TEXT) ON COMMIT DROP;
                INSERT INTO cleanup_smoke_entities(entity_type, entity_id)
                SELECT 'address_correction', id FROM address_corrections WHERE reporter_contact='smoke@example.invalid' OR reason='smoke-test-review'
                UNION ALL SELECT 'field_submission', id FROM field_submissions WHERE submitted_by='Smoke automation' OR candidate_name ILIKE 'Smoke Flow Road%'
                UNION ALL SELECT 'road', id FROM roads WHERE name ILIKE 'Smoke Flow Road%';

                DELETE FROM audit_logs
                WHERE (entity_type, entity_id) IN (SELECT entity_type, entity_id FROM cleanup_smoke_entities)
                   OR entity_id IN (SELECT entity_id FROM cleanup_smoke_entities);

                DELETE FROM address_corrections WHERE reporter_contact='smoke@example.invalid' OR reason='smoke-test-review';
                DELETE FROM field_submissions WHERE submitted_by='Smoke automation' OR candidate_name ILIKE 'Smoke Flow Road%';
                DELETE FROM roads WHERE name ILIKE 'Smoke Flow Road%';
                '''
            )
            _log_action(cursor, actor=actor, action='cleanup-demo-fixtures', entity_type='operator_maintenance', entity_id='demo-fixtures', details={'before': before})
        connection.commit()
    after = demo_fixture_status()
    return {**after, 'before': before, 'deleted': before['total'] - after['total']}


def pilot_readiness_summary() -> dict[str, Any]:
    summary = reporting_summary()
    totals = summary['totals']
    audit_count = 0
    recent_audit_events: list[dict[str, Any]] = []
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) AS count FROM audit_logs')
            audit_count = cursor.fetchone()['count']
            cursor.execute(
                '''
                SELECT action, entity_type, entity_id, actor_username, created_at
                FROM audit_logs
                ORDER BY created_at DESC
                LIMIT 8
                '''
            )
            recent_audit_events = list(cursor.fetchall())

    geotag_breakdown = {row['status']: row['count'] for row in summary.get('geotag_breakdown', [])}
    review_breakdown = {row['review_status']: row['count'] for row in summary.get('review_breakdown', [])}
    correction_breakdown = {row['status']: row['count'] for row in summary.get('correction_breakdown', [])}

    gates = [
        _readiness_gate(
            'Citizen capture intake',
            totals.get('citizen_geotags', 0) > 0,
            f"{totals.get('citizen_geotags', 0)} citizen geotag submissions recorded.",
            'Run at least one clean pilot fixture through geotag capture if this is zero.',
        ),
        _readiness_gate(
            'Administrative review queue',
            totals.get('geotag_queue', 0) > 0 or bool(geotag_breakdown),
            f"Geotag statuses: {geotag_breakdown or 'none recorded'}.",
            'Keep submitted/under-review/field-check statuses visible to reviewers.',
        ),
        _readiness_gate(
            'Field verification workflow',
            totals.get('submissions', 0) > 0,
            f"{totals.get('submissions', 0)} field submissions recorded; statuses: {review_breakdown or 'none recorded'}.",
            'Route at least one uncertain geotag to field verification during pilot rehearsal.',
        ),
        _readiness_gate(
            'Public correction queue',
            totals.get('public_corrections', 0) > 0 or totals.get('correction_queue', 0) == 0,
            f"{totals.get('public_corrections', 0)} public corrections; active queue {totals.get('correction_queue', 0)}; statuses: {correction_breakdown or 'none recorded'}.",
            'Confirm citizens can report corrections without exposing private fields.',
        ),
        _readiness_gate(
            'Published output after full approval',
            totals.get('published_addresses', 0) > 0,
            f"{totals.get('published_addresses', 0)} published registry addresses; {geotag_breakdown.get('registry-ready', 0)} internal registry-ready case files.",
            'After full project approval, publish at least one clean record before public lookup/signage demo.',
        ),
        _readiness_gate(
            'Auditability',
            audit_count > 0,
            f"{audit_count} audit events recorded.",
            'All approval, rejection, duplicate, export, and user changes should remain auditable.',
        ),
    ]

    passed_count = sum(1 for gate in gates if gate['status'] == 'passed')
    readiness_status = 'pilot-ready' if passed_count == len(gates) else 'pilot-prep'
    return {
        'readiness_status': readiness_status,
        'passed_gates': passed_count,
        'total_gates': len(gates),
        'gates': gates,
        'totals': totals,
        'breakdowns': {
            'geotags': summary.get('geotag_breakdown', []),
            'field_reviews': summary.get('review_breakdown', []),
            'public_corrections': summary.get('correction_breakdown', []),
            'publication': summary.get('publication_breakdown', []),
        },
        'recent_audit_events': recent_audit_events,
        'boundaries': [
            'Pilot-ready status does not make address codes legally official without Government adoption.',
            'Government ownership, data-sharing policy, and final national code standard remain institutional decisions.',
            'Public lookup must continue exposing only published records; registry-ready case files remain protected/internal until project approval.',
        ],
    }


def reporting_summary(
    province: str | None = None,
    territory: str | None = None,
    status_filter: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, Any]:
    """Return a read-only reporting summary with the requested filter scope echoed back.

    The current pilot data is aggregate-first; filters are accepted as a stable API
    contract for the staff reports UI and can be applied deeper as record-level
    reporting tables expand.
    """
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
            cursor.execute('SELECT COUNT(*) AS count FROM address_corrections')
            public_corrections = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) AS count FROM address_corrections WHERE status IN ('submitted', 'under-review')")
            correction_queue = cursor.fetchone()['count']
            cursor.execute('SELECT province_code, COUNT(*) AS territory_count FROM territories WHERE is_archived = FALSE GROUP BY province_code ORDER BY province_code ASC')
            territories_by_province = list(cursor.fetchall())
            cursor.execute("SELECT review_status, COUNT(*) AS count FROM field_submissions GROUP BY review_status ORDER BY review_status ASC")
            review_breakdown = list(cursor.fetchall())
            cursor.execute("SELECT status, COUNT(*) AS count FROM publication_packs GROUP BY status ORDER BY status ASC")
            publication_breakdown = list(cursor.fetchall())
            cursor.execute("SELECT status, COUNT(*) AS count FROM address_corrections GROUP BY status ORDER BY status ASC")
            correction_breakdown = list(cursor.fetchall())
            cursor.execute('SELECT COUNT(*) AS count FROM citizen_geotag_submissions')
            citizen_geotags = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) AS count FROM citizen_geotag_submissions WHERE status IN ('submitted', 'under-review', 'needs-field-check')")
            geotag_queue = cursor.fetchone()['count']
            cursor.execute("SELECT status, COUNT(*) AS count FROM citizen_geotag_submissions GROUP BY status ORDER BY status ASC")
            geotag_breakdown = list(cursor.fetchall())
            return {
                'totals': {
                    'territories': territories,
                    'submissions': submissions,
                    'review_queue': review_queue,
                    'published_addresses': published_addresses,
                    'import_jobs': import_jobs,
                    'public_corrections': public_corrections,
                    'correction_queue': correction_queue,
                    'citizen_geotags': citizen_geotags,
                    'geotag_queue': geotag_queue,
                },
                'territories_by_province': territories_by_province,
                'review_breakdown': review_breakdown,
                'publication_breakdown': publication_breakdown,
                'correction_breakdown': correction_breakdown,
                'geotag_breakdown': geotag_breakdown,
                'filters': {
                    'province': province,
                    'territory': territory,
                    'status': status_filter,
                    'date_from': date_from,
                    'date_to': date_to,
                },
            }
