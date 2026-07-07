from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Any

CROCKFORD32 = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
COUNTRY_PREFIX = 'EG'
ADDRESS_CODE_SCHEMA = 'N1'
CELL_SIZE_METERS = 5.0
CELL_SIZE_DEGREES = CELL_SIZE_METERS / 111_320.0
LAT_CELLS = int(math.ceil(180.0 / CELL_SIZE_DEGREES))
LON_CELLS = int(math.ceil(360.0 / CELL_SIZE_DEGREES))
CODE_RE = re.compile(r'^EG-([A-Z]{2})-N1-([0-9A-HJKMNP-TV-Z]{5})([0-9A-HJKMNP-TV-Z]{5})-([0-9A-HJKMNP-TV-Z]{2})$')


@dataclass(frozen=True)
class AddressCodeParts:
    code: str
    country: str
    province_code: str
    schema: str
    latitude_cell: int
    longitude_cell: int
    latitude: float
    longitude: float
    cell_size_meters: float
    checksum: str
    is_valid: bool

    def as_dict(self) -> dict[str, Any]:
        half = CELL_SIZE_DEGREES / 2
        return {
            'code': self.code,
            'country': self.country,
            'province_code': self.province_code,
            'schema': self.schema,
            'latitude_cell': self.latitude_cell,
            'longitude_cell': self.longitude_cell,
            'latitude': round(self.latitude, 7),
            'longitude': round(self.longitude, 7),
            'cell_size_meters': self.cell_size_meters,
            'checksum': self.checksum,
            'is_valid': self.is_valid,
            'bbox': {
                'south': round(self.latitude - half, 7),
                'west': round(self.longitude - half, 7),
                'north': round(self.latitude + half, 7),
                'east': round(self.longitude + half, 7),
            },
            'human_readable': f'{self.country} {self.province_code} {self.schema} {self.code}',
        }


class AddressCodeError(ValueError):
    pass


def _base32_encode(value: int, width: int) -> str:
    if value < 0:
        raise AddressCodeError('address code cell cannot be negative')
    chars: list[str] = []
    current = value
    if current == 0:
        chars.append('0')
    while current:
        current, remainder = divmod(current, 32)
        chars.append(CROCKFORD32[remainder])
    encoded = ''.join(reversed(chars)).rjust(width, '0')
    if len(encoded) > width:
        raise AddressCodeError('address code cell exceeds supported width')
    return encoded


def _base32_decode(value: str) -> int:
    total = 0
    for char in value.upper():
        if char not in CROCKFORD32:
            raise AddressCodeError('address code contains unsupported character')
        total = total * 32 + CROCKFORD32.index(char)
    return total


def _checksum(body: str) -> str:
    digest = hashlib.blake2s(body.encode('utf-8'), digest_size=2).digest()
    value = int.from_bytes(digest, 'big') % (32 * 32)
    return _base32_encode(value, 2)


def _normalize_province_code(province_code: str | None) -> str:
    normalized = (province_code or 'XX').upper().strip()
    if not re.fullmatch(r'[A-Z]{2}', normalized):
        raise AddressCodeError('province code must be two letters')
    return normalized


def _cell_for_latitude(latitude: float) -> int:
    if latitude < -90 or latitude > 90:
        raise AddressCodeError('latitude outside valid range')
    return min(max(int(math.floor((latitude + 90.0) / CELL_SIZE_DEGREES)), 0), LAT_CELLS - 1)


def _cell_for_longitude(longitude: float) -> int:
    if longitude < -180 or longitude > 180:
        raise AddressCodeError('longitude outside valid range')
    return min(max(int(math.floor((longitude + 180.0) / CELL_SIZE_DEGREES)), 0), LON_CELLS - 1)


def _cell_center(cell: int, origin: float) -> float:
    return origin + (cell + 0.5) * CELL_SIZE_DEGREES


def generate_national_address_code(latitude: float, longitude: float, province_code: str | None) -> str:
    """Generate a deterministic national address code from WGS84 coordinates.

    Format: EG-{province}-N1-{lat-cell}{lon-cell}-{checksum}

    N1 means national schema version 1. The coordinate cells are encoded with
    Crockford Base32 at roughly 5m precision. The checksum detects common typos
    and makes the code safer for signage, call-center use, and printed forms.
    """
    province = _normalize_province_code(province_code)
    lat_cell = _cell_for_latitude(float(latitude))
    lon_cell = _cell_for_longitude(float(longitude))
    lat_token = _base32_encode(lat_cell, 5)
    lon_token = _base32_encode(lon_cell, 5)
    body = f'{COUNTRY_PREFIX}-{province}-{ADDRESS_CODE_SCHEMA}-{lat_token}{lon_token}'
    return f'{body}-{_checksum(body)}'


def decode_national_address_code(code: str) -> AddressCodeParts:
    normalized = code.upper().strip().replace(' ', '-')
    match = CODE_RE.fullmatch(normalized)
    if not match:
        raise AddressCodeError('address code does not match EG national code format')
    province, lat_token, lon_token, supplied_checksum = match.groups()
    body = f'{COUNTRY_PREFIX}-{province}-{ADDRESS_CODE_SCHEMA}-{lat_token}{lon_token}'
    expected_checksum = _checksum(body)
    lat_cell = _base32_decode(lat_token)
    lon_cell = _base32_decode(lon_token)
    latitude = _cell_center(lat_cell, -90.0)
    longitude = _cell_center(lon_cell, -180.0)
    return AddressCodeParts(
        code=normalized,
        country=COUNTRY_PREFIX,
        province_code=province,
        schema=ADDRESS_CODE_SCHEMA,
        latitude_cell=lat_cell,
        longitude_cell=lon_cell,
        latitude=latitude,
        longitude=longitude,
        cell_size_meters=CELL_SIZE_METERS,
        checksum=supplied_checksum,
        is_valid=supplied_checksum == expected_checksum,
    )


def validate_national_address_code(code: str) -> dict[str, Any]:
    try:
        decoded = decode_national_address_code(code)
        return decoded.as_dict()
    except AddressCodeError as exc:
        return {
            'code': code,
            'is_valid': False,
            'error': str(exc),
            'schema': ADDRESS_CODE_SCHEMA,
            'cell_size_meters': CELL_SIZE_METERS,
        }
