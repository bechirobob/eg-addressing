import { SiteChrome } from '../../components/SiteChrome';
import { TerritoryAdminPanel } from '../../components/TerritoryAdminPanel';

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

export const dynamic = 'force-dynamic';

async function getTerritories(): Promise<Territory[]> {
  const baseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';

  try {
    const response = await fetch(`${baseUrl}/api/v1/territories`, { cache: 'no-store' });
    if (!response.ok) {
      return [];
    }

    const payload = (await response.json()) as { items: Territory[] };
    return payload.items;
  } catch {
    return [];
  }
}

async function getProvinces(): Promise<Province[]> {
  const baseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';

  try {
    const response = await fetch(`${baseUrl}/api/v1/territories/provinces`, { cache: 'no-store' });
    if (!response.ok) {
      return [];
    }

    const payload = (await response.json()) as { items: Province[] };
    return payload.items;
  } catch {
    return [];
  }
}

export default async function TerritoriesPage() {
  const [territories, provinces] = await Promise.all([getTerritories(), getProvinces()]);
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Territory administration"
      title="Territory Registry Management"
      subtitle="Administrative control surface for maintaining territory records in the national addressing registry."
    >
      <TerritoryAdminPanel initialTerritories={territories} provinces={provinces} apiBaseUrl={publicApiBaseUrl} />
    </SiteChrome>
  );
}
