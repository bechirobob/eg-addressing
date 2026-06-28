'use client';

import { FormEvent, useEffect, useState } from 'react';

import { authorizationHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

type Assignment = {
  assignment_id: string;
  territory_id: string;
  territory: string;
  task: string;
  team: string;
  priority: string;
};

type Submission = {
  id: string;
  assignment_id?: string | null;
  territory_id: string;
  territory_name: string;
  submission_type: 'road' | 'building' | 'address';
  candidate_name: string;
  candidate_status: string;
  notes: string;
  submitted_by: string;
  review_status: string;
  reviewer_note: string;
  registry_entity_id?: string | null;
};

type Territory = { id: string; name: string };

type FieldWorkflowPanelProps = {
  assignments: Assignment[];
  submissions: Submission[];
  territories: Territory[];
  apiBaseUrl: string;
};

export function FieldWorkflowPanel({ assignments, submissions: initialSubmissions, territories, apiBaseUrl }: FieldWorkflowPanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [submissions, setSubmissions] = useState(initialSubmissions);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [form, setForm] = useState({
    assignment_id: assignments[0]?.assignment_id ?? '',
    territory_id: assignments[0]?.territory_id ?? territories[0]?.id ?? '',
    submission_type: 'road' as 'road' | 'building' | 'address',
    candidate_name: '',
    candidate_status: 'submitted',
    notes: '',
    submitted_by: 'Field team operator',
  });

  useEffect(() => {
    if (!token) return;
    void reloadSubmissions(token);
  }, [token]);

  async function reloadSubmissions(activeToken: string) {
    const response = await fetch(`${browserApiBaseUrl}/api/v1/field/submissions`, { headers: authorizationHeader(activeToken) });
    if (!response.ok) {
      setError('Unable to refresh recent submissions.');
      return;
    }
    const payload = (await response.json()) as { items: Submission[] };
    setSubmissions(payload.items ?? []);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !(sessionUser?.role === 'editor' || sessionUser?.role === 'admin')) {
      setError('Sign in as editor or admin before sending field submissions.');
      return;
    }
    setIsSubmitting(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/submissions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token!) },
        body: JSON.stringify({
          ...form,
          assignment_id: form.assignment_id || null,
        }),
      });
      const payload = (await response.json()) as Submission | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to submit field record.');
        return;
      }
      setNotice(`Field submission recorded: ${form.candidate_name}`);
      setForm((current) => ({ ...current, candidate_name: '', notes: '' }));
      await reloadSubmissions(token);
    } catch {
      setError('Unable to submit the field record.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="section-grid territory-admin-grid">
      <article className="panel panel-accent-green">
        <div className="panel-head">
          <p className="section-label">Deployment queue</p>
          <h3>Priority field assignments</h3>
        </div>
        <ul className="assignment-list">
          {assignments.map((assignment) => (
            <li key={assignment.assignment_id} className="assignment-card">
              <div>
                <p className="assignment-kicker">{assignment.priority} priority</p>
                <h4>{assignment.task}</h4>
                <p>{assignment.territory}</p>
              </div>
              <div className="assignment-meta">{assignment.team}</div>
            </li>
          ))}
        </ul>
      </article>

      <article className="panel panel-accent-blue">
        <div className="panel-head">
          <p className="section-label">Field intake</p>
          <h3>Submit registry evidence from the territory</h3>
        </div>
        <p className="institutional-note">
          Signed-in role: <strong>{sessionUser?.role ?? 'guest'}</strong>. This feeds the live verification queue.
        </p>
        {sessionStatus === 'loading' ? <p className="panel-state">Checking access before opening the submission form…</p> : null}
        <form className="territory-form" onSubmit={handleSubmit}>
          <label className="territory-field">
            <span className="territory-label">Assignment</span>
            <select
              className="territory-input"
              value={form.assignment_id}
              onChange={(event) => {
                const assignment = assignments.find((item) => item.assignment_id === event.target.value);
                setForm({
                  ...form,
                  assignment_id: event.target.value,
                  territory_id: assignment?.territory_id ?? form.territory_id,
                  submitted_by: assignment?.team ?? form.submitted_by,
                });
              }}
            >
              {assignments.map((assignment) => (
                <option key={assignment.assignment_id} value={assignment.assignment_id}>
                  {assignment.task} · {assignment.team}
                </option>
              ))}
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Territory</span>
            <select className="territory-input" value={form.territory_id} onChange={(event) => setForm({ ...form, territory_id: event.target.value })}>
              {territories.map((territory) => (
                <option key={territory.id} value={territory.id}>
                  {territory.name}
                </option>
              ))}
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Submission type</span>
            <select className="territory-input" value={form.submission_type} onChange={(event) => setForm({ ...form, submission_type: event.target.value as 'road' | 'building' | 'address' })}>
              <option value="road">Road proposal</option>
              <option value="building">Building proposal</option>
              <option value="address">Address proposal</option>
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Candidate name / label</span>
            <input className="territory-input" value={form.candidate_name} onChange={(event) => setForm({ ...form, candidate_name: event.target.value })} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Candidate status</span>
            <input className="territory-input" value={form.candidate_status} onChange={(event) => setForm({ ...form, candidate_status: event.target.value })} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Submitted by</span>
            <input className="territory-input" value={form.submitted_by} onChange={(event) => setForm({ ...form, submitted_by: event.target.value })} required />
          </label>
          <label className="territory-field territory-field-wide">
            <span className="territory-label">Field notes</span>
            <textarea className="territory-input territory-textarea" value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} rows={4} />
          </label>
          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Submitting…' : 'Submit to verification queue'}
            </button>
          </div>
        </form>
        {notice ? <p className="form-notice success">{notice}</p> : null}
        {error ? <p className="form-notice error">{error}</p> : null}
      </article>

      <article className="panel panel-accent-gold territory-list-panel">
        <div className="panel-head">
          <p className="section-label">Live intake</p>
          <h3>Recently submitted field records</h3>
        </div>
        {submissions.length > 0 ? (
          <ul className="mini-list">
            {submissions.map((submission) => (
              <li key={submission.id}>
                <strong>{submission.candidate_name}</strong>
                <span>
                  {submission.territory_name} · {submission.submission_type} · {submission.review_status}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="panel-state">No field submissions have been recorded yet.</p>
        )}
      </article>
    </section>
  );
}
