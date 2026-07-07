import { SiteChrome } from '../../components/SiteChrome';
import { TrackingLookupPanel } from '../../components/TrackingLookupPanel';

export const dynamic = 'force-dynamic';

export default function TrackingPage() {
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Citizen tracking"
      eyebrowKey="trackEyebrow"
      title="Track a Location Request"
      titleKey="trackTitle"
      subtitle="Check the public-safe status of a submitted location request without exposing private identity details."
      subtitleKey="trackSubtitle"
    >
      <TrackingLookupPanel apiBaseUrl={publicApiBaseUrl} />
    </SiteChrome>
  );
}
