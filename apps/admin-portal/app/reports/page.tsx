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
    public_corrections: number;
    correction_queue: number;
    citizen_geotags?: number;
    geotag_queue?: number;
  };
  territories_by_province: Array<{ province_code: string; territory_count: number }>;
  review_breakdown: Array<{ review_status: string; count: number }>;
  publication_breakdown: Array<{ status: string; count: number }>;
  correction_breakdown: Array<{ status: string; count: number }>;
  geotag_breakdown?: Array<{ status: string; count: number }>;
};

type PilotReadinessSummary = {
  readiness_status: string;
  passed_gates: number;
  total_gates: number;
  gates: Array<{ name: string; status: string; evidence: string; next_step: string }>;
  boundaries: string[];
};

const EMPTY_SUMMARY: ReportingSummary = {
  totals: {
    territories: 0,
    submissions: 0,
    review_queue: 0,
    published_addresses: 0,
    import_jobs: 0,
    public_corrections: 0,
    correction_queue: 0,
    citizen_geotags: 0,
    geotag_queue: 0,
  },
  territories_by_province: [],
  review_breakdown: [],
  publication_breakdown: [],
  correction_breakdown: [],
  geotag_breakdown: [],
};

async function getSummary(baseUrl: string): Promise<ReportingSummary> {
  try {
    const response = await fetch(`${baseUrl}/api/v1/reporting/summary`, { cache: 'no-store' });
    if (!response.ok) return EMPTY_SUMMARY;
    return (await response.json()) as ReportingSummary;
  } catch {
    return EMPTY_SUMMARY;
  }
}

async function getPilotReadiness(baseUrl: string): Promise<PilotReadinessSummary | null> {
  try {
    const response = await fetch(`${baseUrl}/api/v1/pilot-readiness/summary`, { cache: 'no-store' });
    if (!response.ok) return null;
    return (await response.json()) as PilotReadinessSummary;
  } catch {
    return null;
  }
}

export default async function ReportsPage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const [summary, readinessSummary] = await Promise.all([
    getSummary(apiBaseUrl),
    getPilotReadiness(apiBaseUrl),
  ]);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Reporting dashboard"
      eyebrowKey="reportsEyebrow"
      title="Operational Reporting Dashboard"
      titleKey="reportsTitle"
      subtitle="A single operational picture of territory readiness, field intake, verification queue load, publication progress, and intake activity."
      subtitleKey="reportsSubtitle"
    >
      <ReportingDashboardPanel
        summary={summary}
        readinessSummary={readinessSummary}
        apiBaseUrl={publicApiBaseUrl}
      />
    </SiteChrome>
  );
}
