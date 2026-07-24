'use client';

import Link from 'next/link';
import type { FormEvent } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { GovernmentIcon } from './GovernmentIcon';
import { authorizationHeader, csrfHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

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

type EvidenceFile = {
  file_id: string;
  file_name: string;
  content_type: string;
  size_bytes: number;
  access: 'protected';
};

type EvidenceAttachment = {
  type: string;
  reference: string;
  note?: string;
  captured_by?: string;
  captured_at?: string;
  files?: EvidenceFile[];
};

type SpatialEvidence = {
  geometry_type?: 'LineString' | 'Point';
  capture_method?: string;
  evidence_source?: string;
  points?: SpatialPoint[];
  latitude?: number;
  longitude?: number;
  accuracy_meters?: number | null;
  road_reference?: string;
  evidence_attachments?: EvidenceAttachment[];
  grid_cells?: Array<{ grid_code: string }>;
  map_suggestion?: { suggested_road_name?: string | null; confidence?: string; source_attribution?: string | null };
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

type GeotagTask = {
  id: string;
  address_label: string;
  territory_name?: string | null;
  territory_id?: string | null;
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

type PendingSyncItem = {
  id: string;
  created_at: string;
  attempts: number;
  payload: Record<string, unknown>;
};

type QueueMode = 'assignments' | 'location-checks' | 'submissions' | 'sync';

type QueueRecord = {
  key: string;
  id: string;
  label: string;
  territory: string;
  state: string;
  detail: string;
};

const SYNC_STORAGE_KEY = 'egAddressingFieldSyncQueue';

function plainStatus(value?: string | null) {
  return (value || 'unknown').replaceAll('-', ' ').replaceAll('_', ' ');
}

function mapPreviewUrl(latitude: number, longitude: number) {
  const delta = 0.0025;
  return `https://www.openstreetmap.org/export/embed.html?bbox=${longitude - delta}%2C${latitude - delta}%2C${longitude + delta}%2C${latitude + delta}&layer=mapnik&marker=${latitude}%2C${longitude}`;
}

function captureQuality(accuracy?: number | null) {
  if (typeof accuracy !== 'number') return { label: 'Accuracy pending', tone: 'warning' };
  if (accuracy <= 10) return { label: `High accuracy · ±${Math.round(accuracy)} m`, tone: 'success' };
  if (accuracy <= 30) return { label: `Usable accuracy · ±${Math.round(accuracy)} m`, tone: '' };
  return { label: `Recapture advised · ±${Math.round(accuracy)} m`, tone: 'warning' };
}

export function GovernmentFieldOperationsWorkbench({ apiBaseUrl }: { apiBaseUrl: string }) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [tasks, setTasks] = useState<GeotagTask[]>([]);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [territories, setTerritories] = useState<Territory[]>([]);
  const [queueMode, setQueueMode] = useState<QueueMode>('assignments');
  const [selectedKey, setSelectedKey] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [territoryFilter, setTerritoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isOnline, setIsOnline] = useState(true);
  const [syncQueue, setSyncQueue] = useState<PendingSyncItem[]>([]);
  const [taskNote, setTaskNote] = useState('Coordinates and access point checked by the field officer.');
  const [taskEvidenceReference, setTaskEvidenceReference] = useState('FIELD-EVIDENCE-REF-001');
  const [roadPoints, setRoadPoints] = useState<SpatialPoint[]>([]);
  const [buildingPoint, setBuildingPoint] = useState<SpatialPoint | null>(null);
  const [captureForm, setCaptureForm] = useState({
    assignment_id: '',
    territory_id: '',
    submission_type: 'building' as 'road' | 'building' | 'address',
    candidate_name: '',
    candidate_status: 'submitted',
    notes: '',
    submitted_by: 'Field operations officer',
    road_reference: '',
    evidence_reference: 'FIELD-PHOTO-REF-001',
  });

  const canOperate = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';

  function requestHeaders(withJson = false) {
    return {
      ...(withJson ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? authorizationHeader(token) : csrfHeader()),
    };
  }

  const persistSyncQueue = useCallback((next: PendingSyncItem[]) => {
    setSyncQueue(next);
    if (typeof window !== 'undefined') window.localStorage.setItem(SYNC_STORAGE_KEY, JSON.stringify(next));
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    setIsOnline(window.navigator.onLine);
    try {
      const stored = JSON.parse(window.localStorage.getItem(SYNC_STORAGE_KEY) || '[]') as PendingSyncItem[];
      setSyncQueue(Array.isArray(stored) ? stored : []);
    } catch {
      setSyncQueue([]);
    }
    const online = () => setIsOnline(true);
    const offline = () => setIsOnline(false);
    window.addEventListener('online', online);
    window.addEventListener('offline', offline);
    return () => {
      window.removeEventListener('online', online);
      window.removeEventListener('offline', offline);
    };
  }, []);

  const reloadAll = useCallback(async () => {
    if (sessionStatus !== 'ready') return;
    setIsLoading(true);
    setError(null);
    try {
      const request = { credentials: 'include' as const, headers: requestHeaders() };
      const [assignmentResponse, taskResponse, submissionResponse, territoryResponse] = await Promise.all([
        fetch(`${browserApiBaseUrl}/api/v1/field/assignments`, request),
        fetch(`${browserApiBaseUrl}/api/v1/field/geotag-tasks`, request),
        fetch(`${browserApiBaseUrl}/api/v1/field/submissions`, request),
        fetch(`${browserApiBaseUrl}/api/v1/territories`, request),
      ]);
      if (![assignmentResponse, taskResponse, submissionResponse, territoryResponse].every((response) => response.ok)) {
        throw new Error('field-load-failed');
      }
      const assignmentPayload = (await assignmentResponse.json()) as { items?: Assignment[] };
      const taskPayload = (await taskResponse.json()) as { items?: GeotagTask[] };
      const submissionPayload = (await submissionResponse.json()) as { items?: Submission[] };
      const territoryPayload = (await territoryResponse.json()) as { items?: Territory[] };
      const nextAssignments = assignmentPayload.items ?? [];
      const nextTasks = taskPayload.items ?? [];
      const nextSubmissions = submissionPayload.items ?? [];
      const nextTerritories = territoryPayload.items ?? [];
      setAssignments(nextAssignments);
      setTasks(nextTasks);
      setSubmissions(nextSubmissions);
      setTerritories(nextTerritories);
      const firstAssignment = nextAssignments[0];
      const firstTerritory = nextTerritories[0];
      setCaptureForm((current) => ({
        ...current,
        assignment_id: current.assignment_id || firstAssignment?.assignment_id || '',
        territory_id: current.territory_id || firstAssignment?.territory_id || firstTerritory?.id || '',
      }));
    } catch {
      setError('Field assignments and evidence records could not be loaded. Existing device-held work has not been discarded.');
    } finally {
      setIsLoading(false);
    }
  }, [browserApiBaseUrl, sessionStatus, token]);

  useEffect(() => {
    void reloadAll();
  }, [reloadAll]);

  const queueRecords = useMemo<QueueRecord[]>(() => {
    if (queueMode === 'assignments') {
      return assignments.map((item) => ({
        key: `assignment:${item.assignment_id}`,
        id: item.assignment_id,
        label: item.task,
        territory: item.territory,
        state: item.priority,
        detail: item.team,
      }));
    }
    if (queueMode === 'location-checks') {
      return tasks.map((item) => ({
        key: `task:${item.id}`,
        id: item.id,
        label: item.address_label,
        territory: item.territory_name || 'Territory pending',
        state: item.field_status || item.status,
        detail: item.grid_code,
      }));
    }
    if (queueMode === 'submissions') {
      return submissions.map((item) => ({
        key: `submission:${item.id}`,
        id: item.id,
        label: item.candidate_name,
        territory: item.territory_name,
        state: item.review_status,
        detail: plainStatus(item.submission_type),
      }));
    }
    return syncQueue.map((item) => ({
      key: `sync:${item.id}`,
      id: item.id,
      label: String(item.payload.candidate_name || 'Device-held field submission'),
      territory: String(item.payload.territory_id || 'Territory pending'),
      state: 'awaiting sync',
      detail: new Date(item.created_at).toLocaleString(),
    }));
  }, [assignments, queueMode, submissions, syncQueue, tasks]);

  const normalizedSearch = searchQuery.trim().toLowerCase();
  const visibleRecords = useMemo(() => queueRecords.filter((item) => {
    if (territoryFilter !== 'all' && !item.territory.toLowerCase().includes(territoryFilter.toLowerCase())) return false;
    if (statusFilter !== 'all' && plainStatus(item.state).toLowerCase() !== statusFilter) return false;
    if (!normalizedSearch) return true;
    return [item.id, item.label, item.territory, item.state, item.detail].some((value) => value.toLowerCase().includes(normalizedSearch));
  }), [normalizedSearch, queueRecords, statusFilter, territoryFilter]);

  useEffect(() => {
    if (!visibleRecords.length) {
      setSelectedKey('');
      return;
    }
    if (!visibleRecords.some((item) => item.key === selectedKey)) setSelectedKey(visibleRecords[0].key);
  }, [queueMode, visibleRecords, selectedKey]);

  const selectedRecord = visibleRecords.find((item) => item.key === selectedKey) ?? visibleRecords[0] ?? null;
  const selectedAssignment = selectedRecord?.key.startsWith('assignment:') ? assignments.find((item) => item.assignment_id === selectedRecord.id) ?? null : null;
  const selectedTask = selectedRecord?.key.startsWith('task:') ? tasks.find((item) => item.id === selectedRecord.id) ?? null : null;
  const selectedSubmission = selectedRecord?.key.startsWith('submission:') ? submissions.find((item) => item.id === selectedRecord.id) ?? null : null;
  const selectedSync = selectedRecord?.key.startsWith('sync:') ? syncQueue.find((item) => item.id === selectedRecord.id) ?? null : null;

  useEffect(() => {
    if (selectedAssignment) {
      setCaptureForm((current) => ({ ...current, assignment_id: selectedAssignment.assignment_id, territory_id: selectedAssignment.territory_id }));
    }
    if (selectedTask) {
      setCaptureForm((current) => ({
        ...current,
        assignment_id: '',
        territory_id: selectedTask.territory_id || current.territory_id,
        candidate_name: current.candidate_name || selectedTask.address_label,
        submission_type: 'building',
        road_reference: current.road_reference || selectedTask.landmark || '',
      }));
      setBuildingPoint({ latitude: selectedTask.latitude, longitude: selectedTask.longitude, accuracy_meters: selectedTask.accuracy_meters ?? null });
    }
  }, [selectedAssignment?.assignment_id, selectedTask?.id]);

  const statusOptions = Array.from(new Set(queueRecords.map((item) => plainStatus(item.state).toLowerCase()))).sort();
  const territoryOptions = Array.from(new Set(queueRecords.map((item) => item.territory).filter(Boolean))).sort();
  const selectedAccuracy = selectedTask?.accuracy_meters ?? buildingPoint?.accuracy_meters ?? selectedSubmission?.spatial_evidence?.accuracy_meters ?? selectedSubmission?.spatial_evidence?.points?.[0]?.accuracy_meters ?? null;
  const accuracyState = captureQuality(selectedAccuracy);
  const pendingReviewCount = submissions.filter((item) => ['submitted', 'under-review'].includes(item.review_status)).length;

  function buildSpatialEvidence(): SpatialEvidence | Record<string, never> | null {
    const attachment = captureForm.evidence_reference.trim().length >= 3
      ? [{
          type: 'photo-reference',
          reference: captureForm.evidence_reference.trim(),
          note: captureForm.notes.trim(),
          captured_by: captureForm.submitted_by.trim(),
          captured_at: new Date().toISOString(),
        }]
      : [];
    if (captureForm.submission_type === 'road') {
      const start = roadPoints.find((point) => point.role === 'start');
      const end = roadPoints.find((point) => point.role === 'end');
      if (!start || !end) return null;
      return {
        geometry_type: 'LineString',
        capture_method: 'browser-gps',
        evidence_source: 'government-field-workspace',
        points: roadPoints,
        evidence_attachments: attachment,
      };
    }
    if (captureForm.submission_type === 'building') {
      if (!buildingPoint || captureForm.road_reference.trim().length < 2) return null;
      return {
        geometry_type: 'Point',
        capture_method: 'browser-gps',
        evidence_source: 'government-field-workspace',
        latitude: buildingPoint.latitude,
        longitude: buildingPoint.longitude,
        accuracy_meters: buildingPoint.accuracy_meters ?? null,
        road_reference: captureForm.road_reference.trim(),
        evidence_attachments: attachment,
      };
    }
    return {};
  }

  async function capturePosition(target: 'start' | 'end' | 'building') {
    if (!canOperate) {
      setError('Editor or administrator authority is required to capture official field evidence.');
      return;
    }
    if (!navigator.geolocation) {
      setError('This device cannot provide GNSS coordinates. Use an authorized field device with location services enabled.');
      return;
    }
    setBusyAction(`capture-${target}`);
    setError(null);
    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: true, timeout: 20_000, maximumAge: 0 });
      });
      const point: SpatialPoint = {
        latitude: Number(position.coords.latitude.toFixed(7)),
        longitude: Number(position.coords.longitude.toFixed(7)),
        accuracy_meters: Math.round(position.coords.accuracy),
        role: target === 'building' ? undefined : target,
      };
      if (target === 'building') setBuildingPoint(point);
      else setRoadPoints((current) => [...current.filter((item) => item.role !== target), point].sort((a, b) => (a.role === 'start' ? -1 : b.role === 'start' ? 1 : 0)));
      setNotice(`${target === 'building' ? 'Building location' : `Road ${target}`} captured with ±${Math.round(position.coords.accuracy)} m accuracy.`);
    } catch {
      setError('GNSS capture failed. Check device permission, signal, and field safety before retrying.');
    } finally {
      setBusyAction(null);
    }
  }

  function queueSubmission(payload: Record<string, unknown>) {
    const next: PendingSyncItem = {
      id: `pending-${Date.now()}`,
      created_at: new Date().toISOString(),
      attempts: 0,
      payload,
    };
    persistSyncQueue([...syncQueue, next]);
    setQueueMode('sync');
    setSelectedKey(`sync:${next.id}`);
    setNotice('Submission saved on this authorized device for later synchronization. It has not entered the national registry yet.');
  }

  async function postSubmission(payload: Record<string, unknown>) {
    const response = await fetch(`${browserApiBaseUrl}/api/v1/field/submissions`, {
      method: 'POST',
      credentials: 'include',
      headers: requestHeaders(true),
      body: JSON.stringify(payload),
    });
    const result = (await response.json()) as Submission | { detail?: string };
    if (!response.ok) throw new Error('detail' in result && result.detail ? result.detail : 'The field service rejected the submission.');
    return result as Submission;
  }

  async function submitCapture(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canOperate) {
      setError('Editor or administrator authority is required to submit field evidence.');
      return;
    }
    const evidence = buildSpatialEvidence();
    if (evidence === null) {
      setError(captureForm.submission_type === 'road' ? 'Capture both road endpoints before submitting.' : 'Capture the building location and enter its road reference before submitting.');
      return;
    }
    const payload: Record<string, unknown> = {
      assignment_id: captureForm.assignment_id || null,
      territory_id: captureForm.territory_id,
      submission_type: captureForm.submission_type,
      candidate_name: captureForm.candidate_name.trim(),
      candidate_status: captureForm.candidate_status,
      notes: captureForm.notes.trim(),
      submitted_by: captureForm.submitted_by.trim(),
      spatial_evidence: evidence,
    };
    if (!isOnline) {
      queueSubmission(payload);
      return;
    }
    setBusyAction('submit-capture');
    setNotice(null);
    setError(null);
    try {
      const result = await postSubmission(payload);
      setNotice(`Field submission recorded: ${result.candidate_name}. Verification now owns the next authoritative decision.`);
      setCaptureForm((current) => ({ ...current, candidate_name: '', notes: '' }));
      setRoadPoints([]);
      setBuildingPoint(null);
      await reloadAll();
      setQueueMode('submissions');
      setSelectedKey(`submission:${result.id}`);
    } catch (err) {
      if (!navigator.onLine || err instanceof TypeError) {
        queueSubmission(payload);
      } else {
        setError(err instanceof Error ? err.message : 'The field submission could not be completed.');
      }
    } finally {
      setBusyAction(null);
    }
  }

  async function retrySync(item: PendingSyncItem) {
    if (!canOperate || !isOnline) {
      setError(!isOnline ? 'Network connection is required before device-held work can synchronize.' : 'Editor or administrator authority is required to synchronize field work.');
      return;
    }
    setBusyAction(`sync-${item.id}`);
    setError(null);
    try {
      const result = await postSubmission(item.payload);
      persistSyncQueue(syncQueue.filter((candidate) => candidate.id !== item.id));
      setNotice(`Device-held submission synchronized: ${result.candidate_name}.`);
      await reloadAll();
      setQueueMode('submissions');
      setSelectedKey(`submission:${result.id}`);
    } catch (err) {
      const next = syncQueue.map((candidate) => candidate.id === item.id ? { ...candidate, attempts: candidate.attempts + 1 } : candidate);
      persistSyncQueue(next);
      setError(err instanceof Error ? err.message : 'Synchronization failed. The device-held copy remains available.');
    } finally {
      setBusyAction(null);
    }
  }

  async function updateTaskStatus(status: 'visited' | 'verified' | 'needs-recapture' | 'blocked') {
    if (!selectedTask || !canOperate) {
      setError('Select a location check and confirm editor or administrator authority.');
      return;
    }
    setBusyAction(`task-${status}`);
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/geotag-tasks/${encodeURIComponent(selectedTask.id)}/status`, {
        method: 'POST',
        credentials: 'include',
        headers: requestHeaders(true),
        body: JSON.stringify({ field_status: status, field_note: taskNote }),
      });
      const result = (await response.json()) as GeotagTask | { detail?: string };
      if (!response.ok) throw new Error('detail' in result && result.detail ? result.detail : 'The field-check status was not accepted.');
      setNotice(`${selectedTask.address_label}: ${plainStatus(status)} recorded.`);
      await reloadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The field-check status could not be recorded.');
    } finally {
      setBusyAction(null);
    }
  }

  async function recordTaskEvidence() {
    if (!selectedTask || !canOperate) {
      setError('Select a location check and confirm editor or administrator authority.');
      return;
    }
    setBusyAction('task-evidence');
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/geotag-tasks/${encodeURIComponent(selectedTask.id)}/evidence`, {
        method: 'POST',
        credentials: 'include',
        headers: requestHeaders(true),
        body: JSON.stringify({ evidence_type: 'photo-reference', evidence_reference: taskEvidenceReference, evidence_note: taskNote }),
      });
      const result = (await response.json()) as { detail?: string };
      if (!response.ok) throw new Error(result.detail || 'The evidence reference was not accepted.');
      setNotice(`Evidence reference recorded for ${selectedTask.address_label}.`);
      await reloadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The evidence reference could not be recorded.');
    } finally {
      setBusyAction(null);
    }
  }

  async function uploadEvidenceFile(file: File | null) {
    if (!file || !selectedSubmission || !canOperate) return;
    setBusyAction('evidence-upload');
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/field/submissions/${encodeURIComponent(selectedSubmission.id)}/evidence-files?attachment_index=0&file_name=${encodeURIComponent(file.name)}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': file.type || 'application/octet-stream', ...(token ? authorizationHeader(token) : csrfHeader()) },
        body: file,
      });
      const result = (await response.json()) as { detail?: string };
      if (!response.ok) throw new Error(result.detail || 'The protected evidence file was not accepted.');
      setNotice(`Protected evidence uploaded: ${file.name}.`);
      await reloadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The protected evidence file could not be uploaded.');
    } finally {
      setBusyAction(null);
    }
  }

  const captureReady = buildSpatialEvidence() !== null && captureForm.candidate_name.trim().length > 0 && captureForm.territory_id.length > 0;

  return (
    <section className="government-operation-page government-field-workbench" aria-labelledby="field-workbench-title">
      <header className="government-operation-header">
        <div>
          <p>Territorial service delivery</p>
          <h1 id="field-workbench-title">Field Operations</h1>
          <span>Coordinate assignments, inspect mapped locations, capture GNSS evidence, and synchronize verified field work into the protected review flow.</span>
        </div>
        <div className="government-operation-header-actions">
          <Link href="/verify"><GovernmentIcon name="verification" />Open verification</Link>
          <button type="button" onClick={() => void reloadAll()} disabled={isLoading}><GovernmentIcon name="operations" />{isLoading ? 'Refreshing' : 'Refresh operations'}</button>
        </div>
      </header>

      <dl className="government-operation-summary" aria-label="Field operations summary">
        <div><dt>Assignments</dt><dd>{assignments.length}</dd><span>Territorial work orders</span></div>
        <div><dt>Location checks</dt><dd>{tasks.length}</dd><span>Citizen-originated inspections</span></div>
        <div><dt>Awaiting review</dt><dd>{pendingReviewCount}</dd><span>Submitted to verification</span></div>
        <div><dt>Device sync</dt><dd>{syncQueue.length}</dd><span>{isOnline ? 'Connection available' : 'Offline mode active'}</span></div>
        <div><dt>GNSS state</dt><dd className="government-summary-text-value">{accuracyState.label}</dd><span>Selected or captured location</span></div>
      </dl>

      <div className="government-command-bar government-field-command-bar" aria-label="Field operations filters">
        <label className="government-search-field"><GovernmentIcon name="search" /><span className="sr-only">Search field work</span><input type="search" value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Search assignment, address, team, territory, or case" /></label>
        <label><span>Work queue</span><select value={queueMode} onChange={(event) => { setQueueMode(event.target.value as QueueMode); setStatusFilter('all'); }}><option value="assignments">Assignments</option><option value="location-checks">Location checks</option><option value="submissions">Recent submissions</option><option value="sync">Device sync queue</option></select></label>
        <label><span>Territory</span><select value={territoryFilter} onChange={(event) => setTerritoryFilter(event.target.value)}><option value="all">All territories</option>{territoryOptions.map((territory) => <option key={territory} value={territory}>{territory}</option>)}</select></label>
        <label><span>Status</span><select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="all">All states</option>{statusOptions.map((status) => <option key={status} value={status}>{plainStatus(status)}</option>)}</select></label>
        <div className={`government-command-note ${isOnline ? 'success' : ''}`}><GovernmentIcon name={isOnline ? 'readiness' : 'alert'} /><span>{isOnline ? 'Online · authorized synchronization available' : 'Offline · new work stays on this device until synchronized'}</span></div>
      </div>

      {sessionStatus === 'loading' ? <p className="government-inline-state">Resolving field authority and loading assignments…</p> : null}
      {notice ? <p className="government-inline-state success" role="status">{notice}</p> : null}
      {error ? <p className="government-inline-state error" role="alert">{error}</p> : null}

      <div className="government-three-pane-workbench">
        <aside className="government-queue-pane" aria-label="Field operations queue">
          <div className="government-pane-heading"><div><p>Operational queue</p><h2>{queueMode === 'location-checks' ? 'Location checks' : queueMode === 'submissions' ? 'Recent submissions' : queueMode === 'sync' ? 'Device-held work' : 'Assignments'}</h2></div><span>{visibleRecords.length} shown</span></div>
          <div className="government-record-queue">
            {visibleRecords.length ? visibleRecords.map((record) => (
              <button key={record.key} className={selectedRecord?.key === record.key ? 'active' : ''} type="button" onClick={() => setSelectedKey(record.key)}>
                <span className="government-queue-record-title">{record.label}</span>
                <code>{record.id}</code>
                <span>{record.territory} · {record.detail}</span>
                <small className={`government-record-state ${plainStatus(record.state).includes('verified') ? 'success' : plainStatus(record.state).includes('blocked') || plainStatus(record.state).includes('recapture') ? 'warning' : ''}`}>{plainStatus(record.state)}</small>
              </button>
            )) : <div className="government-pane-empty"><GovernmentIcon name="field" /><strong>No matching field work</strong><span>Change the queue or filters. Device-held work remains available when offline.</span></div>}
          </div>
        </aside>

        <article className="government-record-pane" aria-label="Selected field operation">
          {selectedRecord ? (
            <>
              <header className="government-selected-record-header"><div><p>{selectedAssignment ? 'Territorial assignment' : selectedTask ? 'Citizen location check' : selectedSubmission ? 'Field submission' : 'Device-held submission'}</p><h2>{selectedRecord.label}</h2><code>{selectedRecord.id}</code></div><span className={`government-record-state ${accuracyState.tone}`}>{selectedTask || selectedSubmission ? accuracyState.label : plainStatus(selectedRecord.state)}</span></header>
              <nav className="government-record-tabs" aria-label="Field record sections"><span className="active">Work context</span><span>Map</span><span>Evidence</span><span>Synchronization</span></nav>
              <div className="government-record-body">
                <section><div className="government-record-section-heading"><h3>Assignment and authority context</h3><span>Loaded from protected field services</span></div>
                  <dl className="government-record-facts">
                    <div><dt>Territory</dt><dd>{selectedRecord.territory}</dd></div>
                    <div><dt>Operational state</dt><dd>{plainStatus(selectedRecord.state)}</dd></div>
                    {selectedAssignment ? <><div><dt>Assigned team</dt><dd>{selectedAssignment.team}</dd></div><div><dt>Priority</dt><dd>{plainStatus(selectedAssignment.priority)}</dd></div><div><dt>Task</dt><dd>{selectedAssignment.task}</dd></div><div><dt>Assignment ID</dt><dd>{selectedAssignment.assignment_id}</dd></div></> : null}
                    {selectedTask ? <><div><dt>Grid code</dt><dd>{selectedTask.grid_code}</dd></div><div><dt>Landmark</dt><dd>{selectedTask.landmark || 'Not supplied'}</dd></div><div><dt>Coordinates</dt><dd>{selectedTask.latitude}, {selectedTask.longitude}</dd></div><div><dt>Field note</dt><dd>{selectedTask.field_note || 'No field note recorded'}</dd></div></> : null}
                    {selectedSubmission ? <><div><dt>Submission type</dt><dd>{plainStatus(selectedSubmission.submission_type)}</dd></div><div><dt>Submitted by</dt><dd>{selectedSubmission.submitted_by}</dd></div><div><dt>Review state</dt><dd>{plainStatus(selectedSubmission.review_status)}</dd></div><div><dt>Registry link</dt><dd>{selectedSubmission.registry_entity_id || 'Awaiting verification'}</dd></div></> : null}
                    {selectedSync ? <><div><dt>Saved on device</dt><dd>{new Date(selectedSync.created_at).toLocaleString()}</dd></div><div><dt>Sync attempts</dt><dd>{selectedSync.attempts}</dd></div><div><dt>National state</dt><dd>Not submitted</dd></div><div><dt>Device protection</dt><dd>Retained until accepted or removed</dd></div></> : null}
                  </dl>
                </section>

                {(selectedTask || selectedSubmission?.spatial_evidence?.latitude || selectedSubmission?.spatial_evidence?.points?.[0]) ? (
                  <section><div className="government-record-section-heading"><h3>Mapped location</h3><span>Operational map reference; authoritative geometry remains in the evidence record</span></div>
                    {selectedTask ? <iframe className="government-field-map" title={`Map for ${selectedTask.address_label}`} src={mapPreviewUrl(selectedTask.latitude, selectedTask.longitude)} loading="lazy" /> : null}
                    {!selectedTask && selectedSubmission?.spatial_evidence?.latitude && selectedSubmission.spatial_evidence.longitude ? <iframe className="government-field-map" title={`Map for ${selectedSubmission.candidate_name}`} src={mapPreviewUrl(selectedSubmission.spatial_evidence.latitude, selectedSubmission.spatial_evidence.longitude)} loading="lazy" /> : null}
                    {!selectedTask && selectedSubmission?.spatial_evidence?.points?.[0] ? <iframe className="government-field-map" title={`Map for ${selectedSubmission.candidate_name}`} src={mapPreviewUrl(selectedSubmission.spatial_evidence.points[0].latitude, selectedSubmission.spatial_evidence.points[0].longitude)} loading="lazy" /> : null}
                  </section>
                ) : <section><div className="government-record-section-heading"><h3>Mapped location</h3><span>Coordinates will appear after field capture</span></div><div className="government-pane-empty compact"><GovernmentIcon name="mapping" /><strong>No coordinate attached to this work item</strong><span>Use the controlled capture tools before submitting evidence.</span></div></section>}

                <section><div className="government-record-section-heading"><h3>Evidence readiness</h3><span>Automation checks evidence completeness; operators remain responsible for truth and safety</span></div>
                  <div className={`government-evidence-assessment ${selectedAccuracy != null && selectedAccuracy <= 30 ? 'success' : ''}`}><GovernmentIcon name={selectedAccuracy != null && selectedAccuracy <= 30 ? 'readiness' : 'alert'} /><div><strong>{accuracyState.label}</strong><span>{selectedSubmission?.notes || selectedTask?.field_note || selectedAssignment?.task || 'Capture notes and protected evidence before handoff.'}</span></div></div>
                  {selectedSubmission?.spatial_evidence?.evidence_attachments?.length ? <div className="government-evidence-files government-field-evidence-list">{selectedSubmission.spatial_evidence.evidence_attachments.map((attachment, index) => <div className="government-evidence-group" key={`${attachment.reference}-${index}`}><div><strong>{attachment.reference}</strong><span>{plainStatus(attachment.type)} · {attachment.captured_by || 'Field operator'}</span><small>{attachment.note || 'No evidence note supplied.'}</small></div><p>{attachment.files?.length ?? 0} protected file(s) attached</p></div>)}</div> : null}
                </section>
              </div>
            </>
          ) : <div className="government-pane-empty large"><GovernmentIcon name="field" /><strong>Select field work</strong><span>The assignment, map, evidence state, and valid next action will appear here.</span></div>}
        </article>

        <aside className="government-decision-pane" aria-label="Field operation actions">
          <div className="government-pane-heading"><div><p>Field control</p><h2>Valid next actions</h2></div><span>{canOperate ? 'Field authority' : 'Read only'}</span></div>
          <div className="government-decision-body">
            {selectedTask ? <section><h3>Location-check decision</h3><label className="government-note-field"><span>Field note retained with the task</span><textarea rows={4} value={taskNote} onChange={(event) => setTaskNote(event.target.value)} /></label><div className="government-action-stack government-field-task-actions"><button className="primary" type="button" onClick={() => void updateTaskStatus('verified')} disabled={!canOperate || Boolean(busyAction)}>Mark verified</button><button type="button" onClick={() => void updateTaskStatus('visited')} disabled={!canOperate || Boolean(busyAction)}>Record visit</button><button type="button" onClick={() => void updateTaskStatus('needs-recapture')} disabled={!canOperate || Boolean(busyAction)}>Request recapture</button><button className="danger" type="button" onClick={() => void updateTaskStatus('blocked')} disabled={!canOperate || Boolean(busyAction)}>Record blocked access</button></div><label className="government-field-inline-label"><span>Evidence reference</span><input value={taskEvidenceReference} onChange={(event) => setTaskEvidenceReference(event.target.value)} /></label><button className="government-field-secondary-button" type="button" onClick={() => void recordTaskEvidence()} disabled={!canOperate || Boolean(busyAction) || taskEvidenceReference.trim().length < 3}>Record evidence reference</button></section> : null}

            {selectedSync ? <section><h3>Device synchronization</h3><div className="government-action-stack"><button className="primary" type="button" onClick={() => void retrySync(selectedSync)} disabled={!canOperate || !isOnline || Boolean(busyAction)}>{!isOnline ? 'Waiting for connection' : busyAction ? 'Synchronizing…' : 'Synchronize now'}</button><button className="danger" type="button" onClick={() => { persistSyncQueue(syncQueue.filter((item) => item.id !== selectedSync.id)); setNotice('Device-held submission removed. No national record was created.'); }} disabled={Boolean(busyAction)}>Remove device-held copy</button></div></section> : null}

            {selectedSubmission ? <section><h3>Protected evidence upload</h3><label className="government-field-file-input"><span>Attach file to the first evidence reference</span><input type="file" accept="image/jpeg,image/png,application/pdf" onChange={(event) => void uploadEvidenceFile(event.target.files?.[0] ?? null)} disabled={!canOperate || Boolean(busyAction)} /></label><div className="government-action-stack"><Link className="primary" href="/verify">Open verification decision</Link>{selectedSubmission.registry_entity_id ? <Link href={`/registry?entity=${encodeURIComponent(selectedSubmission.registry_entity_id)}`}>Open registry record</Link> : null}</div></section> : null}

            {!selectedSync ? <section><h3>Capture and submit field record</h3><form className="government-create-form government-field-capture-form" onSubmit={submitCapture}>
              <label><span>Assignment</span><select value={captureForm.assignment_id} onChange={(event) => { const assignment = assignments.find((item) => item.assignment_id === event.target.value); setCaptureForm((current) => ({ ...current, assignment_id: event.target.value, territory_id: assignment?.territory_id || current.territory_id })); }}><option value="">Unassigned field case</option>{assignments.map((assignment) => <option key={assignment.assignment_id} value={assignment.assignment_id}>{assignment.task} · {assignment.team}</option>)}</select></label>
              <label><span>Territory</span><select required value={captureForm.territory_id} onChange={(event) => setCaptureForm((current) => ({ ...current, territory_id: event.target.value }))}><option value="">Select territory</option>{territories.map((territory) => <option key={territory.id} value={territory.id}>{territory.name}</option>)}</select></label>
              <label><span>Record type</span><select value={captureForm.submission_type} onChange={(event) => { setCaptureForm((current) => ({ ...current, submission_type: event.target.value as 'road' | 'building' | 'address' })); setRoadPoints([]); setBuildingPoint(null); }}><option value="road">Road</option><option value="building">Building</option><option value="address">Address</option></select></label>
              <label><span>Candidate name</span><input required value={captureForm.candidate_name} onChange={(event) => setCaptureForm((current) => ({ ...current, candidate_name: event.target.value }))} /></label>
              {captureForm.submission_type === 'building' ? <label><span>Road reference</span><input required value={captureForm.road_reference} onChange={(event) => setCaptureForm((current) => ({ ...current, road_reference: event.target.value }))} /></label> : null}
              <label><span>Evidence reference</span><input value={captureForm.evidence_reference} onChange={(event) => setCaptureForm((current) => ({ ...current, evidence_reference: event.target.value }))} /></label>
              <label><span>Field notes</span><textarea rows={3} value={captureForm.notes} onChange={(event) => setCaptureForm((current) => ({ ...current, notes: event.target.value }))} /></label>
              {captureForm.submission_type === 'road' ? <div className="government-field-capture-controls"><button type="button" onClick={() => void capturePosition('start')} disabled={!canOperate || Boolean(busyAction)}>{roadPoints.some((point) => point.role === 'start') ? 'Recapture road start' : 'Capture road start'}</button><button type="button" onClick={() => void capturePosition('end')} disabled={!canOperate || Boolean(busyAction)}>{roadPoints.some((point) => point.role === 'end') ? 'Recapture road end' : 'Capture road end'}</button></div> : null}
              {captureForm.submission_type === 'building' ? <button type="button" className="government-field-capture-location" onClick={() => void capturePosition('building')} disabled={!canOperate || Boolean(busyAction)}>{buildingPoint ? `Recapture location · ±${Math.round(buildingPoint.accuracy_meters ?? 0)} m` : 'Capture building location'}</button> : null}
              <button type="submit" disabled={!canOperate || !captureReady || Boolean(busyAction)}>{!canOperate ? 'Editor or administrator required' : !captureReady ? 'Complete required capture fields' : !isOnline ? 'Save securely for synchronization' : busyAction === 'submit-capture' ? 'Submitting…' : 'Submit to verification'}</button>
            </form></section> : null}

            <section className="government-authority-note"><GovernmentIcon name="alert" /><div><strong>Field capture does not create a public address</strong><span>Submitted evidence enters Verification. Registry promotion and public release remain separate, controlled authority decisions.</span></div></section>
          </div>
        </aside>
      </div>
    </section>
  );
}
