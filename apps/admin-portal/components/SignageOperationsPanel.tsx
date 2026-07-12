'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';

import { useTranslation, translateUiText } from './i18n';
import { authorizationHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

type QualityFlags = {
  accuracy_level: 'high-accuracy' | 'needs-confirmation' | 'weak-gps' | 'unknown';
  accuracy_label: string;
  requires_field_check: boolean;
  duplicate_code: boolean;
  possible_duplicate: boolean;
  recommended_action: string;
};

type DuplicateGroup = {
  count: number;
  items: Array<{ id: string; address_label: string; status: string }>;
};

type GeotagSubmission = {
  id: string;
  territory_id?: string | null;
  territory_name?: string | null;
  address_label: string;
  citizen_name?: string | null;
  citizen_contact?: string | null;
  dip_last4?: string | null;
  dip_masked?: string | null;
  identity_verification_status?: string | null;
  identity_document_verified?: boolean | null;
  identity_verified_at?: string | null;
  landmark: string;
  latitude: number;
  longitude: number;
  accuracy_meters?: number | null;
  capture_method: string;
  grid_code: string;
  status: string;
  duplicate_hint: string;
  duplicate_group?: DuplicateGroup;
  quality_flags?: QualityFlags;
  reviewer_note: string;
  field_submission_id?: string | null;
  signage_batch?: string | null;
  public_lookup_url?: string;
  suggested_road_name?: string | null;
  suggested_local_area?: string | null;
  suggested_place_name?: string | null;
  map_display_name?: string | null;
  road_suggestion_source?: string | null;
  road_suggestion_attribution?: string | null;
  road_suggestion_status?: string | null;
  reviewed_road_name?: string | null;
  automation?: {
    quality_score: number;
    triage_bucket: string;
    process_stage: string;
    next_best_action: string;
    next_best_action_label: string;
    reasons: string[];
    routing?: {
      assigned: boolean;
      territory_id?: string | null;
      territory_name?: string | null;
      assignment_source?: string | null;
      assignment_confidence?: string | null;
    };
    field_work?: { required: boolean; status: string; field_submission_id?: string | null };
    signage?: { ready: boolean; batch?: string | null; export_status: string };
    integration?: { api_record_state: string; partner_api_ready: boolean };
    corrections?: { watch_public_reports: boolean; recommended_queue: string };
  };
};

type ReviewHistoryItem = {
  actor_username?: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  details?: { reviewer_note?: string; field_submission_id?: string | null; [key: string]: unknown } | null;
  created_at?: string | null;
};

type SignageRow = {
  grid_code: string;
  signage_text: string;
  address_label: string;
  territory_name?: string | null;
  latitude: number;
  longitude: number;
  accuracy_meters?: number | null;
  batch?: string | null;
  status: string;
};

type DuplicateSummaryGroup = {
  grid_code: string;
  count: number;
  active_count: number;
  resolved_count: number;
  items: Array<{ id: string; address_label: string; status: string; territory_name?: string | null; field_status?: string | null }>;
};

type SlaItem = {
  id: string;
  type: string;
  label: string;
  status: string;
  age_hours?: number | null;
  due_hours: number;
  state: 'on_time' | 'approaching' | 'overdue' | 'unknown';
};

type AutomationSummary = {
  sla?: {
    items_tracked: number;
    on_time: number;
    approaching: number;
    overdue: number;
    unknown: number;
    oldest_overdue?: SlaItem | null;
    items?: SlaItem[];
  };
  publication_hold?: {
    registry_ready: number;
    public_release_locked: boolean;
    oldest_days: number;
    oldest_hours: number;
    note: string;
  };
};

type CertificateResult = {
  certificate_id: string;
  address_code: string;
  address_label: string;
  status: string;
  qr_payload: string;
  html: string;
};

type SignageOperationsPanelProps = {
  apiBaseUrl: string;
};

const FIELD_REASONS = [
  { label: 'Verify coordinates', note: 'Field check required: GPS accuracy needs confirmation.' },
  { label: 'Check possible same address', note: 'Field check required: possible duplicate or same location cell.' },
  { label: 'Supervisor review', note: 'Field check required: operator requested supervisor verification.' },
];

const DUPLICATE_ACTIONS = [
  { action: 'same-property-merge', label: 'Same address', note: 'Same address suspected. Merge or consolidate during registry review.' },
  { action: 'different-property-same-cell', label: 'Different address, same cell', note: 'Different address may share the same 5m address-code cell. Preserve for field verification.' },
  { action: 'gps-error-recapture', label: 'Request recapture', note: 'GPS error suspected. Request recapture or field coordinate confirmation.' },
  { action: 'send-field-verification', label: 'Send to field', note: 'Possible same address needs field verification before approval/signage.' },
] as const;

function qualityClass(flags?: QualityFlags) {
  if (!flags) return 'warn';
  if (flags.accuracy_level === 'high-accuracy' && !flags.possible_duplicate) return 'ok';
  if (flags.accuracy_level === 'weak-gps' || flags.possible_duplicate) return 'danger';
  return 'warn';
}

function qualityLabel(flags?: QualityFlags) {
  if (!flags) return 'Quality pending';
  if (flags.accuracy_level === 'weak-gps') return 'Location needs confirmation';
  if (flags.possible_duplicate) return 'Possible same address';
  return flags.accuracy_label;
}

function mapPreviewUrl(submission: GeotagSubmission) {
  const delta = 0.0025;
  const west = submission.longitude - delta;
  const east = submission.longitude + delta;
  const south = submission.latitude - delta;
  const north = submission.latitude + delta;
  return `https://www.openstreetmap.org/export/embed.html?bbox=${west}%2C${south}%2C${east}%2C${north}&layer=mapnik&marker=${submission.latitude}%2C${submission.longitude}`;
}

function googleMapsUrl(submission: GeotagSubmission) {
  return `https://www.google.com/maps/search/?api=1&query=${submission.latitude},${submission.longitude}`;
}

function statusLabel(status: string) {
  return status.replaceAll('-', ' ').replaceAll('_', ' ');
}

function slaChipClass(state?: string) {
  if (state === 'overdue') return 'danger';
  if (state === 'approaching') return 'warn';
  if (state === 'on_time') return 'ok';
  return 'warn';
}

function hoursToHuman(hours?: number | null) {
  if (hours == null) return 'age unknown';
  if (hours >= 48) return `${Math.round(hours / 24)}d`;
  return `${Math.round(hours)}h`;
}

export function SignageOperationsPanel({ apiBaseUrl }: SignageOperationsPanelProps) {
  const { t, locale } = useTranslation();
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [submissions, setSubmissions] = useState<GeotagSubmission[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [reviewHistory, setReviewHistory] = useState<ReviewHistoryItem[]>([]);
  const [duplicateGroups, setDuplicateGroups] = useState<DuplicateSummaryGroup[]>([]);
  const [automationSummary, setAutomationSummary] = useState<AutomationSummary | null>(null);
  const [exportRows, setExportRows] = useState<SignageRow[]>([]);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isWorking, setIsWorking] = useState(false);
  const [roadNameReview, setRoadNameReview] = useState('');
  const [dipFull, setDipFull] = useState('');

  const canWrite = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';
  const selectedSubmission = useMemo(
    () => submissions.find((item) => item.id === selectedId) ?? submissions[0] ?? null,
    [selectedId, submissions],
  );
  const recommendedAction = selectedSubmission?.automation?.next_best_action ?? null;
  const approvalBlockedReason = selectedSubmission?.quality_flags?.requires_field_check
    ? 'Approval is blocked until field verification confirms the point.'
    : selectedSubmission?.quality_flags?.possible_duplicate
      ? 'Approval is blocked until the possible duplicate is resolved.'
      : null;
  const isRecommendedAction = (action: string) => recommendedAction === action;
  const statusCounts = useMemo(() => submissions.reduce<Record<string, number>>((acc, item) => {
    acc[item.status] = (acc[item.status] ?? 0) + 1;
    return acc;
  }, {}), [submissions]);
  const activeReviewCount = useMemo(() => submissions.filter((item) => ['submitted', 'under-review', 'needs-field-check'].includes(item.status)).length, [submissions]);
  const terminalReviewCount = useMemo(() => submissions.length - activeReviewCount, [activeReviewCount, submissions]);
  const queueLanes = useMemo(() => {
    const laneLabels: Record<string, string> = {
      'field-verification': 'Field verification',
      'operator-road-review': 'Road/local-area review',
      'ready-for-operator': 'Operator decision',
      'registry-ready': 'Registry-ready hold',
      'closed-rejected': 'Closed/rejected',
    };
    const laneOrder = ['field-verification', 'operator-road-review', 'ready-for-operator', 'registry-ready', 'closed-rejected'];
    const counts = submissions.reduce<Record<string, number>>((acc, item) => {
      const lane = item.automation?.triage_bucket ?? 'ready-for-operator';
      acc[lane] = (acc[lane] ?? 0) + 1;
      return acc;
    }, {});
    return laneOrder
      .filter((lane) => counts[lane])
      .map((lane) => ({ lane, label: laneLabels[lane] ?? statusLabel(lane), count: counts[lane] }));
  }, [submissions]);
  const csvExport = useMemo(() => {
    const header = ['grid_code', 'signage_text', 'address_label', 'territory_name', 'latitude', 'longitude', 'accuracy_meters', 'batch', 'status'];
    const rows = exportRows.map((row) => header.map((key) => JSON.stringify((row as unknown as Record<string, unknown>)[key] ?? '')).join(','));
    return [header.join(','), ...rows].join('\n');
  }, [exportRows]);

  useEffect(() => {
    if (!token) return;
    void reload(token);
  }, [token]);

  useEffect(() => {
    if (!token || !selectedSubmission) {
      setReviewHistory([]);
      return;
    }
    void loadReviewHistory(token, selectedSubmission.id);
  }, [token, selectedSubmission?.id]);

  useEffect(() => {
    setRoadNameReview(selectedSubmission?.reviewed_road_name || selectedSubmission?.suggested_road_name || '');
  }, [selectedSubmission?.id, selectedSubmission?.reviewed_road_name, selectedSubmission?.suggested_road_name]);

  useEffect(() => {
    setDipFull('');
  }, [selectedSubmission?.id]);

  async function loadReviewHistory(activeToken: string, submissionId: string) {
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/${submissionId}/history`, {
        headers: authorizationHeader(activeToken),
      });
      if (!response.ok) {
        setReviewHistory([]);
        return;
      }
      const payload = (await response.json()) as { items: ReviewHistoryItem[] };
      setReviewHistory(payload.items ?? []);
    } catch {
      setReviewHistory([]);
    }
  }

  async function reload(activeToken: string) {
    setError(null);
    const [submissionsResponse, exportResponse, duplicateResponse, automationResponse] = await Promise.all([
      fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions`, { headers: authorizationHeader(activeToken) }),
      fetch(`${browserApiBaseUrl}/api/v1/signage/export`, { headers: authorizationHeader(activeToken) }),
      fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/duplicates/summary`, { headers: authorizationHeader(activeToken) }),
      fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/automation/summary`, { headers: authorizationHeader(activeToken) }),
    ]);
    if (!submissionsResponse.ok || !exportResponse.ok || !duplicateResponse.ok || !automationResponse.ok) {
      setError('Unable to refresh the review desk.');
      return;
    }
    const submissionsPayload = (await submissionsResponse.json()) as { items: GeotagSubmission[] };
    const exportPayload = (await exportResponse.json()) as { items: SignageRow[] };
    const duplicatePayload = (await duplicateResponse.json()) as { groups: DuplicateSummaryGroup[] };
    const automationPayload = (await automationResponse.json()) as AutomationSummary;
    const nextSubmissions = submissionsPayload.items ?? [];
    setSubmissions(nextSubmissions);
    setExportRows(exportPayload.items ?? []);
    setDuplicateGroups(duplicatePayload.groups ?? []);
    setAutomationSummary(automationPayload);
    setSelectedId((current) => current && nextSubmissions.some((item) => item.id === current) ? current : nextSubmissions[0]?.id ?? null);
  }

  async function updateStatus(submissionId: string, action: 'under-review' | 'field-check' | 'registry-ready' | 'reject', reviewer_note?: string) {
    if (!token || !canWrite) {
      setError('Sign in as editor or admin before reviewing location requests.');
      return;
    }
    setIsWorking(true);
    setNotice(null);
    setError(null);
    const defaultNote = action === 'registry-ready'
      ? 'Verified as an official registry case file. Physical signage is locked until full project approval.'
      : action === 'field-check'
        ? 'Sent to field team for confirmation.'
        : action === 'reject'
          ? 'Rejected during operator review.'
          : 'Operator review started.';
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/${submissionId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token) },
        body: JSON.stringify({ reviewer_note: reviewer_note ?? defaultNote }),
      });
      const payload = (await response.json()) as GeotagSubmission | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to update this request.');
        return;
      }
      setNotice(`Location request updated: ${'status' in payload ? statusLabel(payload.status) : statusLabel(action)}.`);
      await reload(token);
      await loadReviewHistory(token, submissionId);
    } catch {
      setError('Unable to update this request.');
    } finally {
      setIsWorking(false);
    }
  }

  async function recordDuplicateDecision(submissionId: string, duplicate_action: string, reviewer_note: string) {
    if (!token || !canWrite) {
      setError('Sign in as editor or admin before reviewing possible same-address records.');
      return;
    }
    setIsWorking(true);
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/${submissionId}/duplicate-decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token) },
        body: JSON.stringify({ duplicate_action, reviewer_note }),
      });
      const payload = (await response.json()) as GeotagSubmission | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to record this decision.');
        return;
      }
      setNotice('Possible same-address decision recorded.');
      await reload(token);
      await loadReviewHistory(token, submissionId);
    } catch {
      setError('Unable to record this decision.');
    } finally {
      setIsWorking(false);
    }
  }

  async function verifyIdentity(submissionId: string) {
    if (!token || !canWrite) {
      setError('Sign in as editor or admin before confirming identity.');
      return;
    }
    const normalizedDip = dipFull.trim();
    if (!/^\d{6,20}$/.test(normalizedDip)) {
      setError('Enter the full D.I.P. as 6 to 20 digits for operator verification. It will not be stored in full.');
      return;
    }
    setIsWorking(true);
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/${submissionId}/identity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token) },
        body: JSON.stringify({
          dip_full: normalizedDip,
          identity_document_verified: true,
          reviewer_note: 'D.I.P. confirmed by authorized operator. Full number was not stored.',
        }),
      });
      const payload = (await response.json()) as GeotagSubmission | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to confirm identity.');
        return;
      }
      setDipFull('');
      setNotice('Identity confirmed. Only masked D.I.P. metadata is retained.');
      await reload(token);
      await loadReviewHistory(token, submissionId);
    } catch {
      setError('Unable to confirm identity.');
    } finally {
      setIsWorking(false);
    }
  }

  async function reviewRoadSuggestion(submissionId: string, action: 'accepted' | 'edited' | 'rejected') {
    if (!token || !canWrite) {
      setError('Sign in as editor or admin before reviewing road-name suggestions.');
      return;
    }
    if (action !== 'rejected' && !roadNameReview.trim()) {
      setError('Enter the road name to accept or edit the suggestion.');
      return;
    }
    setIsWorking(true);
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/${submissionId}/road-suggestion`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token) },
        body: JSON.stringify({
          action,
          reviewed_road_name: action === 'rejected' ? null : roadNameReview.trim(),
          reviewer_note: action === 'rejected' ? 'Rejected map-derived road name during operator review.' : 'Road name reviewed by operator.',
        }),
      });
      const payload = (await response.json()) as GeotagSubmission | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to review this road-name suggestion.');
        return;
      }
      setNotice(`Road-name suggestion ${action}.`);
      await reload(token);
      await loadReviewHistory(token, submissionId);
    } catch {
      setError('Unable to review this road-name suggestion.');
    } finally {
      setIsWorking(false);
    }
  }

  function openCertificateWindow(certificate: CertificateResult) {
    const blob = new Blob([certificate.html], { type: 'text/html;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const certificateWindow = window.open(url, '_blank', 'noopener,noreferrer');
    if (!certificateWindow) {
      window.URL.revokeObjectURL(url);
      setError('Popup blocked. Allow popups to open the certificate.');
      return;
    }
    window.setTimeout(() => window.URL.revokeObjectURL(url), 30_000);
  }

  async function openCertificate(submissionId: string) {
    if (!token) {
      setError('Sign in before opening certificates.');
      return;
    }
    setIsWorking(true);
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/${submissionId}/certificate`, {
        headers: authorizationHeader(token),
      });
      const payload = (await response.json()) as CertificateResult | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to generate certificate.');
        return;
      }
      openCertificateWindow(payload as CertificateResult);
      setNotice('Official certificate opened. Use browser print to save as PDF.');
    } catch {
      setError('Unable to generate certificate.');
    } finally {
      setIsWorking(false);
    }
  }

  function downloadCsv() {
    const blob = new Blob([csvExport], { type: 'text/csv;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'published-signage-location-export.csv';
    link.click();
    window.URL.revokeObjectURL(url);
  }

  async function downloadSignagePack() {
    if (!token) {
      setError('Sign in before generating a signage pack.');
      return;
    }
    setError(null);
    setNotice(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/signage/pack`, { headers: authorizationHeader(token) });
      const payload = await response.json();
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to generate signage pack.');
        return;
      }
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${payload.batch_id || 'signage-pack'}.json`;
      link.click();
      window.URL.revokeObjectURL(url);
      setNotice(`Physical signage pack generated with ${payload.record_count ?? 0} published records.`);
    } catch {
      setError('Unable to generate signage pack right now.');
    }
  }

  return (
    <section className="operator-review-shell">
      <article className="review-desk-header public-task-panel">
        <div>
          <p className="section-label">{t('reviewDesk')}</p>
          <h3>{t('locationRequests')}</h3>
          <p className="public-task-copy">{t('locationRequestsCopy')}</p>
        </div>
        <div className="operator-summary-row" aria-label="Location request status summary">
          <span className="status-chip warn">{t('activeReview')}: {activeReviewCount}</span>
          <span className="status-chip">{t('historyClosed')}: {terminalReviewCount}</span>
        </div>
        {sessionUser?.role === 'admin' ? (
          <div className="registry-secondary-action signage-secondary-action" aria-label="Publication operations handoff">
            <span>Admin-only intake and publication packs stay under publication operations, not staff navigation.</span>
            <Link href="/exports">Open publication operations</Link>
          </div>
        ) : null}
      </article>

      <article className="public-task-panel review-glance-panel">
        <div className="review-glance-head">
          <div>
            <p className="section-label">Attention needed</p>
            <h3>Open issues blocking release</h3>
          </div>
          <div className="operator-summary-row review-glance-chips" aria-label="Location review operation summary">
            <span className="status-chip warn">Overdue: {automationSummary?.sla?.overdue ?? 0}</span>
            <span className="status-chip">Approaching: {automationSummary?.sla?.approaching ?? 0}</span>
            <span className="status-chip warn">Internal hold: {automationSummary?.publication_hold?.registry_ready ?? 0}</span>
            <span className="status-chip">Duplicates: {duplicateGroups.length}</span>
            <span className="status-chip danger">Public release locked</span>
          </div>
        </div>
        <div className="release-status-panel" role="status" aria-label="Public release status">
          <strong>Public release locked</strong>
          <span>Clear {automationSummary?.sla?.overdue ?? 0} overdue reviews before publishing.</span>
        </div>
        <div className="table-wrap desktop-table-wrap blocked-items-table-wrap" aria-label="Blocked items table">
          <table className="data-table desktop-data-table">
            <caption>Blocked items</caption>
            <thead><tr><th scope="col">Location</th><th scope="col">Blocker</th><th scope="col">Owner</th><th scope="col">Action</th></tr></thead>
            <tbody>
              {submissions.slice(0, 6).map((submission) => (
                <tr key={submission.id}>
                  <td><strong>{submission.address_label}</strong></td>
                  <td>{qualityLabel(submission.quality_flags)}</td>
                  <td>{submission.territory_name || 'Registry'}</td>
                  <td><button className="table-action" type="button" onClick={() => setSelectedId(submission.id)}>Open</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <details className="quiet-disclosure compact-review-disclosure">
          <summary>View queue details</summary>
          <div className="compact-review-grid">
            <section>
              <strong>Queue lanes</strong>
              <div className="operator-summary-row" aria-label="Queue status">
                {queueLanes.length ? queueLanes.map((lane) => (
                  <span className="status-chip" key={lane.lane}>{lane.label}: {lane.count}</span>
                )) : <span className="status-chip warn">No queue lanes active</span>}
              </div>
            </section>
            <section>
              <strong>SLA aging</strong>
              <div className="operator-summary-row" aria-label="SLA aging summary">
                <span className="status-chip ok">On time: {automationSummary?.sla?.on_time ?? 0}</span>
                <span className="status-chip warn">Approaching: {automationSummary?.sla?.approaching ?? 0}</span>
                <span className="status-chip danger">Overdue: {automationSummary?.sla?.overdue ?? 0}</span>
              </div>
              {automationSummary?.sla?.items?.length ? (
                <ul className="mini-list duplicate-summary-list">
                  {automationSummary.sla.items.slice(0, 3).map((item) => (
                    <li key={`${item.type}-${item.id}`}>
                      <strong>{item.label}</strong>
                      <span>{item.type} · {statusLabel(item.status)} · {hoursToHuman(item.age_hours)} / {hoursToHuman(item.due_hours)} · {statusLabel(item.state)}</span>
                    </li>
                  ))}
                </ul>
              ) : <p className="panel-state">No active SLA items are waiting.</p>}
            </section>
            <section>
              <strong>Publication hold</strong>
              <p className="institutional-note">Registry-ready records stay internal. Public release, certificates, partner API readiness, and physical signage remain locked until full approval.</p>
              <div className="operator-summary-row" aria-label="Publication hold summary">
                <span className="status-chip warn">Registry-ready hold: {automationSummary?.publication_hold?.registry_ready ?? 0}</span>
                <span className="status-chip">Oldest hold: {automationSummary?.publication_hold?.oldest_days ?? 0}d</span>
              </div>
            </section>
            <section>
              <strong>Duplicate / household matching</strong>
              {duplicateGroups.length ? (
                <ul className="mini-list duplicate-summary-list">
                  {duplicateGroups.slice(0, 3).map((group) => (
                    <li key={group.grid_code}>
                      <details className="inline-disclosure">
                        <summary>
                          <strong>{group.grid_code}</strong>
                          <span>{group.active_count} active · {group.resolved_count} resolved · {group.count} total</span>
                        </summary>
                        <ul>
                          {group.items.map((item) => (
                            <li key={item.id}>{item.address_label} · {statusLabel(item.status)}{item.field_status ? ` · field ${statusLabel(item.field_status)}` : ''}</li>
                          ))}
                        </ul>
                      </details>
                    </li>
                  ))}
                </ul>
              ) : <p className="panel-state">No same-code groups are currently waiting for duplicate review.</p>}
            </section>
          </div>
        </details>
      </article>

      <section className="operator-review-desk" aria-label="Location request review desk">
        <aside className="request-list-panel" aria-label="Location requests">
          <div className="panel-head quiet-head">
            <p className="section-label">{t('queue')}</p>
            <h3>{submissions.length} requests</h3>
          </div>
          {sessionStatus === 'loading' ? <p className="panel-state">Checking operator access…</p> : null}
          {submissions.length ? (
            <div className="request-list" role="list">
              {submissions.map((submission) => {
                const isSelected = selectedSubmission?.id === submission.id;
                const duplicateCount = submission.duplicate_group?.count ?? 1;
                return (
                  <button
                    className={`request-list-item ${isSelected ? 'active' : ''}`}
                    key={submission.id}
                    type="button"
                    onClick={() => setSelectedId(submission.id)}
                    aria-current={isSelected ? 'true' : undefined}
                  >
                    <span className="request-list-title">{submission.address_label}</span>
                    <span>{submission.suggested_local_area || submission.suggested_place_name || submission.territory_name || 'Area pending'} · {submission.automation?.process_stage ?? statusLabel(submission.status)}</span>
                    <span className={`status-chip ${qualityClass(submission.quality_flags)}`}>{qualityLabel(submission.quality_flags)}</span>
                    {submission.automation ? <span className="status-chip warn">{translateUiText(`Next: ${submission.automation.next_best_action.replaceAll('-', ' ')}`, locale)}</span> : null}
                    {duplicateCount > 1 ? <span className="status-chip danger">{t('possibleSameAddress')}</span> : null}
                  </button>
                );
              })}
            </div>
          ) : (
            <p className="panel-state">No location requests have been recorded yet.</p>
          )}
        </aside>

        <article className="request-detail-panel">
          {selectedSubmission ? (
            <>
              <div className="request-detail-head">
                <div>
                  <p className="section-label">{t('selectedRequest')}</p>
                  <h3>{selectedSubmission.address_label}</h3>
                  <p>{selectedSubmission.grid_code}</p>
                </div>
                <span className="status-chip">{statusLabel(selectedSubmission.status)}</span>
              </div>
              <div className="request-detail-grid">
                <div className="operator-finding-card">
                  <span className={`status-chip ${qualityClass(selectedSubmission.quality_flags)}`}>{qualityLabel(selectedSubmission.quality_flags)}</span>
                  <p>{selectedSubmission.latitude}, {selectedSubmission.longitude}</p>
                  <p>Accuracy: {selectedSubmission.accuracy_meters ?? 'not recorded'}m · Source: {selectedSubmission.capture_method.replaceAll('-', ' ')}</p>
                  <p>Map local area: {selectedSubmission.suggested_local_area || selectedSubmission.suggested_place_name || 'not found'}</p>
                  <p>Official routing area: {selectedSubmission.territory_name || 'not selected'}</p>
                  {selectedSubmission.automation?.routing?.assigned ? (
                    <p className="institutional-note">Routing assigned: {selectedSubmission.automation.routing.territory_name} · {selectedSubmission.automation.routing.assignment_source?.replaceAll('-', ' ') ?? 'operator-confirmed'} · {selectedSubmission.automation.routing.assignment_confidence ?? 'confirmed'}</p>
                  ) : null}
                  <p>{selectedSubmission.landmark || 'No landmark supplied.'}</p>
                </div>
                {selectedSubmission.automation ? (
                  <div className="operator-finding-card">
                    <strong>Automation check</strong>
                    <span className="status-chip warn">Score {selectedSubmission.automation.quality_score}/100 · {selectedSubmission.automation.triage_bucket.replaceAll('-', ' ')}</span>
                    <p>{translateUiText(selectedSubmission.automation.next_best_action_label, locale)}</p>
                    <ul>
                      {selectedSubmission.automation.reasons.slice(0, 4).map((reason) => <li key={reason}>{reason}</li>)}
                    </ul>
                    <p>Field: {selectedSubmission.automation.field_work?.required ? 'required' : 'not required'} · Physical signage: {selectedSubmission.automation.signage?.export_status ?? 'locked'} · API: {selectedSubmission.automation.integration?.api_record_state ?? 'not-public'}</p>
                  </div>
                ) : null}
                <div className="operator-finding-card identity-review-card">
                  <strong>{t('citizenIdentity')}</strong>
                  <p>{selectedSubmission.citizen_name || 'No name supplied'} · {selectedSubmission.citizen_contact || 'No contact supplied'}</p>
                  <p>D.I.P.: {selectedSubmission.dip_masked || (selectedSubmission.dip_last4 ? `****${selectedSubmission.dip_last4}` : 'not provided')}</p>
                  <span className={`status-chip ${selectedSubmission.identity_document_verified ? 'ok' : 'warn'}`}>{statusLabel(selectedSubmission.identity_verification_status || 'unverified')}</span>
                  <label className="territory-field territory-field-wide">
                    <span className="territory-label">{t('fullDipForOperator')}</span>
                    <input className="territory-input" inputMode="numeric" value={dipFull} onChange={(event) => setDipFull(event.target.value.replace(/\D/g, '').slice(0, 20))} placeholder="Verified by authorized reviewer only" />
                    <span className="field-help">{t('fullDipHelp')}</span>
                  </label>
                  <div className="calm-action-row">
                    <button className="secondary-action" type="button" disabled={isWorking || !canWrite} onClick={() => void verifyIdentity(selectedSubmission.id)}>{t('confirmIdentity')}</button>
                  </div>
                </div>
                <div className="operator-finding-card">
                  <strong>{t('possibleSameAddress')}</strong>
                  <p>{(selectedSubmission.duplicate_group?.count ?? 1) > 1 ? `${selectedSubmission.duplicate_group?.count} requests share this address code.` : 'No other request shares this address code.'}</p>
                  <ul>
                    {(selectedSubmission.duplicate_group?.items ?? []).map((item) => (
                      <li key={item.id}>{item.address_label} · {statusLabel(item.status)}</li>
                    ))}
                  </ul>
                </div>
                <div className="operator-finding-card road-suggestion-card">
                  <strong>Map-derived location suggestions</strong>
                  {selectedSubmission.suggested_road_name || selectedSubmission.suggested_local_area || selectedSubmission.suggested_place_name ? (
                    <>
                      <p>Local area: {selectedSubmission.suggested_local_area || selectedSubmission.suggested_place_name || 'not found'}</p>
                      <p>Road: {selectedSubmission.suggested_road_name || 'not found'}</p>
                      {selectedSubmission.map_display_name ? <p className="institutional-note">Map display: {selectedSubmission.map_display_name}</p> : null}
                      <span className="status-chip warn">{statusLabel(selectedSubmission.road_suggestion_status || 'pending-review')}</span>
                      <p className="institutional-note">Source: {selectedSubmission.road_suggestion_attribution || selectedSubmission.road_suggestion_source || 'map-derived suggestion'}. Not official until reviewed.</p>
                      <label className="territory-field territory-field-wide">
                        <span className="territory-label">Reviewed road name</span>
                        <input className="territory-input" value={roadNameReview} onChange={(event) => setRoadNameReview(event.target.value)} />
                      </label>
                      <div className="calm-action-row">
                        <button className="secondary-action" type="button" disabled={isWorking || !canWrite} onClick={() => void reviewRoadSuggestion(selectedSubmission.id, 'accepted')}>Accept</button>
                        <button className="secondary-action" type="button" disabled={isWorking || !canWrite} onClick={() => void reviewRoadSuggestion(selectedSubmission.id, 'edited')}>Save edit</button>
                        <button className="danger-action" type="button" disabled={isWorking || !canWrite} onClick={() => void reviewRoadSuggestion(selectedSubmission.id, 'rejected')}>Reject suggestion</button>
                      </div>
                    </>
                  ) : (
                    <p>No map-derived road name is attached to this request.</p>
                  )}
                </div>
              </div>
              <div className="review-map-panel">
                <div className="native-map-preview" role="img" aria-label={`Coordinate preview for ${selectedSubmission.address_label}`}>
                  <span className="native-map-road native-map-road-a" aria-hidden="true" />
                  <span className="native-map-road native-map-road-b" aria-hidden="true" />
                  <span className="native-map-grid native-map-grid-a" aria-hidden="true" />
                  <span className="native-map-grid native-map-grid-b" aria-hidden="true" />
                  <span className="native-map-pin" aria-hidden="true" />
                  <div className="native-map-coordinate-card">
                    <strong>{selectedSubmission.latitude.toFixed(6)}, {selectedSubmission.longitude.toFixed(6)}</strong>
                    <span>{selectedSubmission.accuracy_meters ? `${selectedSubmission.accuracy_meters}m accuracy` : 'Accuracy not recorded'}</span>
                  </div>
                </div>
                <p className="institutional-note">Native preview preserves the recorded coordinates even if external map tiles are unavailable. Use the external map link for satellite/street context.</p>
                <div className="map-link-row">
                  <a className="secondary-action" href={googleMapsUrl(selectedSubmission)} target="_blank" rel="noreferrer">Open external map</a>
                  <a className="secondary-action" href={mapPreviewUrl(selectedSubmission)} target="_blank" rel="noreferrer">Open OSM preview</a>
                  <a className="secondary-action" href={`/code/${selectedSubmission.grid_code}`} target="_blank" rel="noreferrer">View public code page</a>
                </div>
              </div>
              <div className="review-action-section">
                <div className="review-action-group">
                  <p className="section-label">{t('reviewActions')}</p>
                  {selectedSubmission.automation ? (
                    <p className="form-notice success">{translateUiText('Recommended next action', locale)}: <strong>{translateUiText(selectedSubmission.automation.next_best_action_label, locale)}</strong></p>
                  ) : null}
                  {approvalBlockedReason ? <p className="form-notice error">{approvalBlockedReason}</p> : null}
                  <div className="calm-action-row">
                    <button className={`secondary-action ${isRecommendedAction('operator-review') ? 'recommended-action' : ''}`} type="button" disabled={isWorking || !canWrite} onClick={() => void updateStatus(selectedSubmission.id, 'under-review')}>{t('startReview')}</button>
                    {FIELD_REASONS.map((reason) => {
                      const reasonLabel = reason.label === 'Verify coordinates' ? t('verifyCoordinates') : reason.label === 'Supervisor review' ? t('supervisorReview') : t('possibleSameAddress');
                      return (
                        <button className={`secondary-action ${isRecommendedAction('send-field-check') ? 'recommended-action' : ''}`} key={reason.label} type="button" disabled={isWorking || !canWrite} onClick={() => void updateStatus(selectedSubmission.id, 'field-check', reason.note)}>{reasonLabel}</button>
                      );
                    })}
                    <button className={`primary-action ${isRecommendedAction('await-project-publication-approval') || isRecommendedAction('registry-ready-review') ? 'recommended-action' : ''}`} type="button" disabled={isWorking || !canWrite || Boolean(approvalBlockedReason)} aria-describedby={approvalBlockedReason ? 'registry-approval-blocked' : undefined} onClick={() => void updateStatus(selectedSubmission.id, 'registry-ready')}>Approve case file</button>
                    <button className="secondary-action" type="button" disabled={isWorking || selectedSubmission.status !== 'published'} onClick={() => void openCertificate(selectedSubmission.id)}>Open certificate / save PDF</button>
                    <button className="danger-action" type="button" disabled={isWorking || !canWrite} onClick={() => void updateStatus(selectedSubmission.id, 'reject')}>{t('reject')}</button>
                  </div>
                  {approvalBlockedReason ? <p id="signage-approval-blocked" className="field-help">{approvalBlockedReason}</p> : null}
                </div>
                {(selectedSubmission.duplicate_group?.count ?? 1) > 1 ? (
                  <div className="review-action-group">
                    <p className="section-label">Possible same-address decision</p>
                    <div className="calm-action-row">
                      {DUPLICATE_ACTIONS.map((action) => (
                        <button className="secondary-action" type="button" key={action.action} disabled={isWorking || !canWrite} onClick={() => void recordDuplicateDecision(selectedSubmission.id, action.action, action.note)}>{action.label}</button>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>
              <div className="operator-finding-card review-history-card">
                <strong>{t('reviewHistory')}</strong>
                {reviewHistory.length ? (
                  <ul className="mini-list">
                    {reviewHistory.map((event, index) => (
                      <li key={`${event.action}-${event.created_at ?? index}`}>
                        <span>{statusLabel(event.action)} · {event.actor_username ?? 'system'}</span>
                        {event.details?.reviewer_note ? <small>{event.details.reviewer_note}</small> : null}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No operator review actions recorded yet.</p>
                )}
              </div>
            </>
          ) : (
            <p className="panel-state">Select a location request to review.</p>
          )}
        </article>
      </section>

      <article className="public-task-panel signage-export-panel">
        <div className="panel-head quiet-head">
          <p className="section-label">Physical rollout lock</p>
          <h3>Published records only after full project approval</h3>
        </div>
        <p className="public-task-copy">Physical signage outputs are locked until full project approval. Registry-ready case files stay searchable internally without implying fabrication or publication.</p>
        <details className="quiet-disclosure compact-review-disclosure signage-rollout-disclosure">
          <summary>Open physical rollout outputs</summary>
          <div className="territory-form-actions">
            <button className="primary-action" type="button" onClick={downloadCsv} disabled={!exportRows.length}>Download CSV</button>
            <button className="secondary-action" type="button" onClick={() => void downloadSignagePack()} disabled={!exportRows.length}>Generate signage pack JSON</button>
            <button className="secondary-action" type="button" onClick={() => window.print()} disabled={!exportRows.length}>Print list</button>
          </div>
          {exportRows.length ? (
            <>
              <div className="table-wrap desktop-table-wrap signage-batch-table-wrap" aria-label="Signage batches table">
                <table className="data-table desktop-data-table">
                  <caption>Signage batches</caption>
                  <thead><tr><th scope="col">Batch ID</th><th scope="col">Territory</th><th scope="col">Records</th><th scope="col">Status</th><th scope="col">Approver</th><th scope="col">Date</th></tr></thead>
                  <tbody>
                    {exportRows.map((row) => (
                      <tr key={`${row.grid_code}-${row.batch ?? 'batch-table'}`}>
                        <td>{row.batch ?? 'Pending batch'}</td><td>{row.territory_name ?? 'Area pending'}</td><td>{row.address_label}</td><td>{statusLabel(row.status)}</td><td>Project approval required</td><td>Not released</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <ul className="mini-list signage-export-list mobile-card-list">
                {exportRows.map((row) => (
                  <li key={`${row.grid_code}-${row.batch ?? 'batch'}`}>
                    <strong>{row.signage_text}</strong>
                    <span>{row.address_label} · {row.territory_name ?? 'Area pending'} · {row.latitude}, {row.longitude}</span>
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p className="panel-state">No records are published for physical signage yet.</p>
          )}
        </details>
      </article>
      {notice ? <p className="form-notice success">{notice}</p> : null}
      {error ? <p className="form-notice error">{error}</p> : null}
    </section>
  );
}
