import hashlib
import hmac
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any


class EvidenceStorageError(RuntimeError):
    pass


class EvidenceObjectNotFound(EvidenceStorageError):
    pass


def _endpoint() -> str:
    return os.getenv('S3_ENDPOINT') or os.getenv('MINIO_ENDPOINT') or 'http://minio:9000'


def _bucket() -> str:
    return os.getenv('S3_EVIDENCE_BUCKET') or os.getenv('S3_BUCKET') or 'eg-field-evidence'


def _access_key() -> str:
    return os.getenv('S3_ACCESS_KEY') or 'minioadmin'


def _secret_key() -> str:
    return os.getenv('S3_SECRET_KEY') or 'minioadmin'


def _region() -> str:
    return os.getenv('S3_REGION') or 'us-east-1'


def _hash_payload(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sign(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode('utf-8'), hashlib.sha256).digest()


def _signature_key(date_stamp: str) -> bytes:
    key_date = _sign(('AWS4' + _secret_key()).encode('utf-8'), date_stamp)
    key_region = _sign(key_date, _region())
    key_service = _sign(key_region, 's3')
    return _sign(key_service, 'aws4_request')


def _canonical_uri(bucket: str, object_key: str | None = None) -> str:
    encoded_bucket = urllib.parse.quote(bucket, safe='')
    if not object_key:
        return f'/{encoded_bucket}'
    return f'/{encoded_bucket}/' + '/'.join(urllib.parse.quote(part, safe='') for part in object_key.split('/'))


def _request_url(bucket: str, object_key: str | None = None) -> str:
    return _endpoint().rstrip('/') + _canonical_uri(bucket, object_key)


def _signed_headers(method: str, bucket: str, object_key: str | None, payload: bytes, extra_headers: dict[str, str] | None = None) -> dict[str, str]:
    now = datetime.now(timezone.utc)
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = now.strftime('%Y%m%d')
    endpoint = urllib.parse.urlparse(_endpoint())
    host = endpoint.netloc
    payload_hash = _hash_payload(payload)
    headers = {
        'host': host,
        'x-amz-content-sha256': payload_hash,
        'x-amz-date': amz_date,
    }
    for key, value in (extra_headers or {}).items():
        if value:
            headers[key.lower()] = value.strip()
    signed_header_names = sorted(headers)
    canonical_headers = ''.join(f'{name}:{headers[name]}\n' for name in signed_header_names)
    signed_headers_value = ';'.join(signed_header_names)
    canonical_request = '\n'.join([
        method,
        _canonical_uri(bucket, object_key),
        '',
        canonical_headers,
        signed_headers_value,
        payload_hash,
    ])
    credential_scope = f'{date_stamp}/{_region()}/s3/aws4_request'
    string_to_sign = '\n'.join([
        'AWS4-HMAC-SHA256',
        amz_date,
        credential_scope,
        hashlib.sha256(canonical_request.encode('utf-8')).hexdigest(),
    ])
    signature = hmac.new(_signature_key(date_stamp), string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    auth = f'AWS4-HMAC-SHA256 Credential={_access_key()}/{credential_scope}, SignedHeaders={signed_headers_value}, Signature={signature}'
    request_headers = {key: value for key, value in headers.items() if key != 'host'}
    request_headers['Authorization'] = auth
    return request_headers


def ensure_evidence_bucket() -> None:
    payload = b''
    bucket = _bucket()
    headers = _signed_headers('PUT', bucket, None, payload)
    request = urllib.request.Request(_request_url(bucket), data=payload, method='PUT', headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=8):
            return
    except urllib.error.HTTPError as exc:
        if exc.code in {200, 409}:
            return
        raise EvidenceStorageError(f'evidence bucket unavailable: {exc.code}') from exc
    except urllib.error.URLError as exc:
        raise EvidenceStorageError('evidence storage unavailable') from exc


def store_evidence_object(object_key: str, content: bytes, content_type: str) -> dict[str, Any]:
    ensure_evidence_bucket()
    headers = _signed_headers('PUT', _bucket(), object_key, content, {'content-type': content_type})
    request = urllib.request.Request(_request_url(_bucket(), object_key), data=content, method='PUT', headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            etag = response.headers.get('ETag', '').strip('"')
    except urllib.error.HTTPError as exc:
        raise EvidenceStorageError(f'evidence upload failed: {exc.code}') from exc
    except urllib.error.URLError as exc:
        raise EvidenceStorageError('evidence storage unavailable') from exc
    return {
        'bucket': _bucket(),
        'object_key': object_key,
        'size_bytes': len(content),
        'sha256': _hash_payload(content),
        'content_type': content_type,
        'etag': etag,
    }


def read_evidence_object(object_key: str) -> bytes:
    payload = b''
    headers = _signed_headers('GET', _bucket(), object_key, payload)
    request = urllib.request.Request(_request_url(_bucket(), object_key), method='GET', headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise EvidenceObjectNotFound('evidence file not found') from exc
        raise EvidenceStorageError(f'evidence download failed: {exc.code}') from exc
    except urllib.error.URLError as exc:
        raise EvidenceStorageError('evidence storage unavailable') from exc
