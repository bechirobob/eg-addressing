import json
import logging
import os
import re
import secrets
import hmac
from contextvars import ContextVar
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import Cookie, FastAPI, Header, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.data import MODULES
from app.evidence_storage import EvidenceObjectNotFound, EvidenceStorageError, read_evidence_object, store_evidence_object
from app.address_codes import coordinate_grid_cell
from app.ops_status import migration_status
from app.query_contracts import paginated_response
from app.security_posture import apply_security_headers, production_readiness_status
from app.db import (
    AdminUnitProvinceMismatchError,
    AddressCorrectionNotFoundError,
    AddressNotFoundError,
    AuthenticationError,
    BuildingNotFoundError,
    DuplicateAddressError,
    DuplicateBuildingError,
    DuplicateImportJobError,
    DuplicatePublicationPackError,
    DuplicateRoadError,
    DuplicateTerritoryError,
    DuplicateUserError,
    EvidenceAttachmentNotFoundError,
    ImportJobNotFoundError,
    InvalidSubmissionActionError,
    InvalidUserRoleError,
    PublicationPackNotFoundError,
    RoadNotFoundError,
    SubmissionNotFoundError,
    TerritoryNotFoundError,
    UnknownAdminUnitError,
    UnknownBuildingError,
    UnknownProvinceError,
    UnknownRoadError,
    UnknownTerritoryError,
    UserNotFoundError,
    approve_submission,
    archive_address,
    archive_building,
    archive_road,
    archive_territory,
    attach_field_submission_evidence_file,
    authenticate_user_session,
    commit_import_job,
    cleanup_demo_fixtures,
    create_address,
    create_address_correction,
    create_staff_user,
    create_citizen_geotag_submission,
    create_building,
    create_field_submission,
    create_import_job,
    create_publication_pack,
    create_road,
    create_territory,
    demo_fixture_status,
    describe_address_code,
    fetch_addresses,
    fetch_addresses_page,
    fetch_buildings,
    fetch_buildings_page,
    fetch_roads,
    fetch_roads_page,
    fetch_territories,
    fetch_territories_page,
    get_address,
    get_address_record_case_file,
    get_building,
    get_field_submission_evidence_file,
    get_import_rows,
    get_road,
    get_submission,
    get_territory,
    init_db,
    list_address_corrections,
    list_citizen_geotag_submissions,
    list_admin_units as list_admin_units_db,
    list_audit_logs,
    list_audit_logs_page,
    list_field_assignments,
    list_field_submission_evidence_history,
    list_field_submissions,
    list_staff_users,
    list_geotag_field_tasks as list_field_geotag_tasks,
    list_import_jobs,
    list_provinces as list_provinces_db,
    list_publication_packs,
    publish_geotag_submission,
    publish_publication_pack,
    address_record_export,
    build_address_record_certificate,
    build_geotag_certificate,
    find_nearby_address_records,
    geotag_duplicate_summary,
    pilot_readiness_summary,
    preview_citizen_geotag,
    postgis_readiness,
    public_address_code_record_lookup,
    record_geotag_duplicate_decision,
    record_geotag_field_evidence,
    reporting_summary,
    resolve_user_from_token,
    revoke_user_session,
    review_field_submission_evidence,
    review_geotag_road_suggestion,
    search_address_records,
    simulate_geotag_publication_path,
    verify_geotag_identity,
    signage_export,
    update_address,
    update_address_correction_status,
    update_staff_user,
    disable_staff_user,
    revoke_staff_user_sessions,
    update_citizen_geotag_status,
    upsert_address_record_from_geotag,
    update_geotag_field_status,
    update_building,
    update_road,
    update_submission_review_status,
    update_territory,
    normalize_submission_spatial_evidence,
    verify_address,
)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=3, max_length=80)


class StaffUserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40, pattern='^[a-zA-Z0-9_.-]+$')
    full_name: str = Field(min_length=3, max_length=120)
    role: str = Field(pattern='^(admin|editor|viewer|agency_viewer)$')
    password: str = Field(min_length=12, max_length=120)


class StaffUserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=3, max_length=120)
    role: str | None = Field(default=None, pattern='^(admin|editor|viewer|agency_viewer)$')
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=12, max_length=120)


class TerritoryCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    province_code: str = Field(min_length=2, max_length=8)
    admin_unit_id: str | None = Field(default=None, min_length=3, max_length=120)
    type: str = Field(min_length=3, max_length=64)
    readiness: str = Field(min_length=3, max_length=64)


class TerritoryUpdate(TerritoryCreate):
    pass


class RoadCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    territory_id: str = Field(min_length=3, max_length=120)
    status: str = Field(min_length=3, max_length=64)
    length_km: str = Field(min_length=1, max_length=32)


class BuildingCreate(BaseModel):
    label: str = Field(min_length=3, max_length=120)
    territory_id: str = Field(min_length=3, max_length=120)
    road_id: str = Field(min_length=3, max_length=120)
    status: str = Field(min_length=3, max_length=64)
    usage: str = Field(min_length=3, max_length=64)


class AddressCreate(BaseModel):
    formatted: str = Field(min_length=5, max_length=180)
    territory_id: str = Field(min_length=3, max_length=120)
    road_id: str = Field(min_length=3, max_length=120)
    building_id: str = Field(min_length=3, max_length=120)
    status: str = Field(min_length=3, max_length=64)
    public_code: str | None = Field(default=None, min_length=8, max_length=32)
    issuance_method: str = Field(default='manual', min_length=3, max_length=64)
    source: str = Field(default='admin-portal', min_length=3, max_length=64)
    verification_status: str = Field(default='provisional', min_length=3, max_length=64)
    publication_state: str = Field(default='draft', min_length=3, max_length=64)
    superseded_by_address_id: str | None = Field(default=None, min_length=3, max_length=120)
    latitude: float | None = None
    longitude: float | None = None
    accuracy_meters: float | None = None
    point_source_method: str | None = Field(default=None, min_length=3, max_length=64)


class FieldSubmissionCreate(BaseModel):
    assignment_id: str | None = None
    territory_id: str = Field(min_length=3, max_length=120)
    submission_type: str = Field(pattern='^(road|building|address)$')
    candidate_name: str = Field(min_length=3, max_length=180)
    candidate_status: str = Field(min_length=3, max_length=64)
    notes: str = Field(default='', max_length=400)
    submitted_by: str = Field(min_length=3, max_length=120)
    spatial_evidence: dict[str, Any] | None = None


class FieldSpatialEvidenceEnrichRequest(BaseModel):
    territory_id: str = Field(min_length=3, max_length=120)
    submission_type: str = Field(pattern='^(road|building)$')
    spatial_evidence: dict[str, Any]


class ReviewActionRequest(BaseModel):
    reviewer_note: str = Field(default='', max_length=300)


class EvidenceReviewActionRequest(BaseModel):
    decision: str = Field(pattern='^(accepted|needs-recapture|rejected|escalated)$')
    reviewer_note: str = Field(default='', max_length=500)
    attachment_index: int = Field(default=0, ge=0, le=5)
    file_id: str | None = Field(default=None, min_length=3, max_length=80)


class AddressCorrectionCreate(BaseModel):
    query: str = Field(min_length=3, max_length=180)
    correction_type: str = Field(min_length=3, max_length=64)
    reason: str = Field(min_length=3, max_length=180)
    note: str = Field(default='', max_length=500)
    address_id: str | None = Field(default=None, min_length=3, max_length=120)
    public_code: str | None = Field(default=None, min_length=8, max_length=32)
    reporter_name: str | None = Field(default=None, min_length=2, max_length=120)
    reporter_contact: str | None = Field(default=None, min_length=3, max_length=120)
    privacy_notice_acknowledged: bool = False


class CorrectionReviewActionRequest(BaseModel):
    reviewer_note: str = Field(default='', max_length=500)


class CitizenGeotagPreviewRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    territory_id: str | None = Field(default=None, min_length=3, max_length=120)
    province_code: str | None = Field(default=None, min_length=2, max_length=8)


class RoadSuggestionRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class CitizenGeotagCreate(BaseModel):
    territory_id: str | None = Field(default=None, min_length=3, max_length=120)
    province_code: str | None = Field(default=None, min_length=2, max_length=8)
    address_label: str = Field(min_length=5, max_length=180)
    citizen_name: str | None = Field(default=None, min_length=2, max_length=120)
    citizen_contact: str | None = Field(default=None, min_length=3, max_length=120)
    landmark: str = Field(default='', max_length=300)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy_meters: float | None = Field(default=None, ge=0, le=5000)
    capture_method: str = Field(default='browser-gps', min_length=3, max_length=64)
    grid_code: str | None = Field(default=None, min_length=8, max_length=40)
    dip_last4: str | None = Field(default=None, pattern='^\\d{4}$')
    suggested_road_name: str | None = Field(default=None, min_length=2, max_length=180)
    suggested_local_area: str | None = Field(default=None, min_length=2, max_length=180)
    suggested_place_name: str | None = Field(default=None, min_length=2, max_length=180)
    map_display_name: str | None = Field(default=None, min_length=2, max_length=500)
    road_suggestion_source: str | None = Field(default=None, min_length=3, max_length=80)
    road_suggestion_attribution: str | None = Field(default=None, min_length=3, max_length=180)
    privacy_notice_acknowledged: bool = False


class GeotagReviewActionRequest(BaseModel):
    reviewer_note: str = Field(default='', max_length=500)


class GeotagIdentityReviewRequest(BaseModel):
    dip_full: str = Field(pattern='^\\d{6,20}$')
    identity_document_verified: bool = False
    reviewer_note: str = Field(default='', max_length=500)


class RoadSuggestionReviewRequest(BaseModel):
    action: str = Field(pattern='^(accepted|edited|rejected)$')
    reviewed_road_name: str | None = Field(default=None, min_length=2, max_length=180)
    reviewer_note: str = Field(default='', max_length=500)


class GeotagDuplicateDecisionRequest(BaseModel):
    duplicate_action: str = Field(pattern='^(same-property-merge|different-property-same-cell|gps-error-recapture|send-field-verification)$')
    reviewer_note: str = Field(default='', max_length=500)


class GeotagFieldStatusRequest(BaseModel):
    field_status: str = Field(pattern='^(assigned|visited|verified|needs-recapture|blocked)$')
    field_note: str = Field(default='', max_length=500)


class GeotagFieldEvidenceRequest(BaseModel):
    evidence_type: str = Field(pattern='^(photo-reference|site-note|landmark-confirmation|coordinate-confirmation)$')
    evidence_reference: str = Field(min_length=3, max_length=240)
    evidence_note: str = Field(default='', max_length=500)


class ImportRowInput(BaseModel):
    submission_type: str = Field(pattern='^(road|building|address)$')
    territory_id: str = Field(min_length=3, max_length=120)
    candidate_name: str = Field(min_length=3, max_length=180)
    candidate_status: str = Field(min_length=3, max_length=64)
    notes: str = Field(default='', max_length=300)


class ImportJobCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    source_name: str = Field(min_length=3, max_length=120)
    rows: list[ImportRowInput] = Field(min_length=1, max_length=200)


class PublicationPackCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    audience: str = Field(min_length=3, max_length=120)
    status: str = Field(default='draft', pattern='^(draft|published)$')
    address_ids: list[str] = Field(min_length=1, max_length=200)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper(), format='%(message)s')
logger = logging.getLogger('eg-addressing-api')

APP_ENV = os.getenv('APP_ENV', 'local').strip().lower() or 'local'
SESSION_TTL_HOURS = max(1, int(os.getenv('SESSION_TTL_HOURS', '12')))
SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME', 'eg_addressing_session')
CSRF_COOKIE_NAME = os.getenv('CSRF_COOKIE_NAME', 'eg_addressing_csrf')
CSRF_HEADER_NAME = 'x-csrf-token'
SESSION_COOKIE_MODE = os.getenv('SESSION_COOKIE_MODE', 'bearer-local-storage').strip().lower()
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true').strip().lower() not in {'0', 'false', 'no'}
PUBLICATION_RELEASE_ENABLED = os.getenv('PUBLICATION_RELEASE_ENABLED', 'false').strip().lower() in {'1', 'true', 'yes'}
PUBLIC_RATE_LIMIT_ENABLED = os.getenv('PUBLIC_RATE_LIMIT_ENABLED', 'true').strip().lower() not in {'0', 'false', 'no'}
PUBLIC_RATE_LIMIT_MAX_REQUESTS = max(1, int(os.getenv('PUBLIC_RATE_LIMIT_MAX_REQUESTS', '30')))
PUBLIC_RATE_LIMIT_WINDOW_SECONDS = max(1, int(os.getenv('PUBLIC_RATE_LIMIT_WINDOW_SECONDS', '60')))
PUBLIC_RATE_LIMIT_BUCKETS: dict[str, deque[float]] = defaultdict(deque)
EVIDENCE_FILE_MAX_BYTES = int(os.getenv('EVIDENCE_FILE_MAX_BYTES', str(5 * 1024 * 1024)))
EVIDENCE_ALLOWED_CONTENT_TYPES = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
    'application/pdf': 'pdf',
    'text/plain': 'txt',
}
EVIDENCE_BLOCKED_EXTENSIONS = {'.exe', '.dll', '.sh', '.bash', '.bat', '.cmd', '.js', '.mjs', '.py', '.php', '.jar', '.zip', '.7z', '.rar'}
REQUEST_SESSION_COOKIE: ContextVar[str | None] = ContextVar('REQUEST_SESSION_COOKIE', default=None)
NOMINATIM_REVERSE_URL = os.getenv('NOMINATIM_REVERSE_URL', 'https://nominatim.openstreetmap.org/reverse')
NOMINATIM_USER_AGENT = os.getenv('NOMINATIM_USER_AGENT', 'BeCoreOps-EG-Addressing-Pilot/0.1 contact: operator')
NOMINATIM_LAST_REQUEST_AT = 0.0


app = FastAPI(
    title='National Digital Addressing Platform API',
    version='0.1.0',
    description='Operational API for the Equatorial Guinea national digital addressing platform.',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3100', 'http://127.0.0.1:3100'],
    allow_origin_regex=r'^https?://([a-zA-Z0-9.-]+|\[[0-9a-fA-F:]+\]):3100$',
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
    allow_headers=['*'],
)


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get('x-forwarded-for', '').strip()
    if forwarded_for:
        return forwarded_for.split(',', 1)[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return 'unknown'


def _check_public_rate_limit(request: Request, scope: str) -> None:
    if not PUBLIC_RATE_LIMIT_ENABLED:
        return
    now = time.time()
    key = f'{scope}:{_client_ip(request)}'
    bucket = PUBLIC_RATE_LIMIT_BUCKETS[key]
    while bucket and now - bucket[0] > PUBLIC_RATE_LIMIT_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= PUBLIC_RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail='rate limit exceeded',
            headers={'Retry-After': str(PUBLIC_RATE_LIMIT_WINDOW_SECONDS)},
        )
    bucket.append(now)




def _using_secure_cookie_mode() -> bool:
    return SESSION_COOKIE_MODE == 'secure-http-only-cookie'


def _auth_mode() -> str:
    return 'cookie_session' if _using_secure_cookie_mode() else 'bearer_token'


def _has_bearer_authorization(request: Request) -> bool:
    return request.headers.get('authorization', '').startswith('Bearer ')


def _path_exempt_from_csrf(path: str) -> bool:
    return (
        path == '/api/v1/auth/login'
        or path.startswith('/api/v1/public/')
        or path in {'/api/v1/health', '/api/v1/meta'}
    )


def _require_csrf_token(request: Request) -> None:
    if not _using_secure_cookie_mode():
        return
    if request.method not in {'POST', 'PATCH', 'DELETE'}:
        return
    if _path_exempt_from_csrf(request.url.path):
        return
    if _has_bearer_authorization(request):
        return
    if not request.cookies.get(SESSION_COOKIE_NAME):
        return
    csrf_cookie = request.cookies.get(CSRF_COOKIE_NAME, '')
    csrf_header = request.headers.get(CSRF_HEADER_NAME, '')
    if not csrf_cookie or not csrf_header or not hmac.compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='csrf token required')


def _road_suggestion_unavailable() -> dict[str, Any]:
    return {
        'suggested_road_name': None,
        'suggested_local_area': None,
        'suggested_place_name': None,
        'display_name': None,
        'source': 'openstreetmap-nominatim',
        'source_attribution': '© OpenStreetMap contributors',
        'distance_meters': None,
        'confidence': 'none',
        'requires_review': True,
        'status': 'unavailable',
    }


def _extract_road_name(address: dict[str, Any]) -> str | None:
    for key in ('road', 'pedestrian', 'footway', 'residential', 'path', 'cycleway'):
        value = address.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_local_area(address: dict[str, Any]) -> str | None:
    for key in ('neighbourhood', 'suburb', 'quarter', 'city_district', 'hamlet', 'village', 'town', 'city', 'municipality', 'county'):
        value = address.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def suggest_nearest_road_name(latitude: float, longitude: float) -> dict[str, Any]:
    global NOMINATIM_LAST_REQUEST_AT
    elapsed = time.time() - NOMINATIM_LAST_REQUEST_AT
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    query = urllib.parse.urlencode({
        'format': 'jsonv2',
        'lat': f'{latitude:.7f}',
        'lon': f'{longitude:.7f}',
        'zoom': '18',
        'addressdetails': '1',
    })
    request = urllib.request.Request(
        f'{NOMINATIM_REVERSE_URL}?{query}',
        headers={'User-Agent': NOMINATIM_USER_AGENT, 'Accept': 'application/json'},
    )
    try:
        NOMINATIM_LAST_REQUEST_AT = time.time()
        with urllib.request.urlopen(request, timeout=4) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return _road_suggestion_unavailable()

    address = payload.get('address') or {}
    road_name = _extract_road_name(address)
    local_area = _extract_local_area(address)
    place_name = payload.get('name') if isinstance(payload.get('name'), str) else None
    display_name = payload.get('display_name') if isinstance(payload.get('display_name'), str) else None
    if not road_name and not local_area and not place_name:
        return _road_suggestion_unavailable()
    return {
        'suggested_road_name': road_name,
        'suggested_local_area': local_area,
        'suggested_place_name': place_name.strip() if place_name else None,
        'display_name': display_name.strip() if display_name else None,
        'source': 'openstreetmap-nominatim',
        'source_attribution': '© OpenStreetMap contributors',
        'distance_meters': None,
        'confidence': 'medium' if road_name or local_area else 'low',
        'requires_review': True,
        'status': 'suggested',
    }



def _midpoint(points: list[dict[str, Any]]) -> dict[str, float]:
    if not points:
        raise InvalidSubmissionActionError('spatial evidence has no coordinate points')
    return {
        'latitude': round(sum(float(point['latitude']) for point in points) / len(points), 7),
        'longitude': round(sum(float(point['longitude']) for point in points) / len(points), 7),
    }


def _unique_grid_cells(points: list[dict[str, Any]], province_code: str | None) -> list[dict[str, Any]]:
    seen: set[str] = set()
    cells: list[dict[str, Any]] = []
    for point in points:
        cell = coordinate_grid_cell(float(point['latitude']), float(point['longitude']), province_code)
        key = cell['grid_code']
        if key in seen:
            continue
        seen.add(key)
        cells.append(cell)
    return cells


def enrich_field_spatial_evidence(submission_type: str, spatial_evidence: dict[str, Any], territory_id: str) -> dict[str, Any]:
    normalized = normalize_submission_spatial_evidence(submission_type, spatial_evidence)
    territory = get_territory(territory_id)
    province_code = territory.get('province_code')
    if submission_type == 'road':
        points = normalized.get('points') or []
        center = _midpoint(points)
        suggestion = suggest_nearest_road_name(center['latitude'], center['longitude'])
        normalized['map_suggestion'] = {
            'suggested_road_name': suggestion.get('suggested_road_name'),
            'suggested_local_area': suggestion.get('suggested_local_area'),
            'suggested_place_name': suggestion.get('suggested_place_name'),
            'display_name': suggestion.get('display_name'),
            'source': suggestion.get('source'),
            'source_attribution': suggestion.get('source_attribution'),
            'distance_meters': suggestion.get('distance_meters'),
            'confidence': suggestion.get('confidence', 'none'),
            'requires_review': True,
            'status': suggestion.get('status', 'unavailable'),
        }
        normalized['grid_cells'] = _unique_grid_cells(points, province_code)
        normalized['stretch_midpoint'] = center
        normalized['review_confidence'] = 'high' if normalized['map_suggestion']['suggested_road_name'] and len(normalized['grid_cells']) <= 6 else 'medium' if normalized['grid_cells'] else 'low'
        normalized['review_required'] = True
    elif submission_type == 'building':
        point = {'latitude': normalized['latitude'], 'longitude': normalized['longitude']}
        normalized['grid_cells'] = _unique_grid_cells([point], province_code)
        normalized['review_confidence'] = 'medium'
        normalized['review_required'] = True
    return normalized


@app.middleware('http')
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get('x-request-id') or str(uuid.uuid4())
    started_at = time.perf_counter()
    response: Response | None = None
    session_cookie_token = REQUEST_SESSION_COOKIE.set(request.cookies.get(SESSION_COOKIE_NAME))
    try:
        try:
            _require_csrf_token(request)
        except HTTPException as exc:
            response = JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})
            return response
        response = await call_next(request)
        return response
    finally:
        REQUEST_SESSION_COOKIE.reset(session_cookie_token)
        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
        status_code = response.status_code if response else 500
        logger.info(
            {
                'event': 'http_request',
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'status_code': status_code,
                'duration_ms': elapsed_ms,
                'client_ip': _client_ip(request),
                'app_env': APP_ENV,
            }
        )
        if response is not None:
            response.headers['X-Request-ID'] = request_id
            apply_security_headers(response, path=request.url.path)


def _session_token(authorization: str | None = None, session_cookie: str | None = None) -> str:
    if session_cookie:
        return session_cookie.strip()
    contextual_cookie = REQUEST_SESSION_COOKIE.get()
    if contextual_cookie:
        return contextual_cookie.strip()
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='authentication required')
    return authorization.split(' ', 1)[1].strip()


def _bearer_token(authorization: str | None) -> str:
    return _session_token(authorization=authorization)


def _current_user(authorization: str | None, session_cookie: str | None = None) -> dict[str, str]:
    token = _session_token(authorization=authorization, session_cookie=session_cookie)
    try:
        return resolve_user_from_token(token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


def _require_role(user: dict[str, str], *roles: str) -> None:
    if user['role'] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='insufficient role')


def _staff_user_public(user: dict[str, Any]) -> dict[str, Any]:
    return {
        'id': user.get('id'),
        'username': user.get('username'),
        'full_name': user.get('full_name'),
        'role': user.get('role'),
        'is_active': user.get('is_active'),
        'created_at': user.get('created_at'),
        'active_sessions': user.get('active_sessions', 0),
    }


SENSITIVE_DETAIL_KEYS = {'token', 'session_token', 'auth_token', 'access_token', 'refresh_token', 'authorization', 'cookie', 'password', 'password_hash', 'csrf_token', 'secret'}
SENSITIVE_DETAIL_PATTERN = re.compile(r'(token|password|secret|authorization|cookie|csrf)', re.IGNORECASE)


def _is_sensitive_detail_key(key: Any) -> bool:
    normalized = re.sub(r'[^a-z0-9]+', '_', str(key).strip().lower())
    return normalized in SENSITIVE_DETAIL_KEYS or bool(SENSITIVE_DETAIL_PATTERN.search(str(key)))


def _sanitize_timeline_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: ('[protected]' if _is_sensitive_detail_key(key) else _sanitize_timeline_value(inner)) for key, inner in value.items()}
    if isinstance(value, list):
        return [_sanitize_timeline_value(item) for item in value]
    return value


def _sanitize_case_file(case_file: dict[str, Any]) -> dict[str, Any]:
    safe = dict(case_file)
    safe['timeline'] = [_sanitize_timeline_value(item) for item in safe.get('timeline', [])]
    return safe


def _geotag_quality_flags(item: dict[str, Any], duplicate_count: int) -> dict[str, Any]:
    accuracy = item.get('accuracy_meters')
    if accuracy is None:
        accuracy_level = 'unknown'
        accuracy_label = 'Accuracy not recorded'
        requires_field_check = True
    elif accuracy <= 10:
        accuracy_level = 'high-accuracy'
        accuracy_label = 'High accuracy'
        requires_field_check = False
    elif accuracy <= 25:
        accuracy_level = 'needs-confirmation'
        accuracy_label = 'Needs confirmation'
        requires_field_check = True
    else:
        accuracy_level = 'weak-gps'
        accuracy_label = 'Weak GPS — field check required'
        requires_field_check = True
    duplicate_code = duplicate_count > 1
    possible_duplicate = duplicate_code or item.get('duplicate_hint') == 'possible-duplicate'
    recommended_action = 'field-check' if requires_field_check or possible_duplicate else 'registry-ready-review'
    return {
        'accuracy_level': accuracy_level,
        'accuracy_label': accuracy_label,
        'requires_field_check': requires_field_check,
        'duplicate_code': duplicate_code,
        'possible_duplicate': possible_duplicate,
        'recommended_action': recommended_action,
    }


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _hours_since(value: Any, now: datetime) -> float | None:
    parsed = _parse_datetime(value)
    if not parsed:
        return None
    return max(0.0, (now - parsed.astimezone(timezone.utc)).total_seconds() / 3600)


def _sla_state(age_hours: float | None, due_hours: int) -> str:
    if age_hours is None:
        return 'unknown'
    if age_hours > due_hours:
        return 'overdue'
    if age_hours >= due_hours * 0.75:
        return 'approaching'
    return 'on_time'


def _geotag_sla(item: dict[str, Any], automation: dict[str, Any], now: datetime) -> dict[str, Any] | None:
    status_value = item.get('status') or 'submitted'
    if status_value in {'rejected', 'registry-ready', 'published'}:
        return None
    if automation.get('triage_bucket') == 'field-verification':
        label = 'Assign field verification'
        due_hours = 72
    elif automation.get('triage_bucket') == 'field-verification' and item.get('duplicate_hint') == 'possible-duplicate':
        label = 'Supervisor duplicate decision'
        due_hours = 120
    elif automation.get('triage_bucket') == 'field-verification' and automation.get('quality_flags', {}).get('possible_duplicate'):
        label = 'Supervisor duplicate decision'
        due_hours = 120
    else:
        label = 'Review new citizen geotag'
        due_hours = 48
    if item.get('duplicate_hint') == 'possible-duplicate':
        label = 'Supervisor duplicate decision'
        due_hours = 120
    age_hours = _hours_since(item.get('updated_at') or item.get('created_at'), now)
    return {
        'id': item.get('id'),
        'type': 'geotag',
        'label': label,
        'status': status_value,
        'age_hours': round(age_hours, 1) if age_hours is not None else None,
        'due_hours': due_hours,
        'state': _sla_state(age_hours, due_hours),
    }


def _correction_sla(item: dict[str, Any], now: datetime) -> dict[str, Any] | None:
    status_value = item.get('status') or 'submitted'
    if status_value != 'submitted':
        return None
    age_hours = _hours_since(item.get('created_at') or item.get('updated_at'), now)
    return {
        'id': item.get('id'),
        'type': 'correction',
        'label': 'Acknowledge correction request',
        'status': status_value,
        'age_hours': round(age_hours, 1) if age_hours is not None else None,
        'due_hours': 48,
        'state': _sla_state(age_hours, 48),
    }


def _publication_hold_summary(enriched_items: list[dict[str, Any]], now: datetime) -> dict[str, Any]:
    held = [item for item in enriched_items if (item.get('status') == 'registry-ready' or (item.get('automation') or {}).get('integration', {}).get('api_record_state') == 'internal-registry')]
    ages = [_hours_since(item.get('updated_at') or item.get('created_at'), now) for item in held]
    known_ages = [age for age in ages if age is not None]
    return {
        'registry_ready': len(held),
        'public_release_locked': True,
        'oldest_days': round(max(known_ages) / 24) if known_ages else 0,
        'oldest_hours': round(max(known_ages), 1) if known_ages else 0,
        'note': 'Registry-ready records remain internal until full project/institutional approval publishes them.',
    }


def _sla_summary(enriched_items: list[dict[str, Any]], corrections: list[dict[str, Any]], now: datetime) -> dict[str, Any]:
    items = [sla for sla in (_geotag_sla(item, item.get('automation') or {}, now) for item in enriched_items) if sla]
    items.extend(sla for sla in (_correction_sla(item, now) for item in corrections) if sla)
    by_state: dict[str, int] = defaultdict(int)
    for item in items:
        by_state[item['state']] += 1
    overdue = [item for item in items if item['state'] == 'overdue']
    oldest_overdue = max(overdue, key=lambda item: item.get('age_hours') or 0, default=None)
    return {
        'items_tracked': len(items),
        'on_time': by_state.get('on_time', 0),
        'approaching': by_state.get('approaching', 0),
        'overdue': by_state.get('overdue', 0),
        'unknown': by_state.get('unknown', 0),
        'by_state': dict(by_state),
        'oldest_overdue': oldest_overdue,
        'items': sorted(items, key=lambda item: (item['state'] != 'overdue', -(item.get('age_hours') or 0)))[:8],
    }


def _geotag_automation(item: dict[str, Any], quality_flags: dict[str, Any], duplicate_count: int) -> dict[str, Any]:
    status_value = item.get('status') or 'submitted'
    field_status = item.get('field_status') or 'assigned'
    road_status = item.get('road_suggestion_status') or 'not-suggested'
    reasons: list[str] = []
    score = 100

    if quality_flags['accuracy_level'] == 'unknown':
        score -= 30
        reasons.append('GPS accuracy is not recorded, so the point needs confirmation before official use.')
    elif quality_flags['accuracy_level'] == 'needs-confirmation':
        score -= 20
        reasons.append('GPS accuracy is moderate; operator or field confirmation is recommended.')
    elif quality_flags['accuracy_level'] == 'weak-gps':
        score -= 45
        reasons.append('GPS accuracy is weak enough to require field verification.')

    if quality_flags['possible_duplicate']:
        score -= 25
        reasons.append('The national address code or nearby-point check suggests a possible duplicate.')
    if road_status == 'pending-review':
        score -= 10
        reasons.append('Map-derived road/local-area suggestion is waiting for operator review.')
    if not item.get('territory_id'):
        score -= 5
        reasons.append('Official routing area is not selected yet; keep map local-area labels as suggestions.')
    if not item.get('landmark'):
        score -= 5
        reasons.append('No landmark was supplied, which can slow field confirmation.')

    score = max(0, min(100, score))
    if status_value == 'rejected':
        triage_bucket = 'closed-rejected'
        process_stage = 'Closed — rejected'
        next_action = 'closed'
        next_action_label = 'No action unless reopened by an authorized reviewer.'
    elif status_value == 'registry-ready':
        triage_bucket = 'registry-ready'
        process_stage = 'Approved for official case-file registry'
        next_action = 'await-project-publication-approval'
        next_action_label = 'Hold for full project/institutional approval before certificate, physical signage, or public publication.'
    elif status_value == 'needs-field-check' or field_status in {'visited', 'needs-recapture', 'blocked'} or quality_flags['requires_field_check'] or quality_flags['possible_duplicate']:
        triage_bucket = 'field-verification'
        process_stage = 'Needs field verification'
        next_action = 'send-field-check'
        next_action_label = 'Send to field team or record field status before approval.'
    elif road_status == 'pending-review':
        triage_bucket = 'operator-road-review'
        process_stage = 'Operator review'
        next_action = 'review-map-suggestion'
        next_action_label = 'Accept, edit, or reject the map-derived road/local-area suggestion.'
    elif status_value in {'submitted', 'under-review'}:
        triage_bucket = 'ready-for-operator'
        process_stage = 'Ready for operator decision'
        next_action = 'operator-review'
        next_action_label = 'Review evidence, then approve the official case file or send to field check.'
    else:
        triage_bucket = 'monitor'
        process_stage = status_value.replace('-', ' ').title()
        next_action = 'monitor'
        next_action_label = 'Monitor this request for the next workflow event.'

    if not reasons:
        reasons.append('GPS quality and duplicate checks do not show immediate blockers.')

    return {
        'quality_score': score,
        'triage_bucket': triage_bucket,
        'process_stage': process_stage,
        'next_best_action': next_action,
        'next_best_action_label': next_action_label,
        'reasons': reasons[:4],
        'citizen_tracking': {
            'tracking_code': item.get('id'),
            'public_status_label': process_stage,
            'public_next_step': next_action_label,
            'public_lookup_url': f"/code/{item.get('grid_code')}",
        },
        'routing': {
            'assigned': bool(item.get('territory_id')),
            'territory_id': item.get('territory_id'),
            'territory_name': item.get('territory_name'),
            'assignment_source': (item.get('routing_assignment') or {}).get('routing_assignment_source') if isinstance(item.get('routing_assignment'), dict) else ('manual' if item.get('territory_id') else None),
            'assignment_confidence': (item.get('routing_assignment') or {}).get('routing_assignment_confidence') if isinstance(item.get('routing_assignment'), dict) else ('operator-confirmed' if item.get('territory_id') else None),
        },
        'field_work': {
            'required': triage_bucket == 'field-verification',
            'status': field_status,
            'field_submission_id': item.get('field_submission_id'),
        },
        'signage': {
            'ready': status_value == 'published',
            'batch': item.get('signage_batch'),
            'export_status': 'locked-until-full-project-approval' if status_value == 'registry-ready' else ('ready-for-export' if status_value == 'published' else 'not-ready'),
        },
        'corrections': {
            'watch_public_reports': status_value in {'published', 'under-review'},
            'recommended_queue': 'public-corrections' if status_value == 'published' else 'operator-review',
        },
        'integration': {
            'api_record_state': 'public' if status_value == 'published' else ('internal-registry' if status_value == 'registry-ready' else 'not-public'),
            'partner_api_ready': status_value == 'published',
        },
        'dashboard': {
            'metric_bucket': triage_bucket,
            'counts_toward_active_queue': status_value in {'submitted', 'under-review', 'needs-field-check'},
        },
    }


def _automation_summary(enriched_items: list[dict[str, Any]], corrections: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    now = _now_utc()
    corrections = corrections or []
    buckets: dict[str, int] = defaultdict(int)
    next_actions: dict[str, int] = defaultdict(int)
    total_score = 0
    active_count = 0
    field_required = 0
    registry_ready = 0
    api_ready = 0
    for item in enriched_items:
        automation = item.get('automation') or {}
        buckets[automation.get('triage_bucket', 'unknown')] += 1
        next_actions[automation.get('next_best_action', 'unknown')] += 1
        total_score += int(automation.get('quality_score') or 0)
        if automation.get('dashboard', {}).get('counts_toward_active_queue'):
            active_count += 1
        if automation.get('field_work', {}).get('required'):
            field_required += 1
        if automation.get('integration', {}).get('api_record_state') == 'internal-registry':
            registry_ready += 1
        if automation.get('integration', {}).get('partner_api_ready'):
            api_ready += 1
    total = len(enriched_items)
    return {
        'total': total,
        'active_queue': active_count,
        'average_quality_score': round(total_score / total, 1) if total else 0,
        'field_required': field_required,
        'registry_ready': registry_ready,
        'partner_api_ready': api_ready,
        'triage_buckets': [{'bucket': key, 'count': value} for key, value in sorted(buckets.items())],
        'next_actions': [{'action': key, 'count': value} for key, value in sorted(next_actions.items())],
        'sla': _sla_summary(enriched_items, corrections, now),
        'publication_hold': _publication_hold_summary(enriched_items, now),
    }


def _sla_drilldown(enriched_items: list[dict[str, Any]], corrections: list[dict[str, Any]], state_filter: str | None = None) -> dict[str, Any]:
    now = _now_utc()
    sla_items = _sla_summary(enriched_items, corrections, now)['items']
    enriched_by_id = {item.get('id'): item for item in enriched_items}
    rows = []
    for sla in sla_items:
        if state_filter and sla['state'] != state_filter:
            continue
        enriched = enriched_by_id.get(sla['id'], {}) if sla['type'] == 'geotag' else {}
        automation = enriched.get('automation') or {}
        rows.append({
            **sla,
            'address_label': enriched.get('address_label'),
            'grid_code': enriched.get('grid_code'),
            'territory_name': enriched.get('territory_name'),
            'triage_bucket': automation.get('triage_bucket'),
            'next_best_action': automation.get('next_best_action'),
            'next_best_action_label': automation.get('next_best_action_label'),
        })
    return {'state': state_filter or 'all', 'count': len(rows), 'items': rows}


def _public_tracking_payload(item: dict[str, Any], *, lookup_type: str) -> dict[str, Any]:
    enriched = _enrich_geotag_submissions([item])[0]
    automation = enriched.get('automation', {})
    return _strip_identity_fields({
        'lookup_type': lookup_type,
        'id': enriched['id'],
        'grid_code': enriched['grid_code'],
        'status': enriched['status'],
        'address_label': enriched['address_label'],
        'created_at': enriched.get('created_at'),
        'updated_at': enriched.get('updated_at'),
        'tracking': automation.get('citizen_tracking'),
        'process_stage': automation.get('process_stage'),
        'next_step': automation.get('next_best_action_label'),
        'public_lookup_url': enriched.get('public_lookup_url'),
        'publication_state': automation.get('integration', {}).get('api_record_state'),
    })


def _csv_cell(value: Any) -> str:
    text = '' if value is None else str(value)
    return '"' + text.replace('"', '""') + '"'


def _signage_pack(status_value: str = 'published') -> dict[str, Any]:
    rows = signage_export(status=status_value).get('items', [])
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    batch_id = f"signage-pack-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    header = ['grid_code', 'signage_text', 'address_label', 'territory_name', 'latitude', 'longitude', 'accuracy_meters', 'batch', 'status']
    csv_lines = [','.join(header)]
    for row in rows:
        csv_lines.append(','.join(_csv_cell(row.get(key)) for key in header))
    return {
        'batch_id': batch_id,
        'generated_at': generated_at,
        'status_filter': status_value,
        'record_count': len(rows),
        'items': rows,
        'csv': '\n'.join(csv_lines),
        'print_summary': [
            f"{row.get('grid_code')} — {row.get('signage_text') or row.get('address_label')}"
            for row in rows
        ],
        'operator_note': 'Physical signage packs include published records only. Registry-ready case files stay locked until full project/institutional approval.',
    }


def _enrich_geotag_submissions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    code_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        code_groups[item.get('grid_code', '')].append(item)
    enriched = []
    for item in items:
        group = code_groups.get(item.get('grid_code', ''), [])
        quality_flags = _geotag_quality_flags(item, len(group))
        enriched_item = {
            **item,
            'quality_flags': quality_flags,
            'duplicate_group': {
                'count': len(group),
                'items': [
                    {'id': other.get('id'), 'address_label': other.get('address_label'), 'status': other.get('status')}
                    for other in group
                ],
            },
            'public_lookup_url': f"/code/{item.get('grid_code')}",
        }
        enriched_item['automation'] = _geotag_automation(enriched_item, quality_flags, len(group))
        enriched.append(enriched_item)
    return enriched


@app.get('/')
def root() -> dict[str, str]:
    return {'message': 'eg-addressing-api online', 'docs': '/docs'}


@app.get('/api/v1/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': 'eg-addressing-api', 'version': '0.1.0', 'environment': APP_ENV}


@app.get('/api/v1/meta')
def meta() -> dict[str, Any]:
    return {
        'platform': {'name': 'Equatorial Guinea National Digital Addressing Platform', 'mode': 'operational-readiness'},
        'stack': {'backend': 'FastAPI', 'frontend': 'Next.js', 'database': 'PostgreSQL + PostGIS', 'cache': 'Redis', 'storage': 'MinIO'},
        'modules': MODULES,
        'roles': ['viewer', 'editor', 'admin', 'agency_viewer'],
    }


@app.post('/api/v1/auth/login')
def login(payload: LoginRequest, response: Response) -> dict[str, Any]:
    try:
        session = authenticate_user_session(payload.username, payload.password)
        token = session['token']
        session['session_ttl_hours'] = SESSION_TTL_HOURS
        session['auth_mode'] = _auth_mode()
        if _using_secure_cookie_mode():
            csrf_token = secrets.token_urlsafe(32)
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=token,
                max_age=SESSION_TTL_HOURS * 3600,
                httponly=True,
                secure=SESSION_COOKIE_SECURE,
                samesite='lax',
                path='/',
            )
            response.set_cookie(
                key=CSRF_COOKIE_NAME,
                value=csrf_token,
                max_age=SESSION_TTL_HOURS * 3600,
                httponly=False,
                secure=SESSION_COOKIE_SECURE,
                samesite='lax',
                path='/',
            )
            session.pop('token', None)
        return session
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@app.get('/api/v1/auth/me')
def auth_me(authorization: str | None = Header(default=None), eg_addressing_session: str | None = Cookie(default=None)) -> dict[str, Any]:
    return {'user': _current_user(authorization, eg_addressing_session), 'session_ttl_hours': SESSION_TTL_HOURS, 'auth_mode': _auth_mode()}


@app.post('/api/v1/auth/logout', status_code=status.HTTP_204_NO_CONTENT)
def auth_logout(authorization: str | None = Header(default=None), eg_addressing_session: str | None = Cookie(default=None)) -> Response:
    token = _session_token(authorization=authorization, session_cookie=eg_addressing_session)
    user = resolve_user_from_token(token)
    revoke_user_session(token, actor=user)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(SESSION_COOKIE_NAME, path='/')
    response.delete_cookie(CSRF_COOKIE_NAME, path='/')
    return response


@app.get('/api/v1/admin/users')
def admin_list_users(authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    return {'items': [_staff_user_public(item) for item in list_staff_users()]}


@app.post('/api/v1/admin/users', status_code=status.HTTP_201_CREATED)
def admin_create_user(payload: StaffUserCreateRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    try:
        return _staff_user_public(create_staff_user(payload.model_dump(), actor=user))
    except DuplicateUserError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InvalidUserRoleError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.patch('/api/v1/admin/users/{user_id}')
def admin_update_user(user_id: str, payload: StaffUserUpdateRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    update_payload = payload.model_dump(exclude_unset=True)
    if user_id == user['id'] and (update_payload.get('is_active') is False or update_payload.get('role') not in {None, 'admin'}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='cannot deactivate or downgrade current admin account')
    try:
        return _staff_user_public(update_staff_user(user_id, update_payload, actor=user))
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidUserRoleError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.post('/api/v1/admin/users/{user_id}/disable')
def admin_disable_user(user_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    if user_id == user['id']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='cannot disable current admin account')
    try:
        return _staff_user_public(disable_staff_user(user_id, actor=user))
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidUserRoleError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.post('/api/v1/admin/users/{user_id}/revoke-sessions')
def admin_revoke_user_sessions(user_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    if user_id == user['id']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='cannot revoke current admin sessions')
    try:
        return revoke_staff_user_sessions(user_id, actor=user)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidUserRoleError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc



@app.get('/api/v1/territories/provinces')
def list_provinces() -> dict[str, list[dict[str, str]]]:
    return {'items': list_provinces_db()}


@app.get('/api/v1/provinces')
def list_public_provinces() -> dict[str, list[dict[str, str]]]:
    return {'items': list_provinces_db()}


@app.get('/api/v1/admin-units')
def admin_units(
    level: str | None = Query(default=None),
    parent_id: str | None = Query(default=None),
    province_code: str | None = Query(default=None),
) -> dict[str, list[dict[str, Any]]]:
    return {'items': list_admin_units_db(level=level, parent_id=parent_id, province_code=province_code)}


def _public_territory_metadata(row: dict[str, Any]) -> dict[str, Any]:
    is_official_municipality = row.get('type') == 'official-municipality' and row.get('readiness') == 'official-routing'
    is_map_referenced = row.get('type') == 'map-referenced-local-area'
    if is_official_municipality:
        source_label = 'Administrative division table / INEGE-referenced source'
        confidence_label = 'Administrative unit confirmed'
        geometry_status = 'Name-based routing area; surveyed boundary not attached'
        public_status = 'Internal routing only until operator verification and controlled publication'
        routing_status_label = 'Official administrative route'
    elif is_map_referenced:
        source_label = 'Map/local reference used for intake routing'
        confidence_label = 'Local reference; requires operator confirmation'
        geometry_status = 'Point/intake area only; not an official surveyed boundary'
        public_status = 'Pending field verification before publication'
        routing_status_label = 'Referenced local area'
    else:
        source_label = 'Registry seed / operator-maintained routing record'
        confidence_label = 'Registry record; confirm before publication'
        geometry_status = 'Routing record; official geometry not attached'
        public_status = 'Internal review state'
        routing_status_label = 'Pending field verification'
    return {
        'id': row['id'],
        'name': row['name'],
        'province': row.get('province'),
        'province_code': row.get('province_code'),
        'type': row.get('type'),
        'readiness': row.get('readiness'),
        'admin_unit_name': row.get('admin_unit_name'),
        'admin_unit_level': row.get('admin_unit_level'),
        'routing_status_label': routing_status_label,
        'source_label': source_label,
        'confidence_label': confidence_label,
        'geometry_status': geometry_status,
        'public_status': public_status,
    }


@app.get('/api/v1/public/territory-options')
def public_territory_options(
    request: Request,
    province_code: str | None = Query(default=None),
) -> dict[str, list[dict[str, Any]]]:
    _check_public_rate_limit(request, 'public-territory-options')
    rows = fetch_territories(province_code=province_code, include_archived=False)
    return {'items': [_public_territory_metadata(row) for row in rows]}


@app.get('/api/v1/territories')
def list_territories(
    q: str | None = Query(default=None),
    province_code: str | None = Query(default=None),
    readiness: str | None = Query(default=None),
    include_archived: bool = Query(default=False),
    page: int = Query(default=1),
    per_page: int = Query(default=100),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return fetch_territories_page(q=q, province_code=province_code, readiness=readiness, include_archived=include_archived, page=page, per_page=per_page)


@app.get('/api/v1/territories/{territory_id}')
def territory_detail(territory_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    try:
        return get_territory(territory_id)
    except TerritoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post('/api/v1/territories', status_code=status.HTTP_201_CREATED)
def create_territory_endpoint(payload: TerritoryCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return create_territory(payload.model_dump(), actor=user)
    except DuplicateTerritoryError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (UnknownProvinceError, UnknownAdminUnitError, AdminUnitProvinceMismatchError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.patch('/api/v1/territories/{territory_id}')
def update_territory_endpoint(territory_id: str, payload: TerritoryUpdate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_territory(territory_id, payload.model_dump(), actor=user)
    except DuplicateTerritoryError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (UnknownProvinceError, UnknownAdminUnitError, AdminUnitProvinceMismatchError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except TerritoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.delete('/api/v1/territories/{territory_id}')
def archive_territory_endpoint(territory_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    try:
        return archive_territory(territory_id, actor=user)
    except TerritoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get('/api/v1/audit-logs')
def audit_logs(entity_type: str | None = Query(default=None), entity_id: str | None = Query(default=None), page: int = Query(default=1), per_page: int = Query(default=50, ge=1, le=100), authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    return list_audit_logs_page(entity_type=entity_type, entity_id=entity_id, page=page, per_page=per_page)


@app.get('/api/v1/roads')
def list_roads(q: str | None = Query(default=None), territory_id: str | None = Query(default=None), include_archived: bool = Query(default=False), page: int = Query(default=1), per_page: int = Query(default=100), authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return fetch_roads_page(q=q, territory_id=territory_id, include_archived=include_archived, page=page, per_page=per_page)


@app.get('/api/v1/roads/{road_id}')
def road_detail(road_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    try:
        return get_road(road_id)
    except RoadNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post('/api/v1/roads', status_code=status.HTTP_201_CREATED)
def create_road_endpoint(payload: RoadCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return create_road(payload.model_dump(), actor=user)
    except UnknownTerritoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DuplicateRoadError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.patch('/api/v1/roads/{road_id}')
def update_road_endpoint(road_id: str, payload: RoadCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_road(road_id, payload.model_dump(), actor=user)
    except (UnknownTerritoryError, DuplicateRoadError) as exc:
        code = status.HTTP_409_CONFLICT if isinstance(exc, DuplicateRoadError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    except RoadNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.delete('/api/v1/roads/{road_id}')
def archive_road_endpoint(road_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    try:
        return archive_road(road_id, actor=user)
    except RoadNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get('/api/v1/buildings')
def list_buildings(q: str | None = Query(default=None), territory_id: str | None = Query(default=None), include_archived: bool = Query(default=False), page: int = Query(default=1), per_page: int = Query(default=100), authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return fetch_buildings_page(q=q, territory_id=territory_id, include_archived=include_archived, page=page, per_page=per_page)


@app.get('/api/v1/buildings/{building_id}')
def building_detail(building_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    try:
        return get_building(building_id)
    except BuildingNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post('/api/v1/buildings', status_code=status.HTTP_201_CREATED)
def create_building_endpoint(payload: BuildingCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return create_building(payload.model_dump(), actor=user)
    except (UnknownTerritoryError, UnknownRoadError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DuplicateBuildingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.patch('/api/v1/buildings/{building_id}')
def update_building_endpoint(building_id: str, payload: BuildingCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_building(building_id, payload.model_dump(), actor=user)
    except (UnknownTerritoryError, UnknownRoadError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DuplicateBuildingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except BuildingNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.delete('/api/v1/buildings/{building_id}')
def archive_building_endpoint(building_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    try:
        return archive_building(building_id, actor=user)
    except BuildingNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get('/api/v1/addresses')
def list_addresses(q: str | None = Query(default=None), territory_id: str | None = Query(default=None), status_filter: str | None = Query(default=None, alias='status'), include_archived: bool = Query(default=False), page: int = Query(default=1), per_page: int = Query(default=100), authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return fetch_addresses_page(q=q, territory_id=territory_id, status=status_filter, include_archived=include_archived, page=page, per_page=per_page)


@app.get('/api/v1/addresses/{address_id}')
def address_detail(address_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    try:
        return get_address(address_id)
    except AddressNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post('/api/v1/addresses', status_code=status.HTTP_201_CREATED)
def create_address_endpoint(payload: AddressCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return create_address(payload.model_dump(), actor=user)
    except (UnknownTerritoryError, UnknownRoadError, UnknownBuildingError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DuplicateAddressError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.patch('/api/v1/addresses/{address_id}')
def update_address_endpoint(address_id: str, payload: AddressCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_address(address_id, payload.model_dump(), actor=user)
    except (UnknownTerritoryError, UnknownRoadError, UnknownBuildingError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DuplicateAddressError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except AddressNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.delete('/api/v1/addresses/{address_id}')
def archive_address_endpoint(address_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    try:
        return archive_address(address_id, actor=user)
    except AddressNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get('/api/v1/field/assignments')
def field_assignments(authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return {'items': list_field_assignments()}


@app.get('/api/v1/field/geotag-tasks')
def field_geotag_tasks(status_filter: str | None = Query(default=None, alias='status'), territory_id: str | None = Query(default=None), authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return {'items': _enrich_geotag_submissions(list_field_geotag_tasks(status=status_filter, territory_id=territory_id))}


@app.post('/api/v1/field/geotag-tasks/{submission_id}/status')
def update_field_geotag_task_status(submission_id: str, payload: GeotagFieldStatusRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_geotag_field_status(submission_id, payload.field_status, payload.field_note, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/field/geotag-tasks/{submission_id}/evidence')
def record_field_geotag_task_evidence(submission_id: str, payload: GeotagFieldEvidenceRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return _strip_identity_fields(record_geotag_field_evidence(submission_id, payload.evidence_type, payload.evidence_reference, payload.evidence_note, actor=user))
    except (SubmissionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.get('/api/v1/field/submissions')
def field_submissions(review_status: str | None = Query(default=None), territory_id: str | None = Query(default=None), page: int = Query(default=1), per_page: int = Query(default=100), authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return paginated_response(list_field_submissions(review_status=review_status, territory_id=territory_id), page=page, per_page=per_page)



@app.post('/api/v1/field/spatial-evidence/enrich')
def enrich_field_spatial_evidence_endpoint(payload: FieldSpatialEvidenceEnrichRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        enriched = enrich_field_spatial_evidence(payload.submission_type, payload.spatial_evidence, payload.territory_id)
    except (InvalidSubmissionActionError, UnknownTerritoryError, TerritoryNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {'spatial_evidence': enriched, 'review_required': True, 'actor': user['username']}

@app.post('/api/v1/field/submissions', status_code=status.HTTP_201_CREATED)
def create_field_submission_endpoint(payload: FieldSubmissionCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return create_field_submission(payload.model_dump(), actor=user)
    except (UnknownTerritoryError, InvalidSubmissionActionError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SubmissionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def _safe_evidence_file_name(file_name: str) -> str:
    name = Path(file_name).name.strip().replace('\x00', '')
    if not name or len(name) > 120:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid evidence file name')
    suffix = Path(name).suffix.lower()
    if suffix in EVIDENCE_BLOCKED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='evidence file type is not allowed')
    return name


def _validate_evidence_upload(file_name: str, content_type: str, content: bytes) -> str:
    safe_name = _safe_evidence_file_name(file_name)
    normalized_type = (content_type or '').split(';', 1)[0].strip().lower()
    if normalized_type not in EVIDENCE_ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='evidence content type is not allowed')
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='evidence file is empty')
    if len(content) > EVIDENCE_FILE_MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail='evidence file is too large')
    signature = content[:8]
    if normalized_type == 'application/pdf' and not content.startswith(b'%PDF-'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid PDF evidence file')
    if normalized_type == 'image/png' and signature != b'\x89PNG\r\n\x1a\n':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid PNG evidence file')
    if normalized_type == 'image/jpeg' and not content.startswith(b'\xff\xd8\xff'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid JPEG evidence file')
    if normalized_type == 'image/webp' and not (content.startswith(b'RIFF') and content[8:12] == b'WEBP'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid WEBP evidence file')
    return safe_name


@app.post('/api/v1/field/submissions/{submission_id}/evidence-files', status_code=status.HTTP_201_CREATED)
async def upload_field_submission_evidence_file(
    submission_id: str,
    request: Request,
    attachment_index: int = Query(default=0, ge=0, le=5),
    file_name: str = Query(min_length=3, max_length=120),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    content = await request.body()
    content_type = request.headers.get('content-type', '')
    safe_name = _validate_evidence_upload(file_name, content_type, content)
    file_id = f'evidence-{uuid.uuid4().hex[:12]}'
    object_key = f'field-submissions/{submission_id}/{file_id}/{safe_name}'
    try:
        storage_metadata = store_evidence_object(object_key, content, content_type.split(';', 1)[0].strip().lower())
        updated = attach_field_submission_evidence_file(
            submission_id,
            attachment_index,
            {
                **storage_metadata,
                'file_id': file_id,
                'file_name': safe_name,
                'uploaded_at': _now_utc().isoformat(),
            },
            actor=user,
        )
    except EvidenceStorageError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except SubmissionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EvidenceAttachmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidSubmissionActionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {'file': {'file_id': file_id, 'file_name': safe_name, 'content_type': storage_metadata['content_type'], 'size_bytes': storage_metadata['size_bytes'], 'access': 'protected'}, 'submission': updated}


@app.get('/api/v1/field/submissions/{submission_id}/evidence-history')
def field_submission_evidence_history(submission_id: str, limit: int = Query(default=50, ge=1, le=100), authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    try:
        return {'items': list_field_submission_evidence_history(submission_id, limit=limit)}
    except SubmissionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post('/api/v1/field/submissions/{submission_id}/evidence-review')
def review_field_submission_evidence_endpoint(submission_id: str, payload: EvidenceReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return review_field_submission_evidence(submission_id, payload.attachment_index, payload.decision, payload.reviewer_note, file_id=payload.file_id, actor=user)
    except SubmissionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EvidenceAttachmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidSubmissionActionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.get('/api/v1/field/submissions/{submission_id}/evidence-files/{file_id}')
def download_field_submission_evidence_file(submission_id: str, file_id: str, authorization: str | None = Header(default=None)) -> StreamingResponse:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    try:
        metadata = get_field_submission_evidence_file(submission_id, file_id, actor=user)
        content = read_evidence_object(str(metadata['object_key']))
    except SubmissionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (EvidenceAttachmentNotFoundError, EvidenceObjectNotFound) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EvidenceStorageError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    headers = {'Content-Disposition': f'attachment; filename="{Path(str(metadata.get("file_name") or "evidence-file")).name}"'}
    return StreamingResponse(iter([content]), media_type=str(metadata.get('content_type') or 'application/octet-stream'), headers=headers)


@app.post('/api/v1/field/submissions/{submission_id}/under-review')
def mark_submission_under_review(submission_id: str, payload: ReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_submission_review_status(submission_id, 'under-review', payload.reviewer_note, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/field/submissions/{submission_id}/approve')
def approve_submission_endpoint(submission_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return approve_submission(submission_id, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError, UnknownTerritoryError, UnknownRoadError, UnknownBuildingError, DuplicateRoadError, DuplicateBuildingError, DuplicateAddressError) as exc:
        if isinstance(exc, SubmissionNotFoundError):
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, (DuplicateRoadError, DuplicateBuildingError, DuplicateAddressError)):
            code = status.HTTP_409_CONFLICT
        else:
            code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/field/submissions/{submission_id}/reject')
def reject_submission_endpoint(submission_id: str, payload: ReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_submission_review_status(submission_id, 'rejected', payload.reviewer_note, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/field/submissions/{submission_id}/rework')
def rework_submission_endpoint(submission_id: str, payload: ReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_submission_review_status(submission_id, 'needs-rework', payload.reviewer_note, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


def _build_public_extract(result: dict[str, Any]) -> dict[str, Any]:
    public_code = result.get('public_code') or result.get('address_id')
    is_staging_reference = result.get('source') == 'staging-reference-record' or result.get('verification_status') == 'controlled-staging-reference'
    return {
        **result,
        'document_title': 'Staging Address Registry Extract' if is_staging_reference else 'Official Address Registry Extract',
        'document_reference': f"EXTRACT-{public_code}",
        'record_locator': public_code,
        'issued_for': result.get('address_label'),
        'issuing_authority': 'Controlled staging environment · Not an official production record' if is_staging_reference else 'Republic of Equatorial Guinea · National Digital Addressing Platform',
        'extract_status': 'staging-reference' if is_staging_reference else ('ready' if result.get('match_status') == 'verified' else 'not-available'),
    }


@app.get('/api/v1/verification/lookup')
def verification_lookup(query: str = Query(min_length=3)) -> dict[str, Any]:
    result = verify_address(query)
    if not result:
        return {
            'query': query,
            'match_status': 'not-found',
            'public_code': None,
            'address_label': 'No published registry record found',
            'jurisdiction': 'Pilot registry lookup',
            'verification_status': 'not-found',
            'publication_state': 'unpublished',
            'verification_note': 'The query does not match a published address record yet.',
        }
    return result


@app.get('/api/v1/public/verification/{query}')
def public_verification_lookup(query: str, request: Request) -> dict[str, Any]:
    _check_public_rate_limit(request, 'public-verification')
    return verification_lookup(query=query)


@app.get('/api/v1/public/issuance/{query}')
def public_issuance_lookup(query: str, request: Request) -> dict[str, Any]:
    _check_public_rate_limit(request, 'public-issuance')
    return _build_public_extract(verification_lookup(query=query))


@app.get('/api/v1/public/address-code/{code}')
def public_address_code_lookup(code: str, request: Request) -> dict[str, Any]:
    _check_public_rate_limit(request, 'public-address-code')
    return describe_address_code(code)


def _strip_identity_fields(value: Any) -> Any:
    identity_keys = {
        'citizen_name',
        'citizen_contact',
        'dip_last4',
        'dip_masked',
        'dip_full',
        'identity_verification_status',
        'identity_document_verified',
        'reviewer_note',
        'field_note',
    }
    if isinstance(value, dict):
        return {key: _strip_identity_fields(item) for key, item in value.items() if key not in identity_keys}
    if isinstance(value, list):
        return [_strip_identity_fields(item) for item in value]
    return value


@app.get('/api/v1/public/address-code/{code}/record')
def public_address_code_record(code: str, request: Request) -> dict[str, Any]:
    _check_public_rate_limit(request, 'public-address-code-record')
    return _strip_identity_fields(public_address_code_record_lookup(code))


@app.post('/api/v1/public/corrections', status_code=status.HTTP_201_CREATED)
def create_public_correction(payload: AddressCorrectionCreate, request: Request) -> dict[str, Any]:
    _check_public_rate_limit(request, 'public-corrections')
    if not payload.privacy_notice_acknowledged:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='privacy notice acknowledgement required')
    try:
        return create_address_correction(payload.model_dump(), actor=None)
    except AddressNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post('/api/v1/public/geotag/preview')
def public_geotag_preview(payload: CitizenGeotagPreviewRequest, request: Request) -> dict[str, Any]:
    _check_public_rate_limit(request, 'public-geotag-preview')
    try:
        return preview_citizen_geotag(payload.latitude, payload.longitude, territory_id=payload.territory_id, province_code=payload.province_code)
    except UnknownTerritoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.post('/api/v1/public/geotag/road-suggestion')
def public_road_suggestion(payload: RoadSuggestionRequest, request: Request) -> dict[str, Any]:
    _check_public_rate_limit(request, 'public-road-suggestion')
    return suggest_nearest_road_name(payload.latitude, payload.longitude)


@app.post('/api/v1/public/geotag-submissions', status_code=status.HTTP_201_CREATED)
def create_public_geotag_submission(payload: CitizenGeotagCreate, request: Request) -> dict[str, Any]:
    _check_public_rate_limit(request, 'public-geotag-submissions')
    if not payload.privacy_notice_acknowledged:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='privacy notice acknowledgement required')
    try:
        created = create_citizen_geotag_submission(payload.model_dump(), actor=None)
        enriched = _enrich_geotag_submissions([created])[0]
        return enriched
    except UnknownTerritoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.get('/api/v1/public/geotag-submissions/{submission_id}/tracking')
def public_geotag_submission_tracking(submission_id: str, request: Request) -> dict[str, Any]:
    _check_public_rate_limit(request, 'public-geotag-tracking')
    items = [item for item in list_citizen_geotag_submissions() if item['id'] == submission_id]
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='citizen geotag submission not found')
    return _public_tracking_payload(items[0], lookup_type='submission-id')


@app.get('/api/v1/public/tracking/{lookup_code}')
def public_tracking_lookup(lookup_code: str, request: Request) -> dict[str, Any]:
    _check_public_rate_limit(request, 'public-tracking')
    normalized = lookup_code.strip()
    items = list_citizen_geotag_submissions()
    for item in items:
        if item['id'] == normalized:
            return _public_tracking_payload(item, lookup_type='submission-id')
    for item in items:
        if str(item.get('grid_code', '')).upper() == normalized.upper():
            return _public_tracking_payload(item, lookup_type='address-code')
    if normalized.upper().startswith('EG-'):
        record = _strip_identity_fields(public_address_code_record_lookup(normalized))
        return {
            'lookup_type': 'address-code',
            'grid_code': normalized,
            'status': record.get('publication_status', 'not_public'),
            'address_label': (record.get('record') or {}).get('address_label') if isinstance(record.get('record'), dict) else None,
            'process_stage': 'Published record available' if record.get('publication_status') == 'published' else 'Address code not public yet',
            'next_step': 'Use the public record page when publication is approved.' if record.get('publication_status') == 'published' else 'The code is valid or reserved, but public details are locked until approval.',
            'publication_state': 'public' if record.get('publication_status') == 'published' else 'not-public',
            'public_lookup_url': f'/code/{normalized}',
            'address_record': record,
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='tracking record was not found')


@app.get('/api/v1/address-records/search')
def address_record_search(
    q: str | None = Query(default=None, max_length=160),
    status_value: str | None = Query(default=None, alias='status', max_length=40),
    province_code: str | None = Query(default=None, max_length=8),
    limit: int = Query(default=25, ge=1, le=100),
    authorization: str | None = Header(default=None),
) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return {'items': search_address_records(q=q, status=status_value, province_code=province_code, limit=limit)}



@app.get('/api/v1/address-records/export')
def address_records_export_endpoint(status_value: str = Query(default='published', alias='status', max_length=40), authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return address_record_export(status=status_value)


@app.get('/api/v1/address-records/nearby')
def address_records_nearby_endpoint(
    latitude: float | None = Query(default=None, ge=-90, le=90),
    longitude: float | None = Query(default=None, ge=-180, le=180),
    radius_meters: float = Query(default=50.0, ge=1, le=5000),
    limit: int = Query(default=10, ge=1, le=50),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    if latitude is None or longitude is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='latitude and longitude are required')
    try:
        return find_nearby_address_records(latitude=latitude, longitude=longitude, radius_meters=radius_meters, limit=limit)
    except InvalidSubmissionActionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.get('/api/v1/address-records/{address_code}')
def address_record_case_file(address_code: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    try:
        return _sanitize_case_file(get_address_record_case_file(address_code))
    except AddressNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get('/api/v1/address-records/{address_code}/certificate')
def address_record_certificate_endpoint(address_code: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    try:
        return _strip_identity_fields(build_address_record_certificate(address_code))
    except AddressNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidSubmissionActionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.get('/api/v1/geotag-submissions')
def geotag_submissions(status: str | None = Query(default=None), territory_id: str | None = Query(default=None), authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return {'items': _enrich_geotag_submissions(list_citizen_geotag_submissions(status=status, territory_id=territory_id))}


@app.get('/api/v1/geotag-submissions/automation/summary')
def geotag_automation_summary(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    enriched = _enrich_geotag_submissions(list_citizen_geotag_submissions())
    return _automation_summary(enriched, list_address_corrections())


@app.get('/api/v1/geotag-submissions/automation/sla-drilldown')
def geotag_sla_drilldown(state: str | None = Query(default=None, pattern='^(on_time|approaching|overdue|unknown)$'), authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    enriched = _enrich_geotag_submissions(list_citizen_geotag_submissions())
    return _sla_drilldown(enriched, list_address_corrections(), state_filter=state)


@app.get('/api/v1/geotag-submissions/duplicates/summary')
def geotag_duplicates_summary(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return geotag_duplicate_summary()


@app.get('/api/v1/geotag-submissions/{submission_id}/certificate')
def geotag_certificate(submission_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    try:
        return _strip_identity_fields(build_geotag_certificate(submission_id))
    except SubmissionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidSubmissionActionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.get('/api/v1/geotag-submissions/{submission_id}/history')
def geotag_submission_history(submission_id: str, authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return {'items': list_audit_logs(entity_type='citizen_geotag_submission', entity_id=submission_id, limit=25)}


@app.post('/api/v1/geotag-submissions/{submission_id}/identity')
def geotag_identity_review(submission_id: str, payload: GeotagIdentityReviewRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return verify_geotag_identity(submission_id, payload.dip_full, payload.identity_document_verified, payload.reviewer_note, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/geotag-submissions/{submission_id}/under-review')
def mark_geotag_under_review(submission_id: str, payload: GeotagReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_citizen_geotag_status(submission_id, 'under-review', payload.reviewer_note, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/geotag-submissions/{submission_id}/field-check')
def send_geotag_to_field_check(submission_id: str, payload: GeotagReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_citizen_geotag_status(submission_id, 'needs-field-check', payload.reviewer_note, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError, UnknownTerritoryError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/geotag-submissions/{submission_id}/registry-ready')
def mark_geotag_registry_ready(submission_id: str, payload: GeotagReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        updated = update_citizen_geotag_status(submission_id, 'registry-ready', payload.reviewer_note, actor=user)
        address_record = upsert_address_record_from_geotag(updated, actor=user)
        return {**updated, 'address_record': address_record}
    except (SubmissionNotFoundError, InvalidSubmissionActionError, UnknownTerritoryError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/geotag-submissions/{submission_id}/publication-simulation')
def simulate_geotag_publication(submission_id: str, payload: GeotagReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return simulate_geotag_publication_path(submission_id, payload.reviewer_note, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/geotag-submissions/{submission_id}/publish')
def publish_geotag_case_file(submission_id: str, payload: GeotagReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    if not PUBLICATION_RELEASE_ENABLED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='publication release gate is disabled')
    try:
        return _strip_identity_fields(publish_geotag_submission(submission_id, payload.reviewer_note, actor=user))
    except (SubmissionNotFoundError, InvalidSubmissionActionError, UnknownTerritoryError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/geotag-submissions/{submission_id}/reject')
def reject_geotag_submission(submission_id: str, payload: GeotagReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_citizen_geotag_status(submission_id, 'rejected', payload.reviewer_note, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/geotag-submissions/{submission_id}/duplicate-decision')
def geotag_duplicate_decision(submission_id: str, payload: GeotagDuplicateDecisionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return record_geotag_duplicate_decision(submission_id, payload.duplicate_action, payload.reviewer_note, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/geotag-submissions/{submission_id}/road-suggestion')
def geotag_road_suggestion_review(submission_id: str, payload: RoadSuggestionReviewRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return review_geotag_road_suggestion(submission_id, payload.action, payload.reviewed_road_name, payload.reviewer_note, actor=user)
    except (SubmissionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, SubmissionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.get('/api/v1/signage/export')
def signage_export_endpoint(status: str = Query(default='published'), authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin', 'agency_viewer')
    return signage_export(status=status)


@app.get('/api/v1/signage/pack')
def signage_pack_endpoint(status: str = Query(default='published'), authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return _signage_pack(status_value=status)


@app.get('/api/v1/address-corrections')
def address_corrections(status: str | None = Query(default=None), authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    return {'items': list_address_corrections(status=status)}


@app.post('/api/v1/address-corrections/{correction_id}/under-review')
def mark_address_correction_under_review(correction_id: str, payload: CorrectionReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_address_correction_status(correction_id, 'under-review', payload.reviewer_note, actor=user)
    except (AddressCorrectionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, AddressCorrectionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/address-corrections/{correction_id}/resolve')
def resolve_address_correction(correction_id: str, payload: CorrectionReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_address_correction_status(correction_id, 'resolved', payload.reviewer_note, actor=user)
    except (AddressCorrectionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, AddressCorrectionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/api/v1/address-corrections/{correction_id}/reject')
def reject_address_correction(correction_id: str, payload: CorrectionReviewActionRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_address_correction_status(correction_id, 'rejected', payload.reviewer_note, actor=user)
    except (AddressCorrectionNotFoundError, InvalidSubmissionActionError) as exc:
        code = status.HTTP_404_NOT_FOUND if isinstance(exc, AddressCorrectionNotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.get('/api/v1/imports/jobs')
def import_jobs(authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return {'items': list_import_jobs()}


@app.get('/api/v1/imports/jobs/{job_id}/rows')
def import_rows(job_id: str, authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    try:
        return {'items': get_import_rows(job_id)}
    except ImportJobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.post('/api/v1/imports/jobs', status_code=status.HTTP_201_CREATED)
def create_import_job_endpoint(payload: ImportJobCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return create_import_job(payload.model_dump(), actor=user)
    except UnknownTerritoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DuplicateImportJobError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post('/api/v1/imports/jobs/{job_id}/commit')
def commit_import_job_endpoint(job_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return commit_import_job(job_id, actor=user)
    except ImportJobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidSubmissionActionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get('/api/v1/publication/packs')
def publication_packs(authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return {'items': list_publication_packs()}


@app.post('/api/v1/publication/packs', status_code=status.HTTP_201_CREATED)
def create_publication_pack_endpoint(payload: PublicationPackCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    if payload.status == 'published' and user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='admin required to create a published pack')
    try:
        return create_publication_pack(payload.model_dump(), actor=user)
    except AddressNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DuplicatePublicationPackError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post('/api/v1/publication/packs/{pack_id}/publish')
def publish_publication_pack_endpoint(pack_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    if not PUBLICATION_RELEASE_ENABLED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='publication release gate is disabled')
    try:
        return publish_publication_pack(pack_id, actor=user)
    except PublicationPackNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def _ministry_walkthrough_steps() -> list[dict[str, str]]:
    return [
        {
            'step': '1',
            'title': 'Citizen location registration',
            'route': '/geotag',
            'operator_message': 'Capture GPS, accuracy, landmark, province, and public-safe receipt tracking.',
        },
        {
            'step': '2',
            'title': 'Address-code tracking',
            'route': '/track',
            'operator_message': 'Show that citizens can track by receipt ID or official address code without exposing private identity data.',
        },
        {
            'step': '3',
            'title': 'Location review and field routing',
            'route': '/signage',
            'operator_message': 'Review duplicate risk, routing assignment, field-check needs, and registry-ready hold state.',
        },
        {
            'step': '4',
            'title': 'Evidence and SLA command desk',
            'route': '/verify',
            'operator_message': 'Show evidence review, field submissions, and overdue SLA drill-down.',
        },
        {
            'step': '5',
            'title': 'Publication simulation and continuity proof',
            'route': '/reports',
            'operator_message': 'Show command-center totals, restore proof, cleanup readiness, and locked publication simulation boundaries.',
        },
    ]


def latest_restore_drill_report() -> dict[str, Any]:
    report_path = Path(os.getenv('RESTORE_DRILL_REPORT_PATH', '/app/artifacts/operator-digests/restore_drill_latest.json'))
    if not report_path.exists():
        return {'status': 'not-run', 'operator_note': 'No restore drill proof has been recorded yet.'}
    try:
        payload = json.loads(report_path.read_text())
    except (OSError, json.JSONDecodeError):
        return {'status': 'unreadable', 'operator_note': 'Restore drill proof exists but could not be parsed.'}
    if not isinstance(payload, dict):
        return {'status': 'unreadable', 'operator_note': 'Restore drill proof has an invalid shape.'}
    sanitized = dict(payload)
    backup_path = sanitized.pop('backup_path', None)
    if isinstance(backup_path, str) and backup_path:
        sanitized.setdefault('backup_file', Path(backup_path).name)
    return sanitized


@app.get('/api/v1/operator/command-center')
def operator_command_center(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    summary = reporting_summary()
    readiness = pilot_readiness_summary()
    geotags = _enrich_geotag_submissions(list_citizen_geotag_submissions())
    corrections = list_address_corrections()
    automation = _automation_summary(geotags, corrections)
    duplicates = geotag_duplicate_summary()
    return {
        'readiness': {
            'status': readiness.get('readiness_status'),
            'passed_gates': readiness.get('passed_gates'),
            'total_gates': readiness.get('total_gates'),
            'boundaries': readiness.get('boundaries', []),
        },
        'queues': {
            'verification_queue': summary.get('totals', {}).get('review_queue', 0),
            'citizen_geotag_queue': summary.get('totals', {}).get('geotag_queue', 0),
            'public_correction_queue': summary.get('totals', {}).get('correction_queue', 0),
            'active_operator_queue': automation.get('active_queue', 0),
            'field_required': automation.get('field_required', 0),
        },
        'risk_lanes': {
            'duplicate_groups': len(duplicates.get('groups', [])),
            'overdue_sla': automation.get('sla', {}).get('overdue', 0),
            'publication_holds': automation.get('publication_hold', {}).get('registry_ready', 0),
        },
        'publication': {
            'published_addresses': summary.get('totals', {}).get('published_addresses', 0),
            'registry_ready': automation.get('registry_ready', 0),
            'public_release_locked': automation.get('publication_hold', {}).get('public_release_locked', True),
        },
        'demo_fixtures': demo_fixture_status(),
        'restore_drill': latest_restore_drill_report(),
        'migrations': migration_status(),
        'walkthrough': _ministry_walkthrough_steps(),
    }



@app.get('/api/v1/operator/postgis/readiness')
def operator_postgis_readiness(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return postgis_readiness()


@app.get('/api/v1/operator/migrations/status')
def operator_migration_status(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return migration_status()


@app.get('/api/v1/operator/production-readiness')
def operator_production_readiness(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return production_readiness_status()


@app.get('/api/v1/operator/demo-fixtures/status')
def operator_demo_fixture_status(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return demo_fixture_status()


@app.post('/api/v1/operator/demo-fixtures/cleanup')
def operator_demo_fixture_cleanup(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    return cleanup_demo_fixtures(actor=user)


@app.get('/api/v1/operator/restore-drill/latest')
def operator_restore_drill_latest(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return latest_restore_drill_report()


@app.get('/api/v1/reporting/summary')
def reporting_summary_endpoint(
    authorization: str | None = Header(default=None),
    province: str | None = Query(default=None),
    territory: str | None = Query(default=None),
    status_filter: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin', 'agency_viewer')
    if not any([province, territory, status_filter, date_from, date_to]):
        return reporting_summary()
    return reporting_summary(
        province=province,
        territory=territory,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
    )


@app.get('/api/v1/pilot-readiness/summary')
def pilot_readiness_summary_endpoint(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin', 'agency_viewer')
    return pilot_readiness_summary()
