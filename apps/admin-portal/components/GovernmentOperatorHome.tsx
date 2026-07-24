'use client';

import Link from 'next/link';
import { useMemo } from 'react';

import { GovernmentIcon, type GovernmentIconName } from './GovernmentIcon';
import { isRouteAccessible, type OperatorRole } from './site-data';
import { resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

type ReportingSummary = {
  totals: {
    territories: number;
    submissions: number;
    review_queue: number;
    published_addresses: number;
    import_jobs: number;
    public_corrections: number;
    correction_queue: number;
    citizen_geotags?: number;
    geotag_queue?: number;
  };
};

type PilotReadinessSummary = {
  readiness_status: string;
  passed_gates: number;
  total_gates: number;
  gates: Array<{ name: string; status: string; evidence: string; next_step: string }>;
};

type GovernmentOperatorHomeProps = {
  apiBaseUrl: string;
  summary: ReportingSummary;
  readinessSummary: PilotReadinessSummary | null;
};

type WorkArea = {
  label: string;
  description: string;
  count: number | string;
  state: 'normal' | 'attention' | 'ready';
  icon: GovernmentIconName;
  candidateRoutes: string[];
  action: string;
};

function firstAccessibleRoute(role: OperatorRole, routes: string[]) {
  return routes.find((route) => isRouteAccessible(route, role)) ?? '/reports';
}

function stateLabel(state: WorkArea['state']) {
  if (state === 'attention') return 'Requires attention';
  if (state === 'ready') return 'On track';
  return 'Operational';
}

export function GovernmentOperatorHome({ apiBaseUrl, summary, readinessSummary }: GovernmentOperatorHomeProps) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const role: OperatorRole = sessionStatus === 'ready' && sessionUser ? sessionUser.role : 'guest';

  const readinessAttention = readinessSummary
    ? Math.max(readinessSummary.total_gates - readinessSummary.passed_gates, 0)
    : 0;
  const fieldQueue = summary.totals.geotag_queue ?? 0;
  const immediateAttention = summary.totals.review_queue + summary.totals.correction_queue + fieldQueue + readinessAttention;

  const workAreas = useMemo<WorkArea[]>(() => [
    {
      label: 'Verification queue',
      description: 'Submissions awaiting evidence review or an authoritative decision.',
      count: summary.totals.review_queue,
      state: summary.totals.review_queue > 0 ? 'attention' : 'ready',
      icon: 'verification',
      candidateRoutes: ['/verify', '/registry', '/reports'],
      action: 'Open verification work',
    },
    {
      label: 'Field follow-up',
      description: 'Citizen captures requiring field confirmation, correction, or recapture.',
      count: fieldQueue,
      state: fieldQueue > 0 ? 'attention' : 'ready',
      icon: 'field',
      candidateRoutes: ['/field', '/reports'],
      action: 'Open field operations',
    },
    {
      label: 'Correction queue',
      description: 'Address records awaiting correction review and controlled resolution.',
      count: summary.totals.correction_queue,
      state: summary.totals.correction_queue > 0 ? 'attention' : 'ready',
      icon: 'corrections',
      candidateRoutes: ['/registry', '/reports'],
      action: 'Review corrections',
    },
    {
      label: 'Publication readiness',
      description: 'Institutional gates that must pass before official public release.',
      count: readinessSummary ? `${readinessSummary.passed_gates}/${readinessSummary.total_gates}` : 'Unavailable',
      state: readinessAttention > 0 ? 'attention' : readinessSummary ? 'ready' : 'normal',
      icon: 'readiness',
      candidateRoutes: ['/reports', '/admin/staff'],
      action: 'Review readiness',
    },
  ], [fieldQueue, readinessAttention, readinessSummary, summary.totals.correction_queue, summary.totals.review_queue]);

  const moduleActions = [
    {
      href: '/registry',
      label: 'Registry',
      description: 'Find and manage authoritative address records.',
      icon: 'registry' as GovernmentIconName,
    },
    {
      href: '/field',
      label: 'Field Operations',
      description: 'Assign fieldwork and review synchronized evidence.',
      icon: 'field' as GovernmentIconName,
    },
    {
      href: '/territories',
      label: 'Mapping',
      description: 'Review territories and administrative scope.',
      icon: 'mapping' as GovernmentIconName,
    },
    {
      href: '/signage',
      label: 'Publication',
      description: 'Control signage, proofs, and official release.',
      icon: 'publication' as GovernmentIconName,
    },
    {
      href: '/reports',
      label: 'Analytics',
      description: 'Review national workload, progress, and readiness.',
      icon: 'analytics' as GovernmentIconName,
    },
    {
      href: '/admin/staff',
      label: 'Administration',
      description: 'Manage personnel, roles, scope, and access.',
      icon: 'administration' as GovernmentIconName,
    },
  ].filter((item) => isRouteAccessible(item.href, role));

  const nextWorkArea = workAreas.find((area) => area.state === 'attention') ?? workAreas[0];
  const nextHref = firstAccessibleRoute(role, nextWorkArea.candidateRoutes);

  return (
    <div className="government-home">
      <header className="government-home-header">
        <div>
          <p className="government-home-eyebrow">National operations</p>
          <h1>Today’s addressing work</h1>
          <p>
            Begin with the work that requires a decision. Routine processing remains automated; operators handle exceptions, evidence, and official authority.
          </p>
        </div>
        <div className="government-home-primary-action">
          <span>Recommended next action</span>
          <Link href={nextHref}>
            <GovernmentIcon name={nextWorkArea.icon} />
            <strong>{nextWorkArea.action}</strong>
          </Link>
        </div>
      </header>

      <dl className="government-home-summary" aria-label="Current operational summary">
        <div>
          <dt>Requires attention</dt>
          <dd>{immediateAttention}</dd>
          <span>Across active operational queues</span>
        </div>
        <div>
          <dt>Submitted records</dt>
          <dd>{summary.totals.submissions}</dd>
          <span>Current reporting scope</span>
        </div>
        <div>
          <dt>Published addresses</dt>
          <dd>{summary.totals.published_addresses}</dd>
          <span>Official public records</span>
        </div>
        <div>
          <dt>Territories</dt>
          <dd>{summary.totals.territories}</dd>
          <span>Represented in the registry</span>
        </div>
        <div>
          <dt>Readiness gates</dt>
          <dd>{readinessSummary ? `${readinessSummary.passed_gates}/${readinessSummary.total_gates}` : '—'}</dd>
          <span>{readinessSummary?.readiness_status ?? 'Status unavailable'}</span>
        </div>
      </dl>

      <div className="government-home-grid">
        <section className="government-work-table-section" aria-labelledby="government-work-table-title">
          <div className="government-section-heading">
            <div>
              <p>Operational demand</p>
              <h2 id="government-work-table-title">Work requiring review</h2>
            </div>
            <span>Values are read from current platform summaries</span>
          </div>

          <div className="government-work-table" role="table" aria-label="Operational work areas">
            <div className="government-work-table-header" role="row">
              <span role="columnheader">Work area</span>
              <span role="columnheader">Current demand</span>
              <span role="columnheader">State</span>
              <span role="columnheader">Next action</span>
            </div>
            {workAreas.map((area) => {
              const href = firstAccessibleRoute(role, area.candidateRoutes);
              return (
                <div className="government-work-table-row" role="row" key={area.label}>
                  <div className="government-work-area" role="cell">
                    <GovernmentIcon name={area.icon} />
                    <span>
                      <strong>{area.label}</strong>
                      <small>{area.description}</small>
                    </span>
                  </div>
                  <strong className="government-work-count" role="cell">{area.count}</strong>
                  <span className={`government-work-state ${area.state}`} role="cell">{stateLabel(area.state)}</span>
                  <Link href={href} role="cell">{area.action}</Link>
                </div>
              );
            })}
          </div>
        </section>

        <aside className="government-readiness-section" aria-labelledby="government-readiness-title">
          <div className="government-section-heading">
            <div>
              <p>National delivery</p>
              <h2 id="government-readiness-title">Readiness and authority</h2>
            </div>
          </div>

          {readinessSummary ? (
            <ul className="government-readiness-list">
              {readinessSummary.gates.slice(0, 5).map((gate) => (
                <li key={gate.name}>
                  <span className={`government-readiness-marker ${gate.status}`} aria-hidden="true" />
                  <div>
                    <strong>{gate.name}</strong>
                    <span>{gate.evidence}</span>
                    <small>{gate.next_step}</small>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="government-empty-state">
              <GovernmentIcon name="readiness" />
              <strong>Readiness summary unavailable</strong>
              <span>The operational workspace remains available. Review the reporting service before an official release decision.</span>
            </div>
          )}
        </aside>
      </div>

      <section className="government-module-section" aria-labelledby="government-module-title">
        <div className="government-section-heading">
          <div>
            <p>Authorized workspaces</p>
            <h2 id="government-module-title">Continue by responsibility</h2>
          </div>
          <span>Only destinations permitted by the active role are shown</span>
        </div>
        <div className="government-module-list">
          {moduleActions.map((item) => (
            <Link href={item.href} key={item.href}>
              <GovernmentIcon name={item.icon} />
              <span>
                <strong>{item.label}</strong>
                <small>{item.description}</small>
              </span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
