export type GovernmentReportingSummary = {
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

export type GovernmentReadinessSummary = {
  readiness_status: string;
  passed_gates: number;
  total_gates: number;
  gates: Array<{ name: string; status: string; evidence: string; next_step: string }>;
};

const EMPTY_SUMMARY: GovernmentReportingSummary = {
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

async function getReportingSummary(baseUrl: string): Promise<GovernmentReportingSummary> {
  try {
    const response = await fetch(`${baseUrl}/api/v1/reporting/summary`, { cache: 'no-store' });
    if (!response.ok) return EMPTY_SUMMARY;
    return (await response.json()) as GovernmentReportingSummary;
  } catch {
    return EMPTY_SUMMARY;
  }
}

async function getReadinessSummary(baseUrl: string): Promise<GovernmentReadinessSummary | null> {
  try {
    const response = await fetch(`${baseUrl}/api/v1/pilot-readiness/summary`, { cache: 'no-store' });
    if (!response.ok) return null;
    return (await response.json()) as GovernmentReadinessSummary;
  } catch {
    return null;
  }
}

export async function getGovernmentWorkspaceData(baseUrl: string) {
  const [summary, readinessSummary] = await Promise.all([
    getReportingSummary(baseUrl),
    getReadinessSummary(baseUrl),
  ]);
  const attentionCount = summary.totals.review_queue
    + summary.totals.correction_queue
    + (summary.totals.geotag_queue ?? 0)
    + (readinessSummary ? Math.max(readinessSummary.total_gates - readinessSummary.passed_gates, 0) : 0);

  return { summary, readinessSummary, attentionCount };
}
