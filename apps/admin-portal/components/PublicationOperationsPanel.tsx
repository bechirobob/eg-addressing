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
    name: 'Legacy registry intake',
    source_name: 'legacy-registry-bata.csv',
    rows: [createImportRow('row-1', 'territory-bata-urban-core'), createImportRow('row-2', 'territory-oyala-civic-district')],
  });
  const [packName, setPackName] = useState('Published addresses — executive circulation');
  const [packAudience, setPackAudience] = useState('Cabinet / programme steering');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const canWrite = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';
  const canPublish = sessionUser?.role === 'admin';

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
      fetch(`${browserApiBaseUrl}/api/v1/addresses`),
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
      rows: [...current.rows, createImportRow(`row-${current.rows.length + 1}`, current.rows[0]?.territory_id ?? 'territory-bata-urban-core')],
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
    <section className="section-grid territory-admin-grid">
      <article className="panel panel-accent-blue">
        <div className="panel-head">
          <p className="section-label">Intake staging</p>
          <h3>Create migration and intake jobs</h3>
        </div>
        <p className="institutional-note">
          Signed-in role: <strong>{sessionUser?.role ?? 'guest'}</strong>. Prepare structured intake rows without exposing raw payload formats.
        </p>
        {sessionStatus === 'loading' ? <p className="panel-state">Checking access before loading protected publication tools…</p> : null}
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
                    <label className="territory-field">
                      <span className="territory-label">Row {index + 1} type</span>
                      <select className="territory-input" value={row.submission_type} onChange={(event) => updateImportRow(row.id, 'submission_type', event.target.value)}>
                        <option value="road">Road</option>
                        <option value="building">Building</option>
                        <option value="address">Address</option>
                      </select>
                    </label>
                    <label className="territory-field">
                      <span className="territory-label">Territory</span>
                      <select className="territory-input" value={row.territory_id} onChange={(event) => updateImportRow(row.id, 'territory_id', event.target.value)}>
                        <option value="territory-bata-urban-core">Bata Urban Core</option>
                        <option value="territory-oyala-civic-district">Oyala Civic District</option>
                        <option value="territory-ebebiyin-access-corridor">Ebebiyin Access Corridor</option>
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
                    <button className="mini-action-button danger" type="button" onClick={() => removeImportRow(row.id)} disabled={importForm.rows.length === 1 || isSubmitting}>
                      Remove row
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </fieldset>

          <div className="button-row">
            <button className="secondary-button" type="button" onClick={addImportRow} disabled={isSubmitting}>
              Add intake row
            </button>
            <button className="verification-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Working…' : 'Create intake job'}
            </button>
          </div>
        </form>

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
                <button className="mini-action-button primary" type="button" onClick={() => void commitImport(job.id)} disabled={isSubmitting}>
                  Commit into submissions
                </button>
              </div>
            </li>
          ))}
        </ul>
      </article>

      <article className="panel panel-accent-gold">
        <div className="panel-head">
          <p className="section-label">Publication packs</p>
          <h3>Prepare official output groups</h3>
        </div>
        <form className="territory-form" onSubmit={createPack}>
          <label className="territory-field">
            <span className="territory-label">Pack name</span>
            <input className="territory-input" value={packName} onChange={(event) => setPackName(event.target.value)} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Audience</span>
            <input className="territory-input" value={packAudience} onChange={(event) => setPackAudience(event.target.value)} required />
          </label>
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
          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Working…' : 'Create publication pack'}
            </button>
          </div>
        </form>
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
                <button className="mini-action-button primary" type="button" onClick={() => void publishPack(pack.id)} disabled={isSubmitting}>
                  Publish pack
                </button>
              </div>
            </li>
          ))}
        </ul>
      </article>

      <article className="panel panel-accent-green territory-list-panel">
        <div className="panel-head">
          <p className="section-label">Publication-ready records</p>
          <h3>Current address publication state</h3>
        </div>
        {addresses.length > 0 ? (
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
        ) : (
          <p className="panel-state">No address publication records are available yet.</p>
        )}
        {notice ? <p className="form-notice success">{notice}</p> : null}
        {error ? <p className="form-notice error">{error}</p> : null}
      </article>
    </section>
  );
}
