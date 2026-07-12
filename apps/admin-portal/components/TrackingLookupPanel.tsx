'use client';

import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'next/navigation';

import { resolveBrowserApiBaseUrl } from './sessionClient';

type TrackingResponse = {
  id: string;
  grid_code: string;
  status: string;
  address_label: string;
  created_at?: string | null;
  updated_at?: string | null;
  process_stage?: string;
  next_step?: string;
  publication_state?: string;
  public_lookup_url?: string;
  tracking?: {
    tracking_code: string;
    public_status_label: string;
    public_next_step: string;
    public_lookup_url: string;
  } | null;
};

type TrackingLookupPanelProps = {
  apiBaseUrl: string;
};

function normalizeCode(value: string): string {
  return value.trim();
}

function publicationLabel(value?: string): string {
  if (value === 'public') return 'Public / approved for lookup';
  if (value === 'not-public') return 'Not public yet';
  return value || 'Status pending';
}

export function TrackingLookupPanel({ apiBaseUrl }: TrackingLookupPanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const searchParams = useSearchParams();
  const resultRef = useRef<HTMLElement | null>(null);
  const [trackingCode, setTrackingCode] = useState('');
  const [result, setResult] = useState<TrackingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const canSubmit = useMemo(() => normalizeCode(trackingCode).length >= 8, [trackingCode]);

  useEffect(() => {
    const codeFromReceipt = searchParams.get('code');
    if (!codeFromReceipt) return;
    setTrackingCode(codeFromReceipt);
    void lookupTrackingCode(codeFromReceipt);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, browserApiBaseUrl]);

  useEffect(() => {
    if (!result) return;
    window.setTimeout(() => resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
  }, [result]);

  async function lookupTrackingCode(code: string) {
    const normalized = normalizeCode(code);
    if (!normalized) {
      setError('Enter the tracking code provided after location registration.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/public/tracking/${encodeURIComponent(normalized)}`);
      const payload = (await response.json()) as TrackingResponse | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Tracking record was not found.');
        return;
      }
      setResult(payload as TrackingResponse);
    } catch {
      setError('Unable to check tracking status right now.');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalized = normalizeCode(trackingCode);
    await lookupTrackingCode(normalized);
  }

  return (
    <section className="tracking-lookup-flow">
      <article className="public-task-panel civic-panel-blue">
        <div className="panel-head">
          <p className="section-label">Citizen tracking</p>
          <h3>Check the review status of a submitted location</h3>
        </div>
        <p className="public-task-copy">
          Use the tracking code from the location submission receipt. This page only shows public-safe workflow state; it does not expose citizen contact, D.I.P., GPS evidence, or operator-only identity details.
        </p>
        <form className="territory-form tracking-form" onSubmit={handleSubmit}>
          <label className="territory-field territory-field-wide">
            <span className="territory-label">Tracking or address code</span>
            <input
              className="territory-input"
              value={trackingCode}
              onChange={(event) => setTrackingCode(event.target.value)}
              placeholder="Receipt code or EG-BN-… address code"
              autoComplete="off"
              required
            />
            <span className="field-help">Paste the full receipt code exactly as shown after registration. Official address-code lookup remains available from Check address code.</span>
          </label>
          <button className="primary-action" type="submit" disabled={isLoading || !canSubmit}>
            {isLoading ? 'Checking status…' : 'Check tracking status'}
          </button>
        </form>
        {error ? <p className="form-notice error">{error}</p> : null}
      </article>

      {result ? (
        <article className="public-task-panel civic-panel-green" ref={resultRef} aria-live="polite" tabIndex={-1}>
          <div className="panel-head">
            <p className="section-label">Tracking result</p>
            <h3>{result.process_stage || result.tracking?.public_status_label || 'Status available'}</h3>
          </div>
          <div className="summary-grid">
            <div className="summary-card"><strong>{publicationLabel(result.publication_state)}</strong><span>Public status</span></div>
            <div className="summary-card"><strong>{result.grid_code}</strong><span>Address code</span></div>
            <div className="summary-card"><strong>{result.status.replaceAll('-', ' ')}</strong><span>Operator workflow state</span></div>
          </div>
          <p className="form-notice success">Next step: {result.next_step || result.tracking?.public_next_step || 'The operator review team will continue processing this request.'}</p>
          {result.public_lookup_url && result.publication_state === 'public' ? (
            <a className="secondary-action inline-action-link" href={result.public_lookup_url}>Open public address record</a>
          ) : null}
        </article>
      ) : null}
    </section>
  );
}
