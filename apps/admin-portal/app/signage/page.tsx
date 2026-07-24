import type { Metadata } from 'next';

import { GovernmentPublicationWorkbench } from '../../components/GovernmentPublicationWorkbench';
import { GovernmentWorkspaceShell } from '../../components/GovernmentWorkspaceShell';
import { getGovernmentWorkspaceData } from '../../lib/governmentWorkspaceData';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'Publication — EG Addressing',
  description: 'Protected review, release-hold, public publication, certificate, and signage workspace for the Equatorial Guinea National Addressing Platform.',
  robots: { index: false, follow: false },
};

export default async function SignagePage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const { attentionCount } = await getGovernmentWorkspaceData(apiBaseUrl);

  return (
    <GovernmentWorkspaceShell
      apiBaseUrl={publicApiBaseUrl}
      attentionCount={attentionCount}
      sectionLabel="Controlled official release"
      workspaceTitle="Publication"
      workContext={['National publication and signage scope', 'Preparation, approval, publication, and signage remain separate', 'Public release requires administrator authority and an active institutional flag']}
    >
      <GovernmentPublicationWorkbench apiBaseUrl={publicApiBaseUrl} />
    </GovernmentWorkspaceShell>
  );
}
