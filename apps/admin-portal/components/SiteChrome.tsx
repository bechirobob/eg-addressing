import type { ReactNode } from 'react';

import { LocalizedText } from './i18n';
import type { DictionaryKey } from './i18n';
import { RoleAwareChrome } from './RoleAwareChrome';
type ServiceMeta = {
  key: string;
  labelKey: DictionaryKey;
  highlightKeys: DictionaryKey[];
};

function serviceMetaForTitle(title: string): ServiceMeta {
  const normalized = title.toLowerCase();
  if (normalized.includes('national addressing platform')) {
    return { key: 'platform', labelKey: 'servicePlatformLabel', highlightKeys: ['servicePlatform1', 'servicePlatform2', 'servicePlatform3'] };
  }
  if (normalized.includes('signage') || normalized.includes('location review')) {
    return { key: 'signage', labelKey: 'serviceSignageLabel', highlightKeys: ['serviceSignage1', 'serviceSignage2', 'serviceSignage3'] };
  }
  if (normalized.includes('verification') || normalized.includes('evidence')) {
    return { key: 'verification', labelKey: 'serviceEvidenceLabel', highlightKeys: ['serviceEvidence1', 'serviceEvidence2', 'serviceEvidence3'] };
  }
  if (normalized.includes('check address code') || normalized.includes('code status') || normalized.includes('extract')) {
    return { key: 'code', labelKey: 'serviceCodeLabel', highlightKeys: ['serviceCode1', 'serviceCode2', 'serviceCode3'] };
  }
  if (normalized.includes('territory')) {
    return { key: 'territory', labelKey: 'serviceTerritoryLabel', highlightKeys: ['serviceTerritory1', 'serviceTerritory2', 'serviceTerritory3'] };
  }
  if (normalized.includes('registry') || normalized.includes('case files')) {
    return { key: 'registry', labelKey: 'serviceRegistryLabel', highlightKeys: ['serviceRegistry1', 'serviceRegistry2', 'serviceRegistry3'] };
  }
  if (normalized.includes('report')) {
    return { key: 'reports', labelKey: 'serviceReportsLabel', highlightKeys: ['serviceReports1', 'serviceReports2', 'serviceReports3'] };
  }
  if (normalized.includes('publication') || normalized.includes('intake')) {
    return { key: 'publication', labelKey: 'servicePublicationLabel', highlightKeys: ['servicePublication1', 'servicePublication2', 'servicePublication3'] };
  }
  if (normalized.includes('field')) {
    return { key: 'field', labelKey: 'serviceFieldLabel', highlightKeys: ['serviceField1', 'serviceField2', 'serviceField3'] };
  }
  if (normalized.includes('sign-in')) {
    return { key: 'access', labelKey: 'serviceAccessLabel', highlightKeys: ['serviceAccess1', 'serviceAccess2', 'serviceAccess3'] };
  }
  return { key: 'location', labelKey: 'serviceLocationLabel', highlightKeys: ['serviceLocation1', 'serviceLocation2', 'serviceLocation3'] };
}

type SiteChromeProps = {
  title: string;
  subtitle: string;
  eyebrow: string;
  titleKey?: DictionaryKey;
  subtitleKey?: DictionaryKey;
  eyebrowKey?: DictionaryKey;
  apiBaseUrl: string;
  children: ReactNode;
};

export function SiteChrome({ title, subtitle, eyebrow, titleKey, subtitleKey, eyebrowKey, apiBaseUrl, children }: SiteChromeProps) {
  const serviceMeta = serviceMetaForTitle(title);
  return (
    <main className={`page-shell page-shell-${serviceMeta.key}`}>
      <a className="skip-link" href="#main-content">Skip to main content</a>
      <div className="flag-ribbon" aria-hidden="true" />
      <header className="masthead masthead-reference" aria-label="National platform identity">
        <div className="masthead-topline">
          <div className="official-lockup">
            <div className="crest-frame" aria-hidden="true">
              <img src="/eg-coat-of-arms.svg" alt="Coat of arms of Equatorial Guinea" className="crest" />
            </div>
            <p className="kicker"><LocalizedText k="republic" /></p>
          </div>
        </div>
        <div className="masthead-content-grid">
          <div className="masthead-copy">
            <span className="eyebrow">{eyebrowKey ? <LocalizedText k={eyebrowKey} /> : eyebrow}</span>
            <div className="masthead-titles">
              <h1>{titleKey ? <LocalizedText k={titleKey} /> : title}</h1>
              <p className="masthead-subtitle">{subtitleKey ? <LocalizedText k={subtitleKey} /> : subtitle}</p>
            </div>
          </div>
          <div className="civic-hero-illustration" aria-hidden="true">
            <div className="map-slab">
              <span className="map-road map-road-a" />
              <span className="map-road map-road-b" />
              <span className="map-block map-block-a" />
              <span className="map-block map-block-b" />
              <span className="map-block map-block-c" />
              <span className="map-tree map-tree-a" />
              <span className="map-tree map-tree-b" />
              <span className="map-tree map-tree-c" />
              <span className="pin-shadow" />
              <span className="pin-stem" />
              <span className="pin-head" />
              <span className="pin-hole" />
              <span className="map-node map-node-a" />
              <span className="map-node map-node-b" />
              <span className="map-node map-node-c" />
            </div>
          </div>
        </div>
      </header>


      <RoleAwareChrome apiBaseUrl={apiBaseUrl}>
        <div id="main-content" className="desktop-main-content">
          {children}
        </div>
      </RoleAwareChrome>
    </main>
  );
}
