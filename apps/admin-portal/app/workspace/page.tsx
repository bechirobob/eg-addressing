import type { Metadata } from 'next';

import { GovernmentOperatorHome } from '../../components/GovernmentOperatorHome';
import { GovernmentWorkspaceShell } from '../../components/GovernmentWorkspaceShell';
import { SiteChrome } from '../../components/SiteChrome';
import { getGovernmentWorkspaceData } from '../../lib/governmentWorkspaceData';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'National Operations — EG Addressing',
  description: 'Protected national operations workspace for the Equatorial Guinea National Addressing Platform.',
  robots: {
    index: false,
    follow: false,
  },
};

export default async function GovernmentWorkspacePage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const { summary, readinessSummary, attentionCount } = await getGovernmentWorkspaceData(apiBaseUrl);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Government workspace"
      title="National operations"
      subtitle="Protected operational workspace for authoritative addressing services."
    >
      <GovernmentWorkspaceShell
        apiBaseUrl={publicApiBaseUrl}
        attentionCount={attentionCount}
        sectionLabel="Government workspace"
        workspaceTitle="National Operations"
      >
        <GovernmentOperatorHome
          apiBaseUrl={publicApiBaseUrl}
          summary={summary}
          readinessSummary={readinessSummary}
        />
      </GovernmentWorkspaceShell>
    </SiteChrome>
  );
}
