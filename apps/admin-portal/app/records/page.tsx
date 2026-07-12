import { AddressRecordSearchPanel } from '../../components/AddressRecordSearchPanel';
import { SiteChrome } from '../../components/SiteChrome';

export const dynamic = 'force-dynamic';

export default function RecordsPage() {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8100';
  return (
    <SiteChrome
      title="Address Case Files"
      titleKey="recordsTitle"
      subtitle="Search official government address records as structured case files with evidence, routing, and record history context. Evidence is grouped as a case file, not shown as raw rows."
      subtitleKey="recordsSubtitle"
      eyebrow="Official registry layer"
      eyebrowKey="recordsEyebrow"
      apiBaseUrl={apiBaseUrl}
    >
      <AddressRecordSearchPanel apiBaseUrl={apiBaseUrl} />
    </SiteChrome>
  );
}
