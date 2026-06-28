'use client';

import { useEffect, useState } from 'react';

import { authorizationHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

type ReportingSummary = {
  totals: {
    territories: number;
    submissions: number;
    review_queue: number;
    published_addresses: number;
    import_jobs: number;
  };
  territories_by_province: Array<{ province_code: string; territory_count: number }>;
  review_breakdown: Array<{ review_status: string; count: number }>;
  publication_breakdown: Array<{ status: string; count: number }>;
};

type ReportingDashboardPanelProps = {
  summary: ReportingSummary;
  apiBaseUrl: string;
};

export function ReportingDashboardPanel({ summary: initialSummary, apiBaseUrl }: ReportingDashboardPanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [summary, setSummary] = useState(initialSummary);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    if (!token) return;

    async function loadSummary() {
      setIsRefreshing(true);
      setError(null);
      try {
        const response = await fetch(`${browserApiBaseUrl}/api/v1/reporting/summary`, {
          headers: authorizationHeader(token!),
        });
        if (!response.ok) {
          setError('Unable to refresh operational totals.');
          return;
        }
        const payload = (await response.json()) as ReportingSummary;
        setSummary(payload);
      } catch {
        setError('Unable to refresh operational totals.');
      } finally {
        setIsRefreshing(false);
      }
    }

    void loadSummary();
  }, [browserApiBaseUrl, token]);

  return (
    <section className="section-grid territory-admin-grid">
      <article className="panel panel-accent-blue territory-list-panel">
        <div className="panel-head">
          <p className="section-label">National operations status</p>
          <h3>Operational totals</h3>
        </div>
        {sessionStatus === 'loading' || isRefreshing ? <p className="panel-state">Refreshing authenticated reporting totals…</p> : null}
        <div className="summary-grid">
          <div className="summary-card">
            <strong>{summary.totals.territories}</strong>
            <span>Active territories</span>
          </div>
          <div className="summary-card">
            <strong>{summary.totals.submissions}</strong>
            <span>Total submissions</span>
          </div>
          <div className="summary-card">
            <strong>{summary.totals.review_queue}</strong>
            <span>Queue awaiting action</span>
          </div>
          <div className="summary-card">
            <strong>{summary.totals.published_addresses}</strong>
            <span>Published addresses</span>
          </div>
          <div className="summary-card">
            <strong>{summary.totals.import_jobs}</strong>
            <span>Intake jobs</span>
          </div>
        </div>
        {error ? <p className="form-notice error">{error}</p> : null}
      </article>

      <article className="panel panel-accent-gold">
        <div className="panel-head">
          <p className="section-label">Territory spread</p>
          <h3>Territories by province</h3>
        </div>
        {summary.territories_by_province.length > 0 ? (
          <ul className="program-list">
            {summary.territories_by_province.map((row) => (
              <li key={row.province_code}>
                <span>{row.province_code}</span>
                <span>{row.territory_count}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="panel-state">No territory totals are available yet.</p>
        )}
      </article>

      <article className="panel panel-accent-green">
        <div className="panel-head">
          <p className="section-label">Review state</p>
          <h3>Verification queue breakdown</h3>
        </div>
        {summary.review_breakdown.length > 0 ? (
          <ul className="program-list">
            {summary.review_breakdown.map((row) => (
              <li key={row.review_status}>
                <span>{row.review_status}</span>
                <span>{row.count}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="panel-state">No review-state totals are available yet.</p>
        )}
      </article>

      <article className="panel panel-accent-blue">
        <div className="panel-head">
          <p className="section-label">Publication state</p>
          <h3>Official output breakdown</h3>
        </div>
        {summary.publication_breakdown.length > 0 ? (
          <ul className="program-list">
            {summary.publication_breakdown.map((row) => (
              <li key={row.status}>
                <span>{row.status}</span>
                <span>{row.count}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="panel-state">No publication totals are available yet.</p>
        )}
      </article>
    </section>
  );
}
