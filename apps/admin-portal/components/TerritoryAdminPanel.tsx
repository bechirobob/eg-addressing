'use client';

import { useEffect, useMemo, useState } from 'react';

import { clearStoredToken, getStoredToken, type SessionUser } from './demoAuth';
import { authorizationHeader, resolveBrowserApiBaseUrl } from './sessionClient';

type Territory = {
  id: string;
  name: string;
  province_code: string;
  province: string;
  type: string;
  readiness: string;
  is_archived: boolean;
};

type Province = {
  id: string;
  code: string;
  name: string;
};

type TerritoryAdminPanelProps = {
  initialTerritories: Territory[];
  provinces: Province[];
  apiBaseUrl: string;
};

type FormState = {
  name: string;
  province_code: string;
  type: string;
  readiness: string;
};

const emptyForm = (provinceCode: string): FormState => ({
  name: '',
  province_code: provinceCode,
  type: '',
  readiness: '',
});

export function TerritoryAdminPanel({ initialTerritories, provinces, apiBaseUrl }: TerritoryAdminPanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const [territories, setTerritories] = useState(initialTerritories);
  const [selectedTerritory, setSelectedTerritory] = useState<Territory | null>(initialTerritories[0] ?? null);
  const [sessionUser, setSessionUser] = useState<SessionUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] = useState<'loading' | 'ready' | 'guest'>('loading');
  const [search, setSearch] = useState('');
  const [provinceFilter, setProvinceFilter] = useState('');
  const [readinessFilter, setReadinessFilter] = useState('');
  const [includeArchived, setIncludeArchived] = useState(false);
  const [createForm, setCreateForm] = useState<FormState>(emptyForm(provinces[0]?.code ?? ''));
  const [editForm, setEditForm] = useState<FormState>(emptyForm(provinces[0]?.code ?? ''));
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const readinessOptions = useMemo(() => Array.from(new Set(territories.map((item) => item.readiness))).sort(), [territories]);
  const territorySummary = useMemo(
    () => ({
      visible: territories.length,
      active: territories.filter((item) => !item.is_archived).length,
      provinces: new Set(territories.map((item) => item.province_code)).size,
    }),
    [territories],
  );
  const canWrite = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';
  const canArchive = sessionUser?.role === 'admin';
  const writeDisabledReason = !canWrite ? 'Editor or admin required' : isSubmitting ? 'Working…' : null;
  const archiveDisabledReason = !canArchive ? 'Admin required' : isSubmitting ? 'Working…' : null;

  useEffect(() => {
    void loadSession();
  }, []);

  useEffect(() => {
    void loadTerritories();
  }, [search, provinceFilter, readinessFilter, includeArchived]);

  useEffect(() => {
    if (selectedTerritory) {
      setEditForm({
        name: selectedTerritory.name,
        province_code: selectedTerritory.province_code,
        type: selectedTerritory.type,
        readiness: selectedTerritory.readiness,
      });
    }
  }, [selectedTerritory]);

  async function loadSession() {
    const storedToken = getStoredToken();
    if (!storedToken) {
      setToken(null);
      setSessionUser(null);
      setSessionStatus('guest');
      return;
    }

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/auth/me`, { headers: authorizationHeader(storedToken) });
      const payload = (await response.json()) as { user?: SessionUser; detail?: string };
      if (!response.ok || !payload.user) {
        clearStoredToken();
        setToken(null);
        setSessionUser(null);
        setSessionStatus('guest');
        return;
      }
      setToken(storedToken);
      setSessionUser(payload.user);
      setSessionStatus('ready');
    } catch {
      setSessionStatus('guest');
    }
  }

  async function loadTerritories(nextSelectedId?: string | null) {
    setIsRefreshing(true);
    const params = new URLSearchParams();
    if (search) params.set('q', search);
    if (provinceFilter) params.set('province_code', provinceFilter);
    if (readinessFilter) params.set('readiness', readinessFilter);
    if (includeArchived) params.set('include_archived', 'true');

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/territories?${params.toString()}`);
      const payload = (await response.json()) as { items: Territory[] };
      const items = payload.items ?? [];
      setTerritories(items);

      const selectedId = nextSelectedId ?? selectedTerritory?.id ?? null;
      if (!selectedId) {
        setSelectedTerritory(items[0] ?? null);
        return;
      }
      const exact = items.find((item) => item.id === selectedId) ?? null;
      if (exact) {
        setSelectedTerritory(exact);
      } else if (nextSelectedId) {
        await loadTerritoryDetail(nextSelectedId);
      } else {
        setSelectedTerritory(items[0] ?? null);
      }
    } catch {
      setError('Unable to load territory registry.');
    } finally {
      setIsRefreshing(false);
    }
  }

  async function loadTerritoryDetail(territoryId: string) {
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/territories/${territoryId}`);
      if (!response.ok) {
        setError('Unable to load territory detail.');
        return;
      }
      const payload = (await response.json()) as Territory;
      setSelectedTerritory(payload);
    } catch {
      setError('Unable to load territory detail.');
    }
  }

  function setCreateField<K extends keyof FormState>(field: K, value: FormState[K]) {
    setCreateForm((current) => ({ ...current, [field]: value }));
  }

  function setEditField<K extends keyof FormState>(field: K, value: FormState[K]) {
    setEditForm((current) => ({ ...current, [field]: value }));
  }

  async function handleCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !canWrite) {
      setError('Sign in as editor or admin to create territory records.');
      return;
    }

    setIsSubmitting(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/territories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token) },
        body: JSON.stringify(createForm),
      });
      const payload = (await response.json()) as Territory | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to create territory record.');
        return;
      }
      const created = payload as Territory;
      setCreateForm(emptyForm(createForm.province_code));
      setNotice(`Territory created: ${created.name}`);
      await loadTerritories(created.id);
    } catch {
      setError('Network error while creating territory record.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpdate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedTerritory) {
      setError('Select a territory first.');
      return;
    }
    if (!token || !canWrite) {
      setError('Sign in as editor or admin to update territory records.');
      return;
    }

    setIsSubmitting(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/territories/${selectedTerritory.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', ...authorizationHeader(token) },
        body: JSON.stringify(editForm),
      });
      const payload = (await response.json()) as Territory | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to update territory record.');
        return;
      }
      const updated = payload as Territory;
      setSelectedTerritory(updated);
      setNotice(`Territory updated: ${updated.name}`);
      await loadTerritories(updated.id);
    } catch {
      setError('Network error while updating territory record.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleArchive() {
    if (!selectedTerritory) {
      setError('Select a territory first.');
      return;
    }
    if (!token || !canArchive) {
      setError('Sign in as admin to archive territory records.');
      return;
    }

    setIsSubmitting(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/territories/${selectedTerritory.id}`, {
        method: 'DELETE',
        headers: authorizationHeader(token),
      });
      const payload = (await response.json()) as Territory | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to archive territory record.');
        return;
      }
      setNotice(`Territory archived: ${selectedTerritory.name}`);
      await loadTerritories();
    } catch {
      setError('Network error while archiving territory record.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="territory-workspace">
      <article className="public-task-panel territory-command-panel">
        <div className="panel-head quiet-head">
          <p className="section-label">Territory registry</p>
          <h3>Filter and maintain operating areas</h3>
        </div>

        <div className="territory-summary-row" aria-label="Territory registry summary">
          <span><strong>{territorySummary.visible}</strong> visible records</span>
          <span><strong>{territorySummary.active}</strong> active areas</span>
          <span><strong>{territorySummary.provinces}</strong> provinces represented</span>
        </div>

        <div className="filter-grid territory-filter-grid">
          <label className="territory-field">
            <span className="territory-label">Search</span>
            <input className="territory-input" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search territory, province, type" />
          </label>
          <label className="territory-field">
            <span className="territory-label">Province</span>
            <select className="territory-input" value={provinceFilter} onChange={(event) => setProvinceFilter(event.target.value)}>
              <option value="">All provinces</option>
              {provinces.map((province) => (
                <option key={province.code} value={province.code}>{province.name}</option>
              ))}
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Readiness</span>
            <select className="territory-input" value={readinessFilter} onChange={(event) => setReadinessFilter(event.target.value)}>
              <option value="">All readiness states</option>
              {readinessOptions.map((value) => (
                <option key={value} value={value}>{value}</option>
              ))}
            </select>
          </label>
          <label className="checkbox-row">
            <input type="checkbox" checked={includeArchived} onChange={(event) => setIncludeArchived(event.target.checked)} />
            <span>Include archived territories</span>
          </label>
        </div>

        <details className="inline-disclosure territory-create-disclosure">
          <summary>Create new territory</summary>
          <form className="territory-form" onSubmit={handleCreate}>
          <div className="panel-head compact-panel-head">
            <p className="section-label">Create</p>
            <h3>Register a new territory</h3>
          </div>

          <label className="territory-field">
            <span className="territory-label">Territory name</span>
            <input className="territory-input" value={createForm.name} onChange={(event) => setCreateField('name', event.target.value)} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Province</span>
            <select className="territory-input" value={createForm.province_code} onChange={(event) => setCreateField('province_code', event.target.value)} required>
              {provinces.map((province) => (
                <option key={province.code} value={province.code}>{province.name}</option>
              ))}
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Type</span>
            <input className="territory-input" value={createForm.type} onChange={(event) => setCreateField('type', event.target.value)} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Readiness</span>
            <input className="territory-input" value={createForm.readiness} onChange={(event) => setCreateField('readiness', event.target.value)} required />
          </label>
          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={Boolean(writeDisabledReason)}>{writeDisabledReason ?? 'Create territory'}</button>
          </div>
          </form>
        </details>

        {notice ? <p className="form-notice success">{notice}</p> : null}
        {error ? <p className="form-notice error">{error}</p> : null}
      </article>

      <article className="public-task-panel territory-detail-panel">
        <div className="panel-head">
          <p className="section-label">Territory detail</p>
          <h3>Inspect, edit, and archive</h3>
        </div>

        {selectedTerritory ? (
          <>
            <div className="selection-summary compact-territory-summary">
              <strong>{selectedTerritory.name}</strong>
              <span className="status-chip">{selectedTerritory.province_code}</span>
              <span className="status-chip warn">{selectedTerritory.is_archived ? 'archived' : selectedTerritory.readiness}</span>
              <span className="status-chip">{selectedTerritory.type}</span>
            </div>
            <details className="inline-disclosure territory-edit-disclosure">
              <summary>Edit selected territory details</summary>
              <form className="territory-form" onSubmit={handleUpdate}>
            <div className="selection-summary">
              <strong>{selectedTerritory.name}</strong>
              <span className="territory-meta">{selectedTerritory.is_archived ? 'archived' : selectedTerritory.readiness}</span>
            </div>
            <label className="territory-field">
              <span className="territory-label">Territory name</span>
              <input className="territory-input" value={editForm.name} onChange={(event) => setEditField('name', event.target.value)} required />
            </label>
            <label className="territory-field">
              <span className="territory-label">Province</span>
              <select className="territory-input" value={editForm.province_code} onChange={(event) => setEditField('province_code', event.target.value)} required>
                {provinces.map((province) => (
                  <option key={province.code} value={province.code}>{province.name}</option>
                ))}
              </select>
            </label>
            <label className="territory-field">
              <span className="territory-label">Type</span>
              <input className="territory-input" value={editForm.type} onChange={(event) => setEditField('type', event.target.value)} required />
            </label>
            <label className="territory-field">
              <span className="territory-label">Readiness</span>
              <input className="territory-input" value={editForm.readiness} onChange={(event) => setEditField('readiness', event.target.value)} required />
            </label>
            <div className="button-row">
              <button className="verification-button" type="submit" disabled={Boolean(writeDisabledReason)}>{writeDisabledReason ?? 'Save territory changes'}</button>
              <button className="secondary-button" type="button" disabled={Boolean(archiveDisabledReason)} onClick={() => void handleArchive()}>
                {archiveDisabledReason ?? 'Archive territory'}
              </button>
            </div>
            </form>
            </details>
          </>
        ) : (
          <p className="institutional-note">Select a territory from the live registry to inspect its full record.</p>
        )}
      </article>

      <article className="public-task-panel territory-list-panel">
        <div className="panel-head">
          <p className="section-label">Live registry</p>
          <h3>Current territory records</h3>
        </div>
        <p className="institutional-note">{isRefreshing ? 'Refreshing live registry…' : `${territories.length} visible territory records`}</p>

        <ul className="territory-list">
          {territories.map((territory) => (
            <li key={territory.id} className="territory-record">
              <div>
                <h4>{territory.name}</h4>
                <p>{territory.province} ({territory.province_code}) · {territory.type}</p>
              </div>
              <div className="record-actions">
                <span className="territory-meta">{territory.is_archived ? 'archived' : territory.readiness}</span>
                <button className="secondary-button" type="button" onClick={() => void loadTerritoryDetail(territory.id)}>
                  Inspect
                </button>
              </div>
            </li>
          ))}
        </ul>
      </article>
    </section>
  );
}
