'use client';

import { useEffect, useMemo, useState } from 'react';

import { apiJson, apiPath } from './apiClient';
import { authorizationHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

type ReportingSummary = {
  totals: {
    territories: number;
    submissions: number;
    review_queue: number;
    published_addresses: number;
    import_jobs: number;
    public_corrections: number;
    correction_queue: number;
    citizen_geotags?: number;
    geotag_queue?: number;
  };
  territories_by_province: Array<{ province_code: string; territory_count: number }>;
  review_breakdown: Array<{ review_status: string; count: number }>;
  publication_breakdown: Array<{ status: string; count: number }>;
  correction_breakdown: Array<{ status: string; count: number }>;
  geotag_breakdown?: Array<{ status: string; count: number }>;
  filters?: {
    province?: string | null;
    territory?: string | null;
    status?: string | null;
    date_from?: string | null;
    date_to?: string | null;
  };
};

type PilotReadinessSummary = {
  readiness_status: string;
  passed_gates: number;
  total_gates: number;
  gates: Array<{ name: string; status: string; evidence: string; next_step: string }>;
  recent_audit_events?: Array<{ action: string; entity_type: string; entity_id: string; actor_username?: string | null; created_at?: string | null }>;
  boundaries: string[];
};

type ReportingPanelProps = {
  summary: ReportingSummary;
  readinessSummary?: PilotReadinessSummary | null;
  apiBaseUrl: string;
};

const STATUS_OPTIONS = ['All statuses', 'Submitted', 'Under review', 'Needs field check', 'Evidence received', 'Registry ready', 'Published', 'Rejected'];

function apiUrl(baseUrl: string, path: Parameters<typeof apiPath>[0]): string {
  return `${baseUrl}${apiPath(path)}`;
}

function statusText(value: string | undefined): string {
  if (!value) return 'Unknown';
  return value.replaceAll('-', ' ').replace(/\b\w/g, (char) => char.toUpperCase());
}

function readinessStatusLabel(value: string | undefined): string {
  if (value === 'pilot-ready') return 'Ready for controlled review';
  if (value === 'pilot-prep') return 'Preparation required';
  return statusText(value);
}

function formatEvidence(value: string): string {
  return value
    .replaceAll("{'", '')
    .replaceAll("':", ':')
    .replaceAll("',", ',')
    .replaceAll("'}", '')
    .replaceAll("'", '')
    .replaceAll('{', '')
    .replaceAll('}', '')
    .replaceAll(',', ';')
    .replace(/\s+/g, ' ')
    .trim();
}

function auditEntityLabel(event: { entity_type: string; entity_id: string }): string {
  if (event.entity_type === 'session') return 'session: [protected]';
  if (event.entity_id.length > 28) return `${event.entity_type}: [protected-id]`;
  return `${event.entity_type}: ${event.entity_id}`;
}

function rowsFromBreakdown(rows: Array<{ [key: string]: string | number }>, keyName: string) {
  return rows.map((row) => ({ label: statusText(String(row[keyName] ?? 'Unknown')), count: Number(row.count ?? 0) }));
}

function csvCell(value: string | number | null | undefined): string {
  const text = String(value ?? '');
  const safeText = /^[=+\-@\t\r]/.test(text) ? `'${text}` : text;
  return `"${safeText.replaceAll('"', '""')}"`;
}

function safeIsoDate(value: string | null | undefined): string {
  if (!value) return 'not recorded';
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? 'not recorded' : parsed.toISOString();
}

function filterDisplayValue(value: string | null | undefined, fallback: string): string {
  return value && value.trim() ? value : fallback;
}

export function ReportingPanel({ summary: initialSummary, readinessSummary, apiBaseUrl }: ReportingPanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [summary, setSummary] = useState(initialSummary);
  const [readiness, setReadiness] = useState(readinessSummary ?? null);
  const [province, setProvince] = useState('');
  const [territory, setTerritory] = useState('');
  const [status, setStatus] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const provinceOptions = useMemo(() => summary.territories_by_province.map((row) => row.province_code).filter(Boolean), [summary]);
  const reviewRows = rowsFromBreakdown(summary.review_breakdown, 'review_status');
  const publicationRows = rowsFromBreakdown(summary.publication_breakdown, 'status');
  const correctionRows = rowsFromBreakdown(summary.correction_breakdown, 'status');
  const fieldRows = rowsFromBreakdown(summary.geotag_breakdown ?? [], 'status');
  const pendingReviewCount = reviewRows
    .filter((row) => ['Submitted', 'Under Review', 'Needs Field Check', 'Evidence Received'].includes(row.label))
    .reduce((total, row) => total + row.count, 0);
  const blockedPublicationCount = readiness?.gates.filter((gate) => gate.status !== 'passed').length ?? publicationRows
    .filter((row) => !['Published', 'Public'].includes(row.label))
    .reduce((total, row) => total + row.count, 0);
  const fieldQueueCount = summary.totals.geotag_queue ?? fieldRows
    .filter((row) => !['Published', 'Registry Ready', 'Rejected'].includes(row.label))
    .reduce((total, row) => total + row.count, 0);

  async function loadSummary(currentToken: string | null) {
    const params = new URLSearchParams();
    if (province) params.set('province', province);
    if (territory.trim()) params.set('territory', territory.trim());
    if (status) params.set('status_filter', status.toLowerCase().replaceAll(' ', '-'));
    if (dateFrom) params.set('date_from', dateFrom);
    if (dateTo) params.set('date_to', dateTo);
    const suffix = params.toString() ? `?${params.toString()}` : '';
    const payload = await apiJson<ReportingSummary>(`${apiUrl(browserApiBaseUrl, '/api/v1/reporting/summary')}${suffix}`, { token: currentToken ?? undefined });
    setSummary(payload);
  }

  async function loadReadiness(currentToken: string | null) {
    const payload = await apiJson<PilotReadinessSummary>(apiUrl(browserApiBaseUrl, '/api/v1/pilot-readiness/summary'), { token: currentToken ?? undefined });
    setReadiness(payload);
  }

  useEffect(() => {
    if (sessionStatus !== 'ready') return;
    void Promise.all([loadSummary(token), loadReadiness(token)]).catch(() => setError('Reports unavailable. Sign in to view reporting data.'));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [browserApiBaseUrl, sessionStatus, token]);

  async function handleApplyFilters() {
    setIsRefreshing(true);
    setError(null);
    try {
      await Promise.all([loadSummary(token ?? null), loadReadiness(token ?? null)]);
    } catch {
      setError('Unable to refresh report data.');
    } finally {
      setIsRefreshing(false);
    }
  }

  function handleExportReport() {
    const generatedAt = new Date().toISOString();
    const appliedFilters = summary.filters ?? {};
    const filterRows = [
      ['Province', filterDisplayValue(appliedFilters.province, 'All provinces')],
      ['Territory', filterDisplayValue(appliedFilters.territory, 'All territories')],
      ['Status', filterDisplayValue(appliedFilters.status ? statusText(appliedFilters.status) : null, 'All statuses')],
      ['Date from', filterDisplayValue(appliedFilters.date_from, 'Not set')],
      ['Date to', filterDisplayValue(appliedFilters.date_to, 'Not set')],
    ];
    const metricRows = [
      ['Active territories', summary.totals.territories],
      ['Total submissions', summary.totals.submissions],
      ['Verification queue', summary.totals.review_queue],
      ['Published addresses', summary.totals.published_addresses],
      ['Correction reports', summary.totals.public_corrections],
      ['Field activity', summary.totals.citizen_geotags ?? 0],
      ['Need operator review', pendingReviewCount],
      ['Need field/geo follow-up', fieldQueueCount],
      ['Publication gates not clear', blockedPublicationCount],
    ];
    const rows: Array<Array<string | number | null | undefined>> = [
      ['National Digital Addressing Pilot — Reports and audit export'],
      ['Generated at', generatedAt],
      ['Scope note', 'Read-only operational report. Public lookup remains limited to published records.'],
      [],
      ['Filters'],
      ['Filter', 'Value'],
      ...filterRows,
      [],
      ['Summary metrics'],
      ['Metric', 'Value'],
      ...metricRows,
      [],
      ['Workload review queue'],
      ['Status', 'Count'],
      ...reviewRows.map((row) => [row.label, row.count]),
      [],
      ['Field activity'],
      ['Status', 'Count'],
      ...fieldRows.map((row) => [row.label, row.count]),
      [],
      ['Publication status'],
      ['Status', 'Count'],
      ...publicationRows.map((row) => [row.label, row.count]),
      [],
      ['Correction reports'],
      ['Status', 'Count'],
      ...correctionRows.map((row) => [row.label, row.count]),
    ];

    if (readiness) {
      rows.push(
        [],
        ['Publication readiness'],
        ['Status', readinessStatusLabel(readiness.readiness_status)],
        ['Checks passed', `${readiness.passed_gates}/${readiness.total_gates}`],
        [],
        ['Readiness gates'],
        ['Gate', 'Status', 'Evidence', 'Next step'],
        ...readiness.gates.map((gate) => [gate.name, statusText(gate.status), formatEvidence(gate.evidence), gate.next_step]),
      );
      if (readiness.recent_audit_events?.length) {
        rows.push(
          [],
          ['Recent audit events'],
          ['Action', 'Entity', 'Actor', 'Time'],
          ...readiness.recent_audit_events.map((event) => [
            statusText(event.action),
            auditEntityLabel(event),
            event.actor_username ?? 'system',
            safeIsoDate(event.created_at),
          ]),
        );
      }
      if (readiness.boundaries.length) {
        rows.push(
          [],
          ['Governance boundaries'],
          ['Boundary'],
          ...readiness.boundaries.map((boundary) => [boundary]),
        );
      }
    }

    const csv = rows.map((line) => line.map(csvCell).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'national-addressing-report-audit.csv';
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="section-grid reports-service-grid">
      <article className="public-task-panel reports-intro-panel">
        <div className="panel-head">
          <p className="section-label">Reports</p>
          <h3>Track workload, review progress, field activity, and publication readiness.</h3>
        </div>
        <p className="institutional-note">Reports are read-only. Use filters to narrow the view, then export a report for review or briefing.</p>
        {sessionStatus === 'loading' || isRefreshing ? <p className="panel-state">Refreshing report data…</p> : null}
        {error ? <p className="form-notice error">{error}</p> : null}
      </article>

      <article className="public-task-panel reports-summary-panel">
        <div className="panel-head">
          <p className="section-label">Summary</p>
          <h3>What needs action</h3>
        </div>
        <div className="reports-action-strip" aria-label="Operational action summary">
          <div><strong>{pendingReviewCount}</strong><span>Need operator review</span></div>
          <div><strong>{fieldQueueCount}</strong><span>Need field/geo follow-up</span></div>
          <div><strong>{blockedPublicationCount}</strong><span>Publication gates not clear</span></div>
        </div>
        <dl className="metric-row-list">
          <div><dt>Active territories</dt><dd>{summary.totals.territories}</dd></div>
          <div><dt>Total submissions</dt><dd>{summary.totals.submissions}</dd></div>
          <div><dt>Verification queue</dt><dd>{summary.totals.review_queue}</dd></div>
          <div><dt>Published addresses</dt><dd>{summary.totals.published_addresses}</dd></div>
          <div><dt>Correction reports</dt><dd>{summary.totals.public_corrections}</dd></div>
          <div><dt>Field activity</dt><dd>{summary.totals.citizen_geotags ?? 0}</dd></div>
        </dl>
      </article>

      <article className="public-task-panel reports-filter-panel">
        <div className="panel-head">
          <p className="section-label">Filters</p>
          <h3>Report scope</h3>
        </div>
        <div className="reports-filter-grid">
          <label className="territory-field">
            <span className="territory-label">Province</span>
            <select className="territory-input" value={province} onChange={(event) => setProvince(event.target.value)}>
              <option value="">All provinces</option>
              {provinceOptions.map((code) => <option key={code} value={code}>{code}</option>)}
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Territory</span>
            <input className="territory-input" value={territory} onChange={(event) => setTerritory(event.target.value)} placeholder="Name or code" />
          </label>
          <label className="territory-field">
            <span className="territory-label">Date from</span>
            <input className="territory-input" type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
          </label>
          <label className="territory-field">
            <span className="territory-label">Date to</span>
            <input className="territory-input" type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
          </label>
          <label className="territory-field">
            <span className="territory-label">Status</span>
            <select className="territory-input" value={status} onChange={(event) => setStatus(event.target.value)}>
              {STATUS_OPTIONS.map((item) => <option key={item} value={item === 'All statuses' ? '' : item}>{item}</option>)}
            </select>
          </label>
        </div>
        <div className="territory-form-actions">
          <button className="verification-button" type="button" onClick={() => void handleApplyFilters()} disabled={isRefreshing}>Apply filters</button>
          <button className="secondary-action" type="button" onClick={handleExportReport}>Export report</button>
        </div>
      </article>

      <article className="public-task-panel reports-section-panel">
        <div className="panel-head"><p className="section-label">Workload</p><h3>Review queue</h3></div>
        <div className="table-wrap desktop-table-wrap report-table-wrap"><table className="data-table desktop-data-table"><caption>Review queue</caption><thead><tr><th scope="col">Status</th><th scope="col">Count</th></tr></thead><tbody>{reviewRows.map((row) => <tr key={row.label}><td>{row.label}</td><td>{row.count}</td></tr>)}</tbody></table></div>
        <ul className="report-row-list mobile-card-list">{reviewRows.map((row) => <li key={row.label}><span>{row.label}</span><strong>{row.count}</strong></li>)}</ul>
      </article>

      <article className="public-task-panel reports-section-panel">
        <div className="panel-head"><p className="section-label">Field activity</p><h3>Submitted locations</h3></div>
        <div className="table-wrap desktop-table-wrap report-table-wrap"><table className="data-table desktop-data-table"><caption>Field activity</caption><thead><tr><th scope="col">Status</th><th scope="col">Count</th></tr></thead><tbody>{fieldRows.length ? fieldRows.map((row) => <tr key={row.label}><td>{row.label}</td><td>{row.count}</td></tr>) : <tr><td>No field activity in this report scope</td><td>0</td></tr>}</tbody></table></div>
        <ul className="report-row-list mobile-card-list">{fieldRows.length ? fieldRows.map((row) => <li key={row.label}><span>{row.label}</span><strong>{row.count}</strong></li>) : <li><span>No field activity in this report scope</span><strong>0</strong></li>}</ul>
      </article>

      <article className="public-task-panel reports-section-panel">
        <div className="panel-head"><p className="section-label">Publication status</p><h3>Release progress</h3></div>
        <div className="table-wrap desktop-table-wrap report-table-wrap"><table className="data-table desktop-data-table"><caption>Publication status</caption><thead><tr><th scope="col">Status</th><th scope="col">Count</th></tr></thead><tbody>{publicationRows.map((row) => <tr key={row.label}><td>{row.label}</td><td>{row.count}</td></tr>)}</tbody></table></div>
        <ul className="report-row-list mobile-card-list">{publicationRows.map((row) => <li key={row.label}><span>{row.label}</span><strong>{row.count}</strong></li>)}</ul>
      </article>

      <article className="public-task-panel reports-section-panel">
        <div className="panel-head"><p className="section-label">Correction reports</p><h3>Public reports</h3></div>
        <div className="table-wrap desktop-table-wrap report-table-wrap"><table className="data-table desktop-data-table"><caption>Correction reports</caption><thead><tr><th scope="col">Status</th><th scope="col">Count</th></tr></thead><tbody>{correctionRows.map((row) => <tr key={row.label}><td>{row.label}</td><td>{row.count}</td></tr>)}</tbody></table></div>
        <ul className="report-row-list mobile-card-list">{correctionRows.map((row) => <li key={row.label}><span>{row.label}</span><strong>{row.count}</strong></li>)}</ul>
      </article>

      {readiness || readiness === null ? (
        <article className="public-task-panel reports-section-panel reports-readiness-panel">
          <div className="panel-head">
            <p className="section-label">Publication readiness</p>
            <h3>{readiness ? readinessStatusLabel(readiness.readiness_status) : 'Readiness unavailable'}</h3>
          </div>
          {readiness ? (
            <>
              <p className="institutional-note">{readiness.passed_gates}/{readiness.total_gates} checks passed. Publication and signage remain controlled until approval.</p>
              <div className="table-wrap desktop-table-wrap report-table-wrap">
                <table className="data-table desktop-data-table">
                  <caption>Readiness gates</caption>
                  <thead><tr><th scope="col">Gate</th><th scope="col">Status</th><th scope="col">Evidence</th><th scope="col">Next step</th></tr></thead>
                  <tbody>
                    {readiness.gates.map((gate) => (
                      <tr key={gate.name}>
                        <td>{gate.name}</td>
                        <td>{statusText(gate.status)}</td>
                        <td>{formatEvidence(gate.evidence)}</td>
                        <td>{gate.next_step}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <ul className="report-row-list mobile-card-list">
                {readiness.gates.map((gate) => <li key={gate.name}><span>{gate.name} · {formatEvidence(gate.evidence)}</span><strong>{statusText(gate.status)}</strong></li>)}
              </ul>
            </>
          ) : null}
        </article>
      ) : null}

      {readiness?.recent_audit_events?.length ? (
        <article className="public-task-panel reports-section-panel reports-audit-panel">
          <div className="panel-head"><p className="section-label">Audit trail</p><h3>Recent accountability events</h3></div>
          <div className="table-wrap desktop-table-wrap report-table-wrap">
            <table className="data-table desktop-data-table">
              <caption>Recent audit events</caption>
              <thead><tr><th scope="col">Action</th><th scope="col">Entity</th><th scope="col">Actor</th><th scope="col">Time</th></tr></thead>
              <tbody>
                {readiness.recent_audit_events.map((event, index) => (
                  <tr key={`${event.action}-${event.entity_id}-${index}`}>
                    <td>{statusText(event.action)}</td>
                    <td>{auditEntityLabel(event)}</td>
                    <td>{event.actor_username ?? 'system'}</td>
                    <td>{event.created_at ? new Date(event.created_at).toLocaleString() : 'not recorded'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <ul className="report-row-list mobile-card-list">
            {readiness.recent_audit_events.map((event, index) => <li key={`${event.action}-${event.entity_id}-mobile-${index}`}><span>{statusText(event.action)} · {event.entity_type}</span><strong>{event.actor_username ?? 'system'}</strong></li>)}
          </ul>
        </article>
      ) : null}

      {readiness?.boundaries?.length ? (
        <article className="public-task-panel reports-section-panel reports-boundary-panel">
          <div className="panel-head"><p className="section-label">Governance boundary</p><h3>What this report does not approve</h3></div>
          <ul className="mini-list">
            {readiness.boundaries.map((boundary) => <li key={boundary}><strong>Boundary</strong><span>{boundary}</span></li>)}
          </ul>
        </article>
      ) : null}
    </section>
  );
}
