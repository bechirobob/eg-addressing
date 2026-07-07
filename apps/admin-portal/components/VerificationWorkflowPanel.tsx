'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

import { authorizationHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

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
};

type LookupResult = {
  query: string;
  match_status: string;
  address_label: string;
  jurisdiction: string;
  verification_note: string;
  address_id?: string;
};

type VerificationWorkflowPanelProps = {
  submissions: Submission[];
  sampleLookup: LookupResult;
  apiBaseUrl: string;
};

type PromotionResult = {
  entityId: string;
  candidateName: string;
  submissionType: string;
};

type SlaDrilldownItem = {
  id: string;
  type: string;
  label: string;
  status: string;
  state: string;
  age_hours?: number | null;
  due_hours: number;
  address_label?: string | null;
  grid_code?: string | null;
  territory_name?: string | null;
  next_best_action_label?: string | null;
};

export function VerificationWorkflowPanel({ submissions: initialSubmissions, sampleLookup, apiBaseUrl }: VerificationWorkflowPanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [submissions, setSubmissions] = useState(initialSubmissions);
  const [lookupQuery, setLookupQuery] = useState(sampleLookup.query);
  const [lookupResult, setLookupResult] = useState(sampleLookup);
  const [reviewerNote, setReviewerNote] = useState('Evidence reviewed and accepted.');
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastPromotion, setLastPromotion] = useState<PromotionResult | null>(null);
  const [slaItems, setSlaItems] = useState<SlaDrilldownItem[]>([]);
  const [isQueueRefreshing, setIsQueueRefreshing] = useState(false);
  const [isLookupLoading, setIsLookupLoading] = useState(false);
  const [busySubmissionId, setBusySubmissionId] = useState<string | null>(null);
  const canReview = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';

  function reviewDisabledReason(submission: Submission, action: 'under-review' | 'approve' | 'reject' | 'rework') {
    if (!canReview) return 'Editor or admin required';
    if (busySubmissionId === submission.id) return 'Working…';
    if (action === 'under-review' && submission.review_status === 'under-review') return 'Already under review';
    return null;
  }

  const actionableQueue = useMemo(
    () => submissions.filter((submission) => ['submitted', 'under-review'].includes(submission.review_status)),
    [submissions],
  );

  useEffect(() => {
    if (!token) return;
    void reloadQueue(token);
  }, [token]);

  async function reloadQueue(activeToken: string) {
    setIsQueueRefreshing(true);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/submissions`, { headers: authorizationHeader(activeToken) });
      if (!response.ok) {
        setError('Unable to refresh the verification queue.');
        return;
      }
      const payload = (await response.json()) as { items: Submission[] };
      setSubmissions(payload.items ?? []);
      const slaResponse = await fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/automation/sla-drilldown?state=overdue`, { headers: authorizationHeader(activeToken) });
      if (slaResponse.ok) {
        const slaPayload = (await slaResponse.json()) as { items: SlaDrilldownItem[] };
        setSlaItems(slaPayload.items ?? []);
      }
    } catch {
      setError('Unable to refresh the verification queue.');
    } finally {
      setIsQueueRefreshing(false);
    }
  }

  async function sendAction(submission: Submission, action: 'under-review' | 'approve' | 'reject' | 'rework') {
    if (!token || !(sessionUser?.role === 'editor' || sessionUser?.role === 'admin')) {
      setError('Sign in as editor or admin before taking review actions.');
      return;
    }

    setBusySubmissionId(submission.id);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/submissions/${submission.id}/${action}`, {
        method: 'POST',
        headers: {
          ...(action === 'approve' ? {} : { 'Content-Type': 'application/json' }),
          ...authorizationHeader(token!),
        },
        body: action === 'approve' ? undefined : JSON.stringify({ reviewer_note: reviewerNote }),
      });
      const payload = (await response.json()) as Submission | { detail?: string };

      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to update verification state.');
        return;
      }

      if (action === 'approve' && 'registry_entity_id' in payload && payload.registry_entity_id) {
        setLastPromotion({
          entityId: payload.registry_entity_id,
          candidateName: submission.candidate_name,
          submissionType: submission.submission_type,
        });
        setNotice(`Registry promotion completed for ${submission.candidate_name}.`);
      } else {
        setNotice(`Submission ${action.replace('-', ' ')}: ${submission.candidate_name}.`);
      }

      await reloadQueue(token);
    } catch {
      setError('Unable to update verification state.');
    } finally {
      setBusySubmissionId(null);
    }
  }

  async function handleLookup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLookupLoading(true);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/verification/lookup?query=${encodeURIComponent(lookupQuery)}`);
      const payload = (await response.json()) as LookupResult;
      setLookupResult(payload);
    } catch {
      setError('Unable to complete the public verification check.');
    } finally {
      setIsLookupLoading(false);
    }
  }

  return (
    <section className="section-grid territory-admin-grid">
      <article className="public-task-panel civic-panel-blue territory-list-panel">
        <div className="panel-head">
          <p className="section-label">Verification queue</p>
          <h3>Review field submissions before registry promotion</h3>
        </div>
        <p className="institutional-note">
          Signed-in role: <strong>{sessionUser?.role ?? 'guest'}</strong>. Approval creates a registry record and returns the record identifier.
        </p>

        {sessionStatus === 'loading' ? <p className="panel-state">Checking access and loading the current queue…</p> : null}

        <details className="inline-disclosure compact-review-disclosure" open={slaItems.length > 0}>
          <summary>
            <strong>SLA drill-down</strong>
            <span>{slaItems.length} overdue citizen geotag item{slaItems.length === 1 ? '' : 's'}</span>
          </summary>
          {slaItems.length ? (
            <ul className="mini-list">
              {slaItems.map((item) => (
                <li key={item.id}>
                  <strong>{item.address_label ?? item.id}</strong>
                  <span>{item.grid_code ?? item.type} · {item.age_hours ?? 'unknown'}h / {item.due_hours}h · {item.next_best_action_label ?? item.label}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="institutional-note">No overdue geotag SLA items are currently returned by the operational queue.</p>
          )}
        </details>

        <label className="territory-field territory-field-wide">
          <span className="territory-label">Reviewer note</span>
          <textarea className="territory-input territory-textarea" value={reviewerNote} onChange={(event) => setReviewerNote(event.target.value)} rows={3} />
        </label>

        {lastPromotion ? (
          <div className="result-card promotion-card">
            <div>
              <p className="assignment-kicker">Registry promotion confirmed</p>
              <h4>{lastPromotion.candidateName}</h4>
              <p>
                Created as {lastPromotion.submissionType} record <strong>{lastPromotion.entityId}</strong>.
              </p>
            </div>
            <div className="button-stack">
              <a className="secondary-button inline-link-button" href={`/registry?entity=${encodeURIComponent(lastPromotion.entityId)}`}>
                Open in registry
              </a>
            </div>
          </div>
        ) : null}

        {isQueueRefreshing ? <p className="panel-state">Refreshing the queue…</p> : null}

        {actionableQueue.length > 0 ? (
          <ul className="review-list">
            {actionableQueue.map((submission) => {
              const isBusy = busySubmissionId === submission.id;
              return (
                <li key={submission.id} className="review-card">
                  <div>
                    <p className="assignment-kicker">
                      {submission.submission_type} · {submission.review_status}
                    </p>
                    <h4>{submission.candidate_name}</h4>
                    <p>
                      {submission.territory_name} · {submission.submitted_by}
                    </p>
                    <details className="inline-disclosure">
                      <summary>Review evidence and secondary actions</summary>
                      <p>{submission.notes}</p>
                      {submission.registry_entity_id ? (
                        <p className="institutional-note">
                          Registry record: <strong>{submission.registry_entity_id}</strong>
                        </p>
                      ) : null}
                    </details>
                  </div>
                  <div className="button-stack">
                    <button className="mini-action-button" onClick={() => void sendAction(submission, 'under-review')} type="button" disabled={Boolean(reviewDisabledReason(submission, 'under-review'))}>
                      {reviewDisabledReason(submission, 'under-review') ?? 'Mark under review'}
                    </button>
                    <button className="mini-action-button primary" onClick={() => void sendAction(submission, 'approve')} type="button" disabled={Boolean(reviewDisabledReason(submission, 'approve'))}>
                      {reviewDisabledReason(submission, 'approve') ?? 'Approve into registry'}
                    </button>
                    <button className="mini-action-button" onClick={() => void sendAction(submission, 'rework')} type="button" disabled={Boolean(reviewDisabledReason(submission, 'rework'))}>
                      {reviewDisabledReason(submission, 'rework') ?? 'Send to rework'}
                    </button>
                    <button className="mini-action-button danger" onClick={() => void sendAction(submission, 'reject')} type="button" disabled={Boolean(reviewDisabledReason(submission, 'reject'))}>
                      {reviewDisabledReason(submission, 'reject') ?? 'Reject'}
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="panel-state">No submissions are currently awaiting verification action.</p>
        )}
        {notice ? <p className="form-notice success">{notice}</p> : null}
        {error ? <p className="form-notice error">{error}</p> : null}
      </article>

      <article className="public-task-panel civic-panel-green">
        <div className="panel-head">
          <p className="section-label">Public trust check</p>
          <h3>Verify a published registry record</h3>
        </div>
        <form className="territory-form" onSubmit={handleLookup}>
          <label className="territory-field territory-field-wide">
            <span className="territory-label">Registry code or address</span>
            <input className="territory-input" value={lookupQuery} onChange={(event) => setLookupQuery(event.target.value)} required />
          </label>
          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={isLookupLoading}>
              {isLookupLoading ? 'Checking…' : 'Verify record'}
            </button>
          </div>
        </form>
        <div className="result-card">
          <span className={`status-pill ${lookupResult.match_status === 'verified' ? 'ok' : 'warn'}`}>{lookupResult.match_status}</span>
          <div>
            <h4>{lookupResult.address_label}</h4>
            <p>{lookupResult.jurisdiction}</p>
            <p>{lookupResult.verification_note}</p>
          </div>
        </div>
      </article>
    </section>
  );
}
