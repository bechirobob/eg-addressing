'use client';

import { FormEvent, useEffect, useState } from 'react';

import { authorizationHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

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

type PublicationOperationsPanelProps = {
  initialAddresses: Address[];
  initialImportJobs: ImportJob[];
  initialPublicationPacks: PublicationPack[];
  apiBaseUrl: string;
};

type ImportRowDraft = {
  id: string;
  submission_type: 'road' | 'building' | 'address';
  territory_id: string;
  candidate_name: string;
  candidate_status: string;
  notes: string;
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

function createImportRow(id: string, territoryId: string): ImportRowDraft {
  return {
    id,
    submission_type: 'road',
    territory_id: territoryId,
    candidate_name: '',
    candidate_status: 'submitted',
    notes: '',
  };
}

export function PublicationOperationsPanel({
  initialImportJobs,
  initialPublicationPacks,
  initialAddresses,
  apiBaseUrl,
}: PublicationOperationsPanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [addresses, setAddresses] = useState(initialAddresses);
  const [importJobs, setImportJobs] = useState(initialImportJobs);
  const [publicationPacks, setPublicationPacks] = useState(initialPublicationPacks);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedAddressIds, setSelectedAddressIds] = useState<string[]>(
    initialAddresses.filter((item) => item.publication_state !== 'published').slice(0, 2).map((item) => item.id),
  );
  const [importForm, setImportForm] = useState({
    name: 'Malabo pilot intake',
    source_name: 'bioko_norte_pilot_registry.csv',
    rows: [createImportRow('row-1', 'territory-malabo-urban-core'), createImportRow('row-2', 'territory-malabo-aeropuerto-corridor')],
  });
  const [packName, setPackName] = useState('Published addresses — Bioko Norte pilot');
  const [packAudience, setPackAudience] = useState('Pilot review / programme steering');
  const [simulationSubmissionId, setSimulationSubmissionId] = useState('');
  const [simulationNote, setSimulationNote] = useState('Simulation only for ministry workflow demonstration.');
  const [publishSubmissionId, setPublishSubmissionId] = useState('');
  const [publishNote, setPublishNote] = useState('Institutional release approval confirmed for public publication.');
  const [publicationSimulation, setPublicationSimulation] = useState<PublicationSimulation | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const canWrite = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';
  const canPublish = sessionUser?.role === 'admin';
  const publicationSummary = {
    intakeJobs: importJobs.length,
    packs: publicationPacks.length,
    eligibleAddresses: addresses.filter((item) => !item.is_archived).length,
    selectedAddresses: selectedAddressIds.length,
    publishedPacks: publicationPacks.filter((pack) => pack.status === 'published').length,
  };

  useEffect(() => {
    if (!token) return;
    void reloadAll(token).catch(() => {
      setError('Unable to refresh protected publication data.');
    });
  }, [token]);

  async function reloadAll(activeToken: string) {
    const [jobsResponse, packsResponse, addressesResponse] = await Promise.all([
      fetch(`${browserApiBaseUrl}/api/v1/imports/jobs`, { headers: authorizationHeader(activeToken) }),
      fetch(`${browserApiBaseUrl}/api/v1/publication/packs`, { headers: authorizationHeader(activeToken) }),
      fetch(`${browserApiBaseUrl}/api/v1/addresses`, { headers: authorizationHeader(activeToken) }),
    ]);

    if (!jobsResponse.ok || !packsResponse.ok || !addressesResponse.ok) {
      throw new Error('reload failed');
    }

    const jobsPayload = (await jobsResponse.json()) as { items: ImportJob[] };
    const packsPayload = (await packsResponse.json()) as { items: PublicationPack[] };
    const addressesPayload = (await addressesResponse.json()) as { items: Address[] };
    setImportJobs(jobsPayload.items ?? []);
    setPublicationPacks(packsPayload.items ?? []);
    setAddresses(addressesPayload.items ?? []);
  }

  function updateImportRow(rowId: string, field: keyof Omit<ImportRowDraft, 'id'>, value: string) {
    setImportForm((current) => ({
      ...current,
      rows: current.rows.map((row) => (row.id === rowId ? { ...row, [field]: value } : row)),
    }));
  }

  function addImportRow() {
    setImportForm((current) => ({
      ...current,
      rows: [...current.rows, createImportRow(`row-${current.rows.length + 1}`, current.rows[0]?.territory_id ?? 'territory-malabo-urban-core')],
    }));
  }

  function removeImportRow(rowId: string) {
    setImportForm((current) => ({
      ...current,
      rows: current.rows.length === 1 ? current.rows : current.rows.filter((row) => row.id !== rowId),
    }));
  }

  async function handleImportCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !canWrite) {
      setError('Sign in as editor or admin before creating intake jobs.');
      return;
    }

    const rows = importForm.rows
      .map((row) => ({
        submission_type: row.submission_type,
        territory_id: row.territory_id,
        candidate_name: row.candidate_name.trim(),
        candidate_status: row.candidate_status.trim(),
        notes: row.notes.trim(),
      }))
      .filter((row) => row.candidate_name.length > 0);

    if (rows.length === 0) {
      setError('Add at least one intake row before creating the job.');
      return;
    }

    setIsSubmitting(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/imports/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token!) },
        body: JSON.stringify({ name: importForm.name, source_name: importForm.source_name, rows }),
      });
      const payload = (await response.json()) as ImportJob | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to create intake job.');
        return;
      }

      const createdJob = payload as ImportJob;
      setNotice(`Intake job created: ${createdJob.name}`);
      await reloadAll(token);
    } catch {
      setError('Unable to create the intake job.');
    } finally {
      setIsSubmitting(false);
    }
  }


  function commitDisabledReason(job: ImportJob) {
    if (!canWrite) return 'Editor or admin required';
    if (isSubmitting) return 'Working…';
    if (job.status === 'committed') return 'Already committed';
    if (job.valid_rows <= 0) return 'No valid rows';
    return null;
  }

  function publishDisabledReason(pack: PublicationPack) {
    if (!canPublish) return 'Admin required';
    if (isSubmitting) return 'Working…';
    if (pack.status === 'published') return 'Already published';
    if (pack.address_count <= 0) return 'No linked addresses';
    return null;
  }

  async function commitImport(jobId: string) {
    if (!token || !canWrite) {
      setError('Sign in as editor or admin before committing intake jobs.');
      return;
    }

    setIsSubmitting(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/imports/jobs/${jobId}/commit`, {
        method: 'POST',
        headers: authorizationHeader(token!),
      });
      const payload = (await response.json()) as ImportJob | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to commit intake job.');
        return;
      }
      const committedJob = payload as ImportJob;
      setNotice(`Intake committed: ${committedJob.name}`);
      await reloadAll(token);
    } catch {
      setError('Unable to commit the intake job.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function simulatePublication(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !canWrite) {
      setError('Sign in as editor or admin before running a publication simulation.');
      return;
    }
    const submissionId = simulationSubmissionId.trim();
    if (!submissionId) {
      setError('Enter a registry-ready geotag submission ID before running the simulation.');
      return;
    }
    setIsSubmitting(true);
    setNotice(null);
    setError(null);
    setPublicationSimulation(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/${encodeURIComponent(submissionId)}/publication-simulation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token) },
        body: JSON.stringify({ reviewer_note: simulationNote }),
      });
      const payload = (await response.json()) as PublicationSimulation | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to run publication simulation.');
        return;
      }
      setPublicationSimulation(payload as PublicationSimulation);
      setNotice('Release check completed without releasing public records or signage.');
    } catch {
      setError('Unable to run publication simulation.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function publishRegistryReadyCase(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !canPublish) {
      setError('Admin required before publishing a registry-ready case file.');
      return;
    }
    const submissionId = publishSubmissionId.trim();
    if (!submissionId) {
      setError('Enter a registry-ready geotag submission ID before publishing.');
      return;
    }
    setIsSubmitting(true);
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/geotag-submissions/${encodeURIComponent(publishSubmissionId)}/publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token) },
        body: JSON.stringify({ reviewer_note: publishNote }),
      });
      const payload = (await response.json()) as { grid_code?: string; publication?: { certificate_status?: string }; detail?: string };
      if (!response.ok) {
        setError(payload.detail ?? 'Unable to publish registry-ready case file.');
        return;
      }
      setNotice(`Published registry-ready case file: ${payload.grid_code ?? submissionId}`);
      await reloadAll(token);
    } catch {
      setError('Unable to publish registry-ready case file.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function createPack(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !canWrite) {
      setError('Sign in as editor or admin before creating publication packs.');
      return;
    }
    if (selectedAddressIds.length === 0) {
      setError('Select at least one address before creating a publication pack.');
      return;
    }

    setIsSubmitting(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/publication/packs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token!) },
        body: JSON.stringify({ name: packName, audience: packAudience, status: 'draft', address_ids: selectedAddressIds }),
      });
      const payload = (await response.json()) as PublicationPack | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to create publication pack.');
        return;
      }
      const createdPack = payload as PublicationPack;
      setNotice(`Publication pack created: ${createdPack.name}`);
      await reloadAll(token);
    } catch {
      setError('Unable to create the publication pack.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function publishPack(packId: string) {
    if (!token || !canPublish) {
      setError('Sign in as admin before publishing official packs.');
      return;
    }

    setIsSubmitting(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/publication/packs/${packId}/publish`, {
        method: 'POST',
        headers: authorizationHeader(token!),
      });
      const payload = (await response.json()) as PublicationPack | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to publish pack.');
        return;
      }
      const publishedPack = payload as PublicationPack;
      setNotice(`Publication pack published: ${publishedPack.name}`);
      await reloadAll(token);
    } catch {
      setError('Unable to publish the pack.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="section-grid territory-admin-grid desktop-workbench-grid publication-operations-grid">
      <article className="public-task-panel review-glance-panel publication-glance-panel">
        <div className="review-glance-head publication-release-head">
          <div>
            <p className="section-label">Release desk</p>
            <h3>Prepare official outputs after approval</h3>
          </div>
          <dl className="publication-summary-list" aria-label="Release desk summary">
            <div><dt>Intake jobs</dt><dd>{publicationSummary.intakeJobs}</dd></div>
            <div><dt>Packs</dt><dd>{publicationSummary.packs}</dd></div>
            <div><dt>Eligible addresses</dt><dd>{publicationSummary.eligibleAddresses}</dd></div>
            <div><dt>Published packs</dt><dd>{publicationSummary.publishedPacks}</dd></div>
          </dl>
        </div>
        {sessionStatus === 'loading' ? <p className="panel-state">Checking access before loading protected publication tools…</p> : null}
        {notice ? <p className="form-notice success">{notice}</p> : null}
        {error ? <p className="form-notice error">{error}</p> : null}
      </article>

      <article className="public-task-panel civic-panel-gold">
        <div className="panel-head">
          <p className="section-label">Release check</p>
          <h3>Check public release without publishing</h3>
        </div>
        <p className="institutional-note">
          Simulation is locked: it does not create public records, certificates, or physical signage. Use it to demonstrate the approval path for a registry-ready geotag case.
        </p>
        <details className="quiet-disclosure compact-review-disclosure">
          <summary>Open simulation form</summary>
          <form className="territory-form" onSubmit={simulatePublication}>
          <label className="territory-field territory-field-wide">
            <span className="territory-label">Registry-ready geotag submission ID</span>
            <input className="territory-input" value={simulationSubmissionId} onChange={(event) => setSimulationSubmissionId(event.target.value)} placeholder="citizen-geotag-…" />
          </label>
          <label className="territory-field territory-field-wide">
            <span className="territory-label">Simulation note</span>
            <textarea className="territory-input territory-textarea" value={simulationNote} onChange={(event) => setSimulationNote(event.target.value)} rows={3} />
          </label>
          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={!canWrite || isSubmitting}>
              {!canWrite ? 'Editor or admin required' : isSubmitting ? 'Working…' : 'Run simulation only'}
            </button>
          </div>
          </form>
        </details>
        {publicationSimulation ? (
          <div className="result-card">
            <span className="status-pill warn">Simulation only</span>
            <div>
              <h4>{publicationSimulation.address_code ?? publicationSimulation.submission_id}</h4>
              <p>{publicationSimulation.operator_note}</p>
              <p>Public release locked: {publicationSimulation.public_release_locked ? 'yes' : 'no'} · Physical signage locked: {publicationSimulation.physical_signage_locked ? 'yes' : 'no'}</p>
            </div>
          </div>
        ) : null}
      </article>

      <article className="public-task-panel civic-panel-green">
        <div className="panel-head">
          <p className="section-label">Controlled publication</p>
          <h3>Publish registry-ready case file</h3>
        </div>
        <p className="institutional-note">
          Admin-only release action. Use this only after institutional approval; it unlocks public profile proof, certificate generation, and signage export for the selected registry-ready case file.
        </p>
        <form className="territory-form" onSubmit={publishRegistryReadyCase}>
          <label className="territory-field territory-field-wide">
            <span className="territory-label">Registry-ready geotag submission ID</span>
            <input className="territory-input" value={publishSubmissionId} onChange={(event) => setPublishSubmissionId(event.target.value)} placeholder="citizen-geotag-…" />
          </label>
          <label className="territory-field territory-field-wide">
            <span className="territory-label">Publication approval note</span>
            <textarea className="territory-input territory-textarea" value={publishNote} onChange={(event) => setPublishNote(event.target.value)} rows={3} />
          </label>
          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={!canPublish || isSubmitting}>
              {!canPublish ? 'Admin required' : isSubmitting ? 'Working…' : 'Publish registry-ready case file'}
            </button>
          </div>
        </form>
      </article>

      <article className="public-task-panel civic-panel-blue">
        <div className="panel-head">
          <p className="section-label">Intake jobs</p>
          <h3>Create controlled intake jobs</h3>
        </div>
        <details className="quiet-disclosure compact-review-disclosure">
          <summary>Create migration or intake job manually</summary>
          <form className="territory-form" onSubmit={handleImportCreate}>
          <label className="territory-field">
            <span className="territory-label">Job name</span>
            <input className="territory-input" value={importForm.name} onChange={(event) => setImportForm({ ...importForm, name: event.target.value })} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Source file</span>
            <input className="territory-input" value={importForm.source_name} onChange={(event) => setImportForm({ ...importForm, source_name: event.target.value })} required />
          </label>

          <fieldset className="selection-group">
            <legend className="territory-label">Intake rows</legend>
            <div className="selection-list import-row-list">
              {importForm.rows.map((row, index) => (
                <div key={row.id} className="review-card compact-card import-row-card">
                  <div className="import-row-grid">
                    <label className="territory-field" htmlFor={`intake-row-type-${row.id}`}>
                      <span className="territory-label">Row {index + 1} type</span>
                      <select id={`intake-row-type-${row.id}`} className="territory-input" value={row.submission_type} onChange={(event) => updateImportRow(row.id, 'submission_type', event.target.value)}>
                        <option value="road">Road</option>
                        <option value="building">Building</option>
                        <option value="address">Address</option>
                      </select>
                    </label>
                    <label className="territory-field">
                      <span className="territory-label">Territory</span>
                      <select className="territory-input" value={row.territory_id} onChange={(event) => updateImportRow(row.id, 'territory_id', event.target.value)}>
                        <option value="territory-malabo-urban-core">Malabo Urban Core</option>
                        <option value="territory-malabo-aeropuerto-corridor">Carretera del Aeropuerto</option>
                        <option value="territory-malabo-ela-nguema">Ela Nguema</option>
                      </select>
                    </label>
                    <label className="territory-field territory-field-wide">
                      <span className="territory-label">Record name or label</span>
                      <input className="territory-input" value={row.candidate_name} onChange={(event) => updateImportRow(row.id, 'candidate_name', event.target.value)} required />
                    </label>
                    <label className="territory-field">
                      <span className="territory-label">Status</span>
                      <input className="territory-input" value={row.candidate_status} onChange={(event) => updateImportRow(row.id, 'candidate_status', event.target.value)} required />
                    </label>
                    <label className="territory-field territory-field-wide">
                      <span className="territory-label">Notes</span>
                      <textarea className="territory-input territory-textarea" value={row.notes} onChange={(event) => updateImportRow(row.id, 'notes', event.target.value)} rows={3} />
                    </label>
                  </div>
                  <div className="button-stack">
                    <button className="mini-action-button danger" type="button" aria-label={`Remove intake row ${index + 1}`} onClick={() => removeImportRow(row.id)} disabled={importForm.rows.length === 1 || isSubmitting}>
                      Remove row
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </fieldset>

          <div className="button-row">
            <button className="secondary-button" type="button" onClick={addImportRow} disabled={!canWrite || isSubmitting}>
              Add intake row
            </button>
            <button className="verification-button" type="submit" disabled={!canWrite || isSubmitting}>
              {!canWrite ? 'Editor or admin required' : isSubmitting ? 'Working…' : 'Create intake job'}
            </button>
          </div>
          </form>
        </details>

        <ul className="review-list compact-review-list">
          {importJobs.map((job) => (
            <li key={job.id} className="review-card compact-card">
              <div>
                <p className="assignment-kicker">{job.status}</p>
                <h4>{job.name}</h4>
                <p>{job.source_name}</p>
                <p>
                  {job.valid_rows}/{job.total_rows} valid · {job.imported_count} committed
                </p>
              </div>
              <div className="button-stack">
                <button className="mini-action-button primary" type="button" onClick={() => void commitImport(job.id)} disabled={Boolean(commitDisabledReason(job))}>
                  {commitDisabledReason(job) ?? 'Commit into submissions'}
                </button>
              </div>
            </li>
          ))}
        </ul>
      </article>

      <article className="public-task-panel civic-panel-gold">
        <div className="panel-head">
          <p className="section-label">Publication packs</p>
          <h3>Prepare official output groups</h3>
        </div>
        <details className="quiet-disclosure compact-review-disclosure">
          <summary>Create publication pack</summary>
          <form className="territory-form" onSubmit={createPack}>
          <label className="territory-field">
            <span className="territory-label">Pack name</span>
            <input className="territory-input" value={packName} onChange={(event) => setPackName(event.target.value)} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Audience</span>
            <input className="territory-input" value={packAudience} onChange={(event) => setPackAudience(event.target.value)} required />
          </label>
          <details className="quiet-disclosure compact-review-disclosure">
            <summary>{publicationSummary.selectedAddresses} selected from {publicationSummary.eligibleAddresses} eligible addresses</summary>
            <fieldset className="selection-group">
              <legend className="territory-label">Eligible addresses</legend>
            <div className="selection-list">
              {addresses.filter((item) => !item.is_archived).map((address) => (
                <label key={address.id} className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={selectedAddressIds.includes(address.id)}
                    onChange={(event) =>
                      setSelectedAddressIds((current) =>
                        event.target.checked ? [...current, address.id] : current.filter((item) => item !== address.id),
                      )
                    }
                  />
                  <span>
                    {address.formatted} · {address.publication_state}
                  </span>
                </label>
              ))}
            </div>
            </fieldset>
          </details>
          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={!canWrite || isSubmitting}>
              {!canWrite ? 'Editor or admin required' : isSubmitting ? 'Working…' : 'Create publication pack'}
            </button>
          </div>
          </form>
        </details>
        <ul className="review-list compact-review-list">
          {publicationPacks.map((pack) => (
            <li key={pack.id} className="review-card compact-card">
              <div>
                <p className="assignment-kicker">{pack.status}</p>
                <h4>{pack.name}</h4>
                <p>{pack.audience}</p>
                <p>{pack.address_count} linked addresses</p>
              </div>
              <div className="button-stack">
                <button className="mini-action-button primary" type="button" onClick={() => void publishPack(pack.id)} disabled={Boolean(publishDisabledReason(pack))}>
                  {publishDisabledReason(pack) ?? 'Publish pack'}
                </button>
              </div>
            </li>
          ))}
        </ul>
      </article>

      <article className="public-task-panel civic-panel-green territory-list-panel">
        <div className="panel-head">
          <p className="section-label">Publication-ready records</p>
          <h3>Current address publication state</h3>
        </div>
        {addresses.length > 0 ? (
          <details className="quiet-disclosure compact-review-disclosure">
            <summary>{addresses.length} address publication states</summary>
            <ul className="mini-list">
              {addresses.map((address) => (
                <li key={address.id}>
                  <strong>{address.formatted}</strong>
                  <span>
                    {address.territory_name} · {address.status} · {address.publication_state}
                  </span>
                </li>
              ))}
            </ul>
          </details>
        ) : (
          <p className="panel-state">No address publication records are available yet.</p>
        )}
      </article>
    </section>
  );
}
