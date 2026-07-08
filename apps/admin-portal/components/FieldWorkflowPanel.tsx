'use client';

import { FormEvent, useEffect, useState } from 'react';

import { useTranslation, translateUiText } from './i18n';
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

type GeotagFieldTask = {
  id: string;
  address_label: string;
  territory_name?: string | null;
  grid_code: string;
  status: string;
  field_status?: string | null;
  field_note?: string | null;
  latitude: number;
  longitude: number;
  accuracy_meters?: number | null;
  landmark?: string | null;
};

type Territory = { id: string; name: string };

type FieldWorkflowPanelProps = {
  assignments: Assignment[];
  submissions: Submission[];
  territories: Territory[];
  apiBaseUrl: string;
};

export function FieldWorkflowPanel({ assignments, submissions: initialSubmissions, territories, apiBaseUrl }: FieldWorkflowPanelProps) {
  const { locale } = useTranslation();
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [fieldAssignments, setFieldAssignments] = useState(assignments);
  const [fieldTerritories, setFieldTerritories] = useState(territories);
  const [submissions, setSubmissions] = useState(initialSubmissions);
  const [geotagTasks, setGeotagTasks] = useState<GeotagFieldTask[]>([]);
  const [fieldNote, setFieldNote] = useState('Coordinates checked at property entrance.');
  const [evidenceReference, setEvidenceReference] = useState('field-photo-reference-001');
  const [busyTaskId, setBusyTaskId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const canSubmit = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';
  const submitDisabledReason = !canSubmit ? 'Editor or admin required' : isSubmitting ? 'Submitting…' : null;
  const [form, setForm] = useState({
    assignment_id: fieldAssignments[0]?.assignment_id ?? '',
    territory_id: fieldAssignments[0]?.territory_id ?? fieldTerritories[0]?.id ?? '',
    submission_type: 'road' as 'road' | 'building' | 'address',
    candidate_name: '',
    candidate_status: 'submitted',
    notes: '',
    submitted_by: 'Field team operator',
  });

  useEffect(() => {
    if (!token) return;
    void reloadProtectedLookups(token);
    void reloadSubmissions(token);
    void reloadGeotagTasks(token);
  }, [token]);

  useEffect(() => {
    if (!form.assignment_id && fieldAssignments[0]) {
      setForm((current) => ({ ...current, assignment_id: fieldAssignments[0].assignment_id, territory_id: fieldAssignments[0].territory_id }));
    } else if (!form.territory_id && fieldTerritories[0]) {
      setForm((current) => ({ ...current, territory_id: fieldTerritories[0].id }));
    }
  }, [fieldAssignments, fieldTerritories, form.assignment_id, form.territory_id]);

  async function reloadProtectedLookups(activeToken: string) {
    const [assignmentsResponse, territoriesResponse] = await Promise.all([
      fetch(`${browserApiBaseUrl}/api/v1/field/assignments`, { headers: authorizationHeader(activeToken) }),
      fetch(`${browserApiBaseUrl}/api/v1/territories`, { headers: authorizationHeader(activeToken) }),
    ]);
    if (!assignmentsResponse.ok || !territoriesResponse.ok) {
      setError('Unable to refresh protected field lookup lists.');
      return;
    }
    const assignmentsPayload = (await assignmentsResponse.json()) as { items: Assignment[] };
    const territoriesPayload = (await territoriesResponse.json()) as { items: Territory[] };
    setFieldAssignments(assignmentsPayload.items ?? []);
    setFieldTerritories(territoriesPayload.items ?? []);
  }

  async function reloadSubmissions(activeToken: string) {
    const response = await fetch(`${browserApiBaseUrl}/api/v1/field/submissions`, { headers: authorizationHeader(activeToken) });
    if (!response.ok) {
      setError('Unable to refresh recent submissions.');
      return;
    }
    const payload = (await response.json()) as { items: Submission[] };
    setSubmissions(payload.items ?? []);
  }

  async function reloadGeotagTasks(activeToken: string) {
    const response = await fetch(`${browserApiBaseUrl}/api/v1/field/geotag-tasks`, { headers: authorizationHeader(activeToken) });
    if (!response.ok) {
      setError('Unable to refresh assigned location checks.');
      return;
    }
    const payload = (await response.json()) as { items: GeotagFieldTask[] };
    setGeotagTasks(payload.items ?? []);
  }

  async function updateGeotagTask(taskId: string, field_status: 'visited' | 'verified' | 'needs-recapture' | 'blocked') {
    if (!token || !canSubmit) {
      setError('Editor or admin access is required to update field checks.');
      return;
    }
    setBusyTaskId(taskId);
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/geotag-tasks/${taskId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token) },
        body: JSON.stringify({ field_status, field_note: fieldNote }),
      });
      const payload = (await response.json()) as GeotagFieldTask | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to update field check.');
        return;
      }
      setNotice(`Field check ${field_status.replace('-', ' ')}.`);
      await reloadGeotagTasks(token);
    } catch {
      setError('Unable to update field check.');
    } finally {
      setBusyTaskId(null);
    }
  }

  async function recordEvidence(taskId: string) {
    if (!token || !canSubmit) {
      setError('Editor or admin access is required to record field evidence.');
      return;
    }
    setBusyTaskId(taskId);
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/geotag-tasks/${taskId}/evidence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token) },
        body: JSON.stringify({
          evidence_type: 'photo-reference',
          evidence_reference: evidenceReference,
          evidence_note: fieldNote,
        }),
      });
      const payload = (await response.json()) as { detail?: string };
      if (!response.ok) {
        setError(payload.detail ?? 'Unable to record field evidence.');
        return;
      }
      setNotice('Field evidence reference recorded for the task.');
      await reloadGeotagTasks(token);
    } catch {
      setError('Unable to record field evidence.');
    } finally {
      setBusyTaskId(null);
    }
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
    <section className="section-grid territory-admin-grid field-workspace">
      <article className="public-task-panel civic-panel-green field-assignments-panel">
        <div className="panel-head">
          <p className="section-label">Deployment queue</p>
          <h3>Priority field assignments</h3>
        </div>
        <div className="data-command-deck field-command-deck" aria-label="Field operation command lanes">
          <button className="case-lane warn" type="button">
            <span>Assignments</span>
            <strong>{fieldAssignments.length}</strong>
            <small>Risk lane: priority deployment tasks assigned to field teams.</small>
          </button>
          <button className="case-lane" type="button">
            <span>Location checks</span>
            <strong>{geotagTasks.length}</strong>
            <small>Case lane: citizen geotags waiting for field confirmation.</small>
          </button>
          <button className="case-lane ok" type="button">
            <span>Recent intake</span>
            <strong>{submissions.length}</strong>
            <small>Evidence lane: records already submitted into verification.</small>
          </button>
        </div>
        <ul className="assignment-list">
          {fieldAssignments.map((assignment) => (
            <li key={assignment.assignment_id} className="assignment-card">
              <div>
                <p className="assignment-kicker">{translateUiText(`${assignment.priority} priority`, locale)}</p>
                <h4>{assignment.task}</h4>
                <p>{assignment.territory}</p>
              </div>
              <div className="assignment-meta">{assignment.team}</div>
            </li>
          ))}
        </ul>
      </article>

      <article className="public-task-panel civic-panel-gold field-location-checks-panel">
        <div className="panel-head">
          <p className="section-label">Assigned location checks</p>
          <h3>Citizen geotag verification tasks</h3>
        </div>
        <details className="quiet-disclosure compact-review-disclosure">
          <summary>Shared field evidence settings</summary>
          <label className="territory-field territory-field-wide">
            <span className="territory-label">Shared field note for status updates</span>
            <textarea className="territory-input territory-textarea" value={fieldNote} onChange={(event) => setFieldNote(event.target.value)} rows={3} />
          </label>
          <label className="territory-field territory-field-wide">
            <span className="territory-label">Evidence reference</span>
            <input className="territory-input" value={evidenceReference} onChange={(event) => setEvidenceReference(event.target.value)} placeholder="Photo/file reference, not a private credential" />
            <span className="field-help">Records an auditable field evidence reference. Do not paste passwords, D.I.P. scans, or private identity files here.</span>
          </label>
        </details>
        {geotagTasks.length ? (
          <ul className="mini-list field-task-list">
            {geotagTasks.map((task) => {
              const isBusy = busyTaskId === task.id;
              return (
                <li key={task.id}>
                  <details className="inline-disclosure">
                    <summary>
                      <strong>{task.address_label}</strong>
                      <span>{task.territory_name ?? 'Area pending'} · {task.grid_code} · {task.field_status ?? 'assigned'}</span>
                    </summary>
                    <p>{task.latitude}, {task.longitude} · Accuracy: {task.accuracy_meters ?? 'not recorded'}m</p>
                    <p>{task.landmark || 'No landmark supplied.'}</p>
                    <div className="calm-action-row">
                      <a className="secondary-action" href={`https://www.google.com/maps/search/?api=1&query=${task.latitude},${task.longitude}`} target="_blank" rel="noreferrer">Open map</a>
                      <button className="secondary-action" type="button" disabled={isBusy || !canSubmit} onClick={() => void updateGeotagTask(task.id, 'visited')}>Mark visited</button>
                      <button className="secondary-action" type="button" disabled={isBusy || !canSubmit || evidenceReference.trim().length < 3} onClick={() => void recordEvidence(task.id)}>Record evidence</button>
                      <button className="primary-action" type="button" disabled={isBusy || !canSubmit} onClick={() => void updateGeotagTask(task.id, 'verified')}>Confirm verified</button>
                      <button className="secondary-action" type="button" disabled={isBusy || !canSubmit} onClick={() => void updateGeotagTask(task.id, 'needs-recapture')}>Needs recapture</button>
                      <button className="danger-action" type="button" disabled={isBusy || !canSubmit} onClick={() => void updateGeotagTask(task.id, 'blocked')}>Blocked</button>
                    </div>
                  </details>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="panel-state">No citizen geotag field checks are currently assigned.</p>
        )}
      </article>

      <article className="public-task-panel civic-panel-blue field-intake-panel">
        <details className="workbench-panel-disclosure" open>
          <summary>
            <span>
              <small className="section-label">Field intake</small>
              <strong>Submit registry evidence from the territory</strong>
            </span>
            <em>{sessionUser?.role ?? 'guest'} role</em>
          </summary>
          <p className="institutional-note compact-note">
            Feeds the live verification queue. Collapse this panel when reviewing recent intake.
          </p>
          {sessionStatus === 'loading' ? <p className="panel-state">Checking access before opening the submission form…</p> : null}
          <form className="territory-form compact-field-form" onSubmit={handleSubmit}>
          <label className="territory-field">
            <span className="territory-label">Assignment</span>
            <select
              className="territory-input"
              value={form.assignment_id}
              onChange={(event) => {
                const assignment = fieldAssignments.find((item) => item.assignment_id === event.target.value);
                setForm({
                  ...form,
                  assignment_id: event.target.value,
                  territory_id: assignment?.territory_id ?? form.territory_id,
                  submitted_by: assignment?.team ?? form.submitted_by,
                });
              }}
            >
              {fieldAssignments.map((assignment) => (
                <option key={assignment.assignment_id} value={assignment.assignment_id}>
                  {assignment.task} · {assignment.team}
                </option>
              ))}
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Territory</span>
            <select className="territory-input" value={form.territory_id} onChange={(event) => setForm({ ...form, territory_id: event.target.value })}>
              {fieldTerritories.map((territory) => (
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
            <button className="verification-button" type="submit" disabled={Boolean(submitDisabledReason)}>
              {submitDisabledReason ?? 'Submit to verification queue'}
            </button>
          </div>
          </form>
          {notice ? <p className="form-notice success">{notice}</p> : null}
          {error ? <p className="form-notice error">{error}</p> : null}
        </details>
      </article>

      <article className="public-task-panel civic-panel-gold live-intake-panel">
        <details className="workbench-panel-disclosure" open>
          <summary>
            <span>
              <small className="section-label">Live intake</small>
              <strong>Recently submitted field records</strong>
            </span>
            <em>{submissions.length} records</em>
          </summary>
        {submissions.length > 0 ? (
          <ul className="mini-list live-intake-list">
            {submissions.map((submission) => (
              <li key={submission.id}>
                <details className="inline-disclosure">
                  <summary>
                    <strong>{submission.candidate_name}</strong>
                    <span>{submission.territory_name} · {submission.submission_type} · {submission.review_status}</span>
                  </summary>
                  <p>{submission.notes || 'No field notes supplied.'}</p>
                  <p>Submitted by {submission.submitted_by}{submission.registry_entity_id ? ` · Registry link: ${submission.registry_entity_id}` : ''}</p>
                </details>
              </li>
            ))}
          </ul>
        ) : (
          <p className="panel-state">No field submissions have been recorded yet.</p>
        )}
        </details>
      </article>
    </section>
  );
}
