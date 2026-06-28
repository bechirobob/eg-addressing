import { SiteChrome } from '../../components/SiteChrome';
import { ReportingDashboardPanel } from '../../components/ReportingDashboardPanel';

export const dynamic = 'force-dynamic';

type ReportingSummary = {
  totals: {
    territories: number;
    submissions: number;
    review_queue: number;
    published_addresses: number;
    import_jobs: number;
  };
  territories_by_province: Array<{ province_code: string; territory_count: number }>;
  review_breakdown: Array<{ review_status: string; count: number }>;
  publication_breakdown: Array<{ status: string; count: number }>;
};

async function getSummary(baseUrl: string): Promise<ReportingSummary> {
  const bootstrapHeaders = { Authorization: ['Bearer', 'admin-bootstrap-token'].join(' ') };
  try {
    const response = await fetch(`${baseUrl}/api/v1/reporting/summary`, {
      cache: 'no-store',
      headers: bootstrapHeaders,
    });
    if (!response.ok) throw new Error('summary failed');
    return (await response.json()) as ReportingSummary;
  } catch {
    return {
      totals: { territories: 0, submissions: 0, review_queue: 0, published_addresses: 0, import_jobs: 0 },
      territories_by_province: [],
      review_breakdown: [],
      publication_breakdown: [],
    };
  }
}

export default async function ReportsPage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const summary = await getSummary(apiBaseUrl);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Reporting dashboard"
      title="Operational Reporting Dashboard"
      subtitle="A single operational picture of territory readiness, field intake, verification queue load, publication progress, and intake activity."
    >
      <ReportingDashboardPanel
        summary={summary}
        apiBaseUrl={publicApiBaseUrl}
      />
    </SiteChrome>
  );
}
