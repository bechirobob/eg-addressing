'use client';

import Link from 'next/link';
import { useState } from 'react';
import { GovernmentIcon, type GovernmentIconName } from './GovernmentIcon';
import { isRouteAccessible, type OperatorRole } from './site-data';
import { resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';
import { useOperationsSummary } from './useOperationsSummary';
import styles from './GovernmentOperatorHome.module.css';

function firstAccessibleRoute(role: OperatorRole, routes: string[]) {
  return routes.find((route) => isRouteAccessible(route, role));
}

const modules: { href: string; label: string; description: string; icon: GovernmentIconName }[] = [
  { href: '/registry', label: 'Registry', description: 'Authoritative address records', icon: 'registry' },
  { href: '/field', label: 'Field operations', description: 'Assignments and field evidence', icon: 'field' },
  { href: '/territories', label: 'Mapping', description: 'Territories and administrative scope', icon: 'mapping' },
  { href: '/signage', label: 'Publication', description: 'Signage, proofs and controlled release', icon: 'publication' },
  { href: '/reports', label: 'Analytics', description: 'Workload, progress and readiness', icon: 'analytics' },
  { href: '/admin/staff', label: 'Administration', description: 'Personnel, roles and access', icon: 'administration' },
];

export function GovernmentOperatorHome({ apiBaseUrl }: { apiBaseUrl: string }) {
  const baseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(baseUrl);
  const role: OperatorRole = sessionStatus === 'ready' && sessionUser ? sessionUser.role : 'guest';
  const { summary, readiness, loading, updatedAt, refresh } = useOperationsSummary(baseUrl, token, sessionStatus, sessionUser?.id);
  const [view, setView] = useState<'overview' | 'queues' | 'readiness'>('overview');
  const totals = summary?.totals;
  const display = (value: number | undefined) => value === undefined ? '—' : value.toLocaleString();
  const queues: { label: string; description: string; count?: number; icon: GovernmentIconName; routes: string[] }[] = [
    { label: 'Verification queue', description: 'Submissions awaiting evidence review and a decision.', count: totals?.review_queue, icon: 'verification', routes: ['/verify', '/registry', '/reports'] },
    { label: 'Citizen review queue', description: 'Citizen location submissions awaiting review.', count: totals?.geotag_queue, icon: 'field', routes: ['/signage', '/reports'] },
    { label: 'Correction queue', description: 'Reported address corrections awaiting resolution.', count: totals?.correction_queue, icon: 'corrections', routes: ['/reports'] },
  ];
  const next = queues.find((queue) => (queue.count ?? 0) > 0);
  const nextHref = next && firstAccessibleRoute(role, next.routes);
  const overviewGates = readiness?.gates.slice().sort((a, b) => Number(a.status === 'passed') - Number(b.status === 'passed')).slice(0, 4);
  const gateAttention = readiness ? readiness.total_gates - readiness.passed_gates : undefined;

  return (
    <div className={`government-home ${styles.home}`}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>National operations / Daily overview</p>
          <h1>Today’s addressing work</h1>
          <p className={styles.intro}>Review demand, resolve exceptions and keep national delivery moving.</p>
        </div>
        <div className={styles.tools}>
          <span role="status">{loading ? 'Loading current summaries…' : updatedAt ? `Updated ${updatedAt}` : 'Summaries unavailable'}</span>
          <button type="button" onClick={refresh} disabled={loading}>Refresh summaries</button>
        </div>
      </header>

      <dl className={styles.metrics} aria-label="Current operational summary" aria-busy={loading}>
        {[
          ['Submitted records', totals?.submissions, 'Current reporting scope', 'records'],
          ['Published addresses', totals?.published_addresses, 'Published in the platform', 'published'],
          ['Territories', totals?.territories, 'Represented in the registry', 'territory'],
        ].map(([label, count, hint, icon]) => (
          <div key={String(label)}><dt><GovernmentIcon name={icon as GovernmentIconName} />{label}</dt><dd>{display(count as number | undefined)}</dd><small>{hint}</small></div>
        ))}
        <div><dt><GovernmentIcon name="readiness" />Pilot readiness</dt><dd>{readiness ? <>{readiness.passed_gates}<span> / {readiness.total_gates}</span></> : '—'}</dd><small>Gates passed · not release authorization</small></div>
      </dl>

      {!loading && (!summary || !readiness) && <div className={styles.notice} role="status"><GovernmentIcon name="alert" /><p><strong>{!summary ? 'Workload summary unavailable.' : 'Readiness summary unavailable.'}</strong> Missing values are shown as a dash. Refresh to try again; confirm your session if the problem continues.</p></div>}

      <nav className={styles.views} aria-label="Operations view">
        {(['overview', 'queues', 'readiness'] as const).map((item) => <button type="button" key={item} aria-pressed={view === item} onClick={() => setView(item)}>{item === 'overview' ? 'Overview' : item === 'queues' ? 'Work queues' : 'Pilot readiness'}</button>)}
        <span>Current reporting scope</span>
      </nav>

      <div className={`${styles.workspace} ${view !== 'overview' ? styles.single : ''}`}>
        {view !== 'readiness' && <section aria-labelledby="operations-queues-title" className={styles.panel}>
          <div className={styles.sectionHeading}><div><p className={styles.eyebrow}>Operational demand</p><h2 id="operations-queues-title">Work requiring review</h2></div><GovernmentIcon name="operations" /></div>
          <p className={styles.caption}>Values are read from current platform summaries. Queues are shown separately and may overlap.</p>
          <ul className={styles.queues}>
            {queues.map((queue) => {
              const href = firstAccessibleRoute(role, queue.routes);
              return <li key={queue.label}>
                <GovernmentIcon name={queue.icon} />
                <div className={styles.queueText}><h3>{queue.label}</h3><p>{queue.description}</p><span className={(queue.count ?? 0) > 0 ? styles.attention : styles.neutral}>{queue.count === undefined ? loading ? 'Loading' : 'Unavailable' : queue.count > 0 ? 'Awaiting review' : 'No pending items'}</span></div>
                <strong className={styles.count} aria-label={`${queue.label}: ${queue.count === undefined ? 'unavailable' : queue.count}`}>{display(queue.count)}</strong>
                {href && <Link className={styles.rowLink} href={href}>{href === '/reports' ? 'View report' : 'Open workspace'}<span className={styles.srOnly}> for {queue.label}</span><span aria-hidden="true"> ↗</span></Link>}
              </li>;
            })}
          </ul>
          <div className={styles.nextAction}>
            <div><strong>{next ? 'Start with a queue that needs review' : loading ? 'Checking current workload' : !summary ? 'Confirm workload before prioritizing' : 'Continue in your workspace'}</strong><p>Routine processing remains automated; operators handle exceptions, evidence, and official authority.</p></div>
            {next && nextHref && <Link href={nextHref}>{nextHref === '/reports' ? 'Open reporting' : `Open ${next.label.toLowerCase()}`}<span aria-hidden="true"> →</span></Link>}
          </div>
        </section>}

        {view !== 'queues' && <section aria-labelledby="operations-readiness-title" className={styles.panel}>
          <div className={styles.sectionHeading}><div><p className={styles.eyebrow}>Controlled pilot</p><h2 id="operations-readiness-title">Readiness checks</h2></div><GovernmentIcon name="readiness" /></div>
          <p className={styles.caption}>Readiness checks inform review. Official release still requires institutional authority.</p>
          {readiness ? <>
            <div className={styles.readinessSummary}><strong>{readiness.passed_gates} of {readiness.total_gates} gates passed</strong><span>{gateAttention === 0 ? 'All reported gates passed' : `${gateAttention} require attention`}</span></div>
            <progress aria-label="Pilot readiness gates passed" value={readiness.passed_gates} max={readiness.total_gates || 1} />
            <ul className={styles.gates}>{(view === 'overview' ? overviewGates ?? [] : readiness.gates).map((gate, index) => <li key={`${gate.name}-${index}`}><span className={gate.status === 'passed' ? styles.passed : styles.attention}>{gate.status === 'passed' ? 'Passed' : gate.status.replaceAll('_', ' ').replaceAll('-', ' ')}</span><h3>{gate.name}</h3><p>{gate.evidence}</p>{view === 'readiness' && <p><strong>Next step: </strong>{gate.next_step}</p>}</li>)}</ul>
            {view === 'overview' && readiness.gates.length > 4 && <button className={styles.textButton} type="button" onClick={() => setView('readiness')}>View all {readiness.gates.length} checks →</button>}
          </> : <div className={styles.empty}><GovernmentIcon name="readiness" /><strong>{loading ? 'Loading readiness checks' : 'Readiness summary unavailable'}</strong><p>{loading ? 'Retrieving the current pilot summary.' : 'Retry using Refresh summaries. Missing evidence does not mean a gate has passed.'}</p></div>}
        </section>}
      </div>

      <section className={styles.directory} aria-labelledby="operations-directory-title">
        <div className={styles.sectionHeading}><div><p className={styles.eyebrow}>Authorized workspaces</p><h2 id="operations-directory-title">Continue by responsibility</h2></div><p>Only destinations permitted by the active role are shown</p></div>
        <div className={styles.modules}>{modules.filter((item) => isRouteAccessible(item.href, role)).map((item) => <Link href={item.href} key={item.href}><GovernmentIcon name={item.icon} /><span><strong>{item.label}</strong><small>{item.description}</small></span><span aria-hidden="true">↗</span></Link>)}</div>
      </section>
    </div>
  );
}
