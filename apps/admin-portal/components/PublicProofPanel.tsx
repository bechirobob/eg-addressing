'use client';

import { useEffect, useMemo, useState } from 'react';

import { createQrSvg } from '../lib/qr';
import { resolveBrowserApiBaseUrl } from './sessionClient';

type PublicCodeRecord = {
  grid_code: string;
  address_label: string;
  territory_name?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  accuracy_meters?: number | null;
  status: string;
};

type PublicCodeLookup = {
  code: string;
  is_valid: boolean;
  publication_status: 'invalid' | 'not_found' | 'not_public' | 'internal_registry' | 'published';
  province_code?: string;
  schema?: string;
  cell_size_meters?: number;
  record?: PublicCodeRecord | null;
};

type PublicProofPanelProps = {
  apiBaseUrl: string;
  code: string;
};

function displayCoordinate(value?: number | null) {
  return value == null ? 'Unavailable' : value.toFixed(6);
}

function proofStatus(payload: PublicCodeLookup | null) {
  if (!payload) return 'Checking public record';
  if (!payload.is_valid) return 'Invalid address code';
  if (payload.publication_status === 'published') return 'Published public address record';
  return 'Not published for public proof';
}

export function PublicProofPanel({ apiBaseUrl, code }: PublicProofPanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const [payload, setPayload] = useState<PublicCodeLookup | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [profileUrl, setProfileUrl] = useState('');
  const [copyNotice, setCopyNotice] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setProfileUrl(`${window.location.origin}/code/${encodeURIComponent(code)}`);
    }
  }, [code]);

  useEffect(() => {
    let active = true;
    async function load() {
      setError(null);
      try {
        const response = await fetch(`${browserApiBaseUrl}/api/v1/public/address-code/${encodeURIComponent(code)}/record`);
        const nextPayload = (await response.json()) as PublicCodeLookup;
        if (!active) return;
        setPayload(nextPayload);
        if (!response.ok) setError('Unable to load public proof data right now.');
      } catch {
        if (active) setError('Unable to load public proof data right now.');
      }
    }
    void load();
    return () => { active = false; };
  }, [browserApiBaseUrl, code]);

  const qrSvg = useMemo(() => {
    if (!profileUrl) return '';
    return createQrSvg(profileUrl, { title: `QR code for ${code}` });
  }, [code, profileUrl]);

  async function copyProofLink() {
    if (!profileUrl) return;
    try {
      await navigator.clipboard?.writeText(profileUrl);
      setCopyNotice('Public profile link copied.');
    } catch {
      setCopyNotice('Unable to copy link automatically.');
    }
  }

  const record = payload?.record ?? null;
  const latitude = record?.latitude ?? null;
  const longitude = record?.longitude ?? null;
  const canShowProof = payload?.is_valid && payload.publication_status === 'published' && record;

  return (
    <section className="public-proof-flow">
      <article className="public-proof-sheet" aria-labelledby="proof-title">
        <div className="public-proof-header">
          <div>
            <p className="section-label">Public address proof</p>
            <h3 id="proof-title">{code}</h3>
          </div>
          <span className={`status-chip ${canShowProof ? 'ok' : 'warn'}`}>{proofStatus(payload)}</span>
        </div>

        {error ? <p className="form-notice error">{error}</p> : null}
        {!payload ? <p className="panel-state">Checking public record…</p> : null}

        {canShowProof ? (
          <div className="public-proof-body">
            <div className="public-proof-record">
              <p className="section-label">Published record</p>
              <h4>{record.address_label}</h4>
              <dl className="facts-grid issuance-facts-grid calm-facts-grid public-proof-facts">
                <div><dt>Province</dt><dd>{payload.province_code ?? 'Unknown'}</dd></div>
                <div><dt>Territory</dt><dd>{record.territory_name ?? 'Area pending'}</dd></div>
                <div><dt>Latitude</dt><dd>{displayCoordinate(latitude)}</dd></div>
                <div><dt>Longitude</dt><dd>{displayCoordinate(longitude)}</dd></div>
                <div><dt>Accuracy</dt><dd>{record.accuracy_meters == null ? 'Unavailable' : `${record.accuracy_meters}m`}</dd></div>
                <div><dt>Record status</dt><dd>{record.status}</dd></div>
              </dl>
            </div>
            <aside className="public-proof-qr" aria-label="QR verification link">
              {qrSvg ? <div className="qr-code-frame" dangerouslySetInnerHTML={{ __html: qrSvg }} /> : null}
              <p>Scan to open the canonical public address profile.</p>
              <a href={profileUrl}>{profileUrl}</a>
            </aside>
          </div>
        ) : payload ? (
          <p className="institutional-note">This code is not currently eligible for public proof. Only published public records can generate proof pages.</p>
        ) : null}

        <div className="public-profile-actions public-proof-actions no-print" aria-label="Public proof actions">
          <a className="secondary-action" href={`/code/${encodeURIComponent(code)}`}>Open public profile</a>
          <button className="secondary-action" type="button" onClick={copyProofLink} disabled={!profileUrl}>Copy QR link</button>
          <button className="primary-action" type="button" onClick={() => window.print()} disabled={!canShowProof}>Print / save PDF</button>
        </div>
        {copyNotice ? <p className="form-notice success no-print" role="status">{copyNotice}</p> : null}

        <p className="institutional-note public-profile-disclaimer">
          This proof confirms public address-code status only. It is not proof of ownership, private title, property rights, signage approval, or a government-issued ownership certificate.
        </p>
      </article>
    </section>
  );
}
