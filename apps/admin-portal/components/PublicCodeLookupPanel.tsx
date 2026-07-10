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
    <section className="service-start-page public-code-service-page" aria-labelledby="public-code-profile-heading">
      <div className="desktop-home-copy public-code-profile-copy">
        <p className="section-label">Public address profile</p>
        <h2 id="public-code-profile-heading">Address profile</h2>
        <p className="public-task-copy public-code-value"><strong>Address code</strong><span>{code}</span></p>
        {isLoading ? <p className="public-task-copy">Checking address code…</p> : null}
        {error ? <p className="form-notice error">{error}</p> : null}
        {payload ? (
          <>
            <p className="public-task-copy public-code-status-copy">{statusCopy(payload)}</p>
            {record ? <p className="public-code-address-line">{record.address_label}</p> : null}
            {record ? <p className="public-task-copy">{record.territory_name ?? 'Area pending'} · accuracy {record.accuracy_meters ?? 'not recorded'}m · {approvalLabel(payload.publication_status)}</p> : null}
            {!record ? <p className="public-task-copy">Full address details appear only after official approval.</p> : null}
            <div className="service-start-actions public-code-service-actions" aria-label="Public address profile actions">
              {mapsLink ? <a className="primary-action" href={mapsLink} target="_blank" rel="noreferrer">Open map</a> : null}
              <div className="service-start-secondary-actions">
                <a className="secondary-action" href={proofUrl}>Proof / QR</a>
                <button className="secondary-action" type="button" onClick={() => copyText(code, 'Address code')}>Copy code</button>
              </div>
            </div>
            <p className="public-task-copy public-code-secondary-links">
              <button className="inline-action-link" type="button" onClick={shareProfile} disabled={!profileUrl}>Share link</button>
              <span aria-hidden="true"> · </span>
              <button className="inline-action-link" type="button" onClick={() => window.print()}>Print profile</button>
              <span aria-hidden="true"> · </span>
              <a className="inline-action-link" href={correctionUrl}>Report correction</a>
            </p>
          </>
        ) : null}
        {copyNotice ? <p className="form-notice success" role="status">{copyNotice}</p> : null}
      </div>

      <section className="service-start-workflow public-code-record-section" aria-labelledby="public-code-record-heading">
        <p className="section-label">Public record data</p>
        <h2 id="public-code-record-heading">Verification details</h2>
        {payload ? (
          <dl className="facts-grid issuance-facts-grid public-code-facts-grid">
            <div><dt>Publication state</dt><dd>{approvalLabel(payload.publication_status)}</dd></div>
            <div><dt>Province</dt><dd>{payload.province_code ?? 'Unknown'}</dd></div>
            <div><dt>Address-code version</dt><dd>{payload.schema ?? 'Unknown'}</dd></div>
            <div><dt>Location cell</dt><dd>{payload.cell_size_meters ? `${payload.cell_size_meters}m` : 'Unknown'}</dd></div>
            <div><dt>Check characters</dt><dd>{payload.checksum ?? 'Unknown'}</dd></div>
            <div><dt>Latitude</dt><dd>{displayCoordinate(latitude)}</dd></div>
            <div><dt>Longitude</dt><dd>{displayCoordinate(longitude)}</dd></div>
          </dl>
        ) : null}
      </section>

      <section className="service-start-workflow public-code-record-section" aria-labelledby="public-code-boundary-heading">
        <p className="section-label">Public confirmation</p>
        <h2 id="public-code-boundary-heading">What this page confirms</h2>
        <p className="public-task-copy">
          This page confirms public address-code status only. It is not proof of ownership, private title, or a property-rights certificate.
        </p>
      </section>
    </section>
  );
}
