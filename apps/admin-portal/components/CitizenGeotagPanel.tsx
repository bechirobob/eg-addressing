'use client';

import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import type { Map as LeafletMap, LeafletMouseEvent, CircleMarker, Circle } from 'leaflet';

import { resolveBrowserApiBaseUrl } from './sessionClient';

import { useTranslation } from './i18n';

type Province = {
  code: string;
  name: string;
};

type Territory = {
  id: string;
  name: string;
  province?: string;
  province_code?: string;
  type?: string;
  readiness?: string;
  admin_unit_name?: string | null;
  admin_unit_level?: string | null;
  routing_status_label?: string;
  source_label?: string;
  confidence_label?: string;
  geometry_status?: string;
  public_status?: string;
};

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

function territoryForPunto(territories: Territory[], latitude: number, longitude: number): string | null {
  return null;
}

function isLocalhostHost(hostname: string): boolean {
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '[::1]';
}

function statusLabel(status: string): string {
  return status.replaceAll('-', ' ');
}

function readinessLabel(value?: string): string {
  if (value === 'official-routing') return 'Ruta administrativa oficial';
  if (value === 'intake-routing') return 'Área local para ingreso';
  if (value === 'active-mapping') return 'Cartografía activa';
  if (value === 'verification-prep') return 'Pendiente de verificación de campo';
  if (value === 'survey-queue') return 'En cola de levantamiento';
  return value ? statusLabel(value) : 'Pendiente de clasificación';
}

function territoryTypeLabel(value?: string): string {
  if (value === 'official-municipality') return 'Municipio / ruta administrativa';
  if (value === 'map-referenced-local-area') return 'Área local referenciada';
  if (value === 'capital-urban-core') return 'Núcleo urbano capital';
  if (value === 'urban-core') return 'Núcleo urbano';
  return value ? statusLabel(value) : 'Área de enrutamiento';
}

function territoryStatusClass(territory?: Territory | null): string {
  if (!territory) return 'warn';
  if (territory.readiness === 'official-routing') return 'ok';
  if (territory.readiness === 'verification-prep' || territory.readiness === 'survey-queue') return 'warn';
  return '';
}

function sourceLabel(territory?: Territory | null): string {
  return territory?.source_label ?? 'Registro interno de enrutamiento; confirmar antes de publicación';
}

function confidenceLabel(territory?: Territory | null): string {
  return territory?.confidence_label ?? 'Registro interno; confirmar antes de publicación';
}

function geometryLabel(territory?: Territory | null): string {
  return territory?.geometry_status ?? 'Registro de enrutamiento; geometría oficial levantada no adjunta';
}

function publicStatusLabel(territory?: Territory | null): string {
  return territory?.public_status ?? 'Estado interno de revisión';
}

function normalizeAreaNombre(value: string): string {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function territoryForMapArea(territories: Territory[], provinceCode: string, areaNombre?: string | null): string | null {
  if (!areaNombre) return null;
  const normalizedArea = normalizeAreaNombre(areaNombre);
  if (!normalizedArea) return null;
  const exact = territories.find((territory) => territory.province_code === provinceCode && normalizeAreaNombre(territory.name) === normalizedArea);
  if (exact) return exact.id;
  const contains = territories.find((territory) => {
    if (territory.province_code !== provinceCode) return false;
    const territoryNombre = normalizeAreaNombre(territory.name);
    return territoryNombre.includes(normalizedArea) || normalizedArea.includes(territoryNombre);
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
  const [accuracyMeters, setPrecisiónMeters] = useState<number | ''>('');
  const [provinceCode, setProvinceCode] = useState(preferredProvinceCode(provinces));
  const [territoryId, setTerritoryId] = useState(preferredTerritoryId(territories));
  const [addressLabel, setAddressLabel] = useState('');
  const [landmark, setLandmark] = useState('');
  const [citizenNombre, setCitizenNombre] = useState('');
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
  const officialRoutingTerritories = useMemo(
    () => filteredTerritories.filter((territory) => territory.readiness === 'official-routing'),
    [filteredTerritories],
  );
  const localReferenceTerritories = useMemo(
    () => filteredTerritories.filter((territory) => territory.readiness !== 'official-routing'),
    [filteredTerritories],
  );
  const selectedTerritory = useMemo(() => territories.find((territory) => territory.id === territoryId), [territories, territoryId]);
  const selectedProvince = useMemo(() => provinces.find((province) => province.code === provinceCode), [provinceCode, provinces]);
  const mapSuggestedLocalArea = roadSuggestion?.suggested_local_area || roadSuggestion?.suggested_place_name || null;
  const displayedLocalArea = mapSuggestedLocalArea ?? selectedTerritory?.name ?? 'Area pending';

  useEffect(() => {
    const selected = territories.find((territory) => territory.id === territoryId);
    if (selected?.province_code && selected.province_code !== provinceCode) {
      setTerritoryId('');
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
        setPrecisiónMeters('');
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
        const matchedTerritory = territoryForPunto(territories, capturedLatitude, capturedLongitude);
        if (matchedTerritory) setTerritoryId(matchedTerritory);
        setPrecisiónMeters(Math.round(position.coords.accuracy));
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
      setNotice('Código nacional generado. Revise posibles duplicados y sugerencias antes de enviar.');
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
          citizen_name: citizenNombre || null,
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
              {isLocating ? 'Capturando ubicación…' : t('useMyCurrentLocation')}
            </button>
            <button className="secondary-action" type="button" onClick={() => void handlePreview()} disabled={isPreviewing}>
              {isPreviewing ? 'Comprobando punto…' : t('checkAddressCode')}
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
          <span className="location-metric accuracy-metric"><strong>Precisión</strong>{accuracyMeters === '' ? 'No capturada' : `${accuracyMeters}m`}</span>
        </div>
        {notice ? <p className="form-notice success">{notice}</p> : null}
        {!notice && preview ? (
          <p className="form-notice success">Código nacional generado. Revise posibles duplicados y sugerencias antes de enviar.</p>
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
          <span className="form-focus-badge">2 datos esenciales + contacto</span>
        </div>
        <p className="public-task-copy compact-form-intro">Seleccione primero la provincia y el municipio o área de enrutamiento. La posición GPS queda como evidencia técnica y será revisada por un operador autorizado antes de cualquier publicación.</p>
        <form id="citizen-location-form" className="territory-form citizen-form compact-location-form" onSubmit={handleSubmit}>
          <div className="routing-first-block" aria-label="Province and official routing area">
            <label className="territory-field important-field">
              <span className="territory-label">Provincia</span>
              <select className="territory-input" value={provinceCode} onChange={(event) => { setProvinceCode(event.target.value); setTerritoryId(''); setPreview(null); }} required>
                {provinces.map((province) => (
                  <option key={province.code} value={province.code}>{province.name}</option>
                ))}
              </select>
              <span className="field-help">La provincia define el prefijo nacional del código y filtra las rutas disponibles.</span>
            </label>
            <label className="territory-field important-field routing-area-field">
              <span className="territory-label">Distrito / municipio o área de enrutamiento</span>
              <select className="territory-input" value={territoryId} onChange={(event) => { setTerritoryId(event.target.value); setPreview(null); }}>
                <option value="">Pendiente de clasificación por operador</option>
                {officialRoutingTerritories.length ? (
                  <optgroup label="Rutas administrativas oficiales">
                    {officialRoutingTerritories.map((territory) => (
                      <option key={territory.id} value={territory.id}>{territory.name}</option>
                    ))}
                  </optgroup>
                ) : null}
                {localReferenceTerritories.length ? (
                  <optgroup label="Áreas locales referenciadas">
                    {localReferenceTerritories.map((territory) => (
                      <option key={territory.id} value={territory.id}>{territory.name}</option>
                    ))}
                  </optgroup>
                ) : null}
              </select>
              <span className="field-help">Si no está seguro, deje la clasificación pendiente. El operador confirmará el área antes de publicar.</span>
            </label>
            <div className="routing-status-card">
              <span className={`status-chip ${territoryStatusClass(selectedTerritory)}`}>{selectedTerritory?.routing_status_label ?? 'Pendiente de verificación de campo'}</span>
              <strong>{selectedTerritory?.name ?? 'Área pendiente'}</strong>
              <span>{selectedTerritory ? territoryTypeLabel(selectedTerritory.type) : `Provincia seleccionada: ${selectedProvince?.name ?? provinceCode}`}</span>
            </div>
          </div>

          <details className="quiet-disclosure routing-evidence-disclosure" open>
            <summary>Fuente y alcance oficial del enrutamiento</summary>
            <div className="routing-evidence-grid">
              <span><strong>Fuente</strong>{sourceLabel(selectedTerritory)}</span>
              <span><strong>Confianza</strong>{confidenceLabel(selectedTerritory)}</span>
              <span><strong>Geometría</strong>{geometryLabel(selectedTerritory)}</span>
              <span><strong>Publicación</strong>{publicStatusLabel(selectedTerritory)}</span>
            </div>
          </details>

          <div className="essential-form-block">
            <label className="territory-field important-field">
              <span className="territory-label">{t('placeLabel')}</span>
              <input className="territory-input" value={addressLabel} onChange={(event) => setAddressLabel(event.target.value)} required placeholder="Ejemplo: casa cerca de una referencia pública" />
            </label>
            <label className="territory-field important-field">
              <span className="territory-label">{t('landmarkLabel')}</span>
              <input className="territory-input" value={landmark} onChange={(event) => setLandmark(event.target.value)} placeholder="Vía cercana, color de portón o referencia pública" />
            </label>
            <label className="territory-field important-field">
              <span className="territory-label">{t('contactLabel')}</span>
              <input className="territory-input" value={citizenContact} onChange={(event) => setCitizenContact(event.target.value)} placeholder="Teléfono o correo opcional para seguimiento" />
            </label>
          </div>

          <div className="location-suggestion-strip" aria-label="Location capture summary">
            <span><strong>Punto</strong>{latitude.toFixed(5)}, {longitude.toFixed(5)}</span>
            <span><strong>Precisión</strong>{accuracyMeters === '' ? 'No capturada' : `${accuracyMeters}m`}</span>
            <span><strong>Ruta</strong>{selectedTerritory?.name ?? displayedLocalArea}</span>
          </div>

          <details className="quiet-disclosure compact-secondary-disclosure">
            <summary>Datos de identidad opcionales</summary>
            <div className="citizen-form-grid">
              <label className="territory-field">
                <span className="territory-label">Nombre</span>
                <input className="territory-input" value={citizenNombre} onChange={(event) => setCitizenNombre(event.target.value)} placeholder="Opcional" />
              </label>
              <label className="territory-field">
                <span className="territory-label">{t('dipLast4Label')}</span>
                <input className="territory-input" inputMode="numeric" pattern="[0-9]{4}" maxLength={4} value={dipLast4} onChange={(event) => setDipLast4(event.target.value.replace(/\D/g, '').slice(0, 4))} placeholder="Opcional" />
                <span className="field-help">{t('dipLast4Help')}</span>
              </label>
            </div>
          </details>

          <details className="quiet-disclosure compact-secondary-disclosure">
            <summary>Evidencia técnica capturada</summary>
            <div className="citizen-form-grid routing-confirmation-grid">
              <div className="territory-field locked-location-field" aria-label="Captured GPS coordinates">
                <span className="territory-label">Punto GPS</span>
                <strong>{latitude.toFixed(7)}, {longitude.toFixed(7)}</strong>
                <span className="field-help">Capturado desde GPS del dispositivo o marcador del mapa; no se publica sin revisión.</span>
              </div>
              <div className="territory-field locked-location-field" aria-label="Captured GPS accuracy">
                <span className="territory-label">Precisión GPS</span>
                <strong>{accuracyMeters === '' ? 'No capturada' : `${accuracyMeters}m`}</strong>
                <span className="field-help">La precisión se conserva como evidencia técnica.</span>
              </div>
              <div className="territory-field locked-location-field" aria-label="Province">
                <span className="territory-label">Provincia</span>
                <strong>{selectedProvince?.name ?? provinceCode}</strong>
                <span className="field-help">La provincia se revisa junto con el punto GPS y el área seleccionada.</span>
              </div>
            </div>
            <span className="field-help">Los datos técnicos apoyan la revisión. La clasificación oficial y la publicación quedan bajo control de operadores autorizados.</span>
          </details>

          <div className="compact-form-actions">
            <button className="secondary-action" type="button" onClick={() => void handlePreview()} disabled={isPreviewing}>
              {isPreviewing ? 'Comprobando punto…' : t('checkAddressCode')}
            </button>
            <button className="primary-action" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Enviando…' : t('submitLocation')}
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
            <p>Código provisional de dirección</p>
            <strong>{preview.grid_code}</strong>
            <span>{selectedTerritory?.name ?? preview.territory_name ?? 'Área pendiente de clasificación'}</span>
            {preview.address_code ? (
              <span>{preview.address_code.cell_size_meters}m location cell · checksum {preview.address_code.checksum}</span>
            ) : null}
          </div>
        ) : (
          <p className="panel-state">{t('previewPrompt')}</p>
        )}
        {roadSuggestion ? (
          <div className="operator-finding-card">
            <strong>Sugerencias cartográficas</strong>
            {roadSuggestion.suggested_local_area || roadSuggestion.suggested_place_name ? (
              <p>Área local: {roadSuggestion.suggested_local_area || roadSuggestion.suggested_place_name}</p>
            ) : (
              <p>El origen cartográfico no devolvió un área local.</p>
            )}
            {roadSuggestion.suggested_road_name ? (
              <p>Vía: {roadSuggestion.suggested_road_name}</p>
            ) : (
              <p>No se encontró nombre de vía cerca del punto.</p>
            )}
            <span className="status-chip warn">Sugerencia cartográfica · requiere revisión</span>
            <p className="institutional-note">Fuente: {roadSuggestion.source_attribution}. Estos nombres no son oficiales hasta que sean revisados.</p>
          </div>
        ) : null}
        {preview?.duplicate_hints?.length ? (
          <details className="quiet-disclosure">
            <summary>Posible coincidencia cercana</summary>
            <ul className="mini-list">
              {preview.duplicate_hints.map((hint) => (
                <li key={`${hint.source}-${hint.id}`}>
                  <strong>{hint.label}</strong>
                  <span>{hint.distance_meters}m away · {hint.code ?? 'código pendiente'}</span>
                </li>
              ))}
            </ul>
          </details>
        ) : (
          <p className="institutional-note">No se encontró coincidencia cercana para este punto.</p>
        )}
        {result ? (
          <div className="form-notice success">
            Enviado para revisión oficial. Estado: <strong>{result.automation?.process_stage ?? statusLabel(result.status)}</strong>. Conserve este código provisional: <strong>{result.grid_code}</strong>.
            {result.automation?.citizen_tracking?.tracking_code ? <> Código de seguimiento: <strong>{result.automation.citizen_tracking.tracking_code}</strong>.</> : null}
            <br />
            Siguiente paso: {result.automation?.next_best_action_label ?? 'Un operador revisará el punto, duplicados y sugerencias de vía antes de cualquier publicación.'}
            {result.automation?.routing?.assigned ? (
              <><br />Área de enrutamiento asignada automáticamente: <strong>{result.automation.routing.territory_name}</strong>.</>
            ) : null}
            {result.automation?.reasons?.length ? (
              <ul>
                {result.automation.reasons.slice(0, 3).map((reason) => <li key={reason}>{reason}</li>)}
              </ul>
            ) : null}
          </div>
        ) : null}
        <p className="submission-security-note">Todos los envíos se protegen y son revisados por operadores autorizados.</p>
      </article>
    </section>
  );
}
