'use client';

import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import type { Map as LeafletMap, LeafletMouseEvent, CircleMarker, Circle } from 'leaflet';

import { resolveBrowserApiBaseUrl } from './sessionClient';

import { type Locale, useTranslation } from './i18n';

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

function localizedStatusLabel(status: string): string {
  return status.replaceAll('-', ' ');
}

function readinessLabel(value: string | undefined, locale: Locale): string {
  const labels: Record<string, { en: string; es: string }> = {
    'official-routing': { en: 'Official administrative route', es: 'Ruta administrativa oficial' },
    'intake-routing': { en: 'Intake routing area', es: 'Área local para ingreso' },
    'active-mapping': { en: 'Active mapping', es: 'Cartografía activa' },
    'verification-prep': { en: 'Pending field verification', es: 'Pendiente de verificación de campo' },
    'survey-queue': { en: 'Survey queue', es: 'En cola de levantamiento' },
  };
  if (!value) return locale === 'es' ? 'Pendiente de clasificación' : 'Pending classification';
  return labels[value]?.[locale] ?? localizedStatusLabel(value);
}

function territoryTypeLabel(value: string | undefined, locale: Locale): string {
  const labels: Record<string, { en: string; es: string }> = {
    'official-municipality': { en: 'Municipality / administrative route', es: 'Municipio / ruta administrativa' },
    'map-referenced-local-area': { en: 'Referenced local area', es: 'Área local referenciada' },
    'capital-urban-core': { en: 'Capital urban core', es: 'Núcleo urbano capital' },
    'urban-core': { en: 'Urban core', es: 'Núcleo urbano' },
  };
  return value ? labels[value]?.[locale] ?? localizedStatusLabel(value) : locale === 'es' ? 'Área de enrutamiento' : 'Routing area';
}

function territoryStatusClass(territory?: Territory | null): string {
  if (!territory) return 'warn';
  if (territory.readiness === 'official-routing') return 'ok';
  if (territory.readiness === 'verification-prep' || territory.readiness === 'survey-queue') return 'warn';
  return '';
}

function routingStatusLabel(territory: Territory | null | undefined, locale: Locale): string {
  return readinessLabel(territory?.readiness, locale);
}

function sourceLabel(territory: Territory | null | undefined, locale: Locale): string {
  if (territory?.type === 'official-municipality' && territory.readiness === 'official-routing') {
    return locale === 'es' ? 'Tabla de división administrativa / fuente referenciada por INEGE' : 'Administrative division table / INEGE-referenced source';
  }
  if (territory?.type === 'map-referenced-local-area') {
    return locale === 'es' ? 'Referencia cartográfica/local usada para enrutamiento de ingreso' : 'Map/local reference used for intake routing';
  }
  return locale === 'es' ? 'Registro interno de enrutamiento; confirmar antes de publicación' : 'Internal routing record; confirm before publication';
}

function confidenceLabel(territory: Territory | null | undefined, locale: Locale): string {
  if (territory?.type === 'official-municipality' && territory.readiness === 'official-routing') {
    return locale === 'es' ? 'Unidad administrativa confirmada' : 'Administrative unit confirmed';
  }
  if (territory?.type === 'map-referenced-local-area') {
    return locale === 'es' ? 'Referencia local; requiere confirmación del operador' : 'Local reference; requires operator confirmation';
  }
  return locale === 'es' ? 'Registro interno; confirmar antes de publicación' : 'Internal record; confirm before publication';
}

function geometryLabel(territory: Territory | null | undefined, locale: Locale): string {
  if (territory?.type === 'official-municipality') {
    return locale === 'es' ? 'Área de enrutamiento por nombre administrativo; límite topográfico no adjunto' : 'Name-based administrative routing area; surveyed boundary not attached';
  }
  return locale === 'es' ? 'Registro de enrutamiento; geometría oficial levantada no adjunta' : 'Routing record; official surveyed geometry not attached';
}

function publicStatusLabel(territory: Territory | null | undefined, locale: Locale): string {
  if (territory?.readiness === 'official-routing') {
    return locale === 'es' ? 'Enrutamiento interno hasta verificación del operador y publicación controlada' : 'Internal routing only until operator verification and controlled publication';
  }
  if (territory?.readiness === 'intake-routing') {
    return locale === 'es' ? 'Pendiente de verificación de campo antes de publicación' : 'Pending field verification before publication';
  }
  return locale === 'es' ? 'Estado interno de revisión' : 'Internal review state';
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
  const { locale, t } = useTranslation();
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const markerRef = useRef<CircleMarker | null>(null);
  const accuracyCircleRef = useRef<Circle | null>(null);
  const receiptRef = useRef<HTMLDivElement | null>(null);
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
  const receiptTrackingCode = result?.automation?.citizen_tracking?.tracking_code ?? result?.id ?? null;

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

  useEffect(() => {
    if (!result) return;
    window.setTimeout(() => receiptRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
  }, [result]);

  async function handleUseMyLocation() {
    setNotice(null);
    setError(null);
    if (!navigator.geolocation) {
      setError(locale === 'es' ? 'Este navegador no admite captura de ubicación GPS. Aún puede hacer clic en el mapa.' : 'This browser does not support GPS location capture. You can still click the map.');
      return;
    }
    if (typeof window !== 'undefined' && !window.isSecureContext && !isLocalhostHost(window.location.hostname)) {
      setError(locale === 'es' ? 'El navegador bloquea el GPS porque el enlace no es seguro. Use HTTPS o el marcador del mapa.' : 'Your browser is blocking GPS because this link is not secure. Use HTTPS or the map pin.');
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
        setAccuracyMeters(Math.round(position.coords.accuracy));
        setCaptureMethod('browser-gps');
        setRoadSuggestion(null);
        setPreview(null);
        setNotice(locale === 'es' ? 'Ubicación GPS capturada. Mueva el marcador si la posición requiere corrección.' : 'GPS location captured. Move the map pin if the position needs correction.');
        setIsLocating(false);
      },
      () => {
        setError(locale === 'es' ? 'No se pudo capturar la ubicación GPS. Aún puede hacer clic en el mapa.' : 'Unable to capture GPS location. You can still click the map.');
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
      setNotice(locale === 'es' ? 'Código nacional generado. Revise posibles duplicados y sugerencias antes de enviar.' : 'National address code generated. Review possible duplicates and suggestions before submitting.');
    } catch {
      setError(locale === 'es' ? 'No se puede comprobar este punto en este momento.' : 'Unable to preview this point right now.');
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
      setError(locale === 'es' ? 'Los últimos 4 dígitos del D.I.P. deben tener exactamente 4 números. Déjelo en blanco si no desea proporcionarlo ahora.' : 'D.I.P. last 4 must be exactly 4 digits. Leave it blank if you do not want to provide it now.');
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
      setNotice(locale === 'es' ? 'Ubicación enviada para revisión del Gobierno y verificación de campo.' : 'Location submitted for government review and field verification.');
    } catch {
      setError(locale === 'es' ? 'No se puede enviar la ubicación en este momento.' : 'Unable to submit the geotag record right now.');
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
          <ol className="citizen-flow-steps" aria-label={locale === 'es' ? 'Pasos de registro' : 'Registration steps'}>
            <li><strong>1</strong><span>{locale === 'es' ? 'Capturar GPS' : 'Capture GPS'}</span></li>
            <li><strong>2</strong><span>{locale === 'es' ? 'Confirmar marcador' : 'Confirm pin'}</span></li>
            <li><strong>3</strong><span>{locale === 'es' ? 'Añadir referencia' : 'Add landmark'}</span></li>
            <li><strong>4</strong><span>{locale === 'es' ? 'Enviar y seguir' : 'Submit and track'}</span></li>
          </ol>
          <div className="citizen-primary-actions">
            <button className="primary-action location-action" type="button" onClick={() => void handleUseMyLocation()} disabled={isLocating}>
              {isLocating ? (locale === 'es' ? 'Capturando ubicación…' : 'Getting your location…') : t('useMyCurrentLocation')}
            </button>
            <button className="secondary-action" type="button" onClick={() => void handlePreview()} disabled={isPreviewing}>
              {isPreviewing ? (locale === 'es' ? 'Comprobando punto…' : 'Checking point…') : t('checkAddressCode')}
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
          <span className="location-metric accuracy-metric"><strong>{locale === 'es' ? 'Precisión' : 'Accuracy'}</strong>{accuracyMeters === '' ? (locale === 'es' ? 'No capturada' : 'Not captured') : `${accuracyMeters}m`}</span>
        </div>
        {notice ? <p className="form-notice success">{notice}</p> : null}
        {!notice && preview ? (
          <p className="form-notice success">{locale === 'es' ? 'Código nacional generado. Revise posibles duplicados y sugerencias antes de enviar.' : 'National address code generated. Review possible duplicates and suggestions before submitting.'}</p>
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
          <span className="form-focus-badge">{locale === 'es' ? '2 datos esenciales + contacto' : '2 essentials + contact'}</span>
        </div>
        <p className="public-task-copy compact-form-intro">{locale === 'es' ? 'Seleccione primero la provincia y el municipio o área de enrutamiento. La posición GPS queda como evidencia técnica y será revisada por un operador autorizado antes de cualquier publicación.' : 'Select the province and district, municipality, or routing area first. The GPS point is technical evidence and will be reviewed by an authorized operator before publication.'}</p>
        <form id="citizen-location-form" className="territory-form citizen-form compact-location-form" onSubmit={handleSubmit}>
          <div className="routing-first-block" aria-label="Province and official routing area">
            <label className="territory-field important-field">
              <span className="territory-label">{locale === 'es' ? 'Provincia' : 'Province'}</span>
              <select className="territory-input" value={provinceCode} onChange={(event) => { setProvinceCode(event.target.value); setTerritoryId(''); setPreview(null); }} required>
                {provinces.map((province) => (
                  <option key={province.code} value={province.code}>{province.name}</option>
                ))}
              </select>
              <span className="field-help">{locale === 'es' ? 'La provincia define el prefijo nacional del código y filtra las rutas disponibles.' : 'The province defines the national code prefix and filters available routes.'}</span>
            </label>
            <label className="territory-field important-field routing-area-field">
              <span className="territory-label">{locale === 'es' ? 'Distrito / municipio o área de enrutamiento' : 'District / municipality or routing area'}</span>
              <select className="territory-input" value={territoryId} onChange={(event) => { setTerritoryId(event.target.value); setPreview(null); }}>
                <option value="">{locale === 'es' ? 'Pendiente de clasificación por operador' : 'Pending operator classification'}</option>
                {officialRoutingTerritories.length ? (
                  <optgroup label={locale === 'es' ? 'Rutas administrativas oficiales' : 'Official administrative routes'}>
                    {officialRoutingTerritories.map((territory) => (
                      <option key={territory.id} value={territory.id}>{territory.name}</option>
                    ))}
                  </optgroup>
                ) : null}
                {localReferenceTerritories.length ? (
                  <optgroup label={locale === 'es' ? 'Áreas locales referenciadas' : 'Referenced local areas'}>
                    {localReferenceTerritories.map((territory) => (
                      <option key={territory.id} value={territory.id}>{territory.name}</option>
                    ))}
                  </optgroup>
                ) : null}
              </select>
              <span className="field-help">{locale === 'es' ? 'Si no está seguro, deje la clasificación pendiente. El operador confirmará el área antes de publicar.' : 'If you are not sure, leave classification pending. The operator will confirm the area before publication.'}</span>
            </label>
            <div className="routing-status-card">
              <span className={`status-chip ${territoryStatusClass(selectedTerritory)}`}>{routingStatusLabel(selectedTerritory, locale)}</span>
              <strong>{selectedTerritory?.name ?? (locale === 'es' ? 'Área pendiente' : 'Area pending')}</strong>
              <span>{selectedTerritory ? territoryTypeLabel(selectedTerritory.type, locale) : `${locale === 'es' ? 'Provincia seleccionada' : 'Selected province'}: ${selectedProvince?.name ?? provinceCode}`}</span>
            </div>
          </div>

          <details className="quiet-disclosure routing-evidence-disclosure">
            <summary>
              <span>{locale === 'es' ? 'Fuente y alcance oficial del enrutamiento' : 'Source and official routing scope'}</span>
              <small>{selectedTerritory ? routingStatusLabel(selectedTerritory, locale) : (locale === 'es' ? 'Revisión del operador antes de publicar' : 'Operator review before publication')}</small>
            </summary>
            <div className="routing-evidence-grid">
              <span><strong>{locale === 'es' ? 'Fuente' : 'Source'}</strong>{sourceLabel(selectedTerritory, locale)}</span>
              <span><strong>{locale === 'es' ? 'Confianza' : 'Confidence'}</strong>{confidenceLabel(selectedTerritory, locale)}</span>
              <span><strong>{locale === 'es' ? 'Geometría' : 'Geometry'}</strong>{geometryLabel(selectedTerritory, locale)}</span>
              <span><strong>{locale === 'es' ? 'Publicación' : 'Publication'}</strong>{publicStatusLabel(selectedTerritory, locale)}</span>
            </div>
          </details>

          <div className="essential-form-block">
            <label className="territory-field important-field">
              <span className="territory-label">{t('placeLabel')}</span>
              <input className="territory-input" value={addressLabel} onChange={(event) => setAddressLabel(event.target.value)} required placeholder={locale === 'es' ? 'Ejemplo: casa cerca de una referencia pública' : 'Example: house near a public landmark'} />
            </label>
            <label className="territory-field important-field">
              <span className="territory-label">{t('landmarkLabel')}</span>
              <input className="territory-input" value={landmark} onChange={(event) => setLandmark(event.target.value)} placeholder={locale === 'es' ? 'Vía cercana, color de portón o referencia pública' : 'Nearest road, gate color, or public landmark'} />
            </label>
            <label className="territory-field important-field">
              <span className="territory-label">{t('contactLabel')}</span>
              <input className="territory-input" value={citizenContact} onChange={(event) => setCitizenContact(event.target.value)} placeholder={locale === 'es' ? 'Teléfono o correo opcional para seguimiento' : 'Optional phone or email for follow-up'} />
            </label>
          </div>

          <div className="location-suggestion-strip" aria-label="Location capture summary">
            <span><strong>{locale === 'es' ? 'Punto' : 'Point'}</strong>{latitude.toFixed(5)}, {longitude.toFixed(5)}</span>
            <span><strong>{locale === 'es' ? 'Precisión' : 'Accuracy'}</strong>{accuracyMeters === '' ? (locale === 'es' ? 'No capturada' : 'Not captured') : `${accuracyMeters}m`}</span>
            <span><strong>{locale === 'es' ? 'Ruta' : 'Route'}</strong>{selectedTerritory?.name ?? displayedLocalArea}</span>
          </div>

          <details className="quiet-disclosure compact-secondary-disclosure">
            <summary>{locale === 'es' ? 'Datos de identidad opcionales' : 'Optional identity details'}</summary>
            <div className="citizen-form-grid">
              <label className="territory-field">
                <span className="territory-label">{locale === 'es' ? 'Nombre' : 'Name'}</span>
                <input className="territory-input" value={citizenName} onChange={(event) => setCitizenName(event.target.value)} placeholder={locale === 'es' ? 'Opcional' : 'Optional'} />
              </label>
              <label className="territory-field">
                <span className="territory-label">{t('dipLast4Label')}</span>
                <input className="territory-input" inputMode="numeric" pattern="[0-9]{4}" maxLength={4} value={dipLast4} onChange={(event) => setDipLast4(event.target.value.replace(/\D/g, '').slice(0, 4))} placeholder={locale === 'es' ? 'Opcional' : 'Optional'} />
                <span className="field-help">{t('dipLast4Help')}</span>
              </label>
            </div>
          </details>

          <details className="quiet-disclosure compact-secondary-disclosure technical-evidence-disclosure">
            <summary>
              <span>{locale === 'es' ? 'Evidencia técnica capturada' : 'Captured technical evidence'}</span>
              <small>{accuracyMeters === '' ? (locale === 'es' ? 'GPS pendiente' : 'GPS pending') : `${locale === 'es' ? 'Precisión' : 'Accuracy'} ${accuracyMeters}m`}</small>
            </summary>
            <div className="citizen-form-grid routing-confirmation-grid">
              <div className="territory-field locked-location-field" aria-label="Captured GPS coordinates">
                <span className="territory-label">{locale === 'es' ? 'Punto GPS' : 'GPS point'}</span>
                <strong>{latitude.toFixed(7)}, {longitude.toFixed(7)}</strong>
                <span className="field-help">{locale === 'es' ? 'Capturado desde GPS del dispositivo o marcador del mapa; no se publica sin revisión.' : 'Captured from the device GPS or map pin; not published without review.'}</span>
              </div>
              <div className="territory-field locked-location-field" aria-label="Captured GPS accuracy">
                <span className="territory-label">{locale === 'es' ? 'Precisión GPS' : 'GPS accuracy'}</span>
                <strong>{accuracyMeters === '' ? (locale === 'es' ? 'No capturada' : 'Not captured') : `${accuracyMeters}m`}</strong>
                <span className="field-help">{locale === 'es' ? 'La precisión se conserva como evidencia técnica.' : 'Accuracy is kept as technical evidence.'}</span>
              </div>
              <div className="territory-field locked-location-field" aria-label="Province">
                <span className="territory-label">{locale === 'es' ? 'Provincia' : 'Province'}</span>
                <strong>{selectedProvince?.name ?? provinceCode}</strong>
                <span className="field-help">{locale === 'es' ? 'La provincia se revisa junto con el punto GPS y el área seleccionada.' : 'The province is reviewed with the GPS point and selected area.'}</span>
              </div>
            </div>
            <span className="field-help">{locale === 'es' ? 'Los datos técnicos apoyan la revisión. La clasificación oficial y la publicación quedan bajo control de operadores autorizados.' : 'Technical data supports review. Official classification and publication remain controlled by authorized operators.'}</span>
          </details>

          <div className="compact-form-actions">
            <button className="secondary-action" type="button" onClick={() => void handlePreview()} disabled={isPreviewing}>
              {isPreviewing ? (locale === 'es' ? 'Comprobando punto…' : 'Checking point…') : t('checkAddressCode')}
            </button>
            <button className="primary-action" type="submit" disabled={isSubmitting}>
              {isSubmitting ? (locale === 'es' ? 'Enviando…' : 'Submitting…') : t('submitLocation')}
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
            <p>{locale === 'es' ? 'Código provisional de dirección' : 'Provisional address code'}</p>
            <strong>{preview.grid_code}</strong>
            <span>{selectedTerritory?.name ?? preview.territory_name ?? (locale === 'es' ? 'Área pendiente de clasificación' : 'Area pending classification')}</span>
            {preview.address_code ? (
              <span>{preview.address_code.cell_size_meters}m location cell · checksum {preview.address_code.checksum}</span>
            ) : null}
          </div>
        ) : (
          <p className="panel-state">{t('previewPrompt')}</p>
        )}
        {roadSuggestion ? (
          <div className="operator-finding-card">
            <strong>{locale === 'es' ? 'Sugerencias cartográficas' : 'Map suggestions'}</strong>
            {roadSuggestion.suggested_local_area || roadSuggestion.suggested_place_name ? (
              <p>{locale === 'es' ? 'Área local' : 'Local area'}: {roadSuggestion.suggested_local_area || roadSuggestion.suggested_place_name}</p>
            ) : (
              <p>{locale === 'es' ? 'El origen cartográfico no devolvió un área local.' : 'The map source did not return a local area.'}</p>
            )}
            {roadSuggestion.suggested_road_name ? (
              <p>{locale === 'es' ? 'Vía' : 'Road'}: {roadSuggestion.suggested_road_name}</p>
            ) : (
              <p>{locale === 'es' ? 'No se encontró nombre de vía cerca del punto.' : 'No road name was found near this point.'}</p>
            )}
            <span className="status-chip warn">{locale === 'es' ? 'Sugerencia cartográfica · requiere revisión' : 'Map suggestion · review required'}</span>
            <p className="institutional-note">{locale === 'es' ? 'Fuente' : 'Source'}: {roadSuggestion.source_attribution}. {locale === 'es' ? 'Estos nombres no son oficiales hasta que sean revisados.' : 'These names are not official until reviewed.'}</p>
          </div>
        ) : null}
        {preview?.duplicate_hints?.length ? (
          <details className="quiet-disclosure">
            <summary>{locale === 'es' ? 'Posible coincidencia cercana' : 'Possible nearby match'}</summary>
            <ul className="mini-list">
              {preview.duplicate_hints.map((hint) => (
                <li key={`${hint.source}-${hint.id}`}>
                  <strong>{hint.label}</strong>
                  <span>{hint.distance_meters}m {locale === 'es' ? 'de distancia' : 'away'} · {hint.code ?? (locale === 'es' ? 'código pendiente' : 'code pending')}</span>
                </li>
              ))}
            </ul>
          </details>
        ) : (
          <p className="institutional-note">{locale === 'es' ? 'No se encontró coincidencia cercana para este punto.' : 'No nearby match was found for this point.'}</p>
        )}
        {result ? (
          <div className="submission-receipt-card" ref={receiptRef} role="status" aria-live="polite" tabIndex={-1}>
            <div>
              <p className="section-label">{locale === 'es' ? 'Recibo de registro' : 'Submission receipt'}</p>
              <h4>{locale === 'es' ? 'Ubicación enviada para revisión oficial' : 'Location submitted for official review'}</h4>
              <p>{locale === 'es' ? 'El registro no se publica automáticamente. Un operador revisará el punto, duplicados, área de enrutamiento y sugerencias de vía.' : 'This record is not published automatically. An operator will review the point, duplicates, routing area, and road suggestions.'}</p>
            </div>
            <dl className="receipt-code-list">
              <div><dt>{locale === 'es' ? 'Código provisional' : 'Provisional address code'}</dt><dd>{result.grid_code}</dd></div>
              <div><dt>{locale === 'es' ? 'Código de seguimiento' : 'Tracking code'}</dt><dd>{receiptTrackingCode ?? (locale === 'es' ? 'Pendiente' : 'Pending')}</dd></div>
              <div><dt>{locale === 'es' ? 'Estado' : 'Status'}</dt><dd>{result.automation?.process_stage ?? localizedStatusLabel(result.status)}</dd></div>
            </dl>
            <p className="institutional-note"><strong>{locale === 'es' ? 'Siguiente paso:' : 'Next step:'}</strong> {result.automation?.next_best_action_label ?? (locale === 'es' ? 'Un operador revisará el punto antes de cualquier publicación.' : 'An operator will review the point before any publication.')}</p>
            {result.automation?.routing?.assigned ? (
              <p className="institutional-note"><strong>{locale === 'es' ? 'Área asignada:' : 'Assigned route:'}</strong> {result.automation.routing.territory_name}</p>
            ) : null}
            <div className="receipt-actions">
              {receiptTrackingCode ? (
                <a className="primary-action inline-action-link" href={`/track?code=${encodeURIComponent(receiptTrackingCode)}`}>{locale === 'es' ? 'Seguir esta solicitud' : 'Track this request'}</a>
              ) : null}
              <button className="secondary-action" type="button" onClick={() => { setResult(null); setPreview(null); setNotice(null); }}>{locale === 'es' ? 'Registrar otra ubicación' : 'Register another location'}</button>
            </div>
          </div>
        ) : null}
        <p className="submission-security-note">{locale === 'es' ? 'Todos los envíos se protegen y son revisados por operadores autorizados.' : 'All submissions are protected and reviewed by authorized operators.'}</p>
      </article>
    </section>
  );
}
