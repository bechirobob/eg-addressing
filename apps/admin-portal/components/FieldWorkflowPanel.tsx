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

type SpatialPoint = {
  latitude: number;
  longitude: number;
  accuracy_meters?: number | null;
  role?: 'start' | 'midpoint' | 'end';
};

type GridCell = {
  grid_code: string;
  latitude_cell?: number;
  longitude_cell?: number;
  cell_size_meters?: number;
};

type MapSuggestion = {
  suggested_road_name?: string | null;
  suggested_local_area?: string | null;
  suggested_place_name?: string | null;
  display_name?: string | null;
  source?: string | null;
  source_attribution?: string | null;
  distance_meters?: number | null;
  confidence?: string;
  requires_review?: boolean;
  status?: string;
};

type SpatialEvidence = {
  geometry_type?: 'LineString' | 'Point';
  capture_method?: string;
  points?: SpatialPoint[];
  calculated_length_km?: number;
  latitude?: number;
  longitude?: number;
  accuracy_meters?: number | null;
  road_reference?: string;
  evidence_source?: string;
  accuracy_note?: string;
  grid_cells?: GridCell[];
  map_suggestion?: MapSuggestion;
  stretch_midpoint?: { latitude: number; longitude: number };
  review_confidence?: string;
  review_required?: boolean;
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
  spatial_evidence?: SpatialEvidence | null;
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
  const [form, setForm] = useState({
    assignment_id: fieldAssignments[0]?.assignment_id ?? '',
    territory_id: fieldAssignments[0]?.territory_id ?? fieldTerritories[0]?.id ?? '',
    submission_type: 'road' as 'road' | 'building' | 'address',
    candidate_name: '',
    candidate_status: 'submitted',
    notes: '',
    submitted_by: 'Field team operator',
  });
  const [roadPoints, setRoadPoints] = useState<SpatialPoint[]>([]);
  const [buildingPoint, setBuildingPoint] = useState<SpatialPoint | null>(null);
  const [roadReference, setRoadReference] = useState('');
  const [spatialAnalysis, setSpatialAnalysis] = useState<SpatialEvidence | null>(null);
  const [isCapturingGeometry, setIsCapturingGeometry] = useState(false);
  const [isAnalyzingSpatialEvidence, setIsAnalyzingSpatialEvidence] = useState(false);

  function segmentLengthKm(start: SpatialPoint, end: SpatialPoint) {
    const toRadians = (value: number) => (value * Math.PI) / 180;
    const lat1 = toRadians(start.latitude);
    const lat2 = toRadians(end.latitude);
    const dlat = lat2 - lat1;
    const dlon = toRadians(end.longitude - start.longitude);
    const h = Math.sin(dlat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) ** 2;
    return 6371.0088 * 2 * Math.asin(Math.min(1, Math.sqrt(h)));
  }

  function roadLengthKm(points = roadPoints) {
    if (points.length < 2) return 0;
    return points.slice(1).reduce((sum, point, index) => sum + segmentLengthKm(points[index], point), 0);
  }

  function buildSpatialEvidence(): SpatialEvidence | null {
    if (form.submission_type === 'road') {
      const hasStart = roadPoints.some((point) => point.role === 'start');
      const hasEnd = roadPoints.some((point) => point.role === 'end');
      if (roadPoints.length < 2 || !hasStart || !hasEnd) return null;
      const baseEvidence = {
        geometry_type: 'LineString' as const,
        capture_method: 'browser-gps',
        evidence_source: 'field-operator-gps',
        points: roadPoints.map(({ latitude, longitude, role }) => ({ latitude, longitude, role })),
        calculated_length_km: Number(roadLengthKm().toFixed(3)),
        accuracy_note: roadPoints.map((point) => `${point.role ?? 'point'} ±${Math.round(point.accuracy_meters ?? 0)}m`).join(' · '),
      };
      return spatialAnalysis?.geometry_type === 'LineString' ? { ...baseEvidence, ...spatialAnalysis, points: baseEvidence.points } : baseEvidence;
    }
    if (form.submission_type === 'building') {
      if (!buildingPoint || roadReference.trim().length < 2) return null;
      const baseEvidence = {
        geometry_type: 'Point' as const,
        capture_method: 'browser-gps',
        evidence_source: 'field-operator-gps',
        latitude: buildingPoint.latitude,
        longitude: buildingPoint.longitude,
        accuracy_meters: buildingPoint.accuracy_meters ?? null,
        road_reference: roadReference.trim(),
        accuracy_note: `Captured GPS point ±${Math.round(buildingPoint.accuracy_meters ?? 0)}m`,
      };
      return spatialAnalysis?.geometry_type === 'Point' ? { ...baseEvidence, ...spatialAnalysis } : baseEvidence;
    }
    return {};
  }

  const spatialSubmitDisabledReason = (() => {
    if (!canSubmit) return 'Editor or admin required';
    if (isSubmitting) return 'Submitting…';
    if (form.submission_type === 'road' && !buildSpatialEvidence()) return 'Capture road stretch first';
    if (form.submission_type === 'building' && !buildSpatialEvidence()) return 'Capture building location first';
    return null;
  })();

  function loadPilotSampleStretch() {
    setForm((current) => ({
      ...current,
      submission_type: 'road',
      territory_id: current.territory_id || 'territory-malabo-urban-core',
      candidate_name: current.candidate_name || 'Pilot map/grid assisted road stretch',
      notes: current.notes || 'Pilot sample stretch for map/grid-assisted review demonstration.',
    }));
    setRoadPoints([
      { role: 'start', latitude: 3.7521, longitude: 8.7731, accuracy_meters: 8 },
      { role: 'end', latitude: 3.7534, longitude: 8.7759, accuracy_meters: 9 },
    ]);
    setBuildingPoint(null);
    setRoadReference('');
    setSpatialAnalysis(null);
    setNotice('Pilot road stretch loaded. The system will check the map and grid automatically.');
  }

  async function analyzeSpatialEvidence() {
    if (!token || !canSubmit) {
      setError('Editor or admin access is required to analyze map/grid evidence.');
      return;
    }
    const evidence = buildSpatialEvidence();
    if (!evidence || form.submission_type === 'address') {
      setError('Capture road/building spatial evidence before analysis.');
      return;
    }
    setIsAnalyzingSpatialEvidence(true);
    setError(null);
    setNotice(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/spatial-evidence/enrich`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token) },
        body: JSON.stringify({ territory_id: form.territory_id, submission_type: form.submission_type, spatial_evidence: evidence }),
      });
      const payload = (await response.json()) as { spatial_evidence?: SpatialEvidence; detail?: string };
      if (!response.ok || !payload.spatial_evidence) {
        setError(payload.detail ?? 'Unable to analyze map/grid evidence.');
        return;
      }
      setSpatialAnalysis(payload.spatial_evidence);
      setNotice('Map/grid analysis attached to the evidence bundle.');
    } catch {
      setError('Unable to analyze map/grid evidence.');
    } finally {
      setIsAnalyzingSpatialEvidence(false);
    }
  }

  function roadStartCaptured() {
    return roadPoints.some((point) => point.role === 'start');
  }

  function roadEndCaptured() {
    return roadPoints.some((point) => point.role === 'end');
  }

  function roadStepLabel() {
    if (isCapturingGeometry) return 'Capturing GPS…';
    if (!roadStartCaptured()) return 'Capture road start';
    if (!roadEndCaptured()) return 'Capture road end';
    if (isAnalyzingSpatialEvidence) return 'Checking map and grid…';
    if (!spatialAnalysis) return 'Check map and grid';
    return 'Road stretch ready';
  }

  function buildingStepLabel() {
    if (isCapturingGeometry) return 'Capturing GPS…';
    if (!buildingPoint) return 'Capture building location';
    if (roadReference.trim().length < 2) return 'Add nearby road name';
    if (isAnalyzingSpatialEvidence) return 'Checking map and grid…';
    if (!spatialAnalysis) return 'Check map and grid';
    return 'Building location ready';
  }

  function readinessState() {
    if (form.submission_type === 'address') return { label: 'Ready for verification', tone: 'ok' };
    const evidence = buildSpatialEvidence();
    if (!evidence) return { label: 'Needs location evidence', tone: 'warn' };
    if (!spatialAnalysis) return { label: 'System check pending', tone: 'warn' };
    return { label: 'Ready for verification', tone: 'ok' };
  }

  async function continueRoadCapture() {
    if (!roadStartCaptured()) {
      await captureCurrentPosition('road-start');
      return;
    }
    if (!roadEndCaptured()) {
      await captureCurrentPosition('road-end');
      return;
    }
    if (!spatialAnalysis) await analyzeSpatialEvidence();
  }

  async function continueBuildingCapture() {
    if (!buildingPoint) {
      await captureCurrentPosition('building');
      return;
    }
    if (roadReference.trim().length >= 2 && !spatialAnalysis) await analyzeSpatialEvidence();
  }

  async function captureCurrentPosition(target: 'road-start' | 'road-midpoint' | 'road-end' | 'building') {
    if (!navigator.geolocation) {
      setError('This device/browser cannot capture GPS evidence. Use a field device with location services enabled.');
      return;
    }
    setIsCapturingGeometry(true);
    setError(null);
    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 });
      });
      const point: SpatialPoint = {
        latitude: Number(position.coords.latitude.toFixed(7)),
        longitude: Number(position.coords.longitude.toFixed(7)),
        accuracy_meters: Math.round(position.coords.accuracy),
        role: target === 'road-start' ? 'start' : target === 'road-end' ? 'end' : 'midpoint',
      };
      if (target === 'building') {
        setBuildingPoint(point);
        setSpatialAnalysis(null);
        setNotice('Building GPS point captured.');
      } else {
        setSpatialAnalysis(null);
        setRoadPoints((current) => {
          if (point.role === 'midpoint') return [...current.filter((item) => item.role !== 'end'), point, ...current.filter((item) => item.role === 'end')];
          return [...current.filter((item) => item.role !== point.role), point].sort((a, b) => {
            const order = { start: 0, midpoint: 1, end: 2 } as const;
            return order[a.role ?? 'midpoint'] - order[b.role ?? 'midpoint'];
          });
        });
        setNotice(`${point.role} GPS point captured.`);
      }
    } catch {
      setError('Unable to capture GPS. Check browser location permission and field device signal.');
    } finally {
      setIsCapturingGeometry(false);
    }
  }

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

  useEffect(() => {
    if (!token || !canSubmit || spatialAnalysis || isAnalyzingSpatialEvidence || form.submission_type === 'address') return;
    if (!buildSpatialEvidence()) return;
    void analyzeSpatialEvidence();
  }, [token, canSubmit, spatialAnalysis, isAnalyzingSpatialEvidence, form.submission_type, form.territory_id, roadPoints, buildingPoint, roadReference]);

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
          spatial_evidence: buildSpatialEvidence(),
        }),
      });
      const payload = (await response.json()) as Submission | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to submit field record.');
        return;
      }
      setNotice(`Field submission recorded: ${form.candidate_name}`);
      setForm((current) => ({ ...current, candidate_name: '', notes: '' }));
      setRoadPoints([]);
      setBuildingPoint(null);
      setRoadReference('');
      setSpatialAnalysis(null);
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
            Use this like a field checklist. The system handles GPS, map suggestions, grid cells, and distance in the background.
          </p>
          {sessionStatus === 'loading' ? <p className="panel-state">Checking access before opening the submission form…</p> : null}
          <form className="territory-form compact-field-form human-field-form" onSubmit={handleSubmit}>
            <div className="guided-workflow-strip" aria-label="Field evidence progress">
              <span className="step-chip active">1. Identify</span>
              <span className={buildSpatialEvidence() ? 'step-chip active' : 'step-chip'}>2. Capture location</span>
              <span className={spatialAnalysis || form.submission_type === 'address' ? 'step-chip active' : 'step-chip'}>3. System check</span>
              <span className={spatialSubmitDisabledReason ? 'step-chip' : 'step-chip active'}>4. Submit</span>
            </div>
            <div className="human-form-grid">
              <label className="territory-field">
                <span className="territory-label">What are you registering?</span>
                <select className="territory-input" value={form.submission_type} onChange={(event) => { setForm({ ...form, submission_type: event.target.value as 'road' | 'building' | 'address' }); setRoadPoints([]); setBuildingPoint(null); setSpatialAnalysis(null); }}>
                  <option value="road">Road / street stretch</option>
                  <option value="building">Building / property point</option>
                  <option value="address">Address label only</option>
                </select>
              </label>
              <label className="territory-field">
                <span className="territory-label">Name or label people use</span>
                <input className="territory-input" value={form.candidate_name} onChange={(event) => setForm({ ...form, candidate_name: event.target.value })} placeholder="Example: Airport Road extension" required />
              </label>
            </div>

            <details className="quiet-disclosure compact-review-disclosure">
              <summary>Routing details</summary>
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
                <span className="territory-label">Submitted by</span>
                <input className="territory-input" value={form.submitted_by} onChange={(event) => setForm({ ...form, submitted_by: event.target.value })} required />
              </label>
              <input type="hidden" value={form.candidate_status} readOnly />
            </details>

            {form.submission_type === 'road' ? (
              <div className="territory-field territory-field-wide spatial-evidence-capture human-capture-card">
                <div className="human-capture-head">
                  <span className="territory-label">Road stretch</span>
                  <span className={`readiness-pill ${readinessState().tone}`}>{readinessState().label}</span>
                </div>
                <button className="primary-action guided-primary-action" type="button" disabled={isCapturingGeometry || isAnalyzingSpatialEvidence || Boolean(spatialAnalysis)} onClick={() => void continueRoadCapture()}>{roadStepLabel()}</button>
                <p className="field-help">Stand at the beginning of the stretch, tap once. Move to the end, tap again. The system checks the road name, grid cells, and distance automatically.</p>
                <div className="human-evidence-summary">
                  <strong>{roadStartCaptured() ? 'Start captured' : 'Start needed'} → {roadEndCaptured() ? 'End captured' : 'End needed'}</strong>
                  <span>{spatialAnalysis?.map_suggestion?.suggested_road_name ? `Suggested road: ${spatialAnalysis.map_suggestion.suggested_road_name}` : roadPoints.length >= 2 ? 'System check running or ready to run.' : 'No technical input needed from the worker.'}</span>
                  {spatialAnalysis?.calculated_length_km ? <span>Distance: {spatialAnalysis.calculated_length_km} km · Grid coverage saved for reviewer</span> : null}
                </div>
                <details className="quiet-disclosure technical-evidence-disclosure">
                  <summary>Technical evidence</summary>
                  <div className="calm-action-row">
                    <button className="secondary-action" type="button" disabled={isCapturingGeometry} onClick={() => void captureCurrentPosition('road-midpoint')}>Add midpoint if road bends</button>
                    <button className="secondary-action" type="button" onClick={loadPilotSampleStretch}>Load pilot sample</button>
                    <button className="secondary-action" type="button" disabled={isAnalyzingSpatialEvidence || !buildSpatialEvidence()} onClick={() => void analyzeSpatialEvidence()}>{isAnalyzingSpatialEvidence ? 'Checking…' : 'Recheck system analysis'}</button>
                  </div>
                  {roadPoints.length > 0 ? <p>{roadPoints.map((point) => `${point.role}: ${point.latitude}, ${point.longitude} ±${Math.round(point.accuracy_meters ?? 0)}m`).join(' · ')}</p> : null}
                  {spatialAnalysis ? <p>Grid cells: {spatialAnalysis.grid_cells?.map((cell) => cell.grid_code).join(', ') || 'pending'} · Source: {spatialAnalysis.map_suggestion?.source_attribution || spatialAnalysis.map_suggestion?.source || 'server grid analysis'}</p> : null}
                </details>
              </div>
            ) : null}

            {form.submission_type === 'building' ? (
              <div className="territory-field territory-field-wide spatial-evidence-capture human-capture-card">
                <div className="human-capture-head">
                  <span className="territory-label">Building location</span>
                  <span className={`readiness-pill ${readinessState().tone}`}>{readinessState().label}</span>
                </div>
                <button className="primary-action guided-primary-action" type="button" disabled={isCapturingGeometry || isAnalyzingSpatialEvidence || Boolean(spatialAnalysis && buildingPoint)} onClick={() => void continueBuildingCapture()}>{buildingStepLabel()}</button>
                <label className="territory-field territory-field-wide nested-field">
                  <span className="territory-label">Nearby road or frontage</span>
                  <input className="territory-input" value={roadReference} onChange={(event) => { setRoadReference(event.target.value); setSpatialAnalysis(null); }} placeholder="Road, frontage, or access path observed in the field" />
                </label>
                <p className="field-help">Capture the building point and name the road/frontage. The grid check runs automatically before submission.</p>
                <div className="human-evidence-summary">
                  <strong>{buildingPoint ? 'Building point captured' : 'Building point needed'}</strong>
                  <span>{spatialAnalysis?.grid_cells?.length ? `Grid coverage saved: ${spatialAnalysis.grid_cells.map((cell) => cell.grid_code).join(', ')}` : 'No coordinate typing needed.'}</span>
                </div>
                <details className="quiet-disclosure technical-evidence-disclosure">
                  <summary>Technical evidence</summary>
                  {buildingPoint ? <p>{buildingPoint.latitude}, {buildingPoint.longitude} ±{Math.round(buildingPoint.accuracy_meters ?? 0)}m</p> : null}
                  {spatialAnalysis ? <p>Grid cells: {spatialAnalysis.grid_cells?.map((cell) => cell.grid_code).join(', ') || 'pending'}</p> : null}
                </details>
              </div>
            ) : null}

          <label className="territory-field territory-field-wide">
            <span className="territory-label">Field notes</span>
            <textarea className="territory-input territory-textarea" value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} rows={4} />
          </label>
          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={Boolean(spatialSubmitDisabledReason)}>
              {spatialSubmitDisabledReason ?? 'Submit to verification queue'}
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
