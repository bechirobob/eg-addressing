import { SiteChrome } from '../../components/SiteChrome';
import { RegistryCorePanel } from '../../components/RegistryCorePanel';

type Territory = { id: string; name: string; province_code: string; province: string; type: string; readiness: string; is_archived: boolean };
type Road = { id: string; name: string; territory_id: string; territory_name: string; status: string; length_km: string; is_archived: boolean };
type Building = { id: string; label: string; territory_id: string; territory_name: string; road_id: string; road_name: string; status: string; usage: string; is_archived: boolean };
type Address = { id: string; formatted: string; territory_id: string; territory_name: string; road_id: string; road_name: string; building_id: string; building_label: string; province_code: string; status: string; publication_state: string; is_archived: boolean };

export const dynamic = 'force-dynamic';

async function fetchItems<T>(baseUrl: string, path: string): Promise<T[]> {
  try {
    const response = await fetch(`${baseUrl}${path}`, { cache: 'no-store' });
    if (!response.ok) return [];
    const payload = (await response.json()) as { items: T[] };
    return payload.items;
  } catch {
    return [];
  }
}

export default async function RegistryPage({
  searchParams,
}: {
  searchParams?: Promise<{ entity?: string }>;
}) {
  const baseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const resolvedSearchParams = (await searchParams) ?? {};
  const [territories, roads, buildings, addresses] = await Promise.all([
    fetchItems<Territory>(baseUrl, '/api/v1/territories'),
    fetchItems<Road>(baseUrl, '/api/v1/roads'),
    fetchItems<Building>(baseUrl, '/api/v1/buildings'),
    fetchItems<Address>(baseUrl, '/api/v1/addresses'),
  ]);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Registry core"
      title="Roads, Buildings, and Address Registry"
      subtitle="Operational management surfaces for the core address-production entities maintained by the national registry."
    >
      <RegistryCorePanel
        initialTerritories={territories}
        initialRoads={roads}
        initialBuildings={buildings}
        initialAddresses={addresses}
        apiBaseUrl={publicApiBaseUrl}
        highlightEntityId={resolvedSearchParams.entity ?? null}
      />
    </SiteChrome>
  );
}
