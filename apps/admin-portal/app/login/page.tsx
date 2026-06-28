import { SiteChrome } from '../../components/SiteChrome';
import { LoginPanel } from '../../components/LoginPanel';

export const dynamic = 'force-dynamic';

export default function LoginPage() {
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Access control"
      title="Administrative Sign-In"
      subtitle="Role-aware access point for protected registry actions, audit review, and administrative write operations."
    >
      <LoginPanel apiBaseUrl={publicApiBaseUrl} />
    </SiteChrome>
  );
}
