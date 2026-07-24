import type { Metadata } from 'next';
import { notFound } from 'next/navigation';

import styles from './page.module.css';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'BGEDS Design Lab — EG Addressing',
  description: 'Non-production staff workspace foundation for the EG Addressing platform redesign.',
  robots: {
    index: false,
    follow: false,
  },
};

const navigation = [
  ['HM', 'Home', ''],
  ['OP', 'Operations', '23'],
  ['RG', 'Registry', ''],
  ['MP', 'Mapping', ''],
  ['FO', 'Field Operations', '18'],
  ['PB', 'Publication', '4'],
  ['AG', 'Agencies', '2'],
  ['AN', 'Analytics', ''],
];

const queueItems = [
  {
    title: 'Malabo II address verification',
    code: 'EG-BN-MB2-2026-008421',
    meta: 'Submitted 37 minutes ago · Editor queue',
    priority: 'Urgent',
    active: true,
  },
  {
    title: 'Bata road-name correction',
    code: 'EG-LI-BT-2026-003118',
    meta: 'Submitted 1 hour ago · Registry correction',
    priority: '',
    active: false,
  },
  {
    title: 'Luba field recapture',
    code: 'EG-BS-LB-2026-001904',
    meta: 'GPS evidence below threshold · Field team 04',
    priority: 'Attention',
    active: false,
  },
  {
    title: 'Mongomo duplicate review',
    code: 'EG-WN-MG-2026-000776',
    meta: 'Two probable matches · Review required',
    priority: '',
    active: false,
  },
];

function Status({ children, kind = 'default' }: { children: React.ReactNode; kind?: 'default' | 'warning' | 'danger' | 'success' }) {
  const className = kind === 'warning'
    ? styles.statusWarning
    : kind === 'danger'
      ? styles.statusDanger
      : kind === 'success'
        ? styles.statusSuccess
        : styles.status;

  return <span className={className}>{children}</span>;
}

export default function GovernmentDesignLabPage() {
  if (process.env.NEXT_PUBLIC_APP_ENV === 'production') {
    notFound();
  }

  return (
    <main className={styles.page}>
      <div className={styles.notice}>
        <strong>DESIGN LAB — NOT AN OFFICIAL PRODUCTION RECORD</strong>
        <span>BGEDS 1.0 staff-platform foundation · functional data shown here is illustrative</span>
      </div>

      <div className={styles.shell}>
        <aside className={styles.rail} aria-label="Government workspace navigation">
          <div className={styles.identity}>
            <div className={styles.crest}>
              <img src="/eg-coat-of-arms.svg" alt="Coat of arms of Equatorial Guinea" />
            </div>
            <div>
              <p className={styles.identityName}>Republic of Equatorial Guinea</p>
              <p className={styles.identityService}>National Addressing Platform</p>
            </div>
          </div>

          <nav className={styles.nav}>
            <p className={styles.navLabel}>National operations</p>
            {navigation.map(([icon, label, count], index) => (
              <span
                className={index === 1 ? styles.navItemActive : styles.navItem}
                aria-current={index === 1 ? 'page' : undefined}
                key={label}
              >
                <span className={styles.navIcon} aria-hidden="true">{icon}</span>
                <span>{label}</span>
                {count ? <span className={styles.navCount}>{count}</span> : null}
              </span>
            ))}
            <p className={styles.navLabel}>Platform control</p>
            <span className={styles.navItem}>
              <span className={styles.navIcon} aria-hidden="true">AD</span>
              <span>Administration</span>
              <span />
            </span>
            <span className={styles.navItem}>
              <span className={styles.navIcon} aria-hidden="true">SY</span>
              <span>System</span>
              <span />
            </span>
          </nav>

          <div className={styles.railFooter}>
            Controlled staging<br />
            National scope · English
          </div>
        </aside>

        <section className={styles.main}>
          <header className={styles.topbar}>
            <div>
              <p className={styles.workspaceName}>National Operations</p>
              <p className={styles.workspaceScope}>Bioko Norte · All municipalities · Verification mode</p>
            </div>
            <div className={styles.search} role="search">
              Search address, code, person, municipality, or agency reference
              <span className={styles.searchKey}>Ctrl K</span>
            </div>
            <div className={styles.user}>
              <div className={styles.userAvatar} aria-hidden="true">MA</div>
              <div className={styles.userCopy}>
                <p className={styles.userName}>Maria Abeso</p>
                <p className={styles.userRole}>Senior verification officer</p>
              </div>
            </div>
          </header>

          <div className={styles.contextbar}>
            <span><strong>Territory:</strong> Bioko Norte</span>
            <span><strong>Team:</strong> Verification Unit A</span>
            <span><strong>Queue:</strong> Assigned and unassigned</span>
            <button className={styles.contextAction} type="button">Change work context</button>
          </div>

          <div className={styles.content}>
            <header className={styles.pageHeader}>
              <div>
                <p className={styles.eyebrow}>Operations workspace</p>
                <h1 className={styles.title}>Today&apos;s national addressing work</h1>
                <p className={styles.subtitle}>
                  Review assigned cases, resolve exceptions, and move valid records through the authoritative lifecycle without navigating between disconnected modules.
                </p>
              </div>
              <div className={styles.headerActions}>
                <button className={styles.buttonSecondary} type="button">Open saved view</button>
                <button className={styles.buttonPrimary} type="button">Assign next case</button>
              </div>
            </header>

            <section className={styles.summaryStrip} aria-label="Operational summary">
              <div className={styles.summaryItem}>
                <p className={styles.summaryValue}>92</p>
                <p className={styles.summaryLabel}>Awaiting verification</p>
              </div>
              <div className={styles.summaryItem}>
                <p className={styles.summaryValue}>18</p>
                <p className={styles.summaryLabel}>Active field assignments</p>
              </div>
              <div className={styles.summaryItem}>
                <p className={styles.summaryValue}>4</p>
                <p className={styles.summaryLabel}>Publication approvals</p>
              </div>
              <div className={styles.summaryItem}>
                <p className={styles.summaryValue}>7</p>
                <p className={styles.summaryLabel}>Service-level risks</p>
              </div>
              <div className={styles.summaryItem}>
                <p className={styles.summaryValue}>2</p>
                <p className={styles.summaryLabel}>Agency requests</p>
              </div>
            </section>

            <section className={styles.workbench} aria-label="Queue, authoritative record, and decision workbench">
              <div className={styles.queue}>
                <div className={styles.panelHeader}>
                  <h2>Assigned queue</h2>
                  <span className={styles.panelMeta}>23 records</span>
                </div>
                <div className={styles.filterBlock}>
                  <input className={styles.filterInput} aria-label="Filter assigned queue" placeholder="Filter by code, locality, or state" />
                </div>
                {queueItems.map((item) => (
                  <button className={item.active ? styles.queueItemActive : styles.queueItem} type="button" key={item.code}>
                    <span className={styles.queueTopline}>
                      <span className={styles.queueTitle}>{item.title}</span>
                      {item.priority ? <span className={styles.priority}>{item.priority}</span> : null}
                    </span>
                    <span className={styles.queueCode}>{item.code}</span>
                    <span className={styles.queueMeta}>{item.meta}</span>
                  </button>
                ))}
              </div>

              <article className={styles.record}>
                <header className={styles.recordHeader}>
                  <div>
                    <p className={styles.recordType}>Address verification case</p>
                    <h2 className={styles.recordTitle}>Avenida de la Independencia, Malabo II</h2>
                    <p className={styles.recordCode}>EG-BN-MB2-2026-008421</p>
                  </div>
                  <Status kind="warning">Under verification</Status>
                </header>

                <div className={styles.tabs} aria-label="Record sections">
                  <span className={styles.tabActive}>Overview</span>
                  <span className={styles.tab}>Location</span>
                  <span className={styles.tab}>Evidence</span>
                  <span className={styles.tab}>History</span>
                  <span className={styles.tab}>Audit</span>
                </div>

                <div className={styles.recordBody}>
                  <section className={styles.section}>
                    <div className={styles.sectionHeading}>
                      <h3>Authoritative context</h3>
                      <span>Last server update: 09:42</span>
                    </div>
                    <div className={styles.dataGrid}>
                      <div className={styles.dataCell}>
                        <p className={styles.dataLabel}>Province</p>
                        <p className={styles.dataValue}>Bioko Norte</p>
                      </div>
                      <div className={styles.dataCell}>
                        <p className={styles.dataLabel}>Municipality</p>
                        <p className={styles.dataValue}>Malabo</p>
                      </div>
                      <div className={styles.dataCell}>
                        <p className={styles.dataLabel}>District / locality</p>
                        <p className={styles.dataValue}>Malabo II · Semu</p>
                      </div>
                      <div className={styles.dataCell}>
                        <p className={styles.dataLabel}>Routing institution</p>
                        <p className={styles.dataValue}>National Address Registry</p>
                      </div>
                      <div className={styles.dataCell}>
                        <p className={styles.dataLabel}>Coordinate accuracy</p>
                        <p className={styles.dataValue}>4.2 m · GNSS capture</p>
                      </div>
                      <div className={styles.dataCell}>
                        <p className={styles.dataLabel}>Duplicate assessment</p>
                        <p className={styles.dataValue}>No high-confidence match</p>
                      </div>
                    </div>
                  </section>

                  <section className={styles.section}>
                    <div className={styles.sectionHeading}>
                      <h3>Evidence and decision checks</h3>
                      <span>4 required checks · 3 complete</span>
                    </div>
                    <div className={styles.tableWrap}>
                      <table className={styles.table}>
                        <thead>
                          <tr>
                            <th>Check</th>
                            <th>Source</th>
                            <th>Result</th>
                            <th>Reviewer note</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td>Administrative routing</td>
                            <td>Canonical territory registry</td>
                            <td><Status kind="success">Passed</Status></td>
                            <td>Province and municipality valid</td>
                          </tr>
                          <tr>
                            <td>Coordinate quality</td>
                            <td>Field capture 2026-07-23</td>
                            <td><Status kind="success">Passed</Status></td>
                            <td>Accuracy within threshold</td>
                          </tr>
                          <tr>
                            <td>Street and access evidence</td>
                            <td>Three field photographs</td>
                            <td><Status kind="success">Passed</Status></td>
                            <td>Entrance and road visible</td>
                          </tr>
                          <tr>
                            <td>Building-use confirmation</td>
                            <td>Citizen submission</td>
                            <td><Status kind="warning">Review</Status></td>
                            <td>Supporting description incomplete</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </section>
                </div>
              </article>

              <aside className={styles.inspector} aria-label="Evidence and valid actions">
                <div className={styles.panelHeader}>
                  <h3>Decision inspector</h3>
                  <span className={styles.panelMeta}>Role-authorized</span>
                </div>
                <div className={styles.inspectorBody}>
                  <div className={styles.alert}>
                    Building-use confirmation remains incomplete. Approval is unavailable until the record is completed or an authorized exception is recorded.
                  </div>

                  <section className={styles.section}>
                    <div className={styles.sectionHeading}>
                      <h3>Evidence</h3>
                      <span>5 items</span>
                    </div>
                    <ul className={styles.evidenceList}>
                      <li className={styles.evidenceItem}>
                        <p className={styles.evidenceTitle}>Field photograph set</p>
                        <p className={styles.evidenceMeta}>3 images · captured 08:54 · device verified</p>
                      </li>
                      <li className={styles.evidenceItem}>
                        <p className={styles.evidenceTitle}>GNSS observation</p>
                        <p className={styles.evidenceMeta}>4.2 m accuracy · source and timestamp retained</p>
                      </li>
                      <li className={styles.evidenceItem}>
                        <p className={styles.evidenceTitle}>Citizen description</p>
                        <p className={styles.evidenceMeta}>One required description field incomplete</p>
                      </li>
                    </ul>
                  </section>

                  <section className={styles.section}>
                    <div className={styles.sectionHeading}>
                      <h3>Valid next actions</h3>
                    </div>
                    <div className={styles.actionList}>
                      <button type="button">Request missing information</button>
                      <button type="button">Assign field recapture</button>
                      <button type="button">Record authorized exception</button>
                      <button type="button">Place case on hold</button>
                    </div>
                  </section>

                  <section className={styles.section}>
                    <div className={styles.sectionHeading}>
                      <h3>Recent history</h3>
                    </div>
                    <ul className={styles.timeline}>
                      <li className={styles.timelineItem}>
                        <p className={styles.timelineTitle}>Field evidence synchronized</p>
                        <p className={styles.timelineMeta}>09:16 · Field Team 04 · server accepted</p>
                      </li>
                      <li className={styles.timelineItem}>
                        <p className={styles.timelineTitle}>Case assigned</p>
                        <p className={styles.timelineMeta}>09:20 · Verification Unit A</p>
                      </li>
                    </ul>
                  </section>
                </div>
              </aside>
            </section>

            <section className={styles.adminPreview}>
              <header className={styles.pageHeader}>
                <div>
                  <p className={styles.eyebrow}>Staff administration target</p>
                  <h2 className={styles.title}>Personnel, teams, scope, equipment, and access</h2>
                  <p className={styles.subtitle}>
                    Staff administration becomes an operational personnel workspace. Account security remains explicit, but it is no longer the only organizing model.
                  </p>
                </div>
                <div className={styles.headerActions}>
                  <button className={styles.buttonSecondary} type="button">Export authorized roster</button>
                  <button className={styles.buttonPrimary} type="button">Add personnel record</button>
                </div>
              </header>

              <div className={styles.adminGrid}>
                <div className={styles.staffTable}>
                  <div className={styles.staffToolbar}>
                    <strong>National staff roster</strong>
                    <button className={styles.buttonSecondary} type="button">Filters</button>
                    <button className={styles.buttonSecondary} type="button">Teams</button>
                  </div>
                  <table>
                    <thead>
                      <tr>
                        <th>Personnel</th>
                        <th>Institution / team</th>
                        <th>Role</th>
                        <th>Territorial scope</th>
                        <th>Access state</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>Maria Abeso</strong><br />STAFF-000184</td>
                        <td>National Address Registry<br />Verification Unit A</td>
                        <td>Senior verifier</td>
                        <td>Bioko Norte</td>
                        <td><Status kind="success">Active</Status></td>
                      </tr>
                      <tr>
                        <td><strong>Pedro Nsue</strong><br />STAFF-000207</td>
                        <td>Field Operations<br />Field Team 04</td>
                        <td>Field supervisor</td>
                        <td>Malabo and Baney</td>
                        <td><Status kind="success">Active</Status></td>
                      </tr>
                      <tr>
                        <td><strong>Rosa Ondo</strong><br />STAFF-000221</td>
                        <td>Publication Directorate<br />Output Control</td>
                        <td>Publication officer</td>
                        <td>National</td>
                        <td><Status kind="warning">Credential rotation due</Status></td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <aside className={styles.staffInspector}>
                  <div className={styles.panelHeader}>
                    <h3>Personnel record</h3>
                    <span className={styles.panelMeta}>STAFF-000184</span>
                  </div>
                  <div className={styles.staffInspectorBody}>
                    <div className={styles.staffIdentity}>
                      <div className={styles.staffInitials}>MA</div>
                      <div>
                        <p className={styles.staffName}>Maria Abeso</p>
                        <p className={styles.staffMeta}>National Address Registry · Verification Unit A</p>
                      </div>
                    </div>
                    <dl className={styles.definitionList}>
                      <dt>Employment state</dt><dd>Active</dd>
                      <dt>Primary role</dt><dd>Senior verifier</dd>
                      <dt>Territory</dt><dd>Bioko Norte</dd>
                      <dt>Assigned device</dt><dd>EG-OPS-0418</dd>
                      <dt>Sessions</dt><dd>1 active</dd>
                      <dt>Last activity</dt><dd>Today, 09:42</dd>
                    </dl>
                    <div className={styles.actionList}>
                      <button type="button">Open complete personnel record</button>
                      <button type="button">Change role or scope</button>
                      <button type="button">Manage sessions and credentials</button>
                      <button className={styles.buttonDanger} type="button">Suspend access</button>
                    </div>
                  </div>
                </aside>
              </div>
            </section>

            <p className={styles.footerNote}>
              Phase 1 design lab: this route demonstrates the target shell, information density, queue/record/inspector workbench, restrained status treatment, and personnel-centered administration model. It does not alter authoritative workflows or production data.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
