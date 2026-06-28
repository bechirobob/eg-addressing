import type { ReactNode } from 'react';

import { RoleAwareChrome } from './RoleAwareChrome';
import { statusHighlights } from './site-data';

type SiteChromeProps = {
  title: string;
  subtitle: string;
  eyebrow: string;
  apiBaseUrl: string;
  children: ReactNode;
};

export function SiteChrome({ title, subtitle, eyebrow, apiBaseUrl, children }: SiteChromeProps) {
  return (
    <main className="page-shell">
      <div className="flag-ribbon" aria-hidden="true" />

      <header className="masthead" aria-label="National platform identity">
        <div className="masthead-copy">
          <p className="kicker">Republic of Equatorial Guinea</p>
          <div className="masthead-titles">
            <h1>{title}</h1>
            <p className="masthead-subtitle">{subtitle}</p>
          </div>
        </div>
        <div className="crest-frame" aria-hidden="true">
          <img src="/eg-coat-of-arms.svg" alt="Coat of arms of Equatorial Guinea" className="crest" />
        </div>
      </header>

      <section className="hero-card compact-hero">
        <div className="hero-copy-block">
          <span className="eyebrow">{eyebrow}</span>
          <div className="hero-inline-grid">
            <div>
              <h2>{title}</h2>
              <p className="hero-copy">{subtitle}</p>
            </div>
            <ul className="highlight-list">
              {statusHighlights.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <RoleAwareChrome apiBaseUrl={apiBaseUrl}>{children}</RoleAwareChrome>
    </main>
  );
}
