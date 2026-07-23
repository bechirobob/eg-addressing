import type { Metadata } from 'next';

import { GovernmentRegistryWorkbench } from '../../components/GovernmentRegistryWorkbench';
import { GovernmentWorkspaceShell } from '../../components/GovernmentWorkspaceShell';
import { SiteChrome } from '../../components/SiteChrome';
import { getGovernmentWorkspaceData } from '../../lib/governmentWorkspaceData';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'Address Registry — EG Addressing',
  description: 'Protected authoritative address registry workspace for the Republic of Equatorial Guinea.',
  robots: {
    index: false,
    follow: false,
  },
};

export default async function RegistryPage({
  searchParams,
}: {
  searchParams?: Promise<{ entity?: string }>;
}) {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const resolvedSearchParams = (await searchParams) ?? {};
  const { attentionCount } = await getGovernmentWorkspaceData(apiBaseUrl);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Government workspace"
      title="Address Registry"
      subtitle="Protected authoritative records workspace."
    >
      <GovernmentWorkspaceShell
        apiBaseUrl={publicApiBaseUrl}
        attentionCount={attentionCount}
        sectionLabel="Authoritative records"
        workspaceTitle="Address Registry"
        workContext={['National registry scope', 'Addresses · roads · buildings', 'Publication authority remains separate']}
      >
        <GovernmentRegistryWorkbench
          apiBaseUrl={publicApiBaseUrl}
          highlightEntityId={resolvedSearchParams.entity ?? null}
        />
      </GovernmentWorkspaceShell>
    </SiteChrome>
  );
}
