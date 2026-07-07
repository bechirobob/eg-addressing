import { PublicIssuancePanel } from '../../components/PublicIssuancePanel';
import { SiteChrome } from '../../components/SiteChrome';

export const dynamic = 'force-dynamic';

type PublicExtract = {
  query: string;
  match_status: string;
  public_code: string | null;
  address_label: string;
  jurisdiction: string;
  verification_status: string;
  publication_state: string;
  verification_note: string;
  issuance_method?: string;
  source?: string;
  latitude?: number | null;
  longitude?: number | null;
  accuracy_meters?: number | null;
  address_id?: string | null;
  document_title?: string;
  document_reference?: string;
  record_locator?: string | null;
  issued_for?: string;
  issuing_authority?: string;
  extract_status?: string;
};

async function getSampleExtract(baseUrl: string): Promise<PublicExtract> {
  const sampleQuery = 'EG-BN-MALABO-001A';

  try {
    const response = await fetch(`${baseUrl}/api/v1/public/issuance/${encodeURIComponent(sampleQuery)}`, {
      cache: 'no-store',
    });
    if (!response.ok) throw new Error('issuance lookup failed');
    return (await response.json()) as PublicExtract;
  } catch {
    return {
      query: sampleQuery,
      match_status: 'not-found',
      public_code: sampleQuery,
      address_label: 'Published registry extract unavailable',
      jurisdiction: 'National addressing public service',
      verification_status: 'not-found',
      publication_state: 'unpublished',
      verification_note: 'Public extract service is temporarily unavailable.',
      document_title: 'Official Address Registry Extract',
      document_reference: `EXTRACT-${sampleQuery}`,
      record_locator: sampleQuery,
      issuing_authority: 'Republic of Equatorial Guinea · National Digital Addressing Platform',
      extract_status: 'not-available',
    };
  }
}

export default async function IssuePage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const sampleExtract = await getSampleExtract(apiBaseUrl);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Public address service"
      eyebrowKey="publicAddressService"
      title="Check Address Code"
      titleKey="issueTitle"
      subtitle="Check whether an address code is published, valid, or still waiting for official approval, then report a correction if the registry details need review."
      subtitleKey="issueSubtitle"
    >
      <PublicIssuancePanel initialExtract={sampleExtract} apiBaseUrl={publicApiBaseUrl} />
    </SiteChrome>
  );
}
