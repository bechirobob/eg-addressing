'use client';

import { useEffect, useMemo, useState } from 'react';

import { clearStoredToken, getStoredToken, type SessionUser } from './demoAuth';
import { authorizationHeader, resolveBrowserApiBaseUrl } from './sessionClient';

type Territory = {
  id: string;
  name: string;
  province_code: string;
  province: string;
  admin_unit_name?: string | null;
  admin_unit_level?: string | null;
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


function readinessLabel(value: string): string {
  if (value === 'official-routing') return 'Ruta administrativa oficial';
  if (value === 'intake-routing') return 'Área local para ingreso';
  if (value === 'active-mapping') return 'Cartografía activa';
  if (value === 'verification-prep') return 'Pendiente de verificación de campo';
  if (value === 'survey-queue') return 'En cola de levantamiento';
  return value.replaceAll('-', ' ');
}

function territoryTypeLabel(value: string): string {
  if (value === 'official-municipality') return 'Municipio / ruta administrativa';
  if (value === 'map-referenced-local-area') return 'Área local referenciada';
  if (value === 'capital-urban-core') return 'Núcleo urbano capital';
  if (value === 'urban-core') return 'Núcleo urbano';
  return value.replaceAll('-', ' ');
}

function sourceLabel(territory: Territory): string {
  if (territory.type === 'official-municipality' && territory.readiness === 'official-routing') return 'Tabla de división administrativa / fuente referenciada por INEGE';
  if (territory.type === 'map-referenced-local-area') return 'Referencia cartográfica/local usada para enrutamiento de ingreso';
  return 'Registro de enrutamiento mantenido por el operador';
}

function confidenceLabel(territory: Territory): string {
  if (territory.type === 'official-municipality' && territory.readiness === 'official-routing') return 'Unidad administrativa confirmada';
  if (territory.type === 'map-referenced-local-area') return 'Referencia local; requiere confirmación del operador';
  return 'Registro interno; confirmar antes de publicación';
}

function geometryLabel(territory: Territory): string {
  if (territory.type === 'official-municipality') return 'Área de enrutamiento por nombre administrativo; límite topográfico no adjunto';
  return 'Registro de enrutamiento/ingreso; geometría oficial levantada no adjunta';
}

function publicationLabel(territory: Territory): string {
  if (territory.readiness === 'official-routing') return 'Enrutamiento interno hasta verificación del operador y publicación controlada';
  if (territory.readiness === 'intake-routing') return 'Pendiente de verificación de campo antes de publicación';
  return 'Estado interno de revisión';
}

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
      official: territories.filter((item) => item.readiness === 'official-routing').length,
      local: territories.filter((item) => item.type === 'map-referenced-local-area').length,
    }),
    [territories],
  );
  const territoryHierarchy = useMemo(() => {
    return provinces.map((province) => {
      const items = territories.filter((territory) => territory.province_code === province.code && !territory.is_archived);
      return {
        province,
        official: items.filter((territory) => territory.readiness === 'official-routing'),
        local: items.filter((territory) => territory.readiness !== 'official-routing'),
      };
    }).filter((group) => group.official.length || group.local.length);
  }, [provinces, territories]);
  const canWrite = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';
  const canArchive = sessionUser?.role === 'admin';
  const writeDisabledReason = !canWrite ? 'Editor or admin required' : isSubmitting ? 'Working…' : null;
  const archiveDisabledReason = !canArchive ? 'Admin required' : isSubmitting ? 'Working…' : null;

  useEffect(() => {
    void loadSession();
  }, []);

  useEffect(() => {
    void loadTerritories();
  }, [search, provinceFilter, readinessFilter, includeArchived, token]);

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
      if (!token) {
        setTerritories([]);
        setSelectedTerritory(null);
        return;
      }
      const response = await fetch(`${browserApiBaseUrl}/api/v1/territories?${params.toString()}`, { headers: authorizationHeader(token) });
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
      if (!token) return;
      const response = await fetch(`${browserApiBaseUrl}/api/v1/territories/${territoryId}`, { headers: authorizationHeader(token) });
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
          <span><strong>{territorySummary.official}</strong> official routing areas</span>
          <span><strong>{territorySummary.local}</strong> local referenced areas</span>
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
          <label className="checkbox-row" htmlFor="include-archived-territories">
            <input id="include-archived-territories" type="checkbox" checked={includeArchived} onChange={(event) => setIncludeArchived(event.target.checked)} />
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

      <article className="public-task-panel territory-hierarchy-panel">
        <div className="panel-head">
          <p className="section-label">Province hierarchy</p>
          <h3>Province → municipality routing map</h3>
        </div>
        <p className="institutional-note">Official municipality routes are administrative names, not surveyed boundary geometry. Local referenced areas support intake and require operator confirmation.</p>
        <div className="territory-hierarchy-grid">
          {territoryHierarchy.map((group) => (
            <details key={group.province.code} className="quiet-disclosure hierarchy-province" open={group.province.code === provinceFilter || (!provinceFilter && group.province.code === 'BN')}>
              <summary>{group.province.name} · {group.official.length} official · {group.local.length} local</summary>
              {group.official.length ? (
                <div className="hierarchy-lane">
                  <strong>Rutas administrativas oficiales</strong>
                  <div className="hierarchy-chip-list">
                    {group.official.map((territory) => (
                      <button key={territory.id} className="mini-action-button" type="button" onClick={() => void loadTerritoryDetail(territory.id)}>{territory.name}</button>
                    ))}
                  </div>
                </div>
              ) : null}
              {group.local.length ? (
                <div className="hierarchy-lane">
                  <strong>Áreas locales referenciadas</strong>
                  <div className="hierarchy-chip-list">
                    {group.local.map((territory) => (
                      <button key={territory.id} className="mini-action-button" type="button" onClick={() => void loadTerritoryDetail(territory.id)}>{territory.name}</button>
                    ))}
                  </div>
                </div>
              ) : null}
            </details>
          ))}
        </div>
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
              <span className="status-chip warn">{selectedTerritory.is_archived ? 'archived' : readinessLabel(selectedTerritory.readiness)}</span>
              <span className="status-chip">{territoryTypeLabel(selectedTerritory.type)}</span>
              {selectedTerritory.admin_unit_name ? <span className="status-chip ok">{selectedTerritory.admin_unit_level}: {selectedTerritory.admin_unit_name}</span> : null}
            </div>
            <details className="quiet-disclosure territory-evidence-disclosure" open>
              <summary>Fuente, confianza y límite de publicación</summary>
              <div className="routing-evidence-grid">
                <span><strong>Fuente</strong>{sourceLabel(selectedTerritory)}</span>
                <span><strong>Confianza</strong>{confidenceLabel(selectedTerritory)}</span>
                <span><strong>Geometría</strong>{geometryLabel(selectedTerritory)}</span>
                <span><strong>Publicación</strong>{publicationLabel(selectedTerritory)}</span>
              </div>
            </details>
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
                <p>{territory.province} ({territory.province_code}) · {territoryTypeLabel(territory.type)} · {territory.admin_unit_name ?? 'admin unit pending'}</p>
              </div>
              <div className="record-actions">
                <span className="territory-meta">{territory.is_archived ? 'archived' : readinessLabel(territory.readiness)}</span>
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
