import type { Metadata } from 'next';

import { GovernmentPublicationWorkbench } from '../../components/GovernmentPublicationWorkbench';
import { GovernmentWorkspaceShell } from '../../components/GovernmentWorkspaceShell';
import { SiteChrome } from '../../components/SiteChrome';
import { getGovernmentWorkspaceData } from '../../lib/governmentWorkspaceData';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'Publication Outputs — EG Addressing',
  description: 'Administrator-only official publication packs, signage outputs, and controlled intake services.',
  robots: { index: false, follow: false },
};

export default async function ExportsPage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const { attentionCount } = await getGovernmentWorkspaceData(apiBaseUrl);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Government workspace"
      title="Publication Outputs"
      subtitle="Administrator-only official packs, signage exports, and controlled registry intake."
    >
      <GovernmentWorkspaceShell
        apiBaseUrl={publicApiBaseUrl}
        attentionCount={attentionCount}
        sectionLabel="Platform control"
        workspaceTitle="Publication Outputs"
        workContext={['Administrator-only output control', 'Official packs use published or explicitly selected protected records', 'Physical signage remains downstream of public release']}
      >
        <GovernmentPublicationWorkbench apiBaseUrl={publicApiBaseUrl} initialSection="outputs" />
      </GovernmentWorkspaceShell>
    </SiteChrome>
  );
}
