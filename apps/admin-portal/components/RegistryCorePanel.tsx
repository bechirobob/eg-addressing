'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

import { authorizationHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

type Territory = { id: string; name: string; province_code: string; province: string; type: string; readiness: string; is_archived: boolean };
type Road = { id: string; name: string; territory_id: string; territory_name: string; status: string; length_km: string; is_archived: boolean };
type Building = { id: string; label: string; territory_id: string; territory_name: string; road_id: string; road_name: string; status: string; usage: string; is_archived: boolean };
type Address = { id: string; formatted: string; territory_id: string; territory_name: string; road_id: string; road_name: string; building_id: string; building_label: string; province_code: string; status: string; publication_state: string; is_archived: boolean };

type RegistryCorePanelProps = {
  initialTerritories: Territory[];
  initialRoads: Road[];
  initialBuildings: Building[];
  initialAddresses: Address[];
  apiBaseUrl: string;
  highlightEntityId?: string | null;
};

type RegistryFocus =
  | { entityType: 'road'; label: string; id: string }
  | { entityType: 'building'; label: string; id: string }
  | { entityType: 'address'; label: string; id: string }
  | null;

type RegisterTab = 'addresses' | 'roads' | 'buildings';

function plainStatus(value?: string | null) {
  return (value || 'unknown').replaceAll('-', ' ').replaceAll('_', ' ');
}

function publicationLabel(address: Address) {
  if (address.is_archived) return 'Archived';
  if (address.publication_state === 'published') return 'Published';
  if (address.publication_state === 'internal-registry' || address.status === 'registry-ready') return 'Internal hold';
  return 'Draft';
}

export function RegistryCorePanel({
  initialTerritories,
  initialRoads,
  initialBuildings,
  initialAddresses,
  apiBaseUrl,
  highlightEntityId,
}: RegistryCorePanelProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [territories, setTerritories] = useState(initialTerritories.filter((item) => !item.is_archived));
  const [roads, setRoads] = useState(initialRoads);
  const [buildings, setBuildings] = useState(initialBuildings);
  const [addresses, setAddresses] = useState(initialAddresses);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [registryFocus, setRegistryFocus] = useState<RegistryFocus>(null);
  const [activeTab, setActiveTab] = useState<RegisterTab>('addresses');
  const [includeArchived, setIncludeArchived] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const [roadForm, setRoadForm] = useState({ name: '', territory_id: territories[0]?.id ?? '', status: 'draft', length_km: '1.0' });
  const [buildingForm, setBuildingForm] = useState({
    label: '',
    territory_id: territories[0]?.id ?? '',
    road_id: initialRoads[0]?.id ?? '',
    status: 'draft',
    usage: 'residential',
  });
  const [addressForm, setAddressForm] = useState({
    formatted: '',
    territory_id: territories[0]?.id ?? '',
    road_id: initialRoads[0]?.id ?? '',
    building_id: initialBuildings[0]?.id ?? '',
    status: 'draft',
  });
  const [selectedRoadId, setSelectedRoadId] = useState(initialRoads.find((item) => !item.is_archived)?.id ?? initialRoads[0]?.id ?? '');
  const [selectedBuildingId, setSelectedBuildingId] = useState(initialBuildings.find((item) => !item.is_archived)?.id ?? initialBuildings[0]?.id ?? '');
  const [selectedAddressId, setSelectedAddressId] = useState(initialAddresses.find((item) => !item.is_archived)?.id ?? initialAddresses[0]?.id ?? '');

  const normalizedSearchQuery = searchQuery.trim().toLowerCase();
  const visibleRoads = useMemo(() => roads.filter((item) => {
    if (!includeArchived && item.is_archived) return false;
    if (!normalizedSearchQuery) return true;
    return [item.name, item.territory_name, item.status, item.length_km].some((value) => value?.toLowerCase().includes(normalizedSearchQuery));
  }), [roads, includeArchived, normalizedSearchQuery]);
  const visibleBuildings = useMemo(() => buildings.filter((item) => {
    if (!includeArchived && item.is_archived) return false;
    if (!normalizedSearchQuery) return true;
    return [item.label, item.territory_name, item.road_name, item.status, item.usage].some((value) => value?.toLowerCase().includes(normalizedSearchQuery));
  }), [buildings, includeArchived, normalizedSearchQuery]);
  const visibleAddresses = useMemo(() => addresses.filter((item) => {
    if (!includeArchived && item.is_archived) return false;
    if (!normalizedSearchQuery) return true;
    return [item.formatted, item.territory_name, item.road_name, item.building_label, item.status, item.publication_state, item.province_code].some((value) => value?.toLowerCase().includes(normalizedSearchQuery));
  }), [addresses, includeArchived, normalizedSearchQuery]);

  const selectedRoad = roads.find((item) => item.id === selectedRoadId) ?? null;
  const selectedBuilding = buildings.find((item) => item.id === selectedBuildingId) ?? null;
  const selectedAddress = addresses.find((item) => item.id === selectedAddressId) ?? null;
  const canWrite = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';
  const canArchive = sessionUser?.role === 'admin';

  const roadsForBuildingTerritory = useMemo(
    () => roads.filter((item) => item.territory_id === buildingForm.territory_id && !item.is_archived),
    [roads, buildingForm.territory_id],
  );
  const roadsForAddressTerritory = useMemo(
    () => roads.filter((item) => item.territory_id === addressForm.territory_id && !item.is_archived),
    [roads, addressForm.territory_id],
  );
  const buildingsForAddressChain = useMemo(
    () =>
      buildings.filter(
        (item) => item.territory_id === addressForm.territory_id && item.road_id === addressForm.road_id && !item.is_archived,
      ),
    [buildings, addressForm.territory_id, addressForm.road_id],
  );

  const registryCounts = useMemo(
    () => ({
      activeAddresses: addresses.filter((item) => !item.is_archived).length,
      internalHold: addresses.filter((item) => !item.is_archived && (item.publication_state === 'internal-registry' || item.status === 'registry-ready')).length,
      published: addresses.filter((item) => !item.is_archived && item.publication_state === 'published').length,
      archived: addresses.filter((item) => item.is_archived).length,
    }),
    [addresses],
  );

  const caseLanes = useMemo(
    () => [
      {
        key: 'internal-hold',
        label: 'Internal holds',
        count: registryCounts.internalHold,
        tone: 'warn',
        scent: 'Records ready for protected review but not public release.',
      },
      {
        key: 'published',
        label: 'Published cases',
        count: registryCounts.published,
        tone: 'ok',
        scent: 'Public-facing records; changes require careful audit trail.',
      },
      {
        key: 'archive',
        label: 'Archive lane',
        count: registryCounts.archived,
        tone: '',
        scent: 'Hidden records available only for history and cleanup review.',
      },
    ],
    [registryCounts],
  );

  useEffect(() => {
    if (!highlightEntityId) return;

    const highlightedRoad = roads.find((item) => item.id === highlightEntityId);
    if (highlightedRoad) {
      setSelectedRoadId(highlightedRoad.id);
      setActiveTab('roads');
      setRegistryFocus({ entityType: 'road', id: highlightedRoad.id, label: highlightedRoad.name });
      return;
    }

    const highlightedBuilding = buildings.find((item) => item.id === highlightEntityId);
    if (highlightedBuilding) {
      setSelectedBuildingId(highlightedBuilding.id);
      setActiveTab('buildings');
      setRegistryFocus({ entityType: 'building', id: highlightedBuilding.id, label: highlightedBuilding.label });
      return;
    }

    const highlightedAddress = addresses.find((item) => item.id === highlightEntityId);
    if (highlightedAddress) {
      setSelectedAddressId(highlightedAddress.id);
      setActiveTab('addresses');
      setRegistryFocus({ entityType: 'address', id: highlightedAddress.id, label: highlightedAddress.formatted });
    }
  }, [addresses, buildings, highlightEntityId, roads]);

  useEffect(() => {
    if (token) {
      void reloadAll();
    }
  }, [token]);

  async function reloadAll() {
    if (!token) {
      setError('Sign in to load protected registry lists.');
      return;
    }
    setIsRefreshing(true);
    try {
      const auth = authorizationHeader(token);
      const [territoriesResponse, roadsResponse, buildingsResponse, addressesResponse] = await Promise.all([
        fetch(`${browserApiBaseUrl}/api/v1/territories?include_archived=true`, { headers: auth }),
        fetch(`${browserApiBaseUrl}/api/v1/roads?include_archived=true`, { headers: auth }),
        fetch(`${browserApiBaseUrl}/api/v1/buildings?include_archived=true`, { headers: auth }),
        fetch(`${browserApiBaseUrl}/api/v1/addresses?include_archived=true`, { headers: auth }),
      ]);
      if (!territoriesResponse.ok || !roadsResponse.ok || !buildingsResponse.ok || !addressesResponse.ok) {
        setError('Unable to refresh the registry lists.');
        return;
      }
      const territoriesPayload = (await territoriesResponse.json()) as { items: Territory[] };
      const roadsPayload = (await roadsResponse.json()) as { items: Road[] };
      const buildingsPayload = (await buildingsResponse.json()) as { items: Building[] };
      const addressesPayload = (await addressesResponse.json()) as { items: Address[] };
      const nextTerritories = territoriesPayload.items ?? [];
      const nextRoads = roadsPayload.items ?? [];
      const nextBuildings = buildingsPayload.items ?? [];
      const nextAddresses = addressesPayload.items ?? [];
      setTerritories(nextTerritories.filter((item) => !item.is_archived));
      setRoads(nextRoads);
      setBuildings(nextBuildings);
      setAddresses(nextAddresses);
      if (!roadForm.territory_id && nextTerritories[0]) setRoadForm((current) => ({ ...current, territory_id: nextTerritories[0].id }));
      if (!buildingForm.territory_id && nextTerritories[0]) setBuildingForm((current) => ({ ...current, territory_id: nextTerritories[0].id, road_id: nextRoads[0]?.id ?? current.road_id }));
      if (!addressForm.territory_id && nextTerritories[0]) setAddressForm((current) => ({ ...current, territory_id: nextTerritories[0].id, road_id: nextRoads[0]?.id ?? current.road_id, building_id: nextBuildings[0]?.id ?? current.building_id }));
    } catch {
      setError('Unable to refresh the registry lists.');
    } finally {
      setIsRefreshing(false);
    }
  }

  async function mutate<T extends Record<string, string>>(
    path: string,
    method: 'POST' | 'PATCH' | 'DELETE',
    payload?: T,
  ) {
    if (!token || !(canWrite || (canArchive && method === 'DELETE'))) {
      setError('Sign in with sufficient role for this registry action.');
      return null;
    }

    setIsSubmitting(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}${path}`, {
        method,
        headers: { ...(payload ? { 'Content-Type': 'application/json' } : {}), ...authorizationHeader(token!) },
        body: payload ? JSON.stringify(payload) : undefined,
      });
      const result = (await response.json()) as { detail?: string; id?: string };
      if (!response.ok) {
        setError(result.detail ?? 'Registry action failed.');
        return null;
      }
      await reloadAll();
      return result;
    } catch {
      setError('Registry action failed.');
      return null;
    } finally {
      setIsSubmitting(false);
    }
  }

  function archiveEntity(type: 'roads' | 'buildings' | 'addresses', id: string, label: string) {
    void mutate(`/api/v1/${type}/${id}`, 'DELETE').then((result) => {
      if (result) {
        setNotice(`${type === 'addresses' ? 'Address' : type === 'roads' ? 'Road' : 'Building'} archived: ${label}`);
      }
    });
  }

  return (
    <section className="registry-simple-shell" aria-label="Registry administration center">
      <article className="public-task-panel registry-simple-hero">
        <div>
          <p className="section-label">Address registry</p>
          <h2>Search records</h2>
          <p className="public-task-copy">Search, update, and manage official address records.</p>
        </div>
        <label className="territory-field territory-field-wide registry-search-control">
          <span className="territory-label">Search registry records</span>
          <input
            className="territory-input"
            type="search"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search addresses, roads, buildings, status, or territory"
            autoComplete="off"
          />
        </label>
        <div className="operator-summary-row registry-count-line" aria-label="Registry overview">
          <span>Active addresses: <strong>{registryCounts.activeAddresses}</strong></span>
          <span>Internal hold: <strong>{registryCounts.internalHold}</strong></span>
          <span>Published: <strong>{registryCounts.published}</strong></span>
          <span>Archived hidden: <strong>{registryCounts.archived}</strong></span>
        </div>
        <div className="registry-section-list" aria-label="Registry record sections">
          {caseLanes.map((lane) => (
            <button
              key={lane.key}
              className={`registry-section-row ${lane.tone}`}
              type="button"
              onClick={() => {
                setActiveTab('addresses');
                if (lane.key === 'archive') setIncludeArchived(true);
              }}
            >
              <span>{lane.label}</span>
              <strong>{lane.count}</strong>
              <small>{lane.scent}</small>
            </button>
          ))}
        </div>
        <div className="registry-job-tabs" role="tablist" aria-label="Registry sections">
          <button className={activeTab === 'addresses' ? 'active' : ''} type="button" onClick={() => setActiveTab('addresses')}>Addresses</button>
          <button className={activeTab === 'roads' ? 'active' : ''} type="button" onClick={() => setActiveTab('roads')}>Roads</button>
          <button className={activeTab === 'buildings' ? 'active' : ''} type="button" onClick={() => setActiveTab('buildings')}>Buildings</button>
        </div>
        <label className="checkbox-row registry-archive-toggle" htmlFor="include-archived-registry">
          <input id="include-archived-registry" type="checkbox" checked={includeArchived} onChange={(event) => setIncludeArchived(event.target.checked)} />
          <span>Show archived records</span>
        </label>
        {sessionStatus === 'loading' ? <p className="panel-state">Checking access before enabling registry actions…</p> : null}
        {isRefreshing ? <p className="panel-state">Refreshing registry lists…</p> : null}
        {registryFocus ? <p className="form-notice success">Selected from workflow: {registryFocus.label}</p> : null}
        {notice ? <p className="form-notice success">{notice}</p> : null}
        {error ? <p className="form-notice error">{error}</p> : null}
      </article>

      {activeTab === 'addresses' ? (
        <article className="public-task-panel registry-simple-section">
          <div className="panel-head quiet-head">
            <div>
              <p className="section-label">Address register</p>
              <h3>Official address records</h3>
            </div>
            <span className="registry-result-count">{visibleAddresses.length} shown</span>
          </div>

          <details className="quiet-disclosure registry-create-disclosure">
            <summary>Create a new address manually</summary>
            <form
              className="territory-form registry-simple-form"
              onSubmit={(event: FormEvent<HTMLFormElement>) => {
                event.preventDefault();
                void mutate('/api/v1/addresses', 'POST', addressForm).then((result) => {
                  if (result?.id) {
                    setNotice(`Address created: ${addressForm.formatted}`);
                    setSelectedAddressId(result.id);
                    setRegistryFocus({ entityType: 'address', id: result.id, label: addressForm.formatted });
                  }
                });
              }}
            >
              <label className="territory-field territory-field-wide">
                <span className="territory-label">Address name shown to operators</span>
                <input className="territory-input" value={addressForm.formatted} onChange={(event) => setAddressForm({ ...addressForm, formatted: event.target.value })} required />
              </label>
              <label className="territory-field">
                <span className="territory-label">Routing area</span>
                <select
                  className="territory-input"
                  value={addressForm.territory_id}
                  onChange={(event) =>
                    setAddressForm({
                      ...addressForm,
                      territory_id: event.target.value,
                      road_id: roads.filter((road) => road.territory_id === event.target.value && !road.is_archived)[0]?.id ?? '',
                      building_id: '',
                    })
                  }
                >
                  {territories.map((territory) => <option key={territory.id} value={territory.id}>{territory.name}</option>)}
                </select>
              </label>
              <label className="territory-field">
                <span className="territory-label">Road</span>
                <select
                  className="territory-input"
                  value={addressForm.road_id}
                  onChange={(event) =>
                    setAddressForm({
                      ...addressForm,
                      road_id: event.target.value,
                      building_id: buildings.filter((building) => building.road_id === event.target.value && !building.is_archived)[0]?.id ?? '',
                    })
                  }
                >
                  {roadsForAddressTerritory.map((road) => <option key={road.id} value={road.id}>{road.name}</option>)}
                </select>
              </label>
              <label className="territory-field">
                <span className="territory-label">Building</span>
                <select className="territory-input" value={addressForm.building_id} onChange={(event) => setAddressForm({ ...addressForm, building_id: event.target.value })}>
                  {buildingsForAddressChain.map((building) => <option key={building.id} value={building.id}>{building.label}</option>)}
                </select>
              </label>
              <label className="territory-field">
                <span className="territory-label">Starting status</span>
                <select className="territory-input" value={addressForm.status} onChange={(event) => setAddressForm({ ...addressForm, status: event.target.value })}>
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                </select>
              </label>
              <div className="territory-form-actions">
                <button className="verification-button" type="submit" disabled={!canWrite || isSubmitting}>
                  {!canWrite ? 'Editor or admin access required' : isSubmitting ? 'Working…' : 'Create address'}
                </button>
              </div>
            </form>
          </details>

          <div className="registry-simple-layout">
            <aside className="registry-simple-list" aria-label="Address records">
              {visibleAddresses.length ? visibleAddresses.map((address) => (
                <button key={address.id} className={`registry-simple-row ${selectedAddressId === address.id ? 'active' : ''}`} type="button" onClick={() => setSelectedAddressId(address.id)}>
                  <strong>{address.formatted}</strong>
                  <span>{address.territory_name || 'Routing area pending'}</span>
                  <small>{publicationLabel(address)} · {address.is_archived ? 'hidden from daily work' : 'active record'}</small>
                </button>
              )) : <p className="panel-state">No address records match this search.</p>}
            </aside>

            <div className="registry-simple-detail">
              {selectedAddress ? (
                <>
                  <div className="registry-selected-card">
                    <p className="section-label">Selected address</p>
                    <h3>{selectedAddress.formatted}</h3>
                    <div className="operator-summary-row registry-selected-meta">
                      <span>{publicationLabel(selectedAddress)}</span>
                      <span>{selectedAddress.territory_name || 'Routing pending'}</span>
                      <span>{plainStatus(selectedAddress.status)}</span>
                    </div>
                    <p className="public-task-copy">
                      {selectedAddress.is_archived
                        ? 'This record is archived and hidden from normal daily work. Turn on archived records only when auditing history.'
                        : selectedAddress.publication_state === 'published'
                          ? 'This address is published. Treat changes carefully and keep an audit trail.'
                          : 'This address is not public yet. Keep reviewing it internally until it is ready for official publication.'}
                    </p>
                    <details className="quiet-disclosure">
                      <summary>Show record details</summary>
                      <dl className="registry-fact-list">
                        <div><dt>Province</dt><dd>{selectedAddress.province_code || 'Not set'}</dd></div>
                        <div><dt>Road</dt><dd>{selectedAddress.road_name || 'Not set'}</dd></div>
                        <div><dt>Building</dt><dd>{selectedAddress.building_label || 'Not set'}</dd></div>
                        <div><dt>Publication state</dt><dd>{plainStatus(selectedAddress.publication_state)}</dd></div>
                      </dl>
                    </details>
                    <details className="quiet-disclosure">
                      <summary>Admin-only archive action</summary>
                      <p className="institutional-note">Archive removes the record from daily work views. Use this only when the record should no longer be operated on.</p>
                      <button
                        className="mini-action-button danger"
                        type="button"
                        disabled={!canArchive || isSubmitting}
                        title={!canArchive ? 'Admin access required to archive' : undefined}
                        onClick={() => archiveEntity('addresses', selectedAddress.id, selectedAddress.formatted)}
                      >
                        {!canArchive ? 'Admin required' : selectedAddress.is_archived ? 'Already archived' : 'Archive address'}
                      </button>
                    </details>
                  </div>
                </>
              ) : <p className="panel-state">Select an address to inspect it.</p>}
            </div>
          </div>
        </article>
      ) : null}

      {activeTab === 'roads' ? (
        <article className="public-task-panel registry-simple-section">
          <div className="panel-head quiet-head">
            <div>
              <p className="section-label">Road register</p>
              <h3>Roads support address creation</h3>
            </div>
            <span className="registry-result-count">{visibleRoads.length} shown</span>
          </div>
          <details className="quiet-disclosure registry-create-disclosure">
            <summary>Create a new road</summary>
            <form
              className="territory-form registry-simple-form"
              onSubmit={(event: FormEvent<HTMLFormElement>) => {
                event.preventDefault();
                void mutate('/api/v1/roads', 'POST', roadForm).then((result) => {
                  if (result?.id) {
                    setNotice(`Road created: ${roadForm.name}`);
                    setSelectedRoadId(result.id);
                    setRegistryFocus({ entityType: 'road', id: result.id, label: roadForm.name });
                  }
                });
              }}
            >
              <label className="territory-field"><span className="territory-label">Road name</span><input className="territory-input" value={roadForm.name} onChange={(event) => setRoadForm({ ...roadForm, name: event.target.value })} required /></label>
              <label className="territory-field"><span className="territory-label">Routing area</span><select className="territory-input" value={roadForm.territory_id} onChange={(event) => setRoadForm({ ...roadForm, territory_id: event.target.value })}>{territories.map((territory) => <option key={territory.id} value={territory.id}>{territory.name}</option>)}</select></label>
              <label className="territory-field"><span className="territory-label">Status</span><select className="territory-input" value={roadForm.status} onChange={(event) => setRoadForm({ ...roadForm, status: event.target.value })}><option value="draft">Draft</option><option value="active">Active</option></select></label>
              <label className="territory-field"><span className="territory-label">Length (km)</span><input className="territory-input" value={roadForm.length_km} onChange={(event) => setRoadForm({ ...roadForm, length_km: event.target.value })} required /></label>
              <div className="territory-form-actions"><button className="verification-button" type="submit" disabled={!canWrite || isSubmitting}>{!canWrite ? 'Editor or admin required' : isSubmitting ? 'Working…' : 'Create road'}</button></div>
            </form>
          </details>
          <div className="registry-simple-list registry-simple-list-full">
            {visibleRoads.length ? visibleRoads.map((road) => (
              <button key={road.id} className={`registry-simple-row ${selectedRoadId === road.id ? 'active' : ''}`} type="button" onClick={() => setSelectedRoadId(road.id)}>
                <strong>{road.name}</strong><span>{road.territory_name}</span><small>{road.is_archived ? 'Archived' : plainStatus(road.status)}</small>
              </button>
            )) : <p className="panel-state">No road records match this search.</p>}
          </div>
          {selectedRoad ? <details className="quiet-disclosure"><summary>Admin-only archive action</summary><button className="mini-action-button danger" type="button" disabled={!canArchive || isSubmitting || selectedRoad.is_archived} onClick={() => archiveEntity('roads', selectedRoad.id, selectedRoad.name)}>{selectedRoad.is_archived ? 'Already archived' : 'Archive road'}</button></details> : null}
        </article>
      ) : null}

      {activeTab === 'buildings' ? (
        <article className="public-task-panel registry-simple-section">
          <div className="panel-head quiet-head">
            <div>
              <p className="section-label">Building register</p>
              <h3>Buildings connect roads to addresses</h3>
            </div>
            <span className="registry-result-count">{visibleBuildings.length} shown</span>
          </div>
          <details className="quiet-disclosure registry-create-disclosure">
            <summary>Create a new building</summary>
            <form
              className="territory-form registry-simple-form"
              onSubmit={(event: FormEvent<HTMLFormElement>) => {
                event.preventDefault();
                void mutate('/api/v1/buildings', 'POST', buildingForm).then((result) => {
                  if (result?.id) {
                    setNotice(`Building created: ${buildingForm.label}`);
                    setSelectedBuildingId(result.id);
                    setRegistryFocus({ entityType: 'building', id: result.id, label: buildingForm.label });
                  }
                });
              }}
            >
              <label className="territory-field"><span className="territory-label">Building label</span><input className="territory-input" value={buildingForm.label} onChange={(event) => setBuildingForm({ ...buildingForm, label: event.target.value })} required /></label>
              <label className="territory-field"><span className="territory-label">Routing area</span><select className="territory-input" value={buildingForm.territory_id} onChange={(event) => setBuildingForm({ ...buildingForm, territory_id: event.target.value, road_id: roads.filter((road) => road.territory_id === event.target.value && !road.is_archived)[0]?.id ?? '' })}>{territories.map((territory) => <option key={territory.id} value={territory.id}>{territory.name}</option>)}</select></label>
              <label className="territory-field"><span className="territory-label">Road</span><select className="territory-input" value={buildingForm.road_id} onChange={(event) => setBuildingForm({ ...buildingForm, road_id: event.target.value })}>{roadsForBuildingTerritory.map((road) => <option key={road.id} value={road.id}>{road.name}</option>)}</select></label>
              <label className="territory-field"><span className="territory-label">Status</span><select className="territory-input" value={buildingForm.status} onChange={(event) => setBuildingForm({ ...buildingForm, status: event.target.value })}><option value="draft">Draft</option><option value="active">Active</option></select></label>
              <label className="territory-field"><span className="territory-label">Use</span><input className="territory-input" value={buildingForm.usage} onChange={(event) => setBuildingForm({ ...buildingForm, usage: event.target.value })} required /></label>
              <div className="territory-form-actions"><button className="verification-button" type="submit" disabled={!canWrite || isSubmitting}>{!canWrite ? 'Editor or admin required' : isSubmitting ? 'Working…' : 'Create building'}</button></div>
            </form>
          </details>
          <div className="registry-simple-list registry-simple-list-full">
            {visibleBuildings.length ? visibleBuildings.map((building) => (
              <button key={building.id} className={`registry-simple-row ${selectedBuildingId === building.id ? 'active' : ''}`} type="button" onClick={() => setSelectedBuildingId(building.id)}>
                <strong>{building.label}</strong><span>{building.road_name}</span><small>{building.is_archived ? 'Archived' : `${plainStatus(building.usage)} · ${plainStatus(building.status)}`}</small>
              </button>
            )) : <p className="panel-state">No building records match this search.</p>}
          </div>
          {selectedBuilding ? <details className="quiet-disclosure"><summary>Admin-only archive action</summary><button className="mini-action-button danger" type="button" disabled={!canArchive || isSubmitting || selectedBuilding.is_archived} onClick={() => archiveEntity('buildings', selectedBuilding.id, selectedBuilding.label)}>{selectedBuilding.is_archived ? 'Already archived' : 'Archive building'}</button></details> : null}
        </article>
      ) : null}
    </section>
  );
}
