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

function rowsFromBreakdown(rows: Array<{ [key: string]: string | number }>, keyName: string) {
  return rows.map((row) => ({ label: statusText(String(row[keyName] ?? 'Unknown')), count: Number(row.count ?? 0) }));
}

export function ReportingPanel({ summary: initialSummary, readinessSummary, apiBaseUrl }: ReportingPanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [summary, setSummary] = useState(initialSummary);
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

  useEffect(() => {
    if (!token) return;
    void loadSummary(token).catch(() => setError('Reports unavailable. Sign in to view reporting data.'));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [browserApiBaseUrl, token]);

  async function handleApplyFilters() {
    setIsRefreshing(true);
    setError(null);
    try {
      await loadSummary(token ?? null);
    } catch {
      setError('Unable to refresh report data.');
    } finally {
      setIsRefreshing(false);
    }
  }

  function handleExportReport() {
    const lines = [
      ['Metric', 'Value'],
      ['Active territories', summary.totals.territories],
      ['Total submissions', summary.totals.submissions],
      ['Verification queue', summary.totals.review_queue],
      ['Published addresses', summary.totals.published_addresses],
      ['Correction reports', summary.totals.public_corrections],
      ['Field requests', summary.totals.citizen_geotags ?? 0],
    ];
    const csv = lines.map((line) => line.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'national-addressing-report.csv';
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

      <article className="public-task-panel reports-summary-panel">
        <div className="panel-head">
          <p className="section-label">Summary</p>
          <h3>Current workload</h3>
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

      {readinessSummary || readinessSummary === null ? (
        <article className="public-task-panel reports-section-panel">
          <div className="panel-head"><p className="section-label">Publication readiness</p><h3>{readinessSummary ? statusText(readinessSummary.readiness_status) : 'Readiness unavailable'}</h3></div>
          {readinessSummary ? <p className="institutional-note">{readinessSummary.passed_gates}/{readinessSummary.total_gates} checks passed. Publication and signage remain controlled until approval.</p> : null}
        </article>
      ) : null}
    </section>
  );
}
