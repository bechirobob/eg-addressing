import { SiteChrome } from '../../../components/SiteChrome';
import { StaffAdminPanel } from '../../../components/StaffAdminPanel';

export const dynamic = 'force-dynamic';

export default function AdminStaffPage() {
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Admin area"
      title="Staff account control"
      subtitle="Create staff accounts, rotate credentials, sign users out everywhere, and deactivate access from the protected administration area."
    >
      <StaffAdminPanel apiBaseUrl={publicApiBaseUrl} />
    </SiteChrome>
  );
}
