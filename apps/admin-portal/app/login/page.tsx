import { SiteChrome } from '../../components/SiteChrome';
import { LoginPanel } from '../../components/LoginPanel';

export const dynamic = 'force-dynamic';

export default function LoginPage() {
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Staff services"
      eyebrowKey="loginEyebrow"
      title="Staff sign-in"
      titleKey="loginTitle"
      subtitle="Sign in to perform protected registry actions."
      subtitleKey="loginSubtitle"
    >
      <LoginPanel apiBaseUrl={publicApiBaseUrl} />
    </SiteChrome>
  );
}
