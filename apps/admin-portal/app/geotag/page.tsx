import { SiteChrome } from '../../components/SiteChrome';
import { CitizenGeotagPanel } from '../../components/CitizenGeotagPanel';

export const dynamic = 'force-dynamic';

type Province = {
  code: string;
  name: string;
};

type Territory = {
  id: string;
  name: string;
  province?: string;
  province_code?: string;
  readiness?: string;
};

async function getProvinces(baseUrl: string): Promise<Province[]> {
  try {
    const response = await fetch(`${baseUrl}/api/v1/provinces`, { cache: 'no-store' });
    if (!response.ok) return [];
    const payload = (await response.json()) as { items: Province[] };
    return payload.items ?? [];
  } catch {
    return [];
  }
}

async function getTerritories(baseUrl: string): Promise<Territory[]> {
  try {
    const response = await fetch(`${baseUrl}/api/v1/public/territory-options`, { cache: 'no-store' });
    if (!response.ok) return [];
    const payload = (await response.json()) as { items: Territory[] };
    return payload.items ?? [];
  } catch {
    return [];
  }
}

export default async function CitizenGeotagPage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const [provinces, territories] = await Promise.all([getProvinces(apiBaseUrl), getTerritories(apiBaseUrl)]);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Location registration"
      eyebrowKey="geotagEyebrow"
      title="Register a Location"
      titleKey="geotagTitle"
      subtitle="Use GPS to capture the property point, confirm the pin, and send the location for official review."
      subtitleKey="geotagSubtitle"
    >
      <CitizenGeotagPanel apiBaseUrl={publicApiBaseUrl} provinces={provinces} territories={territories} />
    </SiteChrome>
  );
}
