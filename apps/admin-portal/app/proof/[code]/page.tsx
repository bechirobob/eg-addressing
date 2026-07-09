import { SiteChrome } from '../../../components/SiteChrome';
import { PublicProofPanel } from '../../../components/PublicProofPanel';

export const dynamic = 'force-dynamic';

type PublicProofPageProps = {
  params: Promise<{ code: string }>;
};

export default async function PublicProofPage({ params }: PublicProofPageProps) {
  const { code } = await params;
  const decodedCode = decodeURIComponent(code);
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      title="Public Address Proof"
      titleKey="issueTitle"
      eyebrow="Public address service"
      eyebrowKey="publicAddressService"
      subtitle="Print or save a public-safe address-code proof with QR verification."
      subtitleKey="codeSubtitle"
      skipSessionLookup
    >
      <PublicProofPanel apiBaseUrl={publicApiBaseUrl} code={decodedCode} />
    </SiteChrome>
  );
}
