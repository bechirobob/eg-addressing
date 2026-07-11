'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

import { resolveBrowserApiBaseUrl, sessionRequestInit, useStoredSession } from './sessionClient';

type TimelineEvent = {
  event_type: string;
  action?: string | null;
  actor_username?: string | null;
  actor_role?: string | null;
  created_at?: string | null;
  details?: Record<string, unknown>;
};

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
  timeline?: TimelineEvent[];
};

type SearchResponse = { items: AddressRecord[] };
type AddressRecordExportResponse = { source: string; status: string; count: number; csv: string; operator_note?: string };
type AddressRecordCertificateResponse = { certificate_id: string; address_code: string; source: string; html: string };

type AddressRecordHold = {
  address_code: string;
  address_label: string;
  status: string;
  publication_state?: string | null;
  territory_name?: string | null;
  hold_reason: string;
  spatial_risk: {
    level: string;
    nearby_count: number;
    closest_distance_meters?: number | null;
    source: string;
  };
  evidence_status: string;
  certificate_readiness: string;
  signage_readiness: string;
  next_action: string;
};

type AddressRecordHoldsResponse = { source: string; status: string; count: number; items: AddressRecordHold[]; operator_note?: string };

function statusLabel(value?: string | null): string {
  return (value || 'unknown').replaceAll('-', ' ');
}

function formatDate(value?: string | null): string {
  if (!value) return 'not recorded';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return 'not recorded';
  return parsed.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

function eventStage(event: TimelineEvent): string {
  const key = event.event_type || event.action || 'case event';
  const labels: Record<string, string> = {
    'address-record-upserted': 'Canonical record updated',
    'registry-ready': 'Registry ready',
    'publication-approved': 'Publication approved',
    'publish': 'Published',
    'field-check': 'Field check requested',
    'under-review': 'Review opened',
    'approve': 'Approved into registry',
    'evidence-accepted': 'Evidence accepted',
    'evidence-needs-recapture': 'Evidence needs recapture',
    'certificate-generated': 'Certificate generated',
    'signage-pack-generated': 'Signage pack generated',
  };
  return labels[key] || statusLabel(key);
}

function eventEvidence(event: TimelineEvent): string {
  const details = event.details || {};
  const note = details.reviewer_note || details.note || details.decision || details.address_code || details.source_submission_id;
  if (typeof note === 'string' && note.trim()) return note;
  return event.action || event.event_type || 'official audit event';
}

function downloadTextFile(filename: string, content: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function AddressRecordSearchPanel({ apiBaseUrl }: { apiBaseUrl: string }) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [query, setQuery] = useState('');
  const [records, setRecords] = useState<AddressRecord[]>([]);
  const [holds, setHolds] = useState<AddressRecordHold[]>([]);
  const [selected, setSelected] = useState<AddressRecord | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const canSearch = sessionStatus === 'ready';

  const selectedEvidence = useMemo(() => selected?.record_bundle?.evidence, [selected]);

  async function loadHoldRegister() {
    if (!canSearch) {
      return;
    }
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/address-records/holds?status=registry-ready&limit=8`, {
        ...sessionRequestInit(token),
      });
      const payload = (await response.json()) as AddressRecordHoldsResponse | { detail?: string };
      if (response.ok) {
        setHolds((payload as AddressRecordHoldsResponse).items);
      }
    } catch {
      setHolds([]);
    }
  }

  async function searchRecords(nextQuery = query) {
    if (!canSearch) {
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
        ...sessionRequestInit(token),
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
    if (!canSearch) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/address-records/${encodeURIComponent(addressCode)}`, {
        ...sessionRequestInit(token),
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

  async function downloadCanonicalExport() {
    if (!canSearch) {
      setError('Sign in before exporting canonical address records.');
      return;
    }
    setError(null);
    setNotice(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/address-records/export?status=published`, {
        ...sessionRequestInit(token),
      });
      const payload = (await response.json()) as AddressRecordExportResponse | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to export canonical address records.');
        return;
      }
      const exportPayload = payload as AddressRecordExportResponse;
      downloadTextFile('canonical-address-records-published.csv', exportPayload.csv, 'text/csv;charset=utf-8');
      setNotice(`Canonical address record export prepared from ${exportPayload.source}: ${exportPayload.count} row${exportPayload.count === 1 ? '' : 's'}.`);
    } catch {
      setError('Unable to export canonical address records.');
    }
  }

  async function downloadSelectedCertificate() {
    if (!canSearch || !selected) {
      return;
    }
    setError(null);
    setNotice(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/address-records/${encodeURIComponent(selected.address_code)}/certificate`, {
        ...sessionRequestInit(token),
      });
      const payload = (await response.json()) as AddressRecordCertificateResponse | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Certificate is available only for published canonical records.');
        return;
      }
      const certificate = payload as AddressRecordCertificateResponse;
      downloadTextFile(`${certificate.certificate_id}.html`, certificate.html, 'text/html;charset=utf-8');
      setNotice(`Certificate prepared from ${certificate.source}: ${certificate.certificate_id}.`);
    } catch {
      setError('Unable to prepare the selected address certificate.');
    }
  }

  useEffect(() => {
    if (canSearch) {
      void loadHoldRegister();
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
          <p>Search canonical records by address code, routing area, landmark, road, or local area. Evidence is grouped as a compact case file, not shown as raw rows.</p>
        </div>
        <button className="secondary-action" type="button" onClick={() => void downloadCanonicalExport()}>Export canonical records</button>
      </div>

      <div className="registry-hold-workbench" aria-label="Hold register">
        <div className="registry-hold-head">
          <div>
            <p className="section-label">Hold register</p>
            <h3>Registry-ready records held from publication</h3>
          </div>
          <span className="institutional-note">Canonical source: address_records</span>
        </div>
        {holds.length ? (
          <div className="hold-risk-ledger" role="table" aria-label="Compact hold and spatial risk ledger">
            <div className="hold-risk-row hold-risk-row-head" role="row">
              <span>Record</span>
              <span>Spatial risk</span>
              <span>Evidence</span>
              <span>Readiness</span>
              <span>Next action</span>
            </div>
            {holds.map((hold) => (
              <button className="hold-risk-row" role="row" type="button" key={hold.address_code} onClick={() => void loadCaseFile(hold.address_code)}>
                <span><strong>{hold.address_label}</strong><small>{hold.address_code}</small></span>
                <span><strong>{statusLabel(hold.spatial_risk.level)}</strong><small>{hold.spatial_risk.nearby_count} nearby · {hold.spatial_risk.closest_distance_meters ?? 'no'}m closest</small></span>
                <span><strong>{hold.evidence_status}</strong><small>{hold.hold_reason}</small></span>
                <span><strong>Certificate: {hold.certificate_readiness}</strong><small>Signage: {hold.signage_readiness}</small></span>
                <span>{hold.next_action}</span>
              </button>
            ))}
          </div>
        ) : <p className="panel-state">No registry-ready holds found. Publication remains locked until an authorized release exists.</p>}
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
                </div>
                <div className="case-timeline-ledger" aria-label="Compact official timeline">
                  <div className="case-timeline-head">
                    <strong>Compact official timeline</strong>
                    <button className="secondary-action" type="button" onClick={() => void downloadSelectedCertificate()} disabled={selected.status !== 'published'}>Download certificate</button>
                  </div>
                  {(selected.timeline ?? []).length ? (
                    <ol className="case-timeline-list">
                      {(selected.timeline ?? []).slice(-8).map((event, index) => (
                        <li className="case-timeline-row" key={`${event.event_type}-${event.created_at ?? index}`}>
                          <span className="case-timeline-stage">{eventStage(event)}</span>
                          <span className="case-timeline-evidence">{eventEvidence(event)}</span>
                          <span className="case-timeline-meta">{event.actor_username || event.actor_role || 'system'} · {formatDate(event.created_at)}</span>
                        </li>
                      ))}
                    </ol>
                  ) : <p className="institutional-note">Open a case file to load its official timeline.</p>}
                </div>
              </details>
            </>
          ) : <p className="panel-state">Select a record to view the case file.</p>}
        </article>
      </div>
    </section>
  );
}
