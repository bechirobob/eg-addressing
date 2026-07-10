from __future__ import annotations

import os
from typing import Any

from fastapi import Response


def apply_security_headers(response: Response, *, path: str) -> None:
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('Referrer-Policy', 'no-referrer')
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=(self)')
    if path.startswith('/api/'):
        response.headers.setdefault('Cache-Control', 'no-store')


def production_readiness_status() -> dict[str, Any]:
    app_env = os.getenv('APP_ENV', 'development')
    deployment_label = os.getenv('NEXT_PUBLIC_DEPLOYMENT_LABEL') or os.getenv('DEPLOYMENT_LABEL', '')
    normalized_label = deployment_label.strip().lower()
    non_production_label_terms = {'staging', 'pilot', 'not official', 'not-official', 'controlled'}
    production_label_is_clean = not any(term in normalized_label for term in non_production_label_terms)
    deployment_identity_ready = app_env != 'production' or production_label_is_clean
    session_cookie_mode = os.getenv('SESSION_COOKIE_MODE', 'bearer-local-storage')
    default_demo_passwords_allowed = os.getenv('ALLOW_DEFAULT_DEMO_PASSWORDS', 'true').strip().lower() not in {'0', 'false', 'no'}
    checks = {
        'secure_cookie_sessions': {
            'status': 'ready' if session_cookie_mode == 'secure-http-only-cookie' else 'needs_work',
            'detail': 'Use HttpOnly Secure SameSite cookies before broad production exposure.',
        },
        'csrf_for_cookie_sessions': {
            'status': 'ready',
            'detail': 'Cookie-authenticated protected mutations require a matching X-CSRF-Token header; public citizen routes and bearer-token pilot flows remain compatible.',
        },
        'default_demo_passwords_disabled': {
            'status': 'needs_work' if default_demo_passwords_allowed else 'ready',
            'detail': 'Set ALLOW_DEFAULT_DEMO_PASSWORDS=false after replacing seeded demo passwords with real operator credentials.',
        },
        'explicit_migrations': {
            'status': 'ready',
            'detail': 'Schema migrations are tracked in schema_migrations and surfaced in the operator command center.',
        },
        'repeatable_audit_harness': {
            'status': 'ready',
            'detail': 'infra/scripts/audit_all.sh runs backend, frontend, guards, smoke cleanup, and served health.',
        },
        'production_environment': {
            'status': 'ready' if app_env == 'production' else 'needs_work',
            'detail': f'Current APP_ENV is {app_env}; production deploy should set APP_ENV=production with real secrets and monitoring.',
        },
        'deployment_identity': {
            'status': 'ready' if deployment_identity_ready else 'needs_work',
            'detail': 'Production deployments must not carry staging, pilot, controlled, or not-official deployment labels.',
        },
    }
    overall = 'ready' if all(item['status'] == 'ready' for item in checks.values()) else 'needs_work'
    return {
        'status': overall,
        'checks': checks,
        'operator_note': 'This endpoint is intentionally honest: pilot-ready can still be production-needs-work.',
    }
