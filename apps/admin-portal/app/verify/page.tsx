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
  void baseUrl;
  return [];
}

async function getLookup(baseUrl: string): Promise<LookupResult> {
  try {
    const response = await fetch(
      `${baseUrl}/api/v1/verification/lookup?query=${encodeURIComponent('EG-BN-MALABO-001A')}`,
      { cache: 'no-store' },
    );
    if (!response.ok) throw new Error('lookup failed');
    return (await response.json()) as LookupResult;
  } catch {
    return {
      query: 'EG-BN-MALABO-001A',
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
      eyebrow="Evidence desk"
      eyebrowKey="verifyEyebrow"
      title="Evidence Review Workflow"
      titleKey="verifyTitle"
      subtitle="Review submitted evidence, confirm registry decisions, and run public-trust checks before records progress."
      subtitleKey="verifySubtitle"
    >
      <VerificationWorkflowPanel
        submissions={submissions}
        sampleLookup={sampleLookup}
        apiBaseUrl={publicApiBaseUrl}
      />
    </SiteChrome>
  );
}
