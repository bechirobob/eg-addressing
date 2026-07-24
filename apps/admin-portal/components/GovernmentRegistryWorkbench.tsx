'use client';

import Link from 'next/link';
import type { FormEvent } from 'react';
import { useEffect, useMemo, useState } from 'react';

import { GovernmentIcon } from './GovernmentIcon';
import { authorizationHeader, csrfHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

type Territory = {
  id: string;
  name: string;
  province_code: string;
  province: string;
  type: string;
  readiness: string;
  is_archived: boolean;
};

type Road = {
  id: string;
  name: string;
  territory_id: string;
  territory_name: string;
  status: string;
  length_km: string;
  is_archived: boolean;
};

type Building = {
  id: string;
  label: string;
  territory_id: string;
  territory_name: string;
  road_id: string;
  road_name: string;
  status: string;
  usage: string;
  is_archived: boolean;
};

type Address = {
  id: string;
  formatted: string;
  territory_id: string;
  territory_name: string;
  road_id: string;
  road_name: string;
  building_id: string;
  building_label: string;
  province_code: string;
  status: string;
  publication_state: string;
  is_archived: boolean;
};

type RegisterTab = 'addresses' | 'roads' | 'buildings';
type RegistryRecord = Address | Road | Building;

type GovernmentRegistryWorkbenchProps = {
  apiBaseUrl: string;
  highlightEntityId?: string | null;
};

function plainStatus(value?: string | null) {
  return (value || 'unknown').replaceAll('-', ' ').replaceAll('_', ' ');
}

function addressOperationalState(address: Address) {
  if (address.is_archived) return 'Archived';
  if (address.publication_state === 'published') return 'Published';
  if (address.publication_state === 'internal-registry' || address.status === 'registry-ready') return 'Needs verification';
  return plainStatus(address.status || 'draft');
}

function recordLabel(tab: RegisterTab, record: RegistryRecord) {
  if (tab === 'addresses') return (record as Address).formatted;
  if (tab === 'roads') return (record as Road).name;
  return (record as Building).label;
}

function recordTerritory(record: RegistryRecord) {
  return record.territory_name || 'Routing area pending';
}

function recordState(tab: RegisterTab, record: RegistryRecord) {
  if (tab === 'addresses') return addressOperationalState(record as Address);
  return record.is_archived ? 'Archived' : plainStatus(record.status);
}

export function GovernmentRegistryWorkbench({ apiBaseUrl, highlightEntityId }: GovernmentRegistryWorkbenchProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [territories, setTerritories] = useState<Territory[]>([]);
  const [roads, setRoads] = useState<Road[]>([]);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [activeTab, setActiveTab] = useState<RegisterTab>('addresses');
  const [selectedIds, setSelectedIds] = useState<Record<RegisterTab, string>>({ addresses: '', roads: '', buildings: '' });
  const [searchQuery, setSearchQuery] = useState('');
  const [territoryFilter, setTerritoryFilter] = useState('all');
  const [stateFilter, setStateFilter] = useState('all');
  const [includeArchived, setIncludeArchived] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isWorking, setIsWorking] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [addressCreate, setAddressCreate] = useState({ formatted: '', territory_id: '', road_id: '', building_id: '', status: 'draft' });
  const [roadCreate, setRoadCreate] = useState({ name: '', territory_id: '', status: 'draft', length_km: '1.0' });
  const [buildingCreate, setBuildingCreate] = useState({ label: '', territory_id: '', road_id: '', status: 'draft', usage: 'residential' });
  const [editValues, setEditValues] = useState<Record<string, string>>({});

  const canWrite = sessionUser?.role === 'editor' || sessionUser?.role === 'admin';
  const canArchive = sessionUser?.role === 'admin';

  function requestHeaders(withJson = false) {
    return {
      ...(withJson ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? authorizationHeader(token) : csrfHeader()),
    };
  }

  async function reloadRegistry() {
    if (sessionStatus !== 'ready') return;
    setIsLoading(true);
    setError(null);
    try {
      const request = { credentials: 'include' as const, headers: requestHeaders() };
      const [territoryResponse, roadResponse, buildingResponse, addressResponse] = await Promise.all([
        fetch(`${browserApiBaseUrl}/api/v1/territories?include_archived=true`, request),
        fetch(`${browserApiBaseUrl}/api/v1/roads?include_archived=true`, request),
        fetch(`${browserApiBaseUrl}/api/v1/buildings?include_archived=true`, request),
        fetch(`${browserApiBaseUrl}/api/v1/addresses?include_archived=true`, request),
      ]);
      if (![territoryResponse, roadResponse, buildingResponse, addressResponse].every((response) => response.ok)) {
        throw new Error('registry-load-failed');
      }
      const territoryPayload = (await territoryResponse.json()) as { items?: Territory[] };
      const roadPayload = (await roadResponse.json()) as { items?: Road[] };
      const buildingPayload = (await buildingResponse.json()) as { items?: Building[] };
      const addressPayload = (await addressResponse.json()) as { items?: Address[] };
      const nextTerritories = territoryPayload.items ?? [];
      const nextRoads = roadPayload.items ?? [];
      const nextBuildings = buildingPayload.items ?? [];
      const nextAddresses = addressPayload.items ?? [];
      setTerritories(nextTerritories.filter((item) => !item.is_archived));
      setRoads(nextRoads);
      setBuildings(nextBuildings);
      setAddresses(nextAddresses);
      setSelectedIds((current) => ({
        addresses: nextAddresses.some((item) => item.id === current.addresses) ? current.addresses : nextAddresses.find((item) => !item.is_archived)?.id ?? nextAddresses[0]?.id ?? '',
        roads: nextRoads.some((item) => item.id === current.roads) ? current.roads : nextRoads.find((item) => !item.is_archived)?.id ?? nextRoads[0]?.id ?? '',
        buildings: nextBuildings.some((item) => item.id === current.buildings) ? current.buildings : nextBuildings.find((item) => !item.is_archived)?.id ?? nextBuildings[0]?.id ?? '',
      }));
      const firstTerritory = nextTerritories.find((item) => !item.is_archived);
      if (firstTerritory) {
        const firstRoad = nextRoads.find((item) => item.territory_id === firstTerritory.id && !item.is_archived);
        const firstBuilding = nextBuildings.find((item) => item.territory_id === firstTerritory.id && item.road_id === firstRoad?.id && !item.is_archived);
        setAddressCreate((current) => current.territory_id ? current : { ...current, territory_id: firstTerritory.id, road_id: firstRoad?.id ?? '', building_id: firstBuilding?.id ?? '' });
        setRoadCreate((current) => current.territory_id ? current : { ...current, territory_id: firstTerritory.id });
        setBuildingCreate((current) => current.territory_id ? current : { ...current, territory_id: firstTerritory.id, road_id: firstRoad?.id ?? '' });
      }
    } catch {
      setError('The authoritative registry lists could not be loaded. Retry or escalate to platform support.');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void reloadRegistry();
  }, [sessionStatus]);

  useEffect(() => {
    if (!highlightEntityId) return;
    if (addresses.some((item) => item.id === highlightEntityId)) {
      setActiveTab('addresses');
      setSelectedIds((current) => ({ ...current, addresses: highlightEntityId }));
    } else if (roads.some((item) => item.id === highlightEntityId)) {
      setActiveTab('roads');
      setSelectedIds((current) => ({ ...current, roads: highlightEntityId }));
    } else if (buildings.some((item) => item.id === highlightEntityId)) {
      setActiveTab('buildings');
      setSelectedIds((current) => ({ ...current, buildings: highlightEntityId }));
    }
  }, [addresses, buildings, highlightEntityId, roads]);

  const sourceRecords = activeTab === 'addresses' ? addresses : activeTab === 'roads' ? roads : buildings;
  const normalizedSearch = searchQuery.trim().toLowerCase();
  const visibleRecords = useMemo(() => sourceRecords.filter((record) => {
    if (!includeArchived && record.is_archived) return false;
    if (territoryFilter !== 'all' && record.territory_id !== territoryFilter) return false;
    const currentState = recordState(activeTab, record).toLowerCase();
    if (stateFilter !== 'all' && currentState !== stateFilter) return false;
    if (!normalizedSearch) return true;
    const values = activeTab === 'addresses'
      ? [recordLabel(activeTab, record), record.id, recordTerritory(record), (record as Address).road_name, (record as Address).building_label, currentState]
      : activeTab === 'roads'
        ? [recordLabel(activeTab, record), record.id, recordTerritory(record), (record as Road).length_km, currentState]
        : [recordLabel(activeTab, record), record.id, recordTerritory(record), (record as Building).road_name, (record as Building).usage, currentState];
    return values.some((value) => String(value ?? '').toLowerCase().includes(normalizedSearch));
  }), [activeTab, includeArchived, normalizedSearch, sourceRecords, stateFilter, territoryFilter]);

  const selectedRecord = sourceRecords.find((record) => record.id === selectedIds[activeTab]) ?? visibleRecords[0] ?? null;
  const addressCounts = useMemo(() => ({
    total: addresses.filter((item) => !item.is_archived).length,
    review: addresses.filter((item) => !item.is_archived && addressOperationalState(item) === 'Needs verification').length,
    published: addresses.filter((item) => !item.is_archived && item.publication_state === 'published').length,
    archived: addresses.filter((item) => item.is_archived).length,
  }), [addresses]);

  useEffect(() => {
    if (!selectedRecord) {
      setEditValues({});
      return;
    }
    if (activeTab === 'addresses') {
      const address = selectedRecord as Address;
      setEditValues({ formatted: address.formatted, status: address.status });
    } else if (activeTab === 'roads') {
      const road = selectedRecord as Road;
      setEditValues({ name: road.name, status: road.status, length_km: road.length_km });
    } else {
      const building = selectedRecord as Building;
      setEditValues({ label: building.label, status: building.status, usage: building.usage });
    }
  }, [activeTab, selectedRecord?.id]);

  async function mutate(path: string, method: 'POST' | 'PATCH' | 'DELETE', payload?: Record<string, string>) {
    if (!canWrite || (method === 'DELETE' && !canArchive)) {
      setError(method === 'DELETE' ? 'Administrator authority is required to archive registry records.' : 'Editor or administrator authority is required for registry changes.');
      return null;
    }
    setIsWorking(true);
    setNotice(null);
    setError(null);
    try {
      const response = await fetch(`${browserApiBaseUrl}${path}`, {
        method,
        credentials: 'include',
        headers: requestHeaders(Boolean(payload)),
        body: payload ? JSON.stringify(payload) : undefined,
      });
      const result = (await response.json()) as { id?: string; detail?: string };
      if (!response.ok) {
        setError(result.detail ?? 'The registry action was not accepted by the authoritative service.');
        return null;
      }
      await reloadRegistry();
      return result;
    } catch {
      setError('The registry action could not be completed. No success has been recorded.');
      return null;
    } finally {
      setIsWorking(false);
    }
  }

  async function submitCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (activeTab === 'addresses') {
      const result = await mutate('/api/v1/addresses', 'POST', addressCreate);
      if (result?.id) {
        setSelectedIds((current) => ({ ...current, addresses: result.id! }));
        setNotice(`Address created in the protected registry: ${addressCreate.formatted}.`);
        setAddressCreate((current) => ({ ...current, formatted: '' }));
      }
    } else if (activeTab === 'roads') {
      const result = await mutate('/api/v1/roads', 'POST', roadCreate);
      if (result?.id) {
        setSelectedIds((current) => ({ ...current, roads: result.id! }));
        setNotice(`Road created in the protected registry: ${roadCreate.name}.`);
        setRoadCreate((current) => ({ ...current, name: '' }));
      }
    } else {
      const result = await mutate('/api/v1/buildings', 'POST', buildingCreate);
      if (result?.id) {
        setSelectedIds((current) => ({ ...current, buildings: result.id! }));
        setNotice(`Building created in the protected registry: ${buildingCreate.label}.`);
        setBuildingCreate((current) => ({ ...current, label: '' }));
      }
    }
  }

  async function saveSelected() {
    if (!selectedRecord) return;
    const collection = activeTab;
    const result = await mutate(`/api/v1/${collection}/${encodeURIComponent(selectedRecord.id)}`, 'PATCH', editValues);
    if (result) setNotice(`${activeTab === 'addresses' ? 'Address' : activeTab === 'roads' ? 'Road' : 'Building'} record updated with an audit-tracked registry action.`);
  }

  async function archiveSelected() {
    if (!selectedRecord || selectedRecord.is_archived) return;
    const result = await mutate(`/api/v1/${activeTab}/${encodeURIComponent(selectedRecord.id)}`, 'DELETE');
    if (result) setNotice(`${recordLabel(activeTab, selectedRecord)} was archived and removed from normal operational views.`);
  }

  const roadsForAddress = roads.filter((road) => road.territory_id === addressCreate.territory_id && !road.is_archived);
  const buildingsForAddress = buildings.filter((building) => building.territory_id === addressCreate.territory_id && building.road_id === addressCreate.road_id && !building.is_archived);
  const roadsForBuilding = roads.filter((road) => road.territory_id === buildingCreate.territory_id && !road.is_archived);
  const stateOptions = Array.from(new Set(sourceRecords.map((record) => recordState(activeTab, record).toLowerCase()))).sort();

  return (
    <section className="government-operation-page government-registry-workbench" aria-labelledby="registry-workbench-title">
      <header className="government-operation-header">
        <div>
          <p>Authoritative records</p>
          <h1 id="registry-workbench-title">Address Registry</h1>
          <span>Search, inspect, create, update, and route official address records from one controlled workspace.</span>
        </div>
        <div className="government-operation-header-actions">
          <Link href="/verify"><GovernmentIcon name="verification" />Open verification queue</Link>
          <button type="button" onClick={() => void reloadRegistry()} disabled={isLoading}><GovernmentIcon name="operations" />{isLoading ? 'Refreshing' : 'Refresh registry'}</button>
        </div>
      </header>

      <dl className="government-operation-summary" aria-label="Registry status summary">
        <div><dt>Active addresses</dt><dd>{addressCounts.total}</dd><span>Protected registry scope</span></div>
        <div><dt>Needs verification</dt><dd>{addressCounts.review}</dd><span>Not approved for publication</span></div>
        <div><dt>Published</dt><dd>{addressCounts.published}</dd><span>Official public state</span></div>
        <div><dt>Roads</dt><dd>{roads.filter((item) => !item.is_archived).length}</dd><span>Address routing network</span></div>
        <div><dt>Buildings</dt><dd>{buildings.filter((item) => !item.is_archived).length}</dd><span>Addressable structures</span></div>
      </dl>

      <div className="government-command-bar" aria-label="Registry filters">
        <label className="government-search-field">
          <GovernmentIcon name="search" />
          <span className="sr-only">Search current register</span>
          <input type="search" value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Search code, name, road, building, territory, or state" />
        </label>
        <label><span>Register</span><select value={activeTab} onChange={(event) => { setActiveTab(event.target.value as RegisterTab); setStateFilter('all'); }}><option value="addresses">Addresses</option><option value="roads">Roads</option><option value="buildings">Buildings</option></select></label>
        <label><span>Territory</span><select value={territoryFilter} onChange={(event) => setTerritoryFilter(event.target.value)}><option value="all">All territories</option>{territories.map((territory) => <option key={territory.id} value={territory.id}>{territory.name}</option>)}</select></label>
        <label><span>State</span><select value={stateFilter} onChange={(event) => setStateFilter(event.target.value)}><option value="all">All states</option>{stateOptions.map((state) => <option key={state} value={state}>{plainStatus(state)}</option>)}</select></label>
        <label className="government-checkbox-control"><input type="checkbox" checked={includeArchived} onChange={(event) => setIncludeArchived(event.target.checked)} /><span>Include archived</span></label>
      </div>

      {sessionStatus === 'loading' ? <p className="government-inline-state">Resolving operator authority and loading the registry…</p> : null}
      {notice ? <p className="government-inline-state success" role="status">{notice}</p> : null}
      {error ? <p className="government-inline-state error" role="alert">{error}</p> : null}

      <div className="government-three-pane-workbench">
        <aside className="government-queue-pane" aria-label={`${activeTab} register list`}>
          <div className="government-pane-heading"><div><p>Current register</p><h2>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h2></div><span>{visibleRecords.length} shown</span></div>
          <div className="government-record-queue">
            {visibleRecords.length ? visibleRecords.map((record) => {
              const selected = selectedRecord?.id === record.id;
              return (
                <button key={record.id} className={selected ? 'active' : ''} type="button" onClick={() => setSelectedIds((current) => ({ ...current, [activeTab]: record.id }))}>
                  <span className="government-queue-record-title">{recordLabel(activeTab, record)}</span>
                  <code>{record.id}</code>
                  <span>{recordTerritory(record)}</span>
                  <small className={`government-record-state ${recordState(activeTab, record).toLowerCase().includes('publish') ? 'success' : recordState(activeTab, record).toLowerCase().includes('verify') ? 'warning' : ''}`}>{recordState(activeTab, record)}</small>
                </button>
              );
            }) : <div className="government-pane-empty"><GovernmentIcon name="records" /><strong>No matching records</strong><span>Change the filters or create an authorized record.</span></div>}
          </div>
        </aside>

        <article className="government-record-pane" aria-label="Selected registry record">
          {selectedRecord ? (
            <>
              <header className="government-selected-record-header">
                <div><p>{activeTab === 'addresses' ? 'Official address record' : activeTab === 'roads' ? 'Road registry record' : 'Building registry record'}</p><h2>{recordLabel(activeTab, selectedRecord)}</h2><code>{selectedRecord.id}</code></div>
                <span className={`government-record-state ${recordState(activeTab, selectedRecord).toLowerCase().includes('publish') ? 'success' : recordState(activeTab, selectedRecord).toLowerCase().includes('verify') ? 'warning' : ''}`}>{recordState(activeTab, selectedRecord)}</span>
              </header>
              <nav className="government-record-tabs" aria-label="Registry record sections"><span className="active">Overview</span><span>Administrative</span><span>History</span><span>Audit</span></nav>
              <div className="government-record-body">
                <section><div className="government-record-section-heading"><h3>Authoritative context</h3><span>Loaded from the protected registry service</span></div>
                  <dl className="government-record-facts">
                    <div><dt>Territory</dt><dd>{recordTerritory(selectedRecord)}</dd></div>
                    <div><dt>Record state</dt><dd>{recordState(activeTab, selectedRecord)}</dd></div>
                    {activeTab === 'addresses' ? <><div><dt>Province code</dt><dd>{(selectedRecord as Address).province_code || 'Not assigned'}</dd></div><div><dt>Road</dt><dd>{(selectedRecord as Address).road_name || 'Not assigned'}</dd></div><div><dt>Building</dt><dd>{(selectedRecord as Address).building_label || 'Not assigned'}</dd></div><div><dt>Publication state</dt><dd>{plainStatus((selectedRecord as Address).publication_state)}</dd></div></> : null}
                    {activeTab === 'roads' ? <><div><dt>Length</dt><dd>{(selectedRecord as Road).length_km} km</dd></div><div><dt>Operational status</dt><dd>{plainStatus((selectedRecord as Road).status)}</dd></div></> : null}
                    {activeTab === 'buildings' ? <><div><dt>Road</dt><dd>{(selectedRecord as Building).road_name || 'Not assigned'}</dd></div><div><dt>Use</dt><dd>{plainStatus((selectedRecord as Building).usage)}</dd></div></> : null}
                    <div><dt>Archive state</dt><dd>{selectedRecord.is_archived ? 'Archived' : 'Active operational record'}</dd></div>
                  </dl>
                </section>
                <section><div className="government-record-section-heading"><h3>Controlled update</h3><span>Changes are submitted to the existing audit-enabled API</span></div>
                  <div className="government-edit-grid">
                    {activeTab === 'addresses' ? <><label><span>Operator-facing address</span><input value={editValues.formatted ?? ''} onChange={(event) => setEditValues((current) => ({ ...current, formatted: event.target.value }))} /></label><label><span>Registry status</span><select value={editValues.status ?? 'draft'} onChange={(event) => setEditValues((current) => ({ ...current, status: event.target.value }))}><option value="draft">Draft</option><option value="active">Active</option><option value="registry-ready">Registry ready</option></select></label></> : null}
                    {activeTab === 'roads' ? <><label><span>Road name</span><input value={editValues.name ?? ''} onChange={(event) => setEditValues((current) => ({ ...current, name: event.target.value }))} /></label><label><span>Status</span><select value={editValues.status ?? 'draft'} onChange={(event) => setEditValues((current) => ({ ...current, status: event.target.value }))}><option value="draft">Draft</option><option value="active">Active</option></select></label><label><span>Length (km)</span><input value={editValues.length_km ?? ''} onChange={(event) => setEditValues((current) => ({ ...current, length_km: event.target.value }))} /></label></> : null}
                    {activeTab === 'buildings' ? <><label><span>Building label</span><input value={editValues.label ?? ''} onChange={(event) => setEditValues((current) => ({ ...current, label: event.target.value }))} /></label><label><span>Status</span><select value={editValues.status ?? 'draft'} onChange={(event) => setEditValues((current) => ({ ...current, status: event.target.value }))}><option value="draft">Draft</option><option value="active">Active</option></select></label><label><span>Use</span><input value={editValues.usage ?? ''} onChange={(event) => setEditValues((current) => ({ ...current, usage: event.target.value }))} /></label></> : null}
                  </div>
                </section>
              </div>
            </>
          ) : <div className="government-pane-empty large"><GovernmentIcon name="registry" /><strong>Select a registry record</strong><span>The record, authoritative context, and permitted actions will appear here.</span></div>}
        </article>

        <aside className="government-decision-pane" aria-label="Registry actions">
          <div className="government-pane-heading"><div><p>Registry control</p><h2>Valid next actions</h2></div><span>{canWrite ? 'Write authority' : 'Read only'}</span></div>
          <div className="government-decision-body">
            <section><h3>Selected record</h3><div className="government-action-stack"><button className="primary" type="button" onClick={() => void saveSelected()} disabled={!selectedRecord || !canWrite || isWorking}>{!canWrite ? 'Editor or admin required' : isWorking ? 'Working…' : 'Save controlled update'}</button>{activeTab === 'addresses' && selectedRecord && recordState(activeTab, selectedRecord) === 'Needs verification' ? <Link href="/verify">Open evidence decision queue</Link> : null}<button className="danger" type="button" onClick={() => void archiveSelected()} disabled={!selectedRecord || selectedRecord.is_archived || !canArchive || isWorking}>{!canArchive ? 'Administrator required to archive' : selectedRecord?.is_archived ? 'Record already archived' : 'Archive selected record'}</button></div></section>
            <section><h3>Create in current register</h3><form className="government-create-form" onSubmit={(event) => void submitCreate(event)}>
              {activeTab === 'addresses' ? <><label><span>Address name</span><input required value={addressCreate.formatted} onChange={(event) => setAddressCreate((current) => ({ ...current, formatted: event.target.value }))} /></label><label><span>Territory</span><select value={addressCreate.territory_id} onChange={(event) => { const nextRoad = roads.find((road) => road.territory_id === event.target.value && !road.is_archived); const nextBuilding = buildings.find((building) => building.territory_id === event.target.value && building.road_id === nextRoad?.id && !building.is_archived); setAddressCreate((current) => ({ ...current, territory_id: event.target.value, road_id: nextRoad?.id ?? '', building_id: nextBuilding?.id ?? '' })); }}>{territories.map((territory) => <option key={territory.id} value={territory.id}>{territory.name}</option>)}</select></label><label><span>Road</span><select value={addressCreate.road_id} onChange={(event) => { const nextBuilding = buildings.find((building) => building.road_id === event.target.value && !building.is_archived); setAddressCreate((current) => ({ ...current, road_id: event.target.value, building_id: nextBuilding?.id ?? '' })); }}>{roadsForAddress.map((road) => <option key={road.id} value={road.id}>{road.name}</option>)}</select></label><label><span>Building</span><select value={addressCreate.building_id} onChange={(event) => setAddressCreate((current) => ({ ...current, building_id: event.target.value }))}>{buildingsForAddress.map((building) => <option key={building.id} value={building.id}>{building.label}</option>)}</select></label></> : null}
              {activeTab === 'roads' ? <><label><span>Road name</span><input required value={roadCreate.name} onChange={(event) => setRoadCreate((current) => ({ ...current, name: event.target.value }))} /></label><label><span>Territory</span><select value={roadCreate.territory_id} onChange={(event) => setRoadCreate((current) => ({ ...current, territory_id: event.target.value }))}>{territories.map((territory) => <option key={territory.id} value={territory.id}>{territory.name}</option>)}</select></label><label><span>Length (km)</span><input required value={roadCreate.length_km} onChange={(event) => setRoadCreate((current) => ({ ...current, length_km: event.target.value }))} /></label></> : null}
              {activeTab === 'buildings' ? <><label><span>Building label</span><input required value={buildingCreate.label} onChange={(event) => setBuildingCreate((current) => ({ ...current, label: event.target.value }))} /></label><label><span>Territory</span><select value={buildingCreate.territory_id} onChange={(event) => { const nextRoad = roads.find((road) => road.territory_id === event.target.value && !road.is_archived); setBuildingCreate((current) => ({ ...current, territory_id: event.target.value, road_id: nextRoad?.id ?? '' })); }}>{territories.map((territory) => <option key={territory.id} value={territory.id}>{territory.name}</option>)}</select></label><label><span>Road</span><select value={buildingCreate.road_id} onChange={(event) => setBuildingCreate((current) => ({ ...current, road_id: event.target.value }))}>{roadsForBuilding.map((road) => <option key={road.id} value={road.id}>{road.name}</option>)}</select></label><label><span>Use</span><input required value={buildingCreate.usage} onChange={(event) => setBuildingCreate((current) => ({ ...current, usage: event.target.value }))} /></label></> : null}
              <button type="submit" disabled={!canWrite || isWorking}>{!canWrite ? 'Editor or admin required' : isWorking ? 'Working…' : `Create ${activeTab === 'addresses' ? 'address' : activeTab === 'roads' ? 'road' : 'building'}`}</button>
            </form></section>
            <section className="government-authority-note"><GovernmentIcon name="alert" /><div><strong>Publication authority remains separate</strong><span>Creating or updating a registry record does not publish it. Official release remains controlled by the Publication workspace.</span></div></section>
          </div>
        </aside>
      </div>
    </section>
  );
}
