'use client';

import { useEffect, useMemo, useState } from 'react';

import { apiJson, apiPath } from './apiClient';
import { translateUiText, type Locale, useTranslation } from './i18n';
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
};

type PilotReadinessSummary = {
  readiness_status: string;
  passed_gates: number;
  total_gates: number;
  gates: Array<{ name: string; status: string; evidence: string; next_step: string }>;
  boundaries: string[];
};

type AutomationSummary = {
  total: number;
  active_queue: number;
  average_quality_score: number;
  field_required: number;
  signage_ready: number;
  partner_api_ready: number;
  triage_buckets: Array<{ bucket: string; count: number }>;
  next_actions: Array<{ action: string; count: number }>;
};

type CorrectionQueueItem = {
  id: string;
  address_id: string | null;
  public_code: string | null;
  query: string;
  correction_type: string;
  reason: string;
  note: string;
  reporter_name: string | null;
  reporter_contact: string | null;
  status: string;
  reviewer_note: string;
  created_at: string;
  updated_at: string;
  address_label?: string | null;
  jurisdiction?: string | null;
};

type OperatorCommandCenter = {
  readiness: { status?: string; passed_gates?: number; total_gates?: number; boundaries?: string[] };
  queues: {
    verification_queue: number;
    citizen_geotag_queue: number;
    public_correction_queue: number;
    active_operator_queue: number;
    field_required: number;
  };
  risk_lanes: { duplicate_groups: number; overdue_sla: number; publication_holds: number };
  publication: { published_addresses: number; registry_ready: number; public_release_locked: boolean };
  demo_fixtures: { buckets: Array<{ bucket: string; count: number }>; total: number; clean: boolean; deleted?: number };
  restore_drill: {
    status: string;
    generated_at?: string;
    backup_file?: string;
    backup_bytes?: number;
    backup_sha256?: string;
    restore_target?: string;
    temporary_target_removed?: boolean;
    restored_counts?: Array<{ table_name: string; rows: number }>;
    operator_note?: string;
  };
  migrations: {
    status: string;
    applied_count: number;
    expected_count: number;
    pending_count: number;
    latest_version?: string | null;
    latest_filename?: string | null;
    operator_note?: string;
  };
  walkthrough: Array<{ step: string; title: string; route: string; operator_message: string }>;
};

type ReportingDashboardPanelProps = {
  summary: ReportingSummary;
  readinessSummary?: PilotReadinessSummary | null;
  apiBaseUrl: string;
};

const CORRECTION_STATUS_LABELS: Record<string, string> = {
  submitted: 'Submitted',
  'under-review': 'Under review',
  resolved: 'Resolved',
  rejected: 'Rejected',
};

function formatStatus(status: string): string {
  return CORRECTION_STATUS_LABELS[status] ?? status;
}

function formatDateTime(value: string): string {
  try {
    return new Intl.DateTimeFormat('en-GB', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function localizedStatusLabel(value: string | undefined, locale: string): string {
  if (locale !== 'es') return value || 'unknown';
  if (value === 'passed') return 'aprobado';
  if (value === 'not-run') return 'no ejecutado';
  if (value === 'unreadable') return 'ilegible';
  if (value === 'pilot-ready') return 'piloto listo';
  return value || 'desconocido';
}

function localizedCountLabel(count: number, singular: string, plural: string, locale: string): string {
  const label = count === 1 ? singular : plural;
  return locale === 'es' ? translateUiText(label, locale) : label;
}

function localizedAutomationLabel(value: string, locale: Locale): string {
  return translateUiText(value.replaceAll('-', ' '), locale);
}

function apiUrl(baseUrl: string, path: Parameters<typeof apiPath>[0]): string {
  return `${baseUrl}${apiPath(path)}`;
}

export function ReportingDashboardPanel({ summary: initialSummary, readinessSummary, apiBaseUrl }: ReportingDashboardPanelProps) {
  const { locale } = useTranslation();
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [summary, setSummary] = useState(initialSummary);
  const [readiness, setReadiness] = useState(readinessSummary ?? null);
  const [automationSummary, setAutomationSummary] = useState<AutomationSummary | null>(null);
  const [commandCenter, setCommandCenter] = useState<OperatorCommandCenter | null>(null);
  const [queueItems, setQueueItems] = useState<CorrectionQueueItem[]>([]);
  const [queueError, setQueueError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeFilter, setActiveFilter] = useState<'submitted' | 'under-review' | 'resolved' | 'rejected'>('submitted');
  const [reviewerNotes, setReviewerNotes] = useState<Record<string, string>>({});
  const [activeActionId, setActiveActionId] = useState<string | null>(null);

  const canReviewCorrections = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';

  function correctionDisabledReason(item: CorrectionQueueItem, action: 'under-review' | 'resolved' | 'rejected') {
    if (!canReviewCorrections) return 'Editor or admin required';
    if (activeActionId === item.id) return 'Working…';
    if (action === item.status) return `Already ${formatStatus(item.status).toLowerCase()}`;
    return null;
  }

  async function loadSummary(currentToken: string) {
    const payload = await apiJson<ReportingSummary>(apiUrl(browserApiBaseUrl, '/api/v1/reporting/summary'), { token: currentToken });
    setSummary(payload);
  }

  async function loadReadiness(currentToken: string) {
    const payload = await apiJson<PilotReadinessSummary>(apiUrl(browserApiBaseUrl, '/api/v1/pilot-readiness/summary'), { token: currentToken });
    setReadiness(payload);
  }

  async function loadAutomationSummary(currentToken: string) {
    const payload = await apiJson<AutomationSummary>(apiUrl(browserApiBaseUrl, '/api/v1/geotag-submissions/automation/summary'), { token: currentToken });
    setAutomationSummary(payload);
  }

  async function loadCommandCenter(currentToken: string) {
    const payload = await apiJson<OperatorCommandCenter>(apiUrl(browserApiBaseUrl, '/api/v1/operator/command-center'), { token: currentToken });
    setCommandCenter(payload);
  }

  async function cleanupDemoFixtures() {
    if (!token || sessionUser?.role !== 'admin') {
      setError('Admin access is required to clean demo fixtures.');
      return;
    }
    setIsRefreshing(true);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/operator/demo-fixtures/cleanup`, {
        method: 'POST',
        headers: authorizationHeader(token),
      });
      const payload = (await response.json()) as OperatorCommandCenter['demo_fixtures'] | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to clean demo fixtures.');
        return;
      }
      await loadCommandCenter(token);
      await loadSummary(token);
    } catch {
      setError('Unable to clean demo fixtures.');
    } finally {
      setIsRefreshing(false);
    }
  }

  async function loadQueue(currentToken: string, statusFilter: string) {
    const response = await fetch(`${browserApiBaseUrl}/api/v1/address-corrections?status=${encodeURIComponent(statusFilter)}`, {
      headers: authorizationHeader(currentToken),
    });
    if (!response.ok) {
      throw new Error('queue failed');
    }
    const payload = (await response.json()) as { items: CorrectionQueueItem[] };
    setQueueItems(payload.items);
    setReviewerNotes((current) => {
      const next = { ...current };
      for (const item of payload.items) {
        next[item.id] = current[item.id] ?? item.reviewer_note ?? '';
      }
      return next;
    });
  }

  useEffect(() => {
    if (!token) return;
    const currentToken = token;

    async function refreshPanel() {
      setIsRefreshing(true);
      setError(null);
      setQueueError(null);
      try {
        await loadSummary(currentToken);
        await loadReadiness(currentToken);
        await loadAutomationSummary(currentToken);
        await loadCommandCenter(currentToken);
        if (canReviewCorrections) {
          await loadQueue(currentToken, activeFilter);
        } else {
          setQueueItems([]);
        }
      } catch {
        setError('Unable to refresh operational totals.');
        if (canReviewCorrections) {
          setQueueError('Unable to load the public correction queue.');
        }
      } finally {
        setIsRefreshing(false);
      }
    }

    void refreshPanel();
  }, [activeFilter, browserApiBaseUrl, canReviewCorrections, token]);

  const correctionFilterCards = useMemo(
    () => [
      { key: 'submitted', label: 'Submitted', count: summary.correction_breakdown.find((item) => item.status === 'submitted')?.count ?? 0 },
      { key: 'under-review', label: 'Under review', count: summary.correction_breakdown.find((item) => item.status === 'under-review')?.count ?? 0 },
      { key: 'resolved', label: 'Resolved', count: summary.correction_breakdown.find((item) => item.status === 'resolved')?.count ?? 0 },
      { key: 'rejected', label: 'Rejected', count: summary.correction_breakdown.find((item) => item.status === 'rejected')?.count ?? 0 },
    ],
    [summary],
  );


  const riskLanes = commandCenter
    ? [
        {
          key: 'overdue-sla',
          label: 'Overdue SLA',
          count: commandCenter.risk_lanes.overdue_sla,
          route: '/field',
          scent: 'Time-sensitive records that may block ministry confidence.',
        },
        {
          key: 'publication-holds',
          label: 'Publication holds',
          count: commandCenter.risk_lanes.publication_holds,
          route: '/signage',
          scent: 'Registry-ready items intentionally held before public/signage release.',
        },
        {
          key: 'duplicate-groups',
          label: 'Duplicate groups',
          count: commandCenter.risk_lanes.duplicate_groups,
          route: '/geotag',
          scent: 'Possible repeated locations needing operator decision.',
        },
      ]
    : [];

  async function handleCorrectionAction(correctionId: string, action: 'under-review' | 'resolved' | 'rejected') {
    if (!token) return;
    setActiveActionId(correctionId);
    setQueueError(null);
    try {
      const path = action === 'under-review' ? 'under-review' : action === 'resolved' ? 'resolve' : 'reject';
      const response = await fetch(`${browserApiBaseUrl}/api/v1/address-corrections/${correctionId}/${path}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authorizationHeader(token),
        },
        body: JSON.stringify({ reviewer_note: reviewerNotes[correctionId] ?? '' }),
      });
      if (!response.ok) {
        throw new Error('status update failed');
      }
      await loadSummary(token);
      await loadQueue(token, activeFilter);
    } catch {
      setQueueError('Unable to update correction status right now.');
    } finally {
      setActiveActionId(null);
    }
  }

  const visibleQueueItems = queueItems.slice(0, 6);
  const hiddenQueueCount = Math.max(queueItems.length - visibleQueueItems.length, 0);

  return (
    <section className="section-grid territory-admin-grid">
      <article className="public-task-panel civic-panel-green territory-list-panel">
        <div className="panel-head">
          <p className="section-label">Operations desk</p>
          <h3>{commandCenter ? `${commandCenter.queues.active_operator_queue} ${localizedCountLabel(commandCenter.queues.active_operator_queue, 'active item', 'active items', locale)} · ${commandCenter.risk_lanes.overdue_sla} ${localizedCountLabel(commandCenter.risk_lanes.overdue_sla, 'overdue item', 'overdue items', locale)} · ${translateUiText('restore', locale)} ${localizedStatusLabel(commandCenter.restore_drill.status, locale)}` : translateUiText('Command center loading', locale)}</h3>
        </div>
        {commandCenter ? (
          <>
            <div className="summary-grid">
              <div className="summary-card"><strong>{commandCenter.queues.verification_queue}</strong><span>Verification queue</span></div>
              <div className="summary-card"><strong>{commandCenter.queues.field_required}</strong><span>Field checks needed</span></div>
              <div className="summary-card"><strong>{commandCenter.risk_lanes.duplicate_groups}</strong><span>Duplicate groups</span></div>
              <div className="summary-card"><strong>{commandCenter.risk_lanes.publication_holds}</strong><span>Publication holds</span></div>
              <div className="summary-card"><strong>{commandCenter.demo_fixtures.clean ? translateUiText('Clean', locale) : commandCenter.demo_fixtures.total}</strong><span>Demo fixture state</span></div>
              <div className="summary-card"><strong>{localizedStatusLabel(commandCenter.restore_drill.status, locale)}</strong><span>Restore drill</span></div>
            </div>
            <div className="data-command-deck" aria-label="Operator risk lane command deck">
              {riskLanes.map((lane) => (
                <a className="case-lane warn" href={lane.route} key={lane.key}>
                  <span>{lane.label}</span>
                  <strong>{lane.count}</strong>
                  <small>{lane.scent}</small>
                </a>
              ))}
            </div>
            <details className="disclosure-panel">
              <summary>Ministry walkthrough and continuity proof</summary>
              <ol className="mini-list">
                {commandCenter.walkthrough.map((step) => (
                  <li key={step.step}>
                    <strong>{step.step}. {step.title}</strong>
                    <span>{step.operator_message} · <a className="inline-link" href={step.route} aria-label={`Open ministry walkthrough route ${step.route}`}>Open {step.route}</a></span>
                  </li>
                ))}
              </ol>
              <div className="institutional-note">
                <p>{commandCenter.restore_drill.operator_note ?? 'Restore drill proof is not available yet.'}</p>
                {commandCenter.restore_drill.backup_sha256 ? <p>Backup SHA256: <code>{commandCenter.restore_drill.backup_sha256}</code></p> : null}
              </div>
              {commandCenter.demo_fixtures.clean ? (
                <p className="form-notice success">Demo fixture reset state is clean.</p>
              ) : (
                <div className="territory-form-actions">
                  <button className="verification-button" type="button" disabled={sessionUser?.role !== 'admin' || isRefreshing} onClick={() => void cleanupDemoFixtures()}>
                    {sessionUser?.role !== 'admin' ? 'Admin required to clean fixtures' : 'Clean smoke/demo fixtures'}
                  </button>
                </div>
              )}
            </details>
          </>
        ) : (
          <p className="panel-state">Sign in to load the consolidated operator command center.</p>
        )}
      </article>

      <article className="public-task-panel civic-panel-blue territory-list-panel">
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
            <span>Verification queue</span>
          </div>
          <div className="summary-card">
            <strong>{summary.totals.public_corrections}</strong>
            <span>Public correction reports</span>
          </div>
          <div className="summary-card">
            <strong>{summary.totals.correction_queue}</strong>
            <span>Correction queue awaiting action</span>
          </div>
          <div className="summary-card">
            <strong>{summary.totals.published_addresses}</strong>
            <span>Published addresses</span>
          </div>
          <div className="summary-card">
            <strong>{summary.totals.import_jobs}</strong>
            <span>Intake jobs</span>
          </div>
          <div className="summary-card">
            <strong>{summary.totals.citizen_geotags ?? 0}</strong>
            <span>Citizen geotags captured</span>
          </div>
          <div className="summary-card">
            <strong>{summary.totals.geotag_queue ?? 0}</strong>
            <span>Geotag queue awaiting review</span>
          </div>
        </div>
        {error ? <p className="form-notice error">{error}</p> : null}
      </article>

      <article className="public-task-panel civic-panel-blue">
        <div className="panel-head">
          <p className="section-label">Automation support</p>
          <h3>{automationSummary ? `${automationSummary.active_queue} active · score ${automationSummary.average_quality_score}/100` : 'Automation summary unavailable'}</h3>
        </div>
        {automationSummary ? (
          <details className="disclosure-panel">
            <summary>View automation details</summary>
            <div className="summary-grid">
              <div className="summary-card"><strong>{automationSummary.field_required}</strong><span>Need field verification</span></div>
              <div className="summary-card"><strong>{automationSummary.signage_ready}</strong><span>{translateUiText('Ready for signage/export', locale)}</span></div>
              <div className="summary-card"><strong>{automationSummary.partner_api_ready}</strong><span>Public/API-ready records</span></div>
            </div>
            <ul className="program-list">
              {automationSummary.triage_buckets.map((row) => (
                <li key={row.bucket}><span>{localizedAutomationLabel(row.bucket, locale)}</span><span>{row.count}</span></li>
              ))}
            </ul>
          </details>
        ) : (
          <p className="panel-state">Sign in and refresh once the API is reachable to load automation totals.</p>
        )}
      </article>

      <article className="public-task-panel civic-panel-green">
        <div className="panel-head">
          <p className="section-label">Operational readiness</p>
          <h3>{readiness ? `${readiness.passed_gates}/${readiness.total_gates} gates · ${readiness.readiness_status}` : 'Readiness gates unavailable'}</h3>
        </div>
        {readiness ? (
          <details className="disclosure-panel">
            <summary>Show readiness gates</summary>
            <ul className="mini-list">
              {readiness.gates.map((gate) => (
                <li key={gate.name}>
                  <details className="inline-disclosure">
                    <summary>
                      <strong>{translateUiText(gate.name, locale)}</strong>
                      <span>{translateUiText(gate.status, locale)}</span>
                    </summary>
                    <p>{translateUiText(gate.evidence, locale)}</p>
                    <p>{translateUiText('Next:', locale)} {translateUiText(gate.next_step, locale)}</p>
                  </details>
                </li>
              ))}
            </ul>
            <div className="institutional-note">
              {readiness.boundaries.map((boundary) => (
                <p key={boundary}>{boundary}</p>
              ))}
            </div>
          </details>
        ) : (
          <p className="panel-state">Sign in and refresh once the API is reachable to load readiness gates.</p>
        )}
      </article>

      <article className="public-task-panel civic-panel-gold">
        <div className="panel-head">
          <p className="section-label">Territory spread</p>
          <h3>Territories by province</h3>
        </div>
        <details className="disclosure-panel">
          <summary>Show territory spread</summary>
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
        </details>
      </article>

      <article className="public-task-panel civic-panel-green">
        <div className="panel-head">
          <p className="section-label">Review state</p>
          <h3>Verification queue breakdown</h3>
        </div>
        <details className="disclosure-panel">
          <summary>Show verification breakdown</summary>
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
        </details>
      </article>

      <article className="public-task-panel civic-panel-blue">
        <div className="panel-head">
          <p className="section-label">Publication state</p>
          <h3>Official output breakdown</h3>
        </div>
        <details className="disclosure-panel">
          <summary>Show publication breakdown</summary>
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
        </details>
      </article>

      {canReviewCorrections ? (
        <article className="public-task-panel civic-panel-gold issuance-panel">
          <div className="panel-head">
            <div>
              <p className="section-label">Public correction queue</p>
              <h3>Review citizen-reported address corrections</h3>
            </div>
            <p className="panel-copy">Work newest reports first, capture the reviewer note, and move each record into a clear operator state.</p>
          </div>

          <div className="summary-grid">
            {correctionFilterCards.map((card) => (
              <button
                key={card.key}
                type="button"
                className={`selection-item${activeFilter === card.key ? ' active' : ''}`}
                aria-label={`Show correction queue filter ${card.label}`}
                onClick={() => setActiveFilter(card.key as typeof activeFilter)}
              >
                <strong>{card.label}</strong>
                <span>{card.count} reports</span>
              </button>
            ))}
          </div>

          {queueError ? <p className="form-notice error">{queueError}</p> : null}

          {queueItems.length > 0 ? (
            <div className="review-list">
              {visibleQueueItems.map((item) => {
                const busy = activeActionId === item.id;
                return (
                  <article className="review-card" key={item.id}>
                    <div className="review-head">
                      <div>
                        <h3>{item.public_code ?? item.query}</h3>
                        <span>{item.address_label ?? 'No direct address match linked yet'}</span>
                      </div>
                      <strong>{formatStatus(item.status)}</strong>
                    </div>
                    <div className="review-meta">
                      <span>{item.jurisdiction ?? 'Jurisdiction pending'}</span>
                      <span>Filed {formatDateTime(item.created_at)}</span>
                      <span>{item.correction_type}</span>
                    </div>
                    <details className="inline-disclosure">
                      <summary>Correction details and reviewer note</summary>
                    <dl className="detail-grid">
                      <div>
                        <dt>Reason</dt>
                        <dd>{item.reason}</dd>
                      </div>
                      <div>
                        <dt>Reporter</dt>
                        <dd>{item.reporter_name ?? 'Anonymous / not supplied'}</dd>
                      </div>
                      <div>
                        <dt>Contact</dt>
                        <dd>{item.reporter_contact ?? 'Not supplied'}</dd>
                      </div>
                    </dl>
                    {item.note ? (
                      <div className="panel-state">
                        <strong>Citizen note</strong>
                        <span>{item.note}</span>
                      </div>
                    ) : null}
                    <label className="form-field" htmlFor={`reviewer-note-${item.id}`}>
                      <span>Reviewer note</span>
                      <textarea
                        id={`reviewer-note-${item.id}`}
                        className="territory-textarea"
                        value={reviewerNotes[item.id] ?? ''}
                        onChange={(event) =>
                          setReviewerNotes((current) => ({
                            ...current,
                            [item.id]: event.target.value,
                          }))
                        }
                        placeholder="Record what was checked, what changed, or why the report was rejected."
                      />
                    </label>
                    </details>
                    <div className="button-row">
                      <button type="button" className="mini-action-button" disabled={Boolean(correctionDisabledReason(item, 'under-review'))} onClick={() => void handleCorrectionAction(item.id, 'under-review')}>
                        {correctionDisabledReason(item, 'under-review') ?? 'Mark under review'}
                      </button>
                      <button type="button" className="mini-action-button" disabled={Boolean(correctionDisabledReason(item, 'resolved'))} onClick={() => void handleCorrectionAction(item.id, 'resolved')}>
                        {correctionDisabledReason(item, 'resolved') ?? 'Resolve'}
                      </button>
                      <button type="button" className="mini-action-button" disabled={Boolean(correctionDisabledReason(item, 'rejected'))} onClick={() => void handleCorrectionAction(item.id, 'rejected')}>
                        {correctionDisabledReason(item, 'rejected') ?? 'Reject'}
                      </button>
                    </div>
                  </article>
                );
              })}
              {hiddenQueueCount > 0 ? (
                <p className="panel-state queue-limit-note">Showing the newest {visibleQueueItems.length} reports. {hiddenQueueCount} older reports remain available through the active queue filter.</p>
              ) : null}
            </div>
          ) : (
            <p className="panel-state">No correction reports in the {formatStatus(activeFilter).toLowerCase()} queue right now.</p>
          )}
        </article>
      ) : null}
    </section>
  );
}
