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

function displayCoordinate(value?: number | null) {
  return value == null ? 'Unavailable' : value.toFixed(6);
}

export function PublicCodeLookupPanel({ apiBaseUrl, code }: PublicCodeLookupPanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const [payload, setPayload] = useState<PublicCodeLookup | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [profileUrl, setProfileUrl] = useState('');
  const [copyNotice, setCopyNotice] = useState<string | null>(null);
  const mapsLink = useMemo(() => (payload ? mapUrl(payload) : null), [payload]);
  const correctionUrl = `/issue?code=${encodeURIComponent(code)}`;
  const proofUrl = `/proof/${encodeURIComponent(code)}`;

  useEffect(() => {
    if (typeof window !== 'undefined') setProfileUrl(window.location.href);
  }, []);

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

  async function copyText(value: string, label: string) {
    try {
      await navigator.clipboard?.writeText(value);
      setCopyNotice(`${label} copied.`);
    } catch {
      setCopyNotice(`Unable to copy ${label.toLowerCase()} automatically.`);
    }
  }

  async function shareProfile() {
    if (!profileUrl) return;
    if (navigator.share) {
      try {
        await navigator.share({ title: 'Public address code profile', text: code, url: profileUrl });
        setCopyNotice('Verification link shared.');
        return;
      } catch {
        // User may cancel native share. Fall back to copy.
      }
    }
    await copyText(profileUrl, 'Verification link');
  }

  const record = payload?.record ?? null;
  const latitude = record?.latitude ?? payload?.latitude ?? null;
  const longitude = record?.longitude ?? payload?.longitude ?? null;

  return (
    <section className="public-code-status-flow public-address-profile-flow">
      <article className="public-task-panel code-status-panel public-profile-panel">
        <div className="panel-head">
          <p className="section-label">Public address profile</p>
          <h3>{code}</h3>
        </div>
        {isLoading ? <p className="panel-state">Checking address code…</p> : null}
        {error ? <p className="form-notice error">{error}</p> : null}
        {payload ? (
          <div className="approval-status-card public-profile-summary">
            <span className={`status-chip ${statusClass(payload)}`}>{approvalLabel(payload.publication_status)}</span>
            <h4>{statusCopy(payload)}</h4>
            {record ? (
              <div className="approved-record-copy">
                <p>{record.address_label}</p>
                <p>{record.territory_name ?? 'Area pending'} · accuracy {record.accuracy_meters ?? 'not recorded'}m</p>
              </div>
            ) : (
              <p>This code can be checked, but full address details appear only after official approval.</p>
            )}
          </div>
        ) : null}

        <div className="public-profile-actions" aria-label="Public address profile actions">
          <button className="secondary-action" type="button" onClick={() => copyText(code, 'Address code')}>Copy code</button>
          <button className="secondary-action" type="button" onClick={shareProfile} disabled={!profileUrl}>Share link</button>
          <button className="secondary-action" type="button" onClick={() => window.print()}>Print profile</button>
          <a className="secondary-action" href={proofUrl}>Proof / QR</a>
          <a className="secondary-action" href={correctionUrl}>Extract or correction</a>
          {mapsLink ? <a className="primary-action" href={mapsLink} target="_blank" rel="noreferrer">Open map</a> : null}
        </div>
        {copyNotice ? <p className="form-notice success" role="status">{copyNotice}</p> : null}
        <p className="institutional-note public-profile-disclaimer">
          This page confirms public address-code status only. It is not proof of ownership, private title, or a property-rights certificate.
        </p>
      </article>

      <article className="public-task-panel code-detail-panel public-profile-detail-panel">
        <div className="panel-head quiet-head">
          <p className="section-label">Verification details</p>
          <h3>Public record data</h3>
        </div>
        {payload ? (
          <dl className="facts-grid issuance-facts-grid calm-facts-grid public-profile-facts">
            <div><dt>Valid code</dt><dd>{payload.is_valid ? 'Yes' : 'No'}</dd></div>
            <div><dt>Province</dt><dd>{payload.province_code ?? 'Unknown'}</dd></div>
            <div><dt>Address-code version</dt><dd>{payload.schema ?? 'Unknown'}</dd></div>
            <div><dt>Location cell</dt><dd>{payload.cell_size_meters ? `${payload.cell_size_meters}m` : 'Unknown'}</dd></div>
            <div><dt>Check characters</dt><dd>{payload.checksum ?? 'Unknown'}</dd></div>
            <div><dt>Latitude</dt><dd>{displayCoordinate(latitude)}</dd></div>
            <div><dt>Longitude</dt><dd>{displayCoordinate(longitude)}</dd></div>
            <div><dt>Publication state</dt><dd>{approvalLabel(payload.publication_status)}</dd></div>
          </dl>
        ) : null}
      </article>

      <article className="public-task-panel public-code-guide-panel">
        <div className="panel-head quiet-head">
          <p className="section-label">Code guide</p>
          <h3>How to read the address code</h3>
        </div>
        <ul className="program-list public-code-guide-list">
          <li><span><strong>EG</strong> identifies the national addressing system for Equatorial Guinea.</span></li>
          <li><span><strong>Province</strong> identifies the province prefix used during registration and review.</span></li>
          <li><span><strong>N1</strong> identifies the current national address-code grammar.</span></li>
          <li><span><strong>Location cell</strong> gives the approximate public location cell, not private identity data.</span></li>
          <li><span><strong>Check characters</strong> help detect typing errors when a code is copied, printed, or read by phone.</span></li>
        </ul>
      </article>
    </section>
  );
}
