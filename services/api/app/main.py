from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.data import MODULES, PROVINCES
from app.db import (
    AddressNotFoundError,
    AuthenticationError,
    BuildingNotFoundError,
    DuplicateAddressError,
    DuplicateBuildingError,
    DuplicateRoadError,
    DuplicateTerritoryError,
    ImportJobNotFoundError,
    InvalidSubmissionActionError,
    PublicationPackNotFoundError,
    RoadNotFoundError,
    SubmissionNotFoundError,
    TerritoryNotFoundError,
    UnknownBuildingError,
    UnknownProvinceError,
    UnknownRoadError,
    UnknownTerritoryError,
    approve_submission,
    archive_address,
    archive_building,
    archive_road,
    archive_territory,
    authenticate_user_session,
    commit_import_job,
    create_address,
    create_building,
    create_field_submission,
    create_import_job,
    create_publication_pack,
    create_road,
    create_territory,
    fetch_addresses,
    fetch_buildings,
    fetch_roads,
    fetch_territories,
    get_address,
    get_building,
    get_import_rows,
    get_road,
    get_submission,
    get_territory,
    init_db,
    list_audit_logs,
    list_field_assignments,
    list_field_submissions,
    list_import_jobs,
    list_publication_packs,
    publish_publication_pack,
    reporting_summary,
    resolve_user_from_token,
    update_address,
    update_building,
    update_road,
    update_submission_review_status,
    update_territory,
    verify_address,
)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=3, max_length=80)


class TerritoryCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    province_code: str = Field(min_length=2, max_length=8)
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


class FieldSubmissionCreate(BaseModel):
    assignment_id: str | None = None
    territory_id: str = Field(min_length=3, max_length=120)
    submission_type: str = Field(pattern='^(road|building|address)$')
    candidate_name: str = Field(min_length=3, max_length=180)
    candidate_status: str = Field(min_length=3, max_length=64)
    notes: str = Field(default='', max_length=400)
    submitted_by: str = Field(min_length=3, max_length=120)


class ReviewActionRequest(BaseModel):
    reviewer_note: str = Field(default='', max_length=300)


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
    allow_credentials=False,
    allow_methods=['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
    allow_headers=['*'],
)


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='authentication required')
    return authorization.split(' ', 1)[1].strip()


def _current_user(authorization: str | None) -> dict[str, str]:
    token = _bearer_token(authorization)
    try:
        return resolve_user_from_token(token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


def _require_role(user: dict[str, str], *roles: str) -> None:
    if user['role'] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='insufficient role')


@app.get('/')
def root() -> dict[str, str]:
    return {'message': 'eg-addressing-api online', 'docs': '/docs'}


@app.get('/api/v1/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': 'eg-addressing-api', 'version': '0.1.0'}


@app.get('/api/v1/meta')
def meta() -> dict[str, Any]:
    return {
        'platform': {'name': 'Equatorial Guinea National Digital Addressing Platform', 'mode': 'operational-readiness'},
        'stack': {'backend': 'FastAPI', 'frontend': 'Next.js', 'database': 'PostgreSQL + PostGIS', 'cache': 'Redis', 'storage': 'MinIO'},
        'modules': MODULES,
        'roles': ['viewer', 'editor', 'admin'],
    }


@app.post('/api/v1/auth/login')
def login(payload: LoginRequest) -> dict[str, Any]:
    try:
        return authenticate_user_session(payload.username, payload.password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@app.get('/api/v1/auth/me')
def auth_me(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    return {'user': _current_user(authorization)}


@app.get('/api/v1/territories/provinces')
def list_provinces() -> dict[str, list[dict[str, str]]]:
    return {'items': PROVINCES}


@app.get('/api/v1/territories')
def list_territories(
    q: str | None = Query(default=None),
    province_code: str | None = Query(default=None),
    readiness: str | None = Query(default=None),
    include_archived: bool = Query(default=False),
) -> dict[str, list[dict[str, Any]]]:
    return {'items': fetch_territories(q=q, province_code=province_code, readiness=readiness, include_archived=include_archived)}


@app.get('/api/v1/territories/{territory_id}')
def territory_detail(territory_id: str) -> dict[str, Any]:
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
    except UnknownProvinceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.patch('/api/v1/territories/{territory_id}')
def update_territory_endpoint(territory_id: str, payload: TerritoryUpdate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return update_territory(territory_id, payload.model_dump(), actor=user)
    except DuplicateTerritoryError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except UnknownProvinceError as exc:
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
def audit_logs(entity_type: str | None = Query(default=None), entity_id: str | None = Query(default=None), limit: int = Query(default=50, ge=1, le=200), authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    return {'items': list_audit_logs(entity_type=entity_type, entity_id=entity_id, limit=limit)}


@app.get('/api/v1/roads')
def list_roads(q: str | None = Query(default=None), territory_id: str | None = Query(default=None), include_archived: bool = Query(default=False)) -> dict[str, list[dict[str, Any]]]:
    return {'items': fetch_roads(q=q, territory_id=territory_id, include_archived=include_archived)}


@app.get('/api/v1/roads/{road_id}')
def road_detail(road_id: str) -> dict[str, Any]:
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
def list_buildings(q: str | None = Query(default=None), territory_id: str | None = Query(default=None), include_archived: bool = Query(default=False)) -> dict[str, list[dict[str, Any]]]:
    return {'items': fetch_buildings(q=q, territory_id=territory_id, include_archived=include_archived)}


@app.get('/api/v1/buildings/{building_id}')
def building_detail(building_id: str) -> dict[str, Any]:
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
def list_addresses(q: str | None = Query(default=None), territory_id: str | None = Query(default=None), status_filter: str | None = Query(default=None, alias='status'), include_archived: bool = Query(default=False)) -> dict[str, list[dict[str, Any]]]:
    return {'items': fetch_addresses(q=q, territory_id=territory_id, status=status_filter, include_archived=include_archived)}


@app.get('/api/v1/addresses/{address_id}')
def address_detail(address_id: str) -> dict[str, Any]:
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
def field_assignments() -> dict[str, list[dict[str, Any]]]:
    return {'items': list_field_assignments()}


@app.get('/api/v1/field/submissions')
def field_submissions(review_status: str | None = Query(default=None), territory_id: str | None = Query(default=None), authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return {'items': list_field_submissions(review_status=review_status, territory_id=territory_id)}


@app.post('/api/v1/field/submissions', status_code=status.HTTP_201_CREATED)
def create_field_submission_endpoint(payload: FieldSubmissionCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return create_field_submission(payload.model_dump(), actor=user)
    except UnknownTerritoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


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


@app.get('/api/v1/verification/lookup')
def verification_lookup(query: str = Query(min_length=3)) -> dict[str, Any]:
    result = verify_address(query)
    if not result:
        return {
            'query': query,
            'match_status': 'not-found',
            'address_label': 'No published registry record found',
            'jurisdiction': 'Pilot registry lookup',
            'verification_note': 'The query does not match a published address record yet.',
        }
    return result


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


@app.post('/api/v1/imports/jobs/{job_id}/commit')
def commit_import_job_endpoint(job_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return commit_import_job(job_id, actor=user)
    except ImportJobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get('/api/v1/publication/packs')
def publication_packs(authorization: str | None = Header(default=None)) -> dict[str, list[dict[str, Any]]]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return {'items': list_publication_packs()}


@app.post('/api/v1/publication/packs', status_code=status.HTTP_201_CREATED)
def create_publication_pack_endpoint(payload: PublicationPackCreate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'editor', 'admin')
    try:
        return create_publication_pack(payload.model_dump(), actor=user)
    except AddressNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.post('/api/v1/publication/packs/{pack_id}/publish')
def publish_publication_pack_endpoint(pack_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'admin')
    try:
        return publish_publication_pack(pack_id, actor=user)
    except PublicationPackNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@app.get('/api/v1/reporting/summary')
def reporting_summary_endpoint(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _current_user(authorization)
    _require_role(user, 'viewer', 'editor', 'admin')
    return reporting_summary()
