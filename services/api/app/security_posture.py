from __future__ import annotations

import os
from typing import Any

from fastapi import Response

from app.ops_status import migration_status


def apply_security_headers(response: Response, *, path: str) -> None:
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('Referrer-Policy', 'no-referrer')
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=(self)')
    if path.startswith('/api/'):
        response.headers.setdefault('Cache-Control', 'no-store')


def _ready(status: bool, detail: str) -> dict[str, str]:
    return {'status': 'ready' if status else 'needs_work', 'detail': detail}


def production_readiness_status() -> dict[str, Any]:
    app_env = os.getenv('APP_ENV', 'development').strip().lower()
    deployment_label = os.getenv('NEXT_PUBLIC_DEPLOYMENT_LABEL') or os.getenv('DEPLOYMENT_LABEL', '')
    normalized_label = deployment_label.strip().lower()
    non_production_label_terms = {'staging', 'pilot', 'not official', 'not-official', 'controlled'}
    production_label_is_clean = not any(term in normalized_label for term in non_production_label_terms)
    deployment_identity_ready = app_env != 'production' or production_label_is_clean
    session_cookie_mode = os.getenv('SESSION_COOKIE_MODE', 'bearer-local-storage')
    default_demo_passwords_allowed = os.getenv('ALLOW_DEFAULT_DEMO_PASSWORDS', 'true').strip().lower() not in {'0', 'false', 'no'}
    configured_database = bool(os.getenv('DATABASE_URL') or os.getenv('POSTGRES_HOST'))
    migration = migration_status()
    migration_ready = migration.get('status') == 'current'
    production_required_env = {
        'database': configured_database,
        'session_cookie_mode': session_cookie_mode == 'secure-http-only-cookie',
        'default_demo_passwords_disabled': not default_demo_passwords_allowed,
        'deployment_identity': deployment_identity_ready,
    }
    production_config_ready = app_env != 'production' or all(production_required_env.values())
    checks = {
        'secure_cookie_sessions': _ready(
            session_cookie_mode == 'secure-http-only-cookie',
            'Use HttpOnly Secure SameSite cookies before broad production exposure.',
        ),
        'csrf_for_cookie_sessions': {
            'status': 'ready',
            'detail': 'Cookie-authenticated protected mutations require a matching X-CSRF-Token header; public citizen routes and bearer-token pilot flows remain compatible.',
        },
        'default_demo_passwords_disabled': _ready(
            not default_demo_passwords_allowed,
            'Disable default demo passwords after replacing seeded demo passwords with real operator credentials.',
        ),
        'explicit_migrations': {
            'status': 'ready' if migration_ready else 'needs_work',
            'detail': f"Migration state is {migration.get('status', 'unreadable')}; readiness fails closed for pending, checksum mismatch, filename mismatch, unknown ledger state, unreadable state, and missing DB configuration.",
            'migration_status': migration,
        },
        'repeatable_audit_harness': {
            'status': 'ready',
            'detail': 'infra/scripts/audit_all.sh runs backend, frontend, guards, smoke cleanup, and served health.',
        },
        'production_environment': _ready(
            app_env == 'production',
            f'Current APP_ENV is {app_env}; production deploy should set APP_ENV=production with real secrets and monitoring.',
        ),
        'deployment_identity': _ready(
            deployment_identity_ready,
            'Production deployments must not carry staging, pilot, controlled, or not-official deployment labels.',
        ),
        'production_configuration': {
            'status': 'ready' if production_config_ready else 'needs_work',
            'detail': 'Production requires database configuration, secure cookie sessions, disabled default demo passwords, and clean deployment identity.',
            'requirements': production_required_env,
        },
    }
    overall = 'ready' if all(item['status'] == 'ready' for item in checks.values()) else 'needs_work'
    return {
        'status': overall,
        'checks': checks,
        'operator_note': 'This endpoint is intentionally honest: pilot-ready can still be production-needs-work.',
    }
