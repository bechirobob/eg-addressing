import type { Metadata } from 'next';

import { GovernmentOperatorHome } from '../../components/GovernmentOperatorHome';
import { GovernmentWorkspaceShell } from '../../components/GovernmentWorkspaceShell';

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
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

  return (
    <GovernmentWorkspaceShell
      apiBaseUrl={publicApiBaseUrl}
      attentionCount={null}
      sectionLabel="Government workspace"
      workspaceTitle="National Operations"
    >
      <GovernmentOperatorHome
        apiBaseUrl={publicApiBaseUrl}
      />
    </GovernmentWorkspaceShell>
  );
}
