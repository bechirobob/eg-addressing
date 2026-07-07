'use client';

import { useEffect, useMemo, useState } from 'react';

import { resolveBrowserApiBaseUrl } from './sessionClient';

type PublicCodeRecord = {
  grid_code: string;
  address_label: string;
  territory_name?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  accuracy_meters?: number | null;
  status: string;
  signage_batch?: string | null;
};

type PublicCodeLookup = {
  code: string;
  is_valid: boolean;
  publication_status: 'invalid' | 'not_found' | 'not_public' | 'internal_registry' | 'published';
  province_code?: string;
  schema?: string;
  cell_size_meters?: number;
  checksum?: string;
  latitude?: number;
  longitude?: number;
  bbox?: { south: number; west: number; north: number; east: number };
  record?: PublicCodeRecord | null;
};

type PublicCodeLookupPanelProps = {
  apiBaseUrl: string;
  code: string;
};

function statusCopy(payload: PublicCodeLookup | null) {
  if (!payload) return 'Checking address code…';
  if (!payload.is_valid) return 'This address code is not valid';
  if (payload.publication_status === 'published') return 'Approved public address record';
  if (payload.publication_status === 'internal_registry') return 'Official case file ready — not public yet';
  if (payload.publication_status === 'not_public') return 'Valid code, waiting for approval';
  return 'Valid code, no approved record yet';
}

function statusClass(payload: PublicCodeLookup | null) {
  if (!payload || !payload.is_valid) return 'danger';
  if (payload.publication_status === 'published') return 'ok';
  return 'warn';
}

function approvalLabel(status: PublicCodeLookup['publication_status']) {
  if (status === 'published') return 'Published';
  if (status === 'internal_registry') return 'Internal case file ready';
  if (status === 'not_public') return 'Awaiting approval';
  if (status === 'not_found') return 'No approved record';
  return 'Invalid code';
}

function mapUrl(payload: PublicCodeLookup) {
  const lat = payload.record?.latitude ?? payload.latitude;
  const lon = payload.record?.longitude ?? payload.longitude;
  if (lat == null || lon == null) return null;
  return `https://www.google.com/maps/search/?api=1&query=${lat},${lon}`;
}

export function PublicCodeLookupPanel({ apiBaseUrl, code }: PublicCodeLookupPanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const [payload, setPayload] = useState<PublicCodeLookup | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const mapsLink = useMemo(() => (payload ? mapUrl(payload) : null), [payload]);

  useEffect(() => {
    let active = true;
    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`${browserApiBaseUrl}/api/v1/public/address-code/${encodeURIComponent(code)}/record`);
        const nextPayload = (await response.json()) as PublicCodeLookup;
        if (!active) return;
        setPayload(nextPayload);
        if (!response.ok) setError('Unable to load this address code right now.');
      } catch {
        if (active) setError('Unable to load this address code right now.');
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void load();
    return () => { active = false; };
  }, [browserApiBaseUrl, code]);

  return (
    <section className="public-code-status-flow">
      <article className="public-task-panel code-status-panel">
        <div className="panel-head">
          <p className="section-label">Address code status</p>
          <h3>{code}</h3>
        </div>
        {isLoading ? <p className="panel-state">Checking address code…</p> : null}
        {error ? <p className="form-notice error">{error}</p> : null}
        {payload ? (
          <div className="approval-status-card">
            <span className={`status-chip ${statusClass(payload)}`}>{approvalLabel(payload.publication_status)}</span>
            <h4>{statusCopy(payload)}</h4>
            {payload.record ? (
              <div className="approved-record-copy">
                <p>{payload.record.address_label}</p>
                <p>{payload.record.territory_name ?? 'Area pending'} · accuracy {payload.record.accuracy_meters ?? 'not recorded'}m</p>
              </div>
            ) : (
              <p>This code can be checked, but full address details appear only after official approval.</p>
            )}
          </div>
        ) : null}
        <div className="territory-form-actions">
          <button className="secondary-action" type="button" onClick={() => navigator.clipboard?.writeText(code)}>Copy code</button>
          {mapsLink ? <a className="primary-action" href={mapsLink} target="_blank" rel="noreferrer">Open map</a> : null}
        </div>
      </article>

      <article className="public-task-panel code-detail-panel">
        <div className="panel-head quiet-head">
          <p className="section-label">Address code details</p>
          <h3>Verification information</h3>
        </div>
        {payload ? (
          <details className="disclosure-panel">
            <summary>Show technical code details</summary>
            <dl className="facts-grid issuance-facts-grid calm-facts-grid">
              <div><dt>Valid code</dt><dd>{payload.is_valid ? 'Yes' : 'No'}</dd></div>
              <div><dt>Province</dt><dd>{payload.province_code ?? 'Unknown'}</dd></div>
              <div><dt>Address-code version</dt><dd>{payload.schema ?? 'Unknown'}</dd></div>
              <div><dt>Location cell</dt><dd>{payload.cell_size_meters ? `${payload.cell_size_meters}m` : 'Unknown'}</dd></div>
              <div><dt>Check characters</dt><dd>{payload.checksum ?? 'Unknown'}</dd></div>
              <div><dt>Approximate center</dt><dd>{payload.latitude && payload.longitude ? `${payload.latitude}, ${payload.longitude}` : 'Unavailable'}</dd></div>
            </dl>
          </details>
        ) : null}
      </article>
    </section>
  );
}
