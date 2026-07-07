'use client';

import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import type { Map as LeafletMap, LeafletMouseEvent, CircleMarker, Circle } from 'leaflet';

import { resolveBrowserApiBaseUrl } from './sessionClient';

import { useTranslation } from './i18n';

type Province = {
  code: string;
  name: string;
};

type Territory = { id: string; name: string; province?: string; province_code?: string; readiness?: string };

type DuplicateHint = { source: string; id: string; label: string; code: string | null; distance_meters: number };

type AddressCodeDetail = {
  code: string;
  country: string;
  province_code: string;
  schema: string;
  latitude: number;
  longitude: number;
  cell_size_meters: number;
  checksum: string;
  is_valid: boolean;
};

type Preview = {
  grid_code: string;
  address_code?: AddressCodeDetail;
  territory_id: string | null;
  territory_name?: string | null;
  latitude: number;
  longitude: number;
  duplicate_hints: DuplicateHint[];
  signage_label: string;
};

type RoadSuggestion = {
  suggested_road_name: string | null;
  suggested_local_area?: string | null;
  suggested_place_name?: string | null;
  display_name?: string | null;
  source: string;
  source_attribution: string;
  distance_meters: number | null;
  confidence: 'none' | 'low' | 'medium' | 'high' | string;
  requires_review: boolean;
  status: 'suggested' | 'unavailable' | string;
};

type SubmissionResult = Preview & {
  id: string;
  status: string;
  address_label: string;
  duplicate_hint: string;
  automation?: {
    process_stage: string;
    next_best_action_label: string;
    quality_score: number;
    citizen_tracking?: {
      tracking_code: string;
      public_next_step: string;
      public_lookup_url: string;
    };
    routing?: {
      assigned: boolean;
      territory_id?: string | null;
      territory_name?: string | null;
      assignment_source?: string | null;
      assignment_confidence?: string | null;
    };
    reasons?: string[];
  };
};

type CitizenGeotagPanelProps = {
  apiBaseUrl: string;
  provinces: Province[];
  territories: Territory[];
};

const DEFAULT_POINT = { latitude: 3.7523, longitude: 8.7741 };

function preferredProvinceCode(provinces: Province[]): string {
  return provinces.find((province) => province.code === 'BN')?.code ?? provinces[0]?.code ?? 'BN';
}

function preferredTerritoryId(territories: Territory[]): string {
  return '';
}

function territoryForPoint(territories: Territory[], latitude: number, longitude: number): string | null {
  return null;
}

function isLocalhostHost(hostname: string): boolean {
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '[::1]';
}

function statusLabel(status: string): string {
  return status.replaceAll('-', ' ');
}

function normalizeAreaName(value: string): string {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function territoryForMapArea(territories: Territory[], provinceCode: string, areaName?: string | null): string | null {
  if (!areaName) return null;
  const normalizedArea = normalizeAreaName(areaName);
  if (!normalizedArea) return null;
  const exact = territories.find((territory) => territory.province_code === provinceCode && normalizeAreaName(territory.name) === normalizedArea);
  if (exact) return exact.id;
  const contains = territories.find((territory) => {
    if (territory.province_code !== provinceCode) return false;
    const territoryName = normalizeAreaName(territory.name);
    return territoryName.includes(normalizedArea) || normalizedArea.includes(territoryName);
  });
  return contains?.id ?? null;
}

export function CitizenGeotagPanel({ apiBaseUrl, provinces, territories }: CitizenGeotagPanelProps) {
  const { t } = useTranslation();
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const markerRef = useRef<CircleMarker | null>(null);
  const accuracyCircleRef = useRef<Circle | null>(null);
  const [latitude, setLatitude] = useState(DEFAULT_POINT.latitude);
  const [longitude, setLongitude] = useState(DEFAULT_POINT.longitude);
  const [accuracyMeters, setAccuracyMeters] = useState<number | ''>('');
  const [provinceCode, setProvinceCode] = useState(preferredProvinceCode(provinces));
  const [territoryId, setTerritoryId] = useState(preferredTerritoryId(territories));
  const [addressLabel, setAddressLabel] = useState('');
  const [landmark, setLandmark] = useState('');
  const [citizenName, setCitizenName] = useState('');
  const [citizenContact, setCitizenContact] = useState('');
  const [dipLast4, setDipLast4] = useState('');
  const [captureMethod, setCaptureMethod] = useState('manual-map-pin');
  const [preview, setPreview] = useState<Preview | null>(null);
  const [roadSuggestion, setRoadSuggestion] = useState<RoadSuggestion | null>(null);
  const [result, setResult] = useState<SubmissionResult | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLocating, setIsLocating] = useState(false);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const filteredTerritories = useMemo(
    () => territories.filter((territory) => !provinceCode || territory.province_code === provinceCode),
    [territories, provinceCode],
  );
  const selectedTerritory = useMemo(() => territories.find((territory) => territory.id === territoryId), [territories, territoryId]);
  const mapSuggestedLocalArea = roadSuggestion?.suggested_local_area || roadSuggestion?.suggested_place_name || null;
  const displayedLocalArea = mapSuggestedLocalArea ?? selectedTerritory?.name ?? 'Area pending';

  useEffect(() => {
    const selected = territories.find((territory) => territory.id === territoryId);
    if (selected?.province_code && selected.province_code !== provinceCode) {
      setProvinceCode(selected.province_code);
    }
  }, [provinceCode, territories, territoryId]);

  useEffect(() => {
    let cancelled = false;
    async function setupMap() {
      if (!mapContainerRef.current || mapRef.current) return;
      const L = await import('leaflet');
      if (cancelled || !mapContainerRef.current) return;
      const map = L.map(mapContainerRef.current, { zoomControl: true, attributionControl: true }).setView([latitude, longitude], 15);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors',
      }).addTo(map);
      const marker = L.circleMarker([latitude, longitude], {
        radius: 8,
        color: '#123a5a',
        fillColor: '#f4b300',
        fillOpacity: 0.95,
        weight: 3,
      }).addTo(map);
      const accuracyCircle = L.circle([latitude, longitude], {
        radius: 1,
        color: '#123a5a',
        fillColor: '#2f80ed',
        fillOpacity: 0,
        opacity: 0,
        weight: 1,
        interactive: false,
      }).addTo(map);
      accuracyCircleRef.current = accuracyCircle;
      markerRef.current = marker;
      map.on('click', (event: LeafletMouseEvent) => {
        setLatitude(Number(event.latlng.lat.toFixed(7)));
        setLongitude(Number(event.latlng.lng.toFixed(7)));
        setAccuracyMeters('');
        setCaptureMethod('manual-map-pin');
        setRoadSuggestion(null);
        setPreview(null);
      });
      mapRef.current = map;
      setTimeout(() => map.invalidateSize(), 150);
    }
    void setupMap();
    return () => {
      cancelled = true;
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
        markerRef.current = null;
        accuracyCircleRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (markerRef.current) {
      markerRef.current.setLatLng([latitude, longitude]);
    }
    if (accuracyCircleRef.current) {
      accuracyCircleRef.current.setLatLng([latitude, longitude]);
      if (accuracyMeters !== '' && Number(accuracyMeters) > 0) {
        accuracyCircleRef.current.setRadius(Number(accuracyMeters));
        accuracyCircleRef.current.setStyle({ opacity: 0.55, fillOpacity: 0.12 });
      } else {
        accuracyCircleRef.current.setRadius(1);
        accuracyCircleRef.current.setStyle({ opacity: 0, fillOpacity: 0 });
      }
    }
    if (mapRef.current) {
      mapRef.current.setView([latitude, longitude], mapRef.current.getZoom() || 15);
    }
  }, [latitude, longitude, accuracyMeters]);

  async function handleUseMyLocation() {
    setNotice(null);
    setError(null);
    if (!navigator.geolocation) {
      setError('This browser does not support GPS location capture. You can still click the map or enter coordinates manually.');
      return;
    }
    if (typeof window !== 'undefined' && !window.isSecureContext && !isLocalhostHost(window.location.hostname)) {
      setError('Your browser is blocking GPS because this test link is using HTTP. Use the map pin/manual coordinates for now, or test again once we expose this page over HTTPS.');
      return;
    }
    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const capturedLatitude = Number(position.coords.latitude.toFixed(7));
        const capturedLongitude = Number(position.coords.longitude.toFixed(7));
        setLatitude(capturedLatitude);
        setLongitude(capturedLongitude);
        const matchedTerritory = territoryForPoint(territories, capturedLatitude, capturedLongitude);
        if (matchedTerritory) setTerritoryId(matchedTerritory);
        setAccuracyMeters(Math.round(position.coords.accuracy));
        setCaptureMethod('browser-gps');
        setRoadSuggestion(null);
        setPreview(null);
        setNotice('GPS location captured. Move the map pin if the position needs correction.');
        setIsLocating(false);
      },
      () => {
        setError('Unable to capture GPS location. You can still click the map or enter coordinates manually.');
        setIsLocating(false);
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
    );
  }

  async function handlePreview() {
    setIsPreviewing(true);
    setNotice(null);
    setError(null);
    try {
      const previewResponse = await fetch(`${browserApiBaseUrl}/api/v1/public/geotag/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude, longitude, territory_id: territoryId || null, province_code: provinceCode || null }),
      });
      const payload = (await previewResponse.json()) as Preview | { detail?: string };
      if (!previewResponse.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to preview this point.');
        return;
      }
      setPreview(payload as Preview);
      try {
        const roadSuggestionResponse = await fetch(`${browserApiBaseUrl}/api/v1/public/geotag/road-suggestion`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ latitude, longitude }),
        });
        if (roadSuggestionResponse.ok) {
          const roadPayload = (await roadSuggestionResponse.json()) as RoadSuggestion;
          setRoadSuggestion(roadPayload);
        } else {
          setRoadSuggestion(null);
        }
      } catch {
        setRoadSuggestion(null);
      }
      setNotice('National address code generated. Review duplicates and any suggested road name before submitting.');
    } catch {
      setError('Unable to preview this point right now.');
    } finally {
      setIsPreviewing(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setNotice(null);
    setError(null);
    const normalizedDipLast4 = dipLast4.trim();
    if (normalizedDipLast4 && !/^\d{4}$/.test(normalizedDipLast4)) {
      setError('D.I.P. last 4 must be exactly 4 digits. Leave it blank if you do not want to provide it now.');
      setIsSubmitting(false);
      return;
    }
    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/public/geotag-submissions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          territory_id: territoryId || null,
          province_code: provinceCode || null,
          address_label: addressLabel,
          citizen_name: citizenName || null,
          citizen_contact: citizenContact || null,
          dip_last4: normalizedDipLast4 || null,
          landmark,
          latitude,
          longitude,
          accuracy_meters: accuracyMeters === '' ? null : Number(accuracyMeters),
          capture_method: captureMethod,
          suggested_road_name: roadSuggestion?.suggested_road_name ?? null,
          suggested_local_area: roadSuggestion?.suggested_local_area ?? null,
          suggested_place_name: roadSuggestion?.suggested_place_name ?? null,
          map_display_name: roadSuggestion?.display_name ?? null,
          road_suggestion_source: roadSuggestion?.source ?? null,
          road_suggestion_attribution: roadSuggestion?.source_attribution ?? null,
        }),
      });
      const payload = (await response.json()) as SubmissionResult | { detail?: string };
      if (!response.ok) {
        setError('detail' in payload && payload.detail ? payload.detail : 'Unable to submit the geotag record.');
        return;
      }
      setResult(payload as SubmissionResult);
      setPreview(payload as SubmissionResult);
      setNotice('Citizen geotag submitted for Government review and field verification.');
    } catch {
      setError('Unable to submit the geotag record right now.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="citizen-register-flow">
      <article className="public-task-panel location-hero-panel">
        <div className="location-hero-content">
          <div className="panel-head">
            <p className="section-label">{t('step1')}</p>
            <h3>{t('useCurrentLocation')}</h3>
          </div>
          <p className="public-task-copy">
            {t('geotagStep1Copy')}
          </p>
          <div className="citizen-primary-actions">
            <button className="primary-action location-action" type="button" onClick={() => void handleUseMyLocation()} disabled={isLocating}>
              {isLocating ? 'Getting your location…' : t('useMyCurrentLocation')}
            </button>
            <button className="secondary-action" type="button" onClick={() => void handlePreview()} disabled={isPreviewing}>
              {isPreviewing ? 'Checking point…' : t('checkAddressCode')}
            </button>
          </div>
        </div>
        <div className="location-radar" aria-hidden="true">
          <span className="radar-ring radar-ring-1" />
          <span className="radar-ring radar-ring-2" />
          <span className="radar-ring radar-ring-3" />
          <span className="radar-dot" />
        </div>
        <div className="location-status-grid" aria-label="Captured location summary">
          <span className="location-metric latitude-metric"><strong>Latitude</strong>{latitude.toFixed(7)}</span>
          <span className="location-metric longitude-metric"><strong>Longitude</strong>{longitude.toFixed(7)}</span>
          <span className="location-metric accuracy-metric"><strong>Accuracy</strong>{accuracyMeters === '' ? 'Not captured' : `${accuracyMeters}m`}</span>
        </div>
        {notice ? <p className="form-notice success">{notice}</p> : null}
        {!notice && preview ? (
          <p className="form-notice success">National address code generated. Review duplicates and any suggested road name before submitting.</p>
        ) : null}
        {error ? <p className="form-notice error">{error}</p> : null}
      </article>

      <article className="map-confirm-panel">
        <div className="panel-head quiet-head">
          <p className="section-label">{t('step2')}</p>
          <h3>{t('confirmPin')}</h3>
        </div>
        <div className="geotag-map" ref={mapContainerRef} aria-label="Interactive map for location registration" />
        <p className="institutional-note">{t('pinCopy')}</p>
      </article>

      <article className="public-task-panel location-form-panel compact-location-form-panel">
        <div className="panel-head compact-form-head">
          <div>
            <p className="section-label">{t('step3')}</p>
            <h3>{t('addPlaceDetails')}</h3>
          </div>
          <span className="form-focus-badge">2 essentials + contact</span>
        </div>
        <p className="public-task-copy compact-form-intro">Give the review team the local name and one landmark. Technical location data stays available below, but it does not crowd the main form.</p>
        <form id="citizen-location-form" className="territory-form citizen-form compact-location-form" onSubmit={handleSubmit}>
          <div className="essential-form-block">
            <label className="territory-field important-field">
              <span className="territory-label">{t('placeLabel')}</span>
              <input className="territory-input" value={addressLabel} onChange={(event) => setAddressLabel(event.target.value)} required placeholder="Example: House near Malabo civic area" />
            </label>
            <label className="territory-field important-field">
              <span className="territory-label">{t('landmarkLabel')}</span>
              <input className="territory-input" value={landmark} onChange={(event) => setLandmark(event.target.value)} placeholder="Nearest road, gate color, public landmark" />
            </label>
            <label className="territory-field important-field">
              <span className="territory-label">{t('contactLabel')}</span>
              <input className="territory-input" value={citizenContact} onChange={(event) => setCitizenContact(event.target.value)} placeholder="Optional phone or email for follow-up" />
            </label>
          </div>

          <div className="location-suggestion-strip" aria-label="Location capture summary">
            <span><strong>Point</strong>{latitude.toFixed(5)}, {longitude.toFixed(5)}</span>
            <span><strong>Accuracy</strong>{accuracyMeters === '' ? 'Not captured' : `${accuracyMeters}m`}</span>
            <span><strong>Area</strong>{displayedLocalArea}</span>
          </div>

          <details className="quiet-disclosure compact-secondary-disclosure">
            <summary>Optional identity details</summary>
            <div className="citizen-form-grid">
              <label className="territory-field">
                <span className="territory-label">Name</span>
                <input className="territory-input" value={citizenName} onChange={(event) => setCitizenName(event.target.value)} placeholder="Optional" />
              </label>
              <label className="territory-field">
                <span className="territory-label">{t('dipLast4Label')}</span>
                <input className="territory-input" inputMode="numeric" pattern="[0-9]{4}" maxLength={4} value={dipLast4} onChange={(event) => setDipLast4(event.target.value.replace(/\D/g, '').slice(0, 4))} placeholder="Optional" />
                <span className="field-help">{t('dipLast4Help')}</span>
              </label>
            </div>
          </details>

          <details className="quiet-disclosure compact-secondary-disclosure">
            <summary>Confirm official routing area</summary>
            <div className="citizen-form-grid routing-confirmation-grid">
              <div className="territory-field locked-location-field" aria-label="Captured GPS coordinates">
                <span className="territory-label">GPS point</span>
                <strong>{latitude.toFixed(7)}, {longitude.toFixed(7)}</strong>
                <span className="field-help">Captured from the device GPS or map pin; not typed manually.</span>
              </div>
              <div className="territory-field locked-location-field" aria-label="Captured GPS accuracy">
                <span className="territory-label">GPS accuracy</span>
                <strong>{accuracyMeters === '' ? 'Not captured' : `${accuracyMeters}m`}</strong>
                <span className="field-help">Accuracy is recorded as evidence and cannot be edited here.</span>
              </div>
              <div className="territory-field locked-location-field" aria-label="Province">
                <span className="territory-label">Province</span>
                <strong>{provinces.find((province) => province.code === provinceCode)?.name ?? provinceCode}</strong>
                <span className="field-help">Province controls the national code prefix. Map-derived local names stay as suggestions below.</span>
              </div>
              <label className="territory-field routing-area-field">
                <span className="territory-label">Official routing area</span>
                <select className="territory-input" value={territoryId} onChange={(event) => setTerritoryId(event.target.value)}>
                  <option value="">No local area selected yet</option>
                  {filteredTerritories.map((territory) => (
                    <option key={territory.id} value={territory.id}>{territory.name}</option>
                  ))}
                </select>
                <span className="field-help">Optional internal review/dispatch area. Exact map-local-area matches are assigned automatically; broad or uncertain labels stay pending.</span>
              </label>
            </div>
            <span className="field-help">Coordinates and GPS accuracy stay locked. Exact official routing-area matches may be assigned automatically; unmatched map labels remain review-required suggestions.</span>
          </details>

          <div className="compact-form-actions">
            <button className="secondary-action" type="button" onClick={() => void handlePreview()} disabled={isPreviewing}>
              {isPreviewing ? 'Checking point…' : t('checkAddressCode')}
            </button>
            <button className="primary-action" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Submitting…' : t('submitLocation')}
            </button>
          </div>
        </form>
      </article>

      <article className="public-task-panel address-preview-panel">
        <div className="panel-head">
          <p className="section-label">{t('step4')}</p>
          <h3>{t('addressCodePreview')}</h3>
        </div>
        {preview ? (
          <div className="address-code-summary">
            <p>Provisional address code</p>
            <strong>{preview.grid_code}</strong>
            <span>{selectedTerritory?.name ?? preview.territory_name ?? 'Area pending classification'}</span>
            {preview.address_code ? (
              <span>{preview.address_code.cell_size_meters}m location cell · checksum {preview.address_code.checksum}</span>
            ) : null}
          </div>
        ) : (
          <p className="panel-state">{t('previewPrompt')}</p>
        )}
        {roadSuggestion ? (
          <div className="operator-finding-card">
            <strong>Map suggestions</strong>
            {roadSuggestion.suggested_local_area || roadSuggestion.suggested_place_name ? (
              <p>Local area: {roadSuggestion.suggested_local_area || roadSuggestion.suggested_place_name}</p>
            ) : (
              <p>Local area not found from the map source.</p>
            )}
            {roadSuggestion.suggested_road_name ? (
              <p>Road: {roadSuggestion.suggested_road_name}</p>
            ) : (
              <p>Road name not found near this point.</p>
            )}
            <span className="status-chip warn">Map-derived suggestion · review required</span>
            <p className="institutional-note">Source: {roadSuggestion.source_attribution}. These names are not official until reviewed.</p>
          </div>
        ) : null}
        {preview?.duplicate_hints?.length ? (
          <details className="quiet-disclosure">
            <summary>Possible nearby match</summary>
            <ul className="mini-list">
              {preview.duplicate_hints.map((hint) => (
                <li key={`${hint.source}-${hint.id}`}>
                  <strong>{hint.label}</strong>
                  <span>{hint.distance_meters}m away · {hint.code ?? 'code pending'}</span>
                </li>
              ))}
            </ul>
          </details>
        ) : (
          <p className="institutional-note">No nearby match was found for this point.</p>
        )}
        {result ? (
          <div className="form-notice success">
            Submitted for official review. Status: <strong>{result.automation?.process_stage ?? statusLabel(result.status)}</strong>. Keep this provisional code: <strong>{result.grid_code}</strong>.
            {result.automation?.citizen_tracking?.tracking_code ? <> Tracking code: <strong>{result.automation.citizen_tracking.tracking_code}</strong>.</> : null}
            <br />
            Next step: {result.automation?.next_best_action_label ?? 'An operator will check the point, duplicates, and road-name suggestion before it becomes public.'}
            {result.automation?.routing?.assigned ? (
              <><br />Routing area assigned automatically: <strong>{result.automation.routing.territory_name}</strong>.</>
            ) : null}
            {result.automation?.reasons?.length ? (
              <ul>
                {result.automation.reasons.slice(0, 3).map((reason) => <li key={reason}>{reason}</li>)}
              </ul>
            ) : null}
          </div>
        ) : null}
        <p className="submission-security-note">All submissions are encrypted and reviewed by authorized operators.</p>
      </article>
    </section>
  );
}
