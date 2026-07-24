import type { Metadata } from 'next';

import { GovernmentVerificationWorkbench } from '../../components/GovernmentVerificationWorkbench';
import { GovernmentWorkspaceShell } from '../../components/GovernmentWorkspaceShell';
import { getGovernmentWorkspaceData } from '../../lib/governmentWorkspaceData';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'Verification — EG Addressing',
  description: 'Protected evidence review and authoritative decision workspace for the Republic of Equatorial Guinea.',
  robots: {
    index: false,
    follow: false,
  },
};

export default async function VerifyPage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const { attentionCount } = await getGovernmentWorkspaceData(apiBaseUrl);

  return (
    <GovernmentWorkspaceShell
      apiBaseUrl={publicApiBaseUrl}
      attentionCount={attentionCount}
      sectionLabel="Evidence and authority"
      workspaceTitle="Verification"
      workContext={['National verification scope', 'Submitted and under-review cases', 'Approval remains separate from publication']}
    >
      <GovernmentVerificationWorkbench apiBaseUrl={publicApiBaseUrl} />
    </GovernmentWorkspaceShell>
  );
}
