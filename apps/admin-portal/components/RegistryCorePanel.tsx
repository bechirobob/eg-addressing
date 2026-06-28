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
  const [territories] = useState(initialTerritories.filter((item) => !item.is_archived));
  const [roads, setRoads] = useState(initialRoads);
  const [buildings, setBuildings] = useState(initialBuildings);
  const [addresses, setAddresses] = useState(initialAddresses);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [registryFocus, setRegistryFocus] = useState<RegistryFocus>(null);

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
  const [selectedRoadId, setSelectedRoadId] = useState(initialRoads[0]?.id ?? '');
  const [selectedBuildingId, setSelectedBuildingId] = useState(initialBuildings[0]?.id ?? '');
  const [selectedAddressId, setSelectedAddressId] = useState(initialAddresses[0]?.id ?? '');

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

  useEffect(() => {
    if (!highlightEntityId) return;

    const highlightedRoad = roads.find((item) => item.id === highlightEntityId);
    if (highlightedRoad) {
      setSelectedRoadId(highlightedRoad.id);
      setRegistryFocus({ entityType: 'road', id: highlightedRoad.id, label: highlightedRoad.name });
      return;
    }

    const highlightedBuilding = buildings.find((item) => item.id === highlightEntityId);
    if (highlightedBuilding) {
      setSelectedBuildingId(highlightedBuilding.id);
      setRegistryFocus({ entityType: 'building', id: highlightedBuilding.id, label: highlightedBuilding.label });
      return;
    }

    const highlightedAddress = addresses.find((item) => item.id === highlightEntityId);
    if (highlightedAddress) {
      setSelectedAddressId(highlightedAddress.id);
      setRegistryFocus({ entityType: 'address', id: highlightedAddress.id, label: highlightedAddress.formatted });
    }
  }, [addresses, buildings, highlightEntityId, roads]);

  async function reloadAll() {
    setIsRefreshing(true);
    try {
      const [roadsResponse, buildingsResponse, addressesResponse] = await Promise.all([
        fetch(`${browserApiBaseUrl}/api/v1/roads?include_archived=true`),
        fetch(`${browserApiBaseUrl}/api/v1/buildings?include_archived=true`),
        fetch(`${browserApiBaseUrl}/api/v1/addresses?include_archived=true`),
      ]);
      if (!roadsResponse.ok || !buildingsResponse.ok || !addressesResponse.ok) {
        setError('Unable to refresh the registry lists.');
        return;
      }
      const roadsPayload = (await roadsResponse.json()) as { items: Road[] };
      const buildingsPayload = (await buildingsResponse.json()) as { items: Building[] };
      const addressesPayload = (await addressesResponse.json()) as { items: Address[] };
      setRoads(roadsPayload.items ?? []);
      setBuildings(buildingsPayload.items ?? []);
      setAddresses(addressesPayload.items ?? []);
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

  return (
    <section className="section-grid territory-admin-grid">
      <article className="panel panel-accent-blue">
        <div className="panel-head">
          <p className="section-label">Road register</p>
          <h3>Create, update, and archive roads</h3>
        </div>
        <p className="institutional-note">
          Signed-in role: <strong>{sessionUser?.role ?? 'guest'}</strong>. Registry creation and archive controls are protected.
        </p>
        {sessionStatus === 'loading' ? <p className="panel-state">Checking access before enabling registry actions…</p> : null}
        {isRefreshing ? <p className="panel-state">Refreshing registry lists…</p> : null}
        {registryFocus ? (
          <div className="selection-summary">
            <strong>Registry focus: {registryFocus.label}</strong>
            <span className="territory-meta">
              {registryFocus.entityType} · {registryFocus.id}
            </span>
          </div>
        ) : null}
        <form
          className="territory-form"
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
          <label className="territory-field">
            <span className="territory-label">Road name</span>
            <input className="territory-input" value={roadForm.name} onChange={(event) => setRoadForm({ ...roadForm, name: event.target.value })} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Territory</span>
            <select className="territory-input" value={roadForm.territory_id} onChange={(event) => setRoadForm({ ...roadForm, territory_id: event.target.value })}>
              {territories.map((territory) => (
                <option key={territory.id} value={territory.id}>
                  {territory.name}
                </option>
              ))}
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Status</span>
            <input className="territory-input" value={roadForm.status} onChange={(event) => setRoadForm({ ...roadForm, status: event.target.value })} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Length (km)</span>
            <input className="territory-input" value={roadForm.length_km} onChange={(event) => setRoadForm({ ...roadForm, length_km: event.target.value })} required />
          </label>
          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Working…' : 'Create road'}
            </button>
          </div>
        </form>
        <label className="territory-field">
          <span className="territory-label">Selected road</span>
          <select className="territory-input" value={selectedRoadId} onChange={(event) => setSelectedRoadId(event.target.value)}>
            {roads.map((road) => (
              <option key={road.id} value={road.id}>
                {road.name} · {road.is_archived ? 'archived' : road.status}
              </option>
            ))}
          </select>
        </label>
        {selectedRoad ? (
          <div className="button-row">
            <button
              className="mini-action-button"
              type="button"
              disabled={isSubmitting}
              onClick={() =>
                void mutate(`/api/v1/roads/${selectedRoad.id}`, 'PATCH', {
                  name: `${selectedRoad.name} Updated`,
                  territory_id: selectedRoad.territory_id,
                  status: selectedRoad.status,
                  length_km: selectedRoad.length_km,
                }).then((result) => {
                  if (result) {
                    setNotice(`Road updated: ${selectedRoad.name}`);
                    setRegistryFocus({ entityType: 'road', id: selectedRoad.id, label: selectedRoad.name });
                  }
                })
              }
            >
              Quick update
            </button>
            <button
              className="mini-action-button danger"
              type="button"
              disabled={isSubmitting}
              onClick={() =>
                void mutate(`/api/v1/roads/${selectedRoad.id}`, 'DELETE').then((result) => {
                  if (result) {
                    setNotice(`Road archived: ${selectedRoad.name}`);
                  }
                })
              }
            >
              Archive
            </button>
          </div>
        ) : null}
        <ul className="mini-list">
          {roads.map((road) => (
            <li key={road.id}>
              <strong>{road.name}</strong>
              <span>
                {road.territory_name} · {road.status} · {road.is_archived ? 'archived' : 'active'}
              </span>
            </li>
          ))}
        </ul>
      </article>

      <article className="panel panel-accent-gold">
        <div className="panel-head">
          <p className="section-label">Building register</p>
          <h3>Create, update, and archive buildings</h3>
        </div>
        <form
          className="territory-form"
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
          <label className="territory-field">
            <span className="territory-label">Building label</span>
            <input className="territory-input" value={buildingForm.label} onChange={(event) => setBuildingForm({ ...buildingForm, label: event.target.value })} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Territory</span>
            <select
              className="territory-input"
              value={buildingForm.territory_id}
              onChange={(event) =>
                setBuildingForm({
                  ...buildingForm,
                  territory_id: event.target.value,
                  road_id: roads.filter((road) => road.territory_id === event.target.value && !road.is_archived)[0]?.id ?? '',
                })
              }
            >
              {territories.map((territory) => (
                <option key={territory.id} value={territory.id}>
                  {territory.name}
                </option>
              ))}
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Road</span>
            <select className="territory-input" value={buildingForm.road_id} onChange={(event) => setBuildingForm({ ...buildingForm, road_id: event.target.value })}>
              {roadsForBuildingTerritory.map((road) => (
                <option key={road.id} value={road.id}>
                  {road.name}
                </option>
              ))}
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Status</span>
            <input className="territory-input" value={buildingForm.status} onChange={(event) => setBuildingForm({ ...buildingForm, status: event.target.value })} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Usage</span>
            <input className="territory-input" value={buildingForm.usage} onChange={(event) => setBuildingForm({ ...buildingForm, usage: event.target.value })} required />
          </label>
          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Working…' : 'Create building'}
            </button>
          </div>
        </form>
        <label className="territory-field">
          <span className="territory-label">Selected building</span>
          <select className="territory-input" value={selectedBuildingId} onChange={(event) => setSelectedBuildingId(event.target.value)}>
            {buildings.map((building) => (
              <option key={building.id} value={building.id}>
                {building.label} · {building.is_archived ? 'archived' : building.status}
              </option>
            ))}
          </select>
        </label>
        {selectedBuilding ? (
          <div className="button-row">
            <button
              className="mini-action-button"
              type="button"
              disabled={isSubmitting}
              onClick={() =>
                void mutate(`/api/v1/buildings/${selectedBuilding.id}`, 'PATCH', {
                  label: `${selectedBuilding.label} Updated`,
                  territory_id: selectedBuilding.territory_id,
                  road_id: selectedBuilding.road_id,
                  status: selectedBuilding.status,
                  usage: selectedBuilding.usage,
                }).then((result) => {
                  if (result) {
                    setNotice(`Building updated: ${selectedBuilding.label}`);
                    setRegistryFocus({ entityType: 'building', id: selectedBuilding.id, label: selectedBuilding.label });
                  }
                })
              }
            >
              Quick update
            </button>
            <button
              className="mini-action-button danger"
              type="button"
              disabled={isSubmitting}
              onClick={() =>
                void mutate(`/api/v1/buildings/${selectedBuilding.id}`, 'DELETE').then((result) => {
                  if (result) {
                    setNotice(`Building archived: ${selectedBuilding.label}`);
                  }
                })
              }
            >
              Archive
            </button>
          </div>
        ) : null}
        <ul className="mini-list">
          {buildings.map((building) => (
            <li key={building.id}>
              <strong>{building.label}</strong>
              <span>
                {building.road_name} · {building.usage} · {building.is_archived ? 'archived' : 'active'}
              </span>
            </li>
          ))}
        </ul>
      </article>

      <article className="panel panel-accent-green territory-list-panel">
        <div className="panel-head">
          <p className="section-label">Address register</p>
          <h3>Create, update, and archive addresses</h3>
        </div>
        <form
          className="territory-form"
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
            <span className="territory-label">Formatted address</span>
            <input className="territory-input" value={addressForm.formatted} onChange={(event) => setAddressForm({ ...addressForm, formatted: event.target.value })} required />
          </label>
          <label className="territory-field">
            <span className="territory-label">Territory</span>
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
              {territories.map((territory) => (
                <option key={territory.id} value={territory.id}>
                  {territory.name}
                </option>
              ))}
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
              {roadsForAddressTerritory.map((road) => (
                <option key={road.id} value={road.id}>
                  {road.name}
                </option>
              ))}
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Building</span>
            <select className="territory-input" value={addressForm.building_id} onChange={(event) => setAddressForm({ ...addressForm, building_id: event.target.value })}>
              {buildingsForAddressChain.map((building) => (
                <option key={building.id} value={building.id}>
                  {building.label}
                </option>
              ))}
            </select>
          </label>
          <label className="territory-field">
            <span className="territory-label">Status</span>
            <input className="territory-input" value={addressForm.status} onChange={(event) => setAddressForm({ ...addressForm, status: event.target.value })} required />
          </label>
          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Working…' : 'Create address'}
            </button>
          </div>
        </form>
        <label className="territory-field">
          <span className="territory-label">Selected address</span>
          <select className="territory-input" value={selectedAddressId} onChange={(event) => setSelectedAddressId(event.target.value)}>
            {addresses.map((address) => (
              <option key={address.id} value={address.id}>
                {address.formatted} · {address.is_archived ? 'archived' : address.status}
              </option>
            ))}
          </select>
        </label>
        {selectedAddress ? (
          <div className="button-row">
            <button
              className="mini-action-button"
              type="button"
              disabled={isSubmitting}
              onClick={() =>
                void mutate(`/api/v1/addresses/${selectedAddress.id}`, 'PATCH', {
                  formatted: `${selectedAddress.formatted} Updated`,
                  territory_id: selectedAddress.territory_id,
                  road_id: selectedAddress.road_id,
                  building_id: selectedAddress.building_id,
                  status: selectedAddress.status,
                }).then((result) => {
                  if (result) {
                    setNotice(`Address updated: ${selectedAddress.formatted}`);
                    setRegistryFocus({ entityType: 'address', id: selectedAddress.id, label: selectedAddress.formatted });
                  }
                })
              }
            >
              Quick update
            </button>
            <button
              className="mini-action-button danger"
              type="button"
              disabled={isSubmitting}
              onClick={() =>
                void mutate(`/api/v1/addresses/${selectedAddress.id}`, 'DELETE').then((result) => {
                  if (result) {
                    setNotice(`Address archived: ${selectedAddress.formatted}`);
                  }
                })
              }
            >
              Archive
            </button>
          </div>
        ) : null}
        {notice ? <p className="form-notice success">{notice}</p> : null}
        {error ? <p className="form-notice error">{error}</p> : null}
        <ul className="mini-list">
          {addresses.map((address) => (
            <li key={address.id}>
              <strong>{address.formatted}</strong>
              <span>
                {address.territory_name} · {address.publication_state} · {address.is_archived ? 'archived' : 'active'}
              </span>
            </li>
          ))}
        </ul>
      </article>
    </section>
  );
}
