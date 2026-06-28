import { SiteChrome } from '../../components/SiteChrome';
import { PublicationOperationsPanel } from '../../components/PublicationOperationsPanel';

export const dynamic = 'force-dynamic';

type Address = {
  id: string;
  formatted: string;
  territory_name: string;
  status: string;
  publication_state: string;
  is_archived: boolean;
};

type ImportJob = {
  id: string;
  name: string;
  source_name: string;
  status: string;
  imported_count: number;
  total_rows: number;
  valid_rows: number;
};

type PublicationPack = {
  id: string;
  name: string;
  status: string;
  audience: string;
  address_count: number;
};

async function safeFetch<T>(url: string, fallback: T, headers?: Record<string, string>): Promise<T> {
  try {
    const response = await fetch(url, { cache: 'no-store', headers });
    if (!response.ok) return fallback;
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export default async function ExportsPage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const bootstrapHeaders = { Authorization: ['Bearer', 'admin-bootstrap-token'].join(' ') };
  const [addressesPayload, importJobsPayload, publicationPacksPayload] = await Promise.all([
    safeFetch<{ items: Address[] }>(`${apiBaseUrl}/api/v1/addresses`, { items: [] }),
    safeFetch<{ items: ImportJob[] }>(`${apiBaseUrl}/api/v1/imports/jobs`, { items: [] }, bootstrapHeaders),
    safeFetch<{ items: PublicationPack[] }>(`${apiBaseUrl}/api/v1/publication/packs`, { items: [] }, bootstrapHeaders),
  ]);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Official exports"
      title="Publication and Intake Operations"
      subtitle="Migration intake, official publication packs, and controlled output preparation for the national addressing registry."
    >
      <PublicationOperationsPanel
        initialAddresses={addressesPayload.items}
        initialImportJobs={importJobsPayload.items}
        initialPublicationPacks={publicationPacksPayload.items}
        apiBaseUrl={publicApiBaseUrl}
      />
    </SiteChrome>
  );
}
