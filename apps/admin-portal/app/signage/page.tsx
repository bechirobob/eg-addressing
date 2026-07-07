import { SiteChrome } from '../../components/SiteChrome';
import { SignageOperationsPanel } from '../../components/SignageOperationsPanel';

export const dynamic = 'force-dynamic';

export default function SignagePage() {
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Review desk"
      eyebrowKey="signageEyebrow"
      title="Location Review and Registry Readiness"
      titleKey="signageTitle"
      subtitle="Check new location requests, route field confirmation, and approve internal address case files. Physical signage waits for full project approval."
      subtitleKey="signageSubtitle"
    >
      <SignageOperationsPanel apiBaseUrl={publicApiBaseUrl} />
    </SiteChrome>
  );
}
