import type { Metadata } from 'next';

import { GovernmentOperatorHome } from '../../components/GovernmentOperatorHome';
import { GovernmentWorkspaceShell } from '../../components/GovernmentWorkspaceShell';
import { SiteChrome } from '../../components/SiteChrome';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'National Operations — EG Addressing',
  description: 'Protected national operations workspace for the Equatorial Guinea National Addressing Platform.',
  robots: {
    index: false,
    follow: false,
  },
};

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
};

type PilotReadinessSummary = {
  readiness_status: string;
  passed_gates: number;
  total_gates: number;
  gates: Array<{ name: string; status: string; evidence: string; next_step: string }>;
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

export default async function GovernmentWorkspacePage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const [summary, readinessSummary] = await Promise.all([
    getSummary(apiBaseUrl),
    getPilotReadiness(apiBaseUrl),
  ]);
  const attentionCount = summary.totals.review_queue
    + summary.totals.correction_queue
    + (summary.totals.geotag_queue ?? 0)
    + (readinessSummary ? Math.max(readinessSummary.total_gates - readinessSummary.passed_gates, 0) : 0);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Government workspace"
      title="National operations"
      subtitle="Protected operational workspace for authoritative addressing services."
    >
      <GovernmentWorkspaceShell apiBaseUrl={publicApiBaseUrl} attentionCount={attentionCount}>
        <GovernmentOperatorHome
          apiBaseUrl={publicApiBaseUrl}
          summary={summary}
          readinessSummary={readinessSummary}
        />
      </GovernmentWorkspaceShell>
    </SiteChrome>
  );
}
