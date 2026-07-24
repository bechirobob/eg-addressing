'use client';

import Link from 'next/link';
import type { FormEvent } from 'react';
import { useEffect, useMemo, useState } from 'react';

import { GovernmentIcon } from './GovernmentIcon';
import { authorizationHeader, csrfHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

type SpatialPoint = {
  latitude: number;
  longitude: number;
  accuracy_meters?: number | null;
  role?: string;
};

type GridCell = { grid_code: string };

type EvidenceAttachmentFile = {
  file_id: string;
  file_name: string;
  content_type: string;
  size_bytes: number;
  access: 'protected';
  uploaded_by?: string;
  uploaded_at?: string;
  review_status?: 'accepted' | 'needs-recapture' | 'rejected' | 'escalated' | 'pending';
  reviewer_note?: string;
  reviewed_by?: string;
  reviewed_at?: string;
};

type EvidenceAttachment = {
  type: string;
  reference: string;
  note?: string;
  captured_by?: string;
  captured_at?: string;
  files?: EvidenceAttachmentFile[];
  file_count?: number;
  review_status?: 'accepted' | 'needs-recapture' | 'rejected' | 'escalated' | 'pending';
};

type SpatialEvidence = {
  geometry_type?: 'LineString' | 'Point';
  points?: SpatialPoint[];
  calculated_length_km?: number;
  latitude?: number;
  longitude?: number;
  accuracy_meters?: number | null;
  road_reference?: string;
  capture_method?: string;
  evidence_source?: string;
  evidence_attachments?: EvidenceAttachment[];
  grid_cells?: GridCell[];
  map_suggestion?: {
    suggested_road_name?: string | null;
    source?: string | null;
    source_attribution?: string | null;
    confidence?: string;
  };
  review_confidence?: string;
  evidence_review_status?: 'accepted' | 'not-required' | 'pending' | 'blocked' | 'escalated';
};

type Submission = {
  id: string;
  territory_name: string;
  submission_type: string;
  candidate_name: string;
  candidate_status: string;
  review_status: string;
  reviewer_note: string;
  registry_entity_id?: string | null;
  submitted_by: string;
  notes: string;
  spatial_evidence?: SpatialEvidence | null;
};

type SlaDrilldownItem = {
  id: string;
  label: string;
  age_hours?: number | null;
  due_hours: number;
  address_label?: string | null;
  territory_name?: string | null;
  next_best_action_label?: string | null;
};

type EvidenceAuditLog = {
  id: number;
  actor_username?: string | null;
  action: string;
  details?: Record<string, unknown>;
  created_at?: string;
};

type LookupResult = {
  query: string;
  match_status: string;
  address_label: string;
  jurisdiction: string;
  verification_note: string;
  address_id?: string;
};

type PromotionResult = {
  entityId: string;
  candidateName: string;
  submissionType: string;
};

type EvidenceDecision = 'accepted' | 'needs-recapture' | 'rejected' | 'escalated';
type ReviewAction = 'under-review' | 'approve' | 'reject' | 'rework';

type GovernmentVerificationWorkbenchProps = {
  apiBaseUrl: string;
};

function plainStatus(value?: string | null) {
  return (value || 'unknown').replaceAll('-', ' ').replaceAll('_', ' ');
}

function hasRequiredSpatialEvidence(submission: Submission) {
  const evidence = submission.spatial_evidence;
  if (submission.submission_type === 'road') {
    const points = evidence?.points ?? [];
    return evidence?.geometry_type === 'LineString'
      && points.length >= 2
      && points.some((point) => point.role === 'start')
      && points.some((point) => point.role === 'end');
  }
  if (submission.submission_type === 'building') {
    return evidence?.geometry_type === 'Point'
      && typeof evidence.latitude === 'number'
      && typeof evidence.longitude === 'number'
      && typeof evidence.accuracy_meters === 'number'
      && Boolean(evidence.road_reference);
  }
  return true;
}

function evidenceReviewState(submission: Submission) {
  return submission.spatial_evidence?.evidence_review_status ?? 'pending';
}

function evidenceFileCount(submission: Submission) {
  return (submission.spatial_evidence?.evidence_attachments ?? [])
    .reduce((total, attachment) => total + (attachment.files?.length ?? attachment.file_count ?? 0), 0);
}

function evidenceSummary(submission: Submission) {
  const evidence = submission.spatial_evidence;
  if (!evidence || Object.keys(evidence).length === 0) return 'No spatial evidence has been submitted.';
  if (evidence.geometry_type === 'LineString') {
    const name = evidence.map_suggestion?.suggested_road_name || submission.candidate_name;
    const length = evidence.calculated_length_km ? `${evidence.calculated_length_km} km` : 'length pending';
    return `${name} · ${length} · ${evidence.grid_cells?.length ?? 0} grid cells`;
  }
  if (evidence.geometry_type === 'Point') {
    return `${evidence.road_reference ?? 'Road reference pending'} · ${evidence.accuracy_meters ?? 'unknown'} m accuracy`;
  }
  return 'Spatial evidence attached for review.';
}

export function GovernmentVerificationWorkbench({ apiBaseUrl }: GovernmentVerificationWorkbenchProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [slaItems, setSlaItems] = useState<SlaDrilldownItem[]>([]);
  const [evidenceHistory, setEvidenceHistory] = useState<EvidenceAuditLog[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [evidenceFilter, setEvidenceFilter] = useState('all');
  const [reviewerNote, setReviewerNote] = useState('Evidence reviewed against the submitted record and operational requirements.');
  const [isLoading, setIsLoading] = useState(false);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [promotion, setPromotion] = useState<PromotionResult | null>(null);
  const [lookupQuery, setLookupQuery] = useState('');
  const [lookupResult, setLookupResult] = useState<LookupResult | null>(null);
  const [lookupLoading, setLookupLoading] = useState(false);

  const canReview = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';

  function requestHeaders(withJson = false) {
    return {
      ...(withJson ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? authorizationHeader(token) : csrfHeader()),
    };
  }

  async function loadEvidenceHistory(submissionId: string) {
    if (!submissionId || sessionStatus !== 'ready') {
      setEvidenceHistory([]);
      return;
    }
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/submissions/${encodeURIComponent(submissionId)}/evidence-history?limit=20`, {
        credentials: 'include',
        headers: requestHeaders(),
      });
      if (!response.ok) {
        setEvidenceHistory([]);
        return;
      }
      const payload = (await response.json()) as { items?: EvidenceAuditLog[] };
      setEvidenceHistory(payload.items ?? []);
    } catch {
      setEvidenceHistory([]);
    }
  }

  async function reloadQueue() {
    if (sessionStatus !== 'ready') return;
    setIsLoading(true);
    setError(null);
    try {
      const request = { credentials: 'include' as const, headers: requestHeaders() };
      const [queueResponse, slaResponse] = await Promise.all([
        fetch(`${browserApiBaseUrl}/api/v1/field/submissions`, request),
        fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/automation/sla-drilldown?state=overdue`, request),
      ]);
      if (!queueResponse.ok) throw new Error('queue-load-failed');
      const queuePayload = (await queueResponse.json()) as { items?: Submission[] };
      const actionable = (queuePayload.items ?? []).filter((submission) => ['submitted', 'under-review'].includes(submission.review_status));
      setSubmissions(actionable);
      setSelectedId((current) => actionable.some((item) => item.id === current) ? current : actionable[0]?.id ?? '');
      if (slaResponse.ok) {
        const slaPayload = (await slaResponse.json()) as { items?: SlaDrilldownItem[] };
        setSlaItems(slaPayload.items ?? []);
      } else {
        setSlaItems([]);
      }
    } catch {
      setError('The verification queue could not be loaded. Retry or escalate to platform support.');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void reloadQueue();
  }, [sessionStatus]);

  useEffect(() => {
    void loadEvidenceHistory(selectedId);
  }, [selectedId, sessionStatus]);

  const normalizedSearch = searchQuery.trim().toLowerCase();
  const visibleSubmissions = useMemo(() => submissions.filter((submission) => {
    if (statusFilter !== 'all' && submission.review_status !== statusFilter) return false;
    const hasEvidence = hasRequiredSpatialEvidence(submission);
    if (evidenceFilter === 'complete' && !hasEvidence) return false;
    if (evidenceFilter === 'missing' && hasEvidence) return false;
    if (!normalizedSearch) return true;
    return [submission.id, submission.candidate_name, submission.territory_name, submission.submission_type, submission.submitted_by]
      .some((value) => String(value ?? '').toLowerCase().includes(normalizedSearch));
  }), [evidenceFilter, normalizedSearch, statusFilter, submissions]);

  const selectedSubmission = submissions.find((submission) => submission.id === selectedId) ?? visibleSubmissions[0] ?? null;
  const queueCounts = useMemo(() => ({
    total: submissions.length,
    submitted: submissions.filter((item) => item.review_status === 'submitted').length,
    underReview: submissions.filter((item) => item.review_status === 'under-review').length,
    missingEvidence: submissions.filter((item) => !hasRequiredSpatialEvidence(item)).length,
    evidencePending: submissions.filter((item) => !['accepted', 'not-required'].includes(evidenceReviewState(item))).length,
  }), [submissions]);

  function disabledReason(submission: Submission | null, action: ReviewAction) {
    if (!submission) return 'Select a submission';
    if (!canReview) return 'Editor or administrator required';
    if (busyAction) return 'Working…';
    if (action === 'under-review' && submission.review_status === 'under-review') return 'Already under review';
    if (action === 'approve' && !hasRequiredSpatialEvidence(submission)) return 'Required location evidence is missing';
    if (action === 'approve' && !['accepted', 'not-required'].includes(evidenceReviewState(submission))) return 'Protected evidence must be accepted first';
    return null;
  }

  async function sendReviewAction(action: ReviewAction) {
    if (!selectedSubmission) return;
    const reason = disabledReason(selectedSubmission, action);
    if (reason) {
      setError(reason);
      return;
    }
    setBusyAction(action);
    setNotice(null);
    setError(null);
    try {
      const payload = action === 'approve' ? undefined : { reviewer_note: reviewerNote };
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/submissions/${encodeURIComponent(selectedSubmission.id)}/${action}`, {
        method: 'POST',
        credentials: 'include',
        headers: requestHeaders(Boolean(payload)),
        body: payload ? JSON.stringify(payload) : undefined,
      });
      const result = (await response.json()) as Submission | { detail?: string };
      if (!response.ok) {
        setError('detail' in result && result.detail ? result.detail : 'The authoritative review service rejected the action.');
        return;
      }
      if (action === 'approve' && 'registry_entity_id' in result && result.registry_entity_id) {
        setPromotion({ entityId: result.registry_entity_id, candidateName: selectedSubmission.candidate_name, submissionType: selectedSubmission.submission_type });
        setNotice(`${selectedSubmission.candidate_name} was approved and promoted into the protected registry.`);
      } else {
        setNotice(`${selectedSubmission.candidate_name}: ${plainStatus(action)} completed.`);
      }
      await reloadQueue();
    } catch {
      setError('The review action could not be completed. No success has been recorded.');
    } finally {
      setBusyAction(null);
    }
  }

  async function reviewEvidenceFile(attachmentIndex: number, file: EvidenceAttachmentFile, decision: EvidenceDecision) {
    if (!selectedSubmission || !canReview) {
      setError('Editor or administrator authority is required to review protected evidence.');
      return;
    }
    setBusyAction(`evidence-${file.file_id}`);
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/submissions/${encodeURIComponent(selectedSubmission.id)}/evidence-review`, {
        method: 'POST',
        credentials: 'include',
        headers: requestHeaders(true),
        body: JSON.stringify({ attachment_index: attachmentIndex, file_id: file.file_id, decision, reviewer_note: reviewerNote }),
      });
      const result = (await response.json()) as Submission | { detail?: string };
      if (!response.ok) {
        setError('detail' in result && result.detail ? result.detail : 'The evidence decision was not accepted.');
        return;
      }
      setNotice(`${file.file_name}: evidence marked ${plainStatus(decision)}.`);
      await reloadQueue();
      await loadEvidenceHistory(selectedSubmission.id);
    } catch {
      setError('The protected evidence decision could not be completed.');
    } finally {
      setBusyAction(null);
    }
  }

  async function downloadEvidenceFile(file: EvidenceAttachmentFile) {
    if (!selectedSubmission) return;
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/submissions/${encodeURIComponent(selectedSubmission.id)}/evidence-files/${encodeURIComponent(file.file_id)}`, {
        credentials: 'include',
        headers: requestHeaders(),
      });
      if (!response.ok) {
        setError('The protected evidence file could not be downloaded.');
        return;
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.file_name;
      link.click();
      URL.revokeObjectURL(url);
      setNotice(`Protected evidence downloaded: ${file.file_name}.`);
    } catch {
      setError('The protected evidence file could not be downloaded.');
    }
  }

  async function runPublicTrustLookup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLookupLoading(true);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/verification/lookup?query=${encodeURIComponent(lookupQuery)}`);
      if (!response.ok) throw new Error('lookup-failed');
      setLookupResult((await response.json()) as LookupResult);
    } catch {
      setError('The public trust lookup is temporarily unavailable.');
    } finally {
      setLookupLoading(false);
    }
  }

  const attachments = selectedSubmission?.spatial_evidence?.evidence_attachments ?? [];

  return (
    <section className="government-operation-page government-verification-workbench" aria-labelledby="verification-workbench-title">
      <header className="government-operation-header">
        <div><p>Evidence and authority</p><h1 id="verification-workbench-title">Verification</h1><span>Review submitted evidence, resolve exceptions, and make authoritative decisions without leaving the case workspace.</span></div>
        <div className="government-operation-header-actions"><Link href="/registry"><GovernmentIcon name="registry" />Open registry</Link><button type="button" onClick={() => void reloadQueue()} disabled={isLoading}><GovernmentIcon name="operations" />{isLoading ? 'Refreshing' : 'Refresh queue'}</button></div>
      </header>

      <dl className="government-operation-summary" aria-label="Verification queue summary">
        <div><dt>Actionable queue</dt><dd>{queueCounts.total}</dd><span>Submitted and under review</span></div>
        <div><dt>New submissions</dt><dd>{queueCounts.submitted}</dd><span>Awaiting first decision</span></div>
        <div><dt>Under review</dt><dd>{queueCounts.underReview}</dd><span>Assigned operational work</span></div>
        <div><dt>Missing evidence</dt><dd>{queueCounts.missingEvidence}</dd><span>Cannot be approved</span></div>
        <div><dt>Overdue</dt><dd>{slaItems.length}</dd><span>Service-level attention</span></div>
      </dl>

      <div className="government-command-bar" aria-label="Verification filters">
        <label className="government-search-field"><GovernmentIcon name="search" /><span className="sr-only">Search verification queue</span><input type="search" value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Search case, candidate, territory, type, or submitter" /></label>
        <label><span>Queue state</span><select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="all">All active states</option><option value="submitted">Submitted</option><option value="under-review">Under review</option></select></label>
        <label><span>Location evidence</span><select value={evidenceFilter} onChange={(event) => setEvidenceFilter(event.target.value)}><option value="all">All evidence states</option><option value="complete">Required evidence present</option><option value="missing">Required evidence missing</option></select></label>
        <div className="government-command-note"><GovernmentIcon name="alert" /><span>{queueCounts.evidencePending} case{queueCounts.evidencePending === 1 ? '' : 's'} still require an evidence decision</span></div>
      </div>

      {sessionStatus === 'loading' ? <p className="government-inline-state">Resolving reviewer authority and loading the queue…</p> : null}
      {promotion ? <p className="government-inline-state success" role="status">Registry promotion complete: <Link href={`/registry?entity=${encodeURIComponent(promotion.entityId)}`}>{promotion.candidateName} · {promotion.entityId}</Link></p> : null}
      {notice ? <p className="government-inline-state success" role="status">{notice}</p> : null}
      {error ? <p className="government-inline-state error" role="alert">{error}</p> : null}

      <div className="government-three-pane-workbench">
        <aside className="government-queue-pane" aria-label="Verification decision queue">
          <div className="government-pane-heading"><div><p>Decision queue</p><h2>Requires review</h2></div><span>{visibleSubmissions.length} shown</span></div>
          <div className="government-record-queue">
            {visibleSubmissions.length ? visibleSubmissions.map((submission) => (
              <button key={submission.id} className={selectedSubmission?.id === submission.id ? 'active' : ''} type="button" onClick={() => setSelectedId(submission.id)}>
                <span className="government-queue-record-title">{submission.candidate_name}</span>
                <code>{submission.id}</code>
                <span>{submission.territory_name} · {plainStatus(submission.submission_type)}</span>
                <small className={`government-record-state ${hasRequiredSpatialEvidence(submission) ? '' : 'warning'}`}>{hasRequiredSpatialEvidence(submission) ? plainStatus(submission.review_status) : 'Evidence missing'}</small>
              </button>
            )) : <div className="government-pane-empty"><GovernmentIcon name="verification" /><strong>No matching verification work</strong><span>The active queue is empty or the current filters exclude all records.</span></div>}
          </div>
        </aside>

        <article className="government-record-pane" aria-label="Selected verification case">
          {selectedSubmission ? (
            <>
              <header className="government-selected-record-header"><div><p>{plainStatus(selectedSubmission.submission_type)} verification case</p><h2>{selectedSubmission.candidate_name}</h2><code>{selectedSubmission.id}</code></div><span className={`government-record-state ${hasRequiredSpatialEvidence(selectedSubmission) ? '' : 'warning'}`}>{plainStatus(selectedSubmission.review_status)}</span></header>
              <nav className="government-record-tabs" aria-label="Verification case sections"><span className="active">Evidence</span><span>Location</span><span>History</span><span>Audit</span></nav>
              <div className="government-record-body">
                <section><div className="government-record-section-heading"><h3>Case and routing context</h3><span>Human authority remains required</span></div><dl className="government-record-facts"><div><dt>Territory</dt><dd>{selectedSubmission.territory_name}</dd></div><div><dt>Submitted by</dt><dd>{selectedSubmission.submitted_by}</dd></div><div><dt>Candidate state</dt><dd>{plainStatus(selectedSubmission.candidate_status)}</dd></div><div><dt>Review state</dt><dd>{plainStatus(selectedSubmission.review_status)}</dd></div><div><dt>Location evidence</dt><dd>{hasRequiredSpatialEvidence(selectedSubmission) ? 'Required evidence present' : 'Required evidence missing'}</dd></div><div><dt>Evidence review</dt><dd>{plainStatus(evidenceReviewState(selectedSubmission))}</dd></div></dl></section>
                <section><div className="government-record-section-heading"><h3>Spatial evidence</h3><span>{evidenceSummary(selectedSubmission)}</span></div><div className={`government-evidence-assessment ${hasRequiredSpatialEvidence(selectedSubmission) ? 'success' : 'warning'}`}><GovernmentIcon name={hasRequiredSpatialEvidence(selectedSubmission) ? 'readiness' : 'alert'} /><div><strong>{hasRequiredSpatialEvidence(selectedSubmission) ? 'Required location evidence is present' : 'Approval is blocked by missing location evidence'}</strong><span>{selectedSubmission.notes || 'No field note supplied.'}</span></div></div>{selectedSubmission.spatial_evidence?.points?.length ? <div className="government-evidence-table"><div className="government-evidence-table-header"><span>Point</span><span>Latitude</span><span>Longitude</span><span>Accuracy</span></div>{selectedSubmission.spatial_evidence.points.map((point, index) => <div key={`${selectedSubmission.id}-${index}`}><span>{point.role ?? `Point ${index + 1}`}</span><span>{point.latitude}</span><span>{point.longitude}</span><span>{point.accuracy_meters ?? '—'} m</span></div>)}</div> : null}</section>
                <section><div className="government-record-section-heading"><h3>Protected evidence files</h3><span>{evidenceFileCount(selectedSubmission)} files · {plainStatus(evidenceReviewState(selectedSubmission))}</span></div>{attachments.length ? <div className="government-evidence-files">{attachments.map((attachment, attachmentIndex) => <div key={`${attachment.reference}-${attachmentIndex}`} className="government-evidence-group"><div><strong>{attachment.reference}</strong><span>{plainStatus(attachment.type)}{attachment.captured_by ? ` · ${attachment.captured_by}` : ''}</span>{attachment.note ? <small>{attachment.note}</small> : null}</div>{attachment.files?.length ? <ul>{attachment.files.map((file) => <li key={file.file_id}><div><strong>{file.file_name}</strong><span>{Math.ceil(file.size_bytes / 1024)} KB · {plainStatus(file.review_status ?? 'pending')}</span>{file.reviewer_note ? <small>{file.reviewer_note}</small> : null}</div><div><button type="button" onClick={() => void downloadEvidenceFile(file)}>Download</button><button type="button" onClick={() => void reviewEvidenceFile(attachmentIndex, file, 'accepted')} disabled={!canReview || Boolean(busyAction)}>Accept</button><button type="button" onClick={() => void reviewEvidenceFile(attachmentIndex, file, 'needs-recapture')} disabled={!canReview || Boolean(busyAction)}>Recapture</button><button type="button" onClick={() => void reviewEvidenceFile(attachmentIndex, file, 'escalated')} disabled={!canReview || Boolean(busyAction)}>Escalate</button></div></li>)}</ul> : <p>No uploaded file is attached to this evidence reference.</p>}</div>)}</div> : <div className="government-pane-empty compact"><GovernmentIcon name="records" /><strong>No protected evidence files</strong><span>Location data may still be present, but no downloadable evidence file is attached.</span></div>}</section>
                <section><div className="government-record-section-heading"><h3>Recent evidence history</h3><span>{evidenceHistory.length} events returned</span></div>{evidenceHistory.length ? <ol className="government-audit-list">{evidenceHistory.slice(0, 8).map((item) => <li key={item.id}><span>{plainStatus(item.action)}</span><strong>{item.actor_username ?? 'System actor'}</strong><small>{item.created_at ? new Date(item.created_at).toLocaleString() : 'Time unavailable'}</small></li>)}</ol> : <p className="government-record-copy">No evidence-access history was returned for this case.</p>}</section>
              </div>
            </>
          ) : <div className="government-pane-empty large"><GovernmentIcon name="verification" /><strong>Select a verification case</strong><span>Evidence, history, and valid decisions will appear here.</span></div>}
        </article>

        <aside className="government-decision-pane" aria-label="Verification decision inspector">
          <div className="government-pane-heading"><div><p>Decision inspector</p><h2>Valid next actions</h2></div><span>{canReview ? 'Review authority' : 'Read only'}</span></div>
          <div className="government-decision-body">
            <section><h3>Decision note</h3><label className="government-note-field"><span>Reason retained with rework, rejection, and evidence decisions</span><textarea rows={5} value={reviewerNote} onChange={(event) => setReviewerNote(event.target.value)} /></label></section>
            <section><h3>Case transition</h3><div className="government-action-stack"><button className="primary" type="button" onClick={() => void sendReviewAction('approve')} disabled={Boolean(disabledReason(selectedSubmission, 'approve'))}>{disabledReason(selectedSubmission, 'approve') ?? 'Approve and promote to registry'}</button><button type="button" onClick={() => void sendReviewAction('rework')} disabled={Boolean(disabledReason(selectedSubmission, 'rework'))}>{disabledReason(selectedSubmission, 'rework') ?? 'Request correction'}</button><button type="button" onClick={() => void sendReviewAction('under-review')} disabled={Boolean(disabledReason(selectedSubmission, 'under-review'))}>{disabledReason(selectedSubmission, 'under-review') ?? 'Mark under review'}</button><button className="danger" type="button" onClick={() => void sendReviewAction('reject')} disabled={Boolean(disabledReason(selectedSubmission, 'reject'))}>{disabledReason(selectedSubmission, 'reject') ?? 'Reject submission'}</button></div></section>
            {slaItems.length ? <section><h3>Overdue work</h3><ul className="government-overdue-list">{slaItems.slice(0, 5).map((item) => <li key={item.id}><strong>{item.address_label ?? item.label}</strong><span>{item.territory_name ?? 'Territory pending'} · {item.age_hours ?? 'unknown'}h / {item.due_hours}h</span><small>{item.next_best_action_label ?? 'Review required'}</small></li>)}</ul></section> : null}
            <section><h3>Public trust lookup</h3><form className="government-trust-lookup" onSubmit={(event) => void runPublicTrustLookup(event)}><label><span>Published code or address</span><input required value={lookupQuery} onChange={(event) => setLookupQuery(event.target.value)} /></label><button type="submit" disabled={lookupLoading}>{lookupLoading ? 'Checking…' : 'Check published registry'}</button></form>{lookupResult ? <div className={`government-trust-result ${lookupResult.match_status === 'verified' ? 'success' : 'warning'}`}><strong>{plainStatus(lookupResult.match_status)}</strong><span>{lookupResult.address_label}</span><small>{lookupResult.jurisdiction} · {lookupResult.verification_note}</small></div> : null}</section>
            <section className="government-authority-note"><GovernmentIcon name="alert" /><div><strong>Approval is not publication</strong><span>An approved submission is promoted into the protected registry. Public release remains a separate, controlled authority action.</span></div></section>
          </div>
        </aside>
      </div>
    </section>
  );
}
