import { SiteChrome } from '../../../components/SiteChrome';
import { PublicCodeLookupPanel } from '../../../components/PublicCodeLookupPanel';

export const dynamic = 'force-dynamic';

type PublicCodePageProps = {
  params: Promise<{ code: string }>;
};

export default async function PublicCodePage({ params }: PublicCodePageProps) {
  const { code } = await params;
  const decodedCode = decodeURIComponent(code);
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      title="Check Address Code"
      titleKey="issueTitle"
      eyebrow="Public address service"
      eyebrowKey="publicAddressService"
      subtitle="Check whether an address code is valid, officially published, or still waiting for review."
      subtitleKey="codeSubtitle"
    >
      <PublicCodeLookupPanel apiBaseUrl={publicApiBaseUrl} code={decodedCode} />
    </SiteChrome>
  );
}
