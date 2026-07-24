import type { Metadata } from 'next';

import { GovernmentFieldOperationsWorkbench } from '../../components/GovernmentFieldOperationsWorkbench';
import { GovernmentWorkspaceShell } from '../../components/GovernmentWorkspaceShell';
import { SiteChrome } from '../../components/SiteChrome';
import { getGovernmentWorkspaceData } from '../../lib/governmentWorkspaceData';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'Field Operations — EG Addressing',
  description: 'Protected assignment, GNSS evidence, and field synchronization workspace for the Equatorial Guinea National Addressing Platform.',
  robots: { index: false, follow: false },
};

export default async function FieldPage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const { attentionCount } = await getGovernmentWorkspaceData(apiBaseUrl);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Government workspace"
      title="Field operations"
      subtitle="Protected assignment, location inspection, evidence capture, and synchronization services."
    >
      <GovernmentWorkspaceShell
        apiBaseUrl={publicApiBaseUrl}
        attentionCount={attentionCount}
        sectionLabel="Territorial operations"
        workspaceTitle="Field Operations"
        workContext={['National and territorial field scope', 'GNSS evidence and device synchronization', 'Verification owns the next authoritative decision']}
      >
        <GovernmentFieldOperationsWorkbench apiBaseUrl={publicApiBaseUrl} />
      </GovernmentWorkspaceShell>
    </SiteChrome>
  );
}
