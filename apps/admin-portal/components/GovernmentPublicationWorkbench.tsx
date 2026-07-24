'use client';

import Link from 'next/link';
import type { FormEvent } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { GovernmentIcon } from './GovernmentIcon';
import { authorizationHeader, csrfHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

type QualityFlags = {
  accuracy_level: string;
  accuracy_label: string;
  requires_field_check: boolean;
  duplicate_code: boolean;
  possible_duplicate: boolean;
  recommended_action: string;
};

type GeotagSubmission = {
  id: string;
  territory_id?: string | null;
  territory_name?: string | null;
  address_label: string;
  citizen_name?: string | null;
  dip_masked?: string | null;
  identity_verification_status?: string | null;
  identity_document_verified?: boolean | null;
  landmark: string;
  latitude: number;
  longitude: number;
  accuracy_meters?: number | null;
  capture_method: string;
  grid_code: string;
  status: string;
  duplicate_hint: string;
  quality_flags?: QualityFlags;
  reviewer_note: string;
  field_submission_id?: string | null;
  signage_batch?: string | null;
  suggested_road_name?: string | null;
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
    field_work?: { required: boolean; status: string; field_submission_id?: string | null };
    signage?: { ready: boolean; batch?: string | null; export_status: string };
    integration?: { api_record_state: string; partner_api_ready: boolean };
  };
};

type Address = {
  id: string;
  formatted: string;
  territory_name: string;
  status: string;
  publication_state: string;
  is_archived: boolean;
};

type ImportJob = {
  id: string;
  name: string;
  source_name: string;
  status: string;
  imported_count: number;
  total_rows: number;
  valid_rows: number;
};

type PublicationPack = {
  id: string;
  name: string;
  status: string;
  audience: string;
  address_count: number;
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

type DuplicateGroup = {
  grid_code: string;
  count: number;
  active_count: number;
  resolved_count: number;
};

type AutomationSummary = {
  sla?: {
    items_tracked: number;
    on_time: number;
    approaching: number;
    overdue: number;
    unknown: number;
  };
  publication_hold?: {
    registry_ready: number;
    public_release_locked: boolean;
    oldest_days: number;
    oldest_hours: number;
    note: string;
  };
};

type PublicationSimulation = {
  submission_id: string;
  address_code?: string;
  simulation_status: string;
  public_release_locked: boolean;
  physical_signage_locked: boolean;
  resulting_record_status: string;
  operator_note: string;
};

type CertificateResult = {
  certificate_id: string;
  address_code: string;
  address_label: string;
  status: string;
  qr_payload: string;
  html: string;
};

type Section = 'review' | 'release' | 'outputs' | 'intake';

type QueueRecord = {
  key: string;
  id: string;
  label: string;
  territory: string;
  state: string;
  detail: string;
};

function plainStatus(value?: string | null) {
  return (value || 'unknown').replaceAll('-', ' ').replaceAll('_', ' ');
}

function mapPreviewUrl(latitude: number, longitude: number) {
  const delta = 0.0025;
  return `https://www.openstreetmap.org/export/embed.html?bbox=${longitude - delta}%2C${latitude - delta}%2C${longitude + delta}%2C${latitude + delta}&layer=mapnik&marker=${latitude}%2C${longitude}`;
}

function qualityLabel(submission: GeotagSubmission) {
  if (submission.quality_flags?.requires_field_check) return 'Field confirmation required';
  if (submission.quality_flags?.possible_duplicate) return 'Duplicate decision required';
  return submission.quality_flags?.accuracy_label || 'Quality review pending';
}

function releaseCandidate(submission: GeotagSubmission) {
  return submission.status === 'registry-ready';
}

export function GovernmentPublicationWorkbench({
  apiBaseUrl,
  initialSection = 'review',
}: {
  apiBaseUrl: string;
  initialSection?: Section;
}) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const publicationReleaseEnabled = process.env.NEXT_PUBLIC_PUBLICATION_RELEASE_ENABLED === 'true';
  const [section, setSection] = useState<Section>(initialSection);
  const [submissions, setSubmissions] = useState<GeotagSubmission[]>([]);
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [importJobs, setImportJobs] = useState<ImportJob[]>([]);
  const [packs, setPacks] = useState<PublicationPack[]>([]);
  const [exportRows, setExportRows] = useState<SignageRow[]>([]);
  const [duplicateGroups, setDuplicateGroups] = useState<DuplicateGroup[]>([]);
  const [automation, setAutomation] = useState<AutomationSummary | null>(null);
  const [selectedKey, setSelectedKey] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [territoryFilter, setTerritoryFilter] = useState('all');
  const [reviewNote, setReviewNote] = useState('Reviewed against location, identity, duplicate, and release-readiness controls.');
  const [roadName, setRoadName] = useState('');
  const [dipFull, setDipFull] = useState('');
  const [duplicateAction, setDuplicateAction] = useState('send-field-verification');
  const [selectedAddressIds, setSelectedAddressIds] = useState<string[]>([]);
  const [packForm, setPackForm] = useState({ name: 'Official addressing publication pack', audience: 'Government and approved institutional partners' });
  const [simulationForm, setSimulationForm] = useState({ submission_id: '', note: 'Controlled release simulation for institutional review.' });
  const [publishForm, setPublishForm] = useState({ submission_id: '', note: 'Institutional release approval confirmed for public publication.' });
  const [simulation, setSimulation] = useState<PublicationSimulation | null>(null);
  const [intakeForm, setIntakeForm] = useState({ name: 'Controlled registry intake', source_name: 'authorized_registry_intake.csv', territory_id: '', submission_type: 'road', candidate_name: '', notes: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canPrepare = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';
  const canPublish = sessionUser?.role === 'admin' && publicationReleaseEnabled;

  function requestHeaders(withJson = false) {
    return {
      ...(withJson ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? authorizationHeader(token) : csrfHeader()),
    };
  }

  const reload = useCallback(async () => {
    if (sessionStatus !== 'ready') return;
    setIsLoading(true);
    setError(null);
    try {
      const request = { credentials: 'include' as const, headers: requestHeaders() };
      const [submissionResponse, addressResponse, jobResponse, packResponse, exportResponse, duplicateResponse, automationResponse] = await Promise.all([
        fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions`, request),
        fetch(`${browserApiBaseUrl}/api/v1/addresses`, request),
        fetch(`${browserApiBaseUrl}/api/v1/imports/jobs`, request),
        fetch(`${browserApiBaseUrl}/api/v1/publication/packs`, request),
        fetch(`${browserApiBaseUrl}/api/v1/signage/export`, request),
        fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/duplicates/summary`, request),
        fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/automation/summary`, request),
      ]);
      if (![submissionResponse, addressResponse, jobResponse, packResponse, exportResponse, duplicateResponse, automationResponse].every((response) => response.ok)) throw new Error('publication-load-failed');
      const submissionPayload = (await submissionResponse.json()) as { items?: GeotagSubmission[] };
      const addressPayload = (await addressResponse.json()) as { items?: Address[] };
      const jobPayload = (await jobResponse.json()) as { items?: ImportJob[] };
      const packPayload = (await packResponse.json()) as { items?: PublicationPack[] };
      const exportPayload = (await exportResponse.json()) as { items?: SignageRow[] };
      const duplicatePayload = (await duplicateResponse.json()) as { groups?: DuplicateGroup[] };
      const automationPayload = (await automationResponse.json()) as AutomationSummary;
      const nextSubmissions = submissionPayload.items ?? [];
      const nextAddresses = addressPayload.items ?? [];
      setSubmissions(nextSubmissions);
      setAddresses(nextAddresses);
      setImportJobs(jobPayload.items ?? []);
      setPacks(packPayload.items ?? []);
      setExportRows(exportPayload.items ?? []);
      setDuplicateGroups(duplicatePayload.groups ?? []);
      setAutomation(automationPayload);
      setSelectedAddressIds((current) => current.length ? current.filter((id) => nextAddresses.some((address) => address.id === id && !address.is_archived)) : nextAddresses.filter((address) => !address.is_archived && address.publication_state !== 'published').slice(0, 3).map((address) => address.id));
      const firstRelease = nextSubmissions.find(releaseCandidate);
      setSimulationForm((current) => ({ ...current, submission_id: current.submission_id || firstRelease?.id || '' }));
      setPublishForm((current) => ({ ...current, submission_id: current.submission_id || firstRelease?.id || '' }));
      setIntakeForm((current) => ({ ...current, territory_id: current.territory_id || nextSubmissions[0]?.territory_id || '' }));
    } catch {
      setError('Publication review, release, and output data could not be loaded. No release state has changed.');
    } finally {
      setIsLoading(false);
    }
  }, [browserApiBaseUrl, sessionStatus, token]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const queueRecords = useMemo<QueueRecord[]>(() => {
    if (section === 'outputs') {
      return packs.map((pack) => ({ key: `pack:${pack.id}`, id: pack.id, label: pack.name, territory: pack.audience, state: pack.status, detail: `${pack.address_count} address records` }));
    }
    if (section === 'intake') {
      return importJobs.map((job) => ({ key: `job:${job.id}`, id: job.id, label: job.name, territory: job.source_name, state: job.status, detail: `${job.valid_rows}/${job.total_rows} valid rows` }));
    }
    const source = section === 'release' ? submissions.filter((submission) => ['registry-ready', 'published'].includes(submission.status)) : submissions;
    return source.map((submission) => ({
      key: `submission:${submission.id}`,
      id: submission.id,
      label: submission.address_label,
      territory: submission.territory_name || 'Territory pending',
      state: submission.status,
      detail: submission.grid_code,
    }));
  }, [importJobs, packs, section, submissions]);

  const normalizedSearch = searchQuery.trim().toLowerCase();
  const visibleRecords = useMemo(() => queueRecords.filter((record) => {
    if (statusFilter !== 'all' && plainStatus(record.state).toLowerCase() !== statusFilter) return false;
    if (territoryFilter !== 'all' && record.territory !== territoryFilter) return false;
    if (!normalizedSearch) return true;
    return [record.id, record.label, record.territory, record.state, record.detail].some((value) => value.toLowerCase().includes(normalizedSearch));
  }), [normalizedSearch, queueRecords, statusFilter, territoryFilter]);

  useEffect(() => {
    if (!visibleRecords.length) {
      setSelectedKey('');
      return;
    }
    if (!visibleRecords.some((record) => record.key === selectedKey)) setSelectedKey(visibleRecords[0].key);
  }, [section, selectedKey, visibleRecords]);

  const selectedRecord = visibleRecords.find((record) => record.key === selectedKey) ?? visibleRecords[0] ?? null;
  const selectedSubmission = selectedRecord?.key.startsWith('submission:') ? submissions.find((submission) => submission.id === selectedRecord.id) ?? null : null;
  const selectedPack = selectedRecord?.key.startsWith('pack:') ? packs.find((pack) => pack.id === selectedRecord.id) ?? null : null;
  const selectedJob = selectedRecord?.key.startsWith('job:') ? importJobs.find((job) => job.id === selectedRecord.id) ?? null : null;

  useEffect(() => {
    setRoadName(selectedSubmission?.reviewed_road_name || selectedSubmission?.suggested_road_name || '');
    setDipFull('');
    if (selectedSubmission && releaseCandidate(selectedSubmission)) {
      setSimulationForm((current) => ({ ...current, submission_id: selectedSubmission.id }));
      setPublishForm((current) => ({ ...current, submission_id: selectedSubmission.id }));
    }
  }, [selectedSubmission?.id]);

  const activeReviewCount = submissions.filter((submission) => ['submitted', 'under-review', 'needs-field-check'].includes(submission.status)).length;
  const blockerCount = submissions.filter((submission) => submission.quality_flags?.requires_field_check || submission.quality_flags?.possible_duplicate).length;
  const registryReadyCount = submissions.filter(releaseCandidate).length;
  const publishedPackCount = packs.filter((pack) => pack.status === 'published').length;
  const statusOptions = Array.from(new Set(queueRecords.map((record) => plainStatus(record.state).toLowerCase()))).sort();
  const territoryOptions = Array.from(new Set(queueRecords.map((record) => record.territory).filter(Boolean))).sort();

  async function runAction(action: () => Promise<void>, label: string) {
    setBusyAction(label);
    setNotice(null);
    setError(null);
    try {
      await action();
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The publication operation could not be completed.');
    } finally {
      setBusyAction(null);
    }
  }

  async function postJson<T>(path: string, body?: Record<string, unknown>): Promise<T> {
    const response = await fetch(`${browserApiBaseUrl}${path}`, {
      method: 'POST',
      credentials: 'include',
      headers: requestHeaders(Boolean(body)),
      body: body ? JSON.stringify(body) : undefined,
    });
    const payload = (await response.json()) as T & { detail?: string };
    if (!response.ok) throw new Error(payload.detail || 'The authoritative service rejected the operation.');
    return payload;
  }

  async function updateCase(action: 'under-review' | 'field-check' | 'registry-ready' | 'reject') {
    if (!selectedSubmission || !canPrepare) {
      setError('Editor or administrator authority is required for publication preparation.');
      return;
    }
    if (action === 'registry-ready' && (selectedSubmission.quality_flags?.requires_field_check || selectedSubmission.quality_flags?.possible_duplicate)) {
      setError('Clear field-confirmation and duplicate blockers before placing this case in the release hold.');
      return;
    }
    await runAction(async () => {
      const result = await postJson<GeotagSubmission>(`/api/v1/geotag-submissions/${encodeURIComponent(selectedSubmission.id)}/${action}`, { reviewer_note: reviewNote });
      setNotice(`${result.address_label}: ${plainStatus(result.status)} recorded.`);
    }, `case-${action}`);
  }

  async function recordDuplicateDecision() {
    if (!selectedSubmission || !canPrepare) return;
    await runAction(async () => {
      await postJson<GeotagSubmission>(`/api/v1/geotag-submissions/${encodeURIComponent(selectedSubmission.id)}/duplicate-decision`, { duplicate_action: duplicateAction, reviewer_note: reviewNote });
      setNotice('Duplicate decision recorded and retained with the case history.');
    }, 'duplicate-decision');
  }

  async function reviewRoadSuggestion(action: 'accepted' | 'edited' | 'rejected') {
    if (!selectedSubmission || !canPrepare) return;
    if (action !== 'rejected' && roadName.trim().length < 2) {
      setError('Enter the reviewed road name before accepting or editing the suggestion.');
      return;
    }
    await runAction(async () => {
      await postJson<GeotagSubmission>(`/api/v1/geotag-submissions/${encodeURIComponent(selectedSubmission.id)}/road-suggestion`, {
        action,
        reviewed_road_name: action === 'rejected' ? null : roadName.trim(),
        reviewer_note: reviewNote,
      });
      setNotice(`Road-name suggestion ${action}.`);
    }, `road-${action}`);
  }

  async function verifyIdentity() {
    if (!selectedSubmission || !canPrepare) return;
    const normalized = dipFull.trim();
    if (!/^\d{6,20}$/.test(normalized)) {
      setError('Enter the full D.I.P. as 6 to 20 digits. The full value will not be stored.');
      return;
    }
    await runAction(async () => {
      await postJson<GeotagSubmission>(`/api/v1/geotag-submissions/${encodeURIComponent(selectedSubmission.id)}/identity`, {
        dip_full: normalized,
        identity_document_verified: true,
        reviewer_note: 'D.I.P. confirmed by an authorized operator. Full value was not retained.',
      });
      setDipFull('');
      setNotice('Identity confirmed. Only masked verification metadata is retained.');
    }, 'identity-verification');
  }

  async function simulateRelease(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canPrepare || !simulationForm.submission_id.trim()) {
      setError('Editor or administrator authority and a release-hold case ID are required.');
      return;
    }
    await runAction(async () => {
      const result = await postJson<PublicationSimulation>(`/api/v1/geotag-submissions/${encodeURIComponent(simulationForm.submission_id.trim())}/publication-simulation`, { reviewer_note: simulationForm.note });
      setSimulation(result);
      setNotice('Release simulation completed. No public record, certificate, or physical signage was released.');
    }, 'release-simulation');
  }

  function publishCaseDisabledReason() {
    if (!publicationReleaseEnabled) return 'Institutional approval lock active';
    if (sessionUser?.role !== 'admin') return 'Administrator required';
    if (!publishForm.submission_id.trim()) return 'Select a release-hold case';
    if (busyAction) return 'Working…';
    return null;
  }

  async function publishCase(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const reason = publishCaseDisabledReason();
    if (reason) {
      setError(reason);
      return;
    }
    await runAction(async () => {
      const result = await postJson<{ grid_code?: string }>(`/api/v1/geotag-submissions/${encodeURIComponent(publishForm.submission_id.trim())}/publish`, { reviewer_note: publishForm.note });
      setNotice(`Official public release completed: ${result.grid_code || publishForm.submission_id}.`);
    }, 'public-release');
  }

  async function createPack(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canPrepare || !selectedAddressIds.length) {
      setError('Select at least one eligible address and confirm editor or administrator authority.');
      return;
    }
    await runAction(async () => {
      const result = await postJson<PublicationPack>('/api/v1/publication/packs', { name: packForm.name, audience: packForm.audience, status: 'draft', address_ids: selectedAddressIds });
      setNotice(`Publication pack created: ${result.name}.`);
      setSection('outputs');
      setSelectedKey(`pack:${result.id}`);
    }, 'create-pack');
  }

  function publishPackDisabledReason(pack: PublicationPack | null) {
    if (!pack) return 'Select a publication pack';
    if (!publicationReleaseEnabled) return 'Institutional approval lock active';
    if (!canPublish) return 'Administrator required';
    if (pack.status === 'published') return 'Already published';
    if (pack.address_count <= 0) return 'No linked addresses';
    if (busyAction) return 'Working…';
    return null;
  }

  async function publishSelectedPack() {
    const reason = publishPackDisabledReason(selectedPack);
    if (reason || !selectedPack) {
      setError(reason || 'Select a publication pack.');
      return;
    }
    await runAction(async () => {
      const result = await postJson<PublicationPack>(`/api/v1/publication/packs/${encodeURIComponent(selectedPack.id)}/publish`);
      setNotice(`Official publication pack published: ${result.name}.`);
    }, 'publish-pack');
  }

  async function createIntakeJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canPrepare || !intakeForm.territory_id || !intakeForm.candidate_name.trim()) {
      setError('Complete the authorized intake row and confirm editor or administrator authority.');
      return;
    }
    await runAction(async () => {
      const result = await postJson<ImportJob>('/api/v1/imports/jobs', {
        name: intakeForm.name,
        source_name: intakeForm.source_name,
        rows: [{
          submission_type: intakeForm.submission_type,
          territory_id: intakeForm.territory_id,
          candidate_name: intakeForm.candidate_name.trim(),
          candidate_status: 'submitted',
          notes: intakeForm.notes.trim(),
        }],
      });
      setNotice(`Controlled intake job created: ${result.name}.`);
      setIntakeForm((current) => ({ ...current, candidate_name: '', notes: '' }));
    }, 'create-intake');
  }

  async function commitSelectedJob() {
    if (!selectedJob || !canPrepare) return;
    if (selectedJob.status === 'committed' || selectedJob.valid_rows <= 0) {
      setError(selectedJob.status === 'committed' ? 'This intake job is already committed.' : 'This intake job has no valid rows.');
      return;
    }
    await runAction(async () => {
      const result = await postJson<ImportJob>(`/api/v1/imports/jobs/${encodeURIComponent(selectedJob.id)}/commit`);
      setNotice(`Intake committed into the protected submission flow: ${result.name}.`);
    }, 'commit-intake');
  }

  function downloadCsv() {
    const header = ['grid_code', 'signage_text', 'address_label', 'territory_name', 'latitude', 'longitude', 'accuracy_meters', 'batch', 'status'];
    const rows = exportRows.map((row) => header.map((key) => JSON.stringify((row as unknown as Record<string, unknown>)[key] ?? '')).join(','));
    const blob = new Blob([[header.join(','), ...rows].join('\n')], { type: 'text/csv;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'official-signage-location-export.csv';
    link.click();
    window.URL.revokeObjectURL(url);
  }

  async function downloadSignagePack() {
    setBusyAction('signage-pack');
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/signage/pack`, { credentials: 'include', headers: requestHeaders() });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'The signage pack could not be generated.');
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${payload.batch_id || 'official-signage-pack'}.json`;
      link.click();
      window.URL.revokeObjectURL(url);
      setNotice(`Signage pack generated with ${payload.record_count ?? 0} published records.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The signage pack could not be generated.');
    } finally {
      setBusyAction(null);
    }
  }

  async function openCertificate() {
    if (!selectedSubmission) return;
    setBusyAction('certificate');
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/${encodeURIComponent(selectedSubmission.id)}/certificate`, { credentials: 'include', headers: requestHeaders() });
      const payload = (await response.json()) as CertificateResult & { detail?: string };
      if (!response.ok) throw new Error(payload.detail || 'The official certificate could not be generated.');
      const blob = new Blob([payload.html], { type: 'text/html;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank', 'noopener,noreferrer');
      window.setTimeout(() => window.URL.revokeObjectURL(url), 30_000);
      setNotice(`Official certificate opened: ${payload.address_code}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The official certificate could not be generated.');
    } finally {
      setBusyAction(null);
    }
  }

  return (
    <section className="government-operation-page government-publication-workbench" aria-labelledby="publication-workbench-title">
      <header className="government-operation-header">
        <div>
          <p>Controlled official release</p>
          <h1 id="publication-workbench-title">Publication</h1>
          <span>Resolve release blockers, hold verified records, simulate institutional approval, and prepare controlled public and physical outputs.</span>
        </div>
        <div className="government-operation-header-actions"><Link href="/registry"><GovernmentIcon name="registry" />Open registry</Link><button type="button" onClick={() => void reload()} disabled={isLoading}><GovernmentIcon name="operations" />{isLoading ? 'Refreshing' : 'Refresh publication'}</button></div>
      </header>

      <dl className="government-operation-summary" aria-label="Publication operations summary">
        <div><dt>Open review</dt><dd>{activeReviewCount}</dd><span>Cases before release hold</span></div>
        <div><dt>Release blockers</dt><dd>{blockerCount}</dd><span>Field or duplicate decisions</span></div>
        <div><dt>Registry-ready hold</dt><dd>{registryReadyCount}</dd><span>Approval is not publication</span></div>
        <div><dt>Publication packs</dt><dd>{packs.length}</dd><span>{publishedPackCount} officially published</span></div>
        <div><dt>Signage output</dt><dd>{exportRows.length}</dd><span>{publicationReleaseEnabled ? 'Release flag enabled' : 'Institutional lock active'}</span></div>
      </dl>

      <div className="government-command-bar government-publication-command-bar" aria-label="Publication filters">
        <label className="government-search-field"><GovernmentIcon name="search" /><span className="sr-only">Search publication work</span><input type="search" value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Search case, grid code, pack, source, territory, or state" /></label>
        <label><span>Workspace section</span><select value={section} onChange={(event) => { setSection(event.target.value as Section); setStatusFilter('all'); setTerritoryFilter('all'); }}><option value="review">Review and readiness</option><option value="release">Release hold</option><option value="outputs">Official outputs</option><option value="intake">Controlled intake</option></select></label>
        <label><span>Territory or audience</span><select value={territoryFilter} onChange={(event) => setTerritoryFilter(event.target.value)}><option value="all">All</option>{territoryOptions.map((territory) => <option key={territory} value={territory}>{territory}</option>)}</select></label>
        <label><span>Status</span><select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="all">All states</option>{statusOptions.map((status) => <option key={status} value={status}>{plainStatus(status)}</option>)}</select></label>
        <div className={`government-command-note ${publicationReleaseEnabled ? 'success' : ''}`}><GovernmentIcon name={publicationReleaseEnabled ? 'readiness' : 'alert'} /><span>{publicationReleaseEnabled ? 'Institutional release flag enabled; administrator authority still required' : 'Public release and physical signage remain institutionally locked'}</span></div>
      </div>

      {sessionStatus === 'loading' ? <p className="government-inline-state">Resolving publication authority and loading controlled release data…</p> : null}
      {notice ? <p className="government-inline-state success" role="status">{notice}</p> : null}
      {error ? <p className="government-inline-state error" role="alert">{error}</p> : null}

      <div className="government-three-pane-workbench">
        <aside className="government-queue-pane" aria-label="Publication work queue">
          <div className="government-pane-heading"><div><p>Controlled queue</p><h2>{section === 'outputs' ? 'Publication packs' : section === 'intake' ? 'Intake jobs' : section === 'release' ? 'Release hold' : 'Review and readiness'}</h2></div><span>{visibleRecords.length} shown</span></div>
          <div className="government-record-queue">
            {visibleRecords.length ? visibleRecords.map((record) => (
              <button key={record.key} className={selectedRecord?.key === record.key ? 'active' : ''} type="button" onClick={() => setSelectedKey(record.key)}><span className="government-queue-record-title">{record.label}</span><code>{record.id}</code><span>{record.territory} · {record.detail}</span><small className={`government-record-state ${['published', 'committed'].includes(record.state) ? 'success' : ['needs-field-check', 'rejected'].includes(record.state) ? 'warning' : ''}`}>{plainStatus(record.state)}</small></button>
            )) : <div className="government-pane-empty"><GovernmentIcon name="publication" /><strong>No matching publication work</strong><span>Change the workspace section or filters. Release controls remain unchanged.</span></div>}
          </div>
        </aside>

        <article className="government-record-pane" aria-label="Selected publication record">
          {selectedSubmission ? <><header className="government-selected-record-header"><div><p>Location publication case</p><h2>{selectedSubmission.address_label}</h2><code>{selectedSubmission.id} · {selectedSubmission.grid_code}</code></div><span className={`government-record-state ${selectedSubmission.status === 'published' ? 'success' : blockerCount ? 'warning' : ''}`}>{plainStatus(selectedSubmission.status)}</span></header><nav className="government-record-tabs" aria-label="Publication case sections"><span className="active">Readiness</span><span>Map</span><span>Identity</span><span>Release history</span></nav><div className="government-record-body">
            <section><div className="government-record-section-heading"><h3>Release-readiness context</h3><span>Automated triage supports but does not replace official authority</span></div><dl className="government-record-facts"><div><dt>Territory</dt><dd>{selectedSubmission.territory_name || 'Not assigned'}</dd></div><div><dt>Grid code</dt><dd>{selectedSubmission.grid_code}</dd></div><div><dt>Accuracy</dt><dd>{selectedSubmission.accuracy_meters == null ? 'Not recorded' : `±${Math.round(selectedSubmission.accuracy_meters)} m`}</dd></div><div><dt>Capture method</dt><dd>{plainStatus(selectedSubmission.capture_method)}</dd></div><div><dt>Identity</dt><dd>{plainStatus(selectedSubmission.identity_verification_status)}</dd></div><div><dt>Road review</dt><dd>{plainStatus(selectedSubmission.road_suggestion_status)}</dd></div><div><dt>Field work</dt><dd>{plainStatus(selectedSubmission.automation?.field_work?.status)}</dd></div><div><dt>Partner API</dt><dd>{selectedSubmission.automation?.integration?.partner_api_ready ? 'Ready after release' : 'Not ready'}</dd></div></dl></section>
            <section><div className="government-record-section-heading"><h3>Automated blocker assessment</h3><span>Quality score {selectedSubmission.automation?.quality_score ?? 'not returned'}</span></div><div className={`government-evidence-assessment ${!selectedSubmission.quality_flags?.requires_field_check && !selectedSubmission.quality_flags?.possible_duplicate ? 'success' : ''}`}><GovernmentIcon name={!selectedSubmission.quality_flags?.requires_field_check && !selectedSubmission.quality_flags?.possible_duplicate ? 'readiness' : 'alert'} /><div><strong>{qualityLabel(selectedSubmission)}</strong><span>{selectedSubmission.automation?.next_best_action_label || selectedSubmission.quality_flags?.recommended_action || 'Authorized operator review required.'}</span></div></div>{selectedSubmission.automation?.reasons?.length ? <ul className="government-safeguard-list">{selectedSubmission.automation.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul> : null}</section>
            <section><div className="government-record-section-heading"><h3>Mapped location</h3><span>Map reference for operator review</span></div><iframe className="government-field-map" title={`Map for ${selectedSubmission.address_label}`} src={mapPreviewUrl(selectedSubmission.latitude, selectedSubmission.longitude)} loading="lazy" /></section>
            <section><div className="government-record-section-heading"><h3>Road and identity review</h3><span>Sensitive identity values are never retained in full</span></div><dl className="government-record-facts"><div><dt>Suggested road</dt><dd>{selectedSubmission.suggested_road_name || 'No suggestion'}</dd></div><div><dt>Reviewed road</dt><dd>{selectedSubmission.reviewed_road_name || 'Not confirmed'}</dd></div><div><dt>Attribution</dt><dd>{selectedSubmission.road_suggestion_attribution || 'Not available'}</dd></div><div><dt>Masked D.I.P.</dt><dd>{selectedSubmission.dip_masked || 'Not verified'}</dd></div></dl></section>
          </div></> : null}

          {selectedPack ? <><header className="government-selected-record-header"><div><p>Official publication pack</p><h2>{selectedPack.name}</h2><code>{selectedPack.id}</code></div><span className={`government-record-state ${selectedPack.status === 'published' ? 'success' : ''}`}>{plainStatus(selectedPack.status)}</span></header><nav className="government-record-tabs"><span className="active">Pack context</span><span>Addresses</span><span>Authority</span><span>Audit</span></nav><div className="government-record-body"><section><div className="government-record-section-heading"><h3>Official output group</h3><span>Controlled publication service</span></div><dl className="government-record-facts"><div><dt>Audience</dt><dd>{selectedPack.audience}</dd></div><div><dt>Address count</dt><dd>{selectedPack.address_count}</dd></div><div><dt>Pack state</dt><dd>{plainStatus(selectedPack.status)}</dd></div><div><dt>Release flag</dt><dd>{publicationReleaseEnabled ? 'Enabled' : 'Institutional lock active'}</dd></div></dl></section><section><div className="government-record-section-heading"><h3>Selected eligible addresses</h3><span>{selectedAddressIds.length} selected for new pack preparation</span></div><div className="government-publication-address-list">{addresses.filter((address) => selectedAddressIds.includes(address.id)).map((address) => <div key={address.id}><strong>{address.formatted}</strong><span>{address.territory_name} · {plainStatus(address.publication_state)}</span></div>)}</div></section></div></> : null}

          {selectedJob ? <><header className="government-selected-record-header"><div><p>Controlled intake job</p><h2>{selectedJob.name}</h2><code>{selectedJob.id}</code></div><span className={`government-record-state ${selectedJob.status === 'committed' ? 'success' : ''}`}>{plainStatus(selectedJob.status)}</span></header><nav className="government-record-tabs"><span className="active">Validation</span><span>Source</span><span>Commit</span><span>Audit</span></nav><div className="government-record-body"><section><div className="government-record-section-heading"><h3>Intake validation result</h3><span>Rows enter the protected submission flow, not the public registry</span></div><dl className="government-record-facts"><div><dt>Source</dt><dd>{selectedJob.source_name}</dd></div><div><dt>Status</dt><dd>{plainStatus(selectedJob.status)}</dd></div><div><dt>Total rows</dt><dd>{selectedJob.total_rows}</dd></div><div><dt>Valid rows</dt><dd>{selectedJob.valid_rows}</dd></div><div><dt>Committed rows</dt><dd>{selectedJob.imported_count}</dd></div><div><dt>Invalid rows</dt><dd>{Math.max(selectedJob.total_rows - selectedJob.valid_rows, 0)}</dd></div></dl></section></div></> : null}

          {!selectedSubmission && !selectedPack && !selectedJob ? <div className="government-pane-empty large"><GovernmentIcon name="publication" /><strong>Select publication work</strong><span>Readiness, map, controlled outputs, and valid authority actions will appear here.</span></div> : null}
        </article>

        <aside className="government-decision-pane" aria-label="Publication actions">
          <div className="government-pane-heading"><div><p>Release control</p><h2>Valid next actions</h2></div><span>{canPublish ? 'Release authority active' : canPrepare ? 'Preparation authority' : 'Read only'}</span></div>
          <div className="government-decision-body">
            {selectedSubmission && section === 'review' ? <><section><h3>Operator review note</h3><label className="government-note-field"><span>Retained with review, field, duplicate, road, and rejection decisions</span><textarea rows={5} value={reviewNote} onChange={(event) => setReviewNote(event.target.value)} /></label></section><section><h3>Case transition</h3><div className="government-action-stack"><button className="primary" type="button" onClick={() => void updateCase('registry-ready')} disabled={!canPrepare || Boolean(busyAction) || Boolean(selectedSubmission.quality_flags?.requires_field_check) || Boolean(selectedSubmission.quality_flags?.possible_duplicate)}>Place in release hold</button><button type="button" onClick={() => void updateCase('under-review')} disabled={!canPrepare || Boolean(busyAction)}>Mark under review</button><button type="button" onClick={() => void updateCase('field-check')} disabled={!canPrepare || Boolean(busyAction)}>Send to field confirmation</button><button className="danger" type="button" onClick={() => void updateCase('reject')} disabled={!canPrepare || Boolean(busyAction)}>Reject case</button></div></section><section><h3>Duplicate and road decisions</h3><label className="government-field-inline-label"><span>Duplicate decision</span><select value={duplicateAction} onChange={(event) => setDuplicateAction(event.target.value)}><option value="same-property-merge">Same address · merge</option><option value="different-property-same-cell">Different address · same grid cell</option><option value="gps-error-recapture">GPS error · recapture</option><option value="send-field-verification">Send to field verification</option></select></label><button className="government-field-secondary-button" type="button" onClick={() => void recordDuplicateDecision()} disabled={!canPrepare || Boolean(busyAction)}>Record duplicate decision</button><label className="government-field-inline-label"><span>Reviewed road name</span><input value={roadName} onChange={(event) => setRoadName(event.target.value)} /></label><div className="government-publication-inline-actions"><button type="button" onClick={() => void reviewRoadSuggestion('accepted')} disabled={!canPrepare || Boolean(busyAction)}>Accept</button><button type="button" onClick={() => void reviewRoadSuggestion('edited')} disabled={!canPrepare || Boolean(busyAction)}>Save edit</button><button type="button" onClick={() => void reviewRoadSuggestion('rejected')} disabled={!canPrepare || Boolean(busyAction)}>Reject</button></div></section><section><h3>Identity confirmation</h3><label className="government-field-inline-label"><span>Full D.I.P. for one-time verification</span><input type="password" inputMode="numeric" autoComplete="off" value={dipFull} onChange={(event) => setDipFull(event.target.value.replace(/\D/g, ''))} /></label><button className="government-field-secondary-button" type="button" onClick={() => void verifyIdentity()} disabled={!canPrepare || Boolean(busyAction) || dipFull.length < 6}>Confirm without retaining full value</button></section></> : null}

            {section === 'release' ? <><section><h3>Release simulation</h3><form className="government-create-form" onSubmit={simulateRelease}><label><span>Release-hold case ID</span><input required value={simulationForm.submission_id} onChange={(event) => setSimulationForm((current) => ({ ...current, submission_id: event.target.value }))} /></label><label><span>Simulation note</span><textarea rows={3} value={simulationForm.note} onChange={(event) => setSimulationForm((current) => ({ ...current, note: event.target.value }))} /></label><button type="submit" disabled={!canPrepare || Boolean(busyAction)}>Run simulation only</button></form>{simulation ? <div className="government-trust-result success"><strong>{plainStatus(simulation.simulation_status)}</strong><span>{simulation.address_code || simulation.submission_id}</span><small>{simulation.operator_note} · Public release locked: {simulation.public_release_locked ? 'yes' : 'no'} · Physical signage locked: {simulation.physical_signage_locked ? 'yes' : 'no'}</small></div> : null}</section><section><h3>Official public release</h3><form className="government-create-form" onSubmit={publishCase}><label><span>Release-hold case ID</span><input required value={publishForm.submission_id} onChange={(event) => setPublishForm((current) => ({ ...current, submission_id: event.target.value }))} /></label><label><span>Institutional approval note</span><textarea rows={3} value={publishForm.note} onChange={(event) => setPublishForm((current) => ({ ...current, note: event.target.value }))} /></label><button type="submit" disabled={Boolean(publishCaseDisabledReason())}>{publishCaseDisabledReason() ?? 'Publish official address'}</button></form>{selectedSubmission?.status === 'published' ? <button className="government-field-secondary-button" type="button" onClick={() => void openCertificate()} disabled={Boolean(busyAction)}>Open official certificate</button> : null}</section></> : null}

            {section === 'outputs' ? <><section><h3>Create publication pack</h3><form className="government-create-form" onSubmit={createPack}><label><span>Pack name</span><input required value={packForm.name} onChange={(event) => setPackForm((current) => ({ ...current, name: event.target.value }))} /></label><label><span>Audience</span><input required value={packForm.audience} onChange={(event) => setPackForm((current) => ({ ...current, audience: event.target.value }))} /></label><div className="government-publication-address-selector">{addresses.filter((address) => !address.is_archived).map((address) => <label key={address.id}><input type="checkbox" checked={selectedAddressIds.includes(address.id)} onChange={(event) => setSelectedAddressIds((current) => event.target.checked ? [...current, address.id] : current.filter((id) => id !== address.id))} /><span>{address.formatted} · {plainStatus(address.publication_state)}</span></label>)}</div><button type="submit" disabled={!canPrepare || !selectedAddressIds.length || Boolean(busyAction)}>Create controlled pack</button></form></section><section><h3>Selected pack</h3><div className="government-action-stack"><button className="primary" type="button" onClick={() => void publishSelectedPack()} disabled={Boolean(publishPackDisabledReason(selectedPack))}>{publishPackDisabledReason(selectedPack) ?? 'Publish official pack'}</button><button type="button" onClick={downloadCsv} disabled={!exportRows.length}>Download signage CSV</button><button type="button" onClick={() => void downloadSignagePack()} disabled={!exportRows.length || Boolean(busyAction)}>Generate signage pack</button></div></section></> : null}

            {section === 'intake' ? <><section><h3>Create controlled intake job</h3><form className="government-create-form" onSubmit={createIntakeJob}><label><span>Job name</span><input required value={intakeForm.name} onChange={(event) => setIntakeForm((current) => ({ ...current, name: event.target.value }))} /></label><label><span>Authorized source name</span><input required value={intakeForm.source_name} onChange={(event) => setIntakeForm((current) => ({ ...current, source_name: event.target.value }))} /></label><label><span>Territory ID</span><input required value={intakeForm.territory_id} onChange={(event) => setIntakeForm((current) => ({ ...current, territory_id: event.target.value }))} /></label><label><span>Record type</span><select value={intakeForm.submission_type} onChange={(event) => setIntakeForm((current) => ({ ...current, submission_type: event.target.value }))}><option value="road">Road</option><option value="building">Building</option><option value="address">Address</option></select></label><label><span>Record name</span><input required value={intakeForm.candidate_name} onChange={(event) => setIntakeForm((current) => ({ ...current, candidate_name: event.target.value }))} /></label><label><span>Notes</span><textarea rows={3} value={intakeForm.notes} onChange={(event) => setIntakeForm((current) => ({ ...current, notes: event.target.value }))} /></label><button type="submit" disabled={!canPrepare || Boolean(busyAction)}>Create intake job</button></form></section><section><h3>Selected intake job</h3><div className="government-action-stack"><button className="primary" type="button" onClick={() => void commitSelectedJob()} disabled={!selectedJob || !canPrepare || Boolean(busyAction) || selectedJob.status === 'committed' || selectedJob.valid_rows <= 0}>{selectedJob?.status === 'committed' ? 'Already committed' : selectedJob && selectedJob.valid_rows <= 0 ? 'No valid rows' : 'Commit into submission flow'}</button></div></section></> : null}

            <section className="government-authority-note"><GovernmentIcon name="alert" /><div><strong>Preparation, approval, publication, and signage are separate states</strong><span>Registry-ready records remain protected. Public release requires administrator authority, an active institutional flag, and an explicit approval action. Physical signage is generated only from published records.</span></div></section>
          </div>
        </aside>
      </div>

      <div className="government-publication-footnote"><span>Automation status: {automation?.sla?.overdue ?? 0} overdue · {automation?.sla?.approaching ?? 0} approaching · {duplicateGroups.length} duplicate group(s).</span><span>{automation?.publication_hold?.note || 'Publication authority remains controlled by institutional policy.'}</span></div>
    </section>
  );
}
