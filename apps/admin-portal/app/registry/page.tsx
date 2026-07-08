import { SiteChrome } from '../../components/SiteChrome';
import { RegistryCorePanel } from '../../components/RegistryCorePanel';

type Territory = { id: string; name: string; province_code: string; province: string; type: string; readiness: string; is_archived: boolean };
type Road = { id: string; name: string; territory_id: string; territory_name: string; status: string; length_km: string; is_archived: boolean };
type Building = { id: string; label: string; territory_id: string; territory_name: string; road_id: string; road_name: string; status: string; usage: string; is_archived: boolean };
type Address = { id: string; formatted: string; territory_id: string; territory_name: string; road_id: string; road_name: string; building_id: string; building_label: string; province_code: string; status: string; publication_state: string; is_archived: boolean };

export const dynamic = 'force-dynamic';

export default async function RegistryPage({
  searchParams,
}: {
  searchParams?: Promise<{ entity?: string }>;
}) {
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const resolvedSearchParams = (await searchParams) ?? {};
  const territories: Territory[] = [];
  const roads: Road[] = [];
  const buildings: Building[] = [];
  const addresses: Address[] = [];

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Staff service"
      eyebrowKey="registryEyebrow"
      title="Address registry"
      titleKey="registryTitle"
      subtitle="Search, update, and manage official address records."
      subtitleKey="registrySubtitle"
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
