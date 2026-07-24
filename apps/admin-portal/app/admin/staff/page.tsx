import type { Metadata } from 'next';

import { GovernmentAdministrationWorkbench } from '../../../components/GovernmentAdministrationWorkbench';
import { GovernmentWorkspaceShell } from '../../../components/GovernmentWorkspaceShell';
import { getGovernmentWorkspaceData } from '../../../lib/governmentWorkspaceData';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'Administration — EG Addressing',
  description: 'Protected personnel, role, account-state, and session-control workspace for the Equatorial Guinea National Addressing Platform.',
  robots: { index: false, follow: false },
};

export default async function AdminStaffPage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const { attentionCount } = await getGovernmentWorkspaceData(apiBaseUrl);

  return (
    <GovernmentWorkspaceShell
      apiBaseUrl={publicApiBaseUrl}
      attentionCount={attentionCount}
      sectionLabel="Platform control"
      workspaceTitle="Administration"
      workContext={['National personnel register', 'Administrator authority required', 'Least privilege and session revocation controls active']}
    >
      <GovernmentAdministrationWorkbench apiBaseUrl={publicApiBaseUrl} />
    </GovernmentWorkspaceShell>
  );
}
