import { SiteChrome } from '../../components/SiteChrome';

export const dynamic = 'force-dynamic';

const escalationContacts = [
  {
    role: 'Incident owner / first point of contact',
    name: 'Benji — BeCoreOps',
    status: 'Primary contact for controlled pilot coordination, incident decisions, and ministry-facing handoff.',
  },
  {
    role: 'Technical escalation',
    name: 'BeCoreOps technical desk',
    status: 'Handles server health, access control, backups, deployment verification, and evidence collection.',
  },
  {
    role: 'Government decision-maker',
    name: 'Pending ministry appointment',
    status: 'Required before any pilot record can be treated as official national publication authority.',
  },
] as const;

const dailyChecks = [
  'Open the public site through HTTPS and confirm the staging banner is visible.',
  'Check API health returns status ok and environment staging.',
  'Confirm raw service ports remain closed from the public internet.',
  'Review public geotag and correction queues for test rows or urgent citizen follow-up.',
] as const;

const incidentSteps = [
  'Pause publication, export, signage, or certificate actions until the issue is understood.',
  'Notify Benji first, then technical escalation if the issue affects access, privacy, evidence, or uptime.',
  'Preserve logs, request references, screenshots, and incident notes before making destructive changes.',
  'Rotate credentials and revoke sessions if account exposure is suspected.',
  'Record the resolution and verification evidence before reopening the pilot workflow.',
] as const;

const protectedDataRules = [
  'Do not share passwords, session cookies, backup keys, database URLs, or private object-storage links in chat or public documents.',
  'Do not publish full D.I.P. values or private citizen identity data on public proof pages.',
  'Treat the current environment as controlled staging until ministry appointment and production authorization are complete.',
  'Use staging reference language for demo records; do not imply final government publication.',
] as const;

export default function OperationsRunbookPage() {
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Pilot operations"
      title="Operations Runbook"
      subtitle="Controlled staging procedures for the National Addressing Platform: ownership, incident handling, privacy boundaries, backups, and publication authority."
      skipSessionLookup
    >
      <section className="service-start-page desktop-home-start" aria-labelledby="runbook-heading">
        <div className="desktop-home-intro">
          <div className="desktop-home-copy">
            <p className="section-label">Operational ownership</p>
            <h2 id="runbook-heading">Pilot operations and escalation</h2>
            <p>
              This runbook keeps the controlled pilot operationally safe. It does not convert staging data into official production records, and it does not expose private credentials or backup keys.
            </p>
            <div className="service-start-actions" aria-label="Runbook primary actions">
              <a className="button button-primary service-start-primary" href="/api/v1/health">
                Check API health
              </a>
              <p className="service-start-secondary-actions public-task-copy">
                <a className="inline-action-link" href="/reports">Review reports</a>
                <span aria-hidden="true"> · </span>
                <a className="inline-action-link" href="/login">Staff sign-in</a>
              </p>
            </div>
          </div>
          <aside className="desktop-before-start" aria-labelledby="runbook-status-heading">
            <p className="section-label">Current status</p>
            <h2 id="runbook-status-heading">Controlled staging only</h2>
            <ul>
              <li>Public services remain available through HTTPS.</li>
              <li>Internal services remain private and are not directly exposed to the public internet.</li>
              <li>Ministry appointment is still pending.</li>
            </ul>
          </aside>
        </div>

        <section className="service-start-workflow" aria-labelledby="contacts-heading">
          <p className="section-label">Escalation chain</p>
          <h2 id="contacts-heading">Named contacts and decision authority</h2>
          <ol>
            {escalationContacts.map((contact, index) => (
              <li key={contact.role}>
                <span>{index + 1}</span>
                <strong>{contact.name}</strong>
                <small>{contact.role}. {contact.status}</small>
              </li>
            ))}
          </ol>
        </section>

        <div className="desktop-home-intro" aria-label="Operations runbook procedures">
          <article className="desktop-before-start">
            <p className="section-label">Daily checks</p>
            <h2>Before a pilot review</h2>
            <ul>
              {dailyChecks.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>

          <article className="desktop-before-start">
            <p className="section-label">Incident response</p>
            <h2>If something goes wrong</h2>
            <ul>
              {incidentSteps.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
        </div>

        <section className="service-start-workflow" aria-labelledby="data-boundaries-heading">
          <p className="section-label">Privacy and publication boundaries</p>
          <h2 id="data-boundaries-heading">What must stay protected</h2>
          <ol>
            {protectedDataRules.map((rule, index) => (
              <li key={rule}>
                <span>{index + 1}</span>
                {rule}
              </li>
            ))}
          </ol>
        </section>

        <section className="service-start-staff" aria-labelledby="runbook-close-heading">
          <div>
            <p className="section-label">Publication authority</p>
            <h2 id="runbook-close-heading">Government approval remains pending</h2>
            <p>
              The platform is ready for controlled pilot review only. Final national production authority requires the pending ministry appointment and written approval path.
            </p>
          </div>
          <a className="button button-secondary" href="/">Return home</a>
        </section>
      </section>
    </SiteChrome>
  );
}
