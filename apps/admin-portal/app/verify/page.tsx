import { SiteChrome } from '../../components/SiteChrome';
import { VerificationWorkflowPanel } from '../../components/VerificationWorkflowPanel';

export const dynamic = 'force-dynamic';

type Submission = {
  id: string;
  territory_name: string;
  submission_type: string;
  candidate_name: string;
  candidate_status: string;
  review_status: string;
  reviewer_note: string;
  registry_entity_id?: string | null;
  submitted_by: string;
  notes: string;
};

type LookupResult = {
  query: string;
  match_status: string;
  address_label: string;
  jurisdiction: string;
  verification_note: string;
  address_id?: string;
};

async function getSubmissions(baseUrl: string): Promise<Submission[]> {
  const bootstrapHeaders = { Authorization: ['Bearer', 'admin-bootstrap-token'].join(' ') };
  try {
    const response = await fetch(`${baseUrl}/api/v1/field/submissions`, {
      cache: 'no-store',
      headers: bootstrapHeaders,
    });
    if (!response.ok) return [];
    const payload = (await response.json()) as { items: Submission[] };
    return payload.items ?? [];
  } catch {
    return [];
  }
}

async function getLookup(baseUrl: string): Promise<LookupResult> {
  try {
    const response = await fetch(
      `${baseUrl}/api/v1/verification/lookup?query=${encodeURIComponent('Avenida de la Independencia')}`,
      { cache: 'no-store' },
    );
    if (!response.ok) throw new Error('lookup failed');
    return (await response.json()) as LookupResult;
  } catch {
    return {
      query: 'Avenida de la Independencia',
      match_status: 'not-found',
      address_label: 'No published registry record found',
      jurisdiction: 'National registry lookup',
      verification_note: 'Lookup service is temporarily unavailable.',
    };
  }
}

export default async function VerifyPage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const [submissions, sampleLookup] = await Promise.all([getSubmissions(apiBaseUrl), getLookup(apiBaseUrl)]);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Verification portal"
      title="Verification and Review Workflow"
      subtitle="Review queue, decision control, and public-trust verification for records entering the national registry."
    >
      <VerificationWorkflowPanel
        submissions={submissions}
        sampleLookup={sampleLookup}
        apiBaseUrl={publicApiBaseUrl}
      />
    </SiteChrome>
  );
}
