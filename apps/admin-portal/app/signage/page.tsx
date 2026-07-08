import { SiteChrome } from '../../components/SiteChrome';
import { SignageOperationsPanel } from '../../components/SignageOperationsPanel';

export const dynamic = 'force-dynamic';

export default function SignagePage() {
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Publication"
      eyebrowKey="signageEyebrow"
      title="Publication & signage"
      titleKey="signageTitle"
      subtitle="Review approved address records before public release and physical signage."
      subtitleKey="signageSubtitle"
    >
      <SignageOperationsPanel apiBaseUrl={publicApiBaseUrl} />
    </SiteChrome>
  );
}
