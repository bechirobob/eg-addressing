'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

import { authorizationHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

type AddressRecord = {
  address_code: string;
  address_label: string;
  status: string;
  publication_state?: string;
  province_code?: string | null;
  territory_name?: string | null;
  latitude: number;
  longitude: number;
  accuracy_meters?: number | null;
  record_bundle?: {
    identity?: { address_code?: string; source_submission_id?: string };
    routing?: { territory_name?: string | null; assignment_source?: string | null; assignment_confidence?: string | null };
    evidence?: { gps_capture?: { accuracy_meters?: number | null; capture_method?: string | null }; field_verification?: { status?: string | null } };
    outputs?: { signage_batch?: string | null; certificate_id?: string | null; public_lookup_url?: string | null };
    search?: { landmark?: string | null; road_name?: string | null; suggested_local_area?: string | null };
  };
  timeline?: Array<{ event_type: string; actor_username?: string | null; actor_role?: string | null; created_at?: string | null }>;
};

type SearchResponse = { items: AddressRecord[] };

function statusLabel(value?: string | null): string {
  return (value || 'unknown').replaceAll('-', ' ');
}

export function AddressRecordSearchPanel({ apiBaseUrl }: { apiBaseUrl: string }) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [query, setQuery] = useState('');
  const [records, setRecords] = useState<AddressRecord[]>([]);
  const [selected, setSelected] = useState<AddressRecord | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const canSearch = sessionStatus === 'ready' && Boolean(token);

  const selectedEvidence = useMemo(() => selected?.record_bundle?.evidence, [selected]);

  async function searchRecords(nextQuery = query) {
    if (!token) {
      setError('Sign in to search official address case files.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setNotice(null);
    try {
      const params = new URLSearchParams();
      if (nextQuery.trim()) {
        params.set('q', nextQuery.trim());
      }
      params.set('limit', '25');
      const response = await fetch(`${browserApiBaseUrl}/api/v1/address-records/search?${params.toString()}`, {
        headers: authorizationHeader(token),
      });
      const payload = (await response.json()) as SearchResponse | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to search address records.');
        return;
      }
      const items = (payload as SearchResponse).items;
      setRecords(items);
      setSelected(items[0] ?? null);
      setNotice(items.length ? `${items.length} address case file${items.length === 1 ? '' : 's'} found.` : 'No address case files matched that search.');
    } catch {
      setError('Unable to reach the address record search service.');
    } finally {
      setIsLoading(false);
    }
  }

  async function loadCaseFile(addressCode: string) {
    if (!token) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/address-records/${encodeURIComponent(addressCode)}`, {
        headers: authorizationHeader(token),
      });
      const payload = (await response.json()) as AddressRecord | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to open address case file.');
        return;
      }
      setSelected(payload as AddressRecord);
    } catch {
      setError('Unable to open the address case file.');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (canSearch) {
      void searchRecords('');
    }
  }, [canSearch]);

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void searchRecords(query);
  }

  if (sessionStatus === 'loading') {
    return <p className="panel-state">Checking operator session…</p>;
  }

  if (!canSearch) {
    return <p className="panel-state">Sign in with an authorized account to search official address case files.</p>;
  }

  return (
    <section className="operations-panel" aria-label="Official address case files">
      <div className="registry-toolbar">
        <div>
          <p className="section-label">Official registry layer</p>
          <h2>Address Case Files</h2>
          <p>Search canonical records by address code, routing area, landmark, road, or local area. Evidence is grouped as a case file, not shown as raw rows.</p>
        </div>
      </div>

      <form className="territory-form" onSubmit={submitSearch}>
        <label className="territory-field territory-field-wide">
          <span className="territory-label">Search official address records</span>
          <input className="territory-input" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="EG-BN-N1…, Ela Nguema, landmark, road" />
        </label>
        <div className="territory-form-actions">
          <button className="primary-action" type="submit" disabled={isLoading}>{isLoading ? 'Searching…' : 'Search case files'}</button>
        </div>
      </form>

      {notice ? <p className="form-notice success">{notice}</p> : null}
      {error ? <p className="form-notice error">{error}</p> : null}

      <div className="review-layout">
        <aside className="request-list-panel">
          <p className="section-label">Search results</p>
          {records.length ? records.map((record) => (
            <button key={record.address_code} className={`request-list-item ${selected?.address_code === record.address_code ? 'active' : ''}`} type="button" onClick={() => void loadCaseFile(record.address_code)}>
              <strong>{record.address_label}</strong>
              <span>{record.address_code}</span>
              <small>{statusLabel(record.status)} · {record.record_bundle?.routing?.territory_name || record.territory_name || 'routing pending'}</small>
            </button>
          )) : <p className="panel-state">No canonical address records yet.</p>}
        </aside>

        <article className="request-detail-panel">
          {selected ? (
            <>
              <div className="request-detail-head compact-case-head">
                <div>
                  <p className="section-label">Address case file</p>
                  <h3>{selected.address_label}</h3>
                  <p>{selected.address_code}</p>
                </div>
                <div className="operator-summary-row compact-case-chips" aria-label="Selected case summary">
                  <span className="status-chip ok">{statusLabel(selected.status)}</span>
                  <span className="status-chip">{selected.record_bundle?.routing?.territory_name || selected.territory_name || 'routing pending'}</span>
                  <span className="status-chip">{statusLabel(selected.publication_state || 'internal review')}</span>
                </div>
              </div>
              <p className="public-task-copy compact-case-summary">This case is selected. Technical evidence, GPS details, and audit timeline are available below only when needed.</p>
              <details className="quiet-disclosure compact-review-disclosure">
                <summary>Show technical evidence and timeline</summary>
                <div className="request-detail-grid">
                  <div className="operator-finding-card">
                    <strong>Location authority</strong>
                    <p>{selected.latitude}, {selected.longitude}</p>
                    <p>Accuracy: {selected.accuracy_meters ?? selectedEvidence?.gps_capture?.accuracy_meters ?? 'not recorded'}m · CRS: EPSG:4326</p>
                    <p>Routing: {selected.record_bundle?.routing?.territory_name || selected.territory_name || 'not assigned'}</p>
                    <p className="institutional-note">Source: {selected.record_bundle?.routing?.assignment_source || 'operator-confirmed'} · Confidence: {selected.record_bundle?.routing?.assignment_confidence || 'confirmed'}</p>
                  </div>
                  <div className="operator-finding-card">
                    <strong>Searchable context</strong>
                    <p>Landmark: {selected.record_bundle?.search?.landmark || 'not supplied'}</p>
                    <p>Road/local area: {selected.record_bundle?.search?.road_name || selected.record_bundle?.search?.suggested_local_area || 'not supplied'}</p>
                    <p>Province: {selected.province_code || selected.record_bundle?.identity?.address_code?.split('-')[1] || 'unknown'}</p>
                  </div>
                  <div className="operator-finding-card">
                    <strong>Evidence</strong>
                    <p>GPS capture: {selectedEvidence?.gps_capture?.capture_method || 'recorded'}</p>
                    <p>Field status: {selectedEvidence?.field_verification?.status || 'not recorded'}</p>
                    <p>Certificate: {selected.record_bundle?.outputs?.certificate_id || 'pending'}</p>
                    <p>Signage batch: {selected.record_bundle?.outputs?.signage_batch || 'not batched'}</p>
                  </div>
                  <div className="operator-finding-card">
                    <strong>Timeline</strong>
                    {(selected.timeline ?? []).length ? (
                      <ul>
                        {(selected.timeline ?? []).map((event, index) => (
                          <li key={`${event.event_type}-${index}`}>{statusLabel(event.event_type)} · {event.actor_username || event.actor_role || 'system'}</li>
                        ))}
                      </ul>
                    ) : <p>Open a case file to load its official timeline.</p>}
                  </div>
                </div>
              </details>
            </>
          ) : <p className="panel-state">Select a record to view the case file.</p>}
        </article>
      </div>
    </section>
  );
}
