import { SiteChrome } from '../components/SiteChrome';
import { LocalizedText } from '../components/i18n';

export const dynamic = 'force-dynamic';

const operatingStages = ['stageCitizenCapture', 'stageOperatorReview', 'stageFieldVerification', 'stageOfficialPublication'] as const;

export default function HomePage() {
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="National platform"
      eyebrowKey="homeEyebrow"
      title="National Addressing Platform"
      titleKey="homeTitle"
      subtitle="Use this service to register a location, check an official address code, or track a submitted request."
      subtitleKey="homeSubtitle"
    >
      <section className="service-start-page desktop-home-start" aria-labelledby="public-services-heading">
        <div className="desktop-home-intro">
          <div className="desktop-home-copy">
            <p className="section-label">Public service</p>
            <h2 id="public-services-heading">National Addressing Platform</h2>
            <p>Use this service to register a location, check an official address code, or track a submitted request.</p>
            <div className="service-start-actions" aria-label="Public addressing services">
              <a className="button button-primary service-start-primary" href="/geotag">
                <LocalizedText k="homeRegisterLabel" />
              </a>
              <p className="service-start-secondary-actions public-task-copy">
                <a className="inline-action-link" href="/issue">
                  <LocalizedText k="homeCheckLabel" />
                </a>
                <span aria-hidden="true"> · </span>
                <a className="inline-action-link" href="/track">
                  <LocalizedText k="homeTrackAction" />
                </a>
              </p>
            </div>
          </div>
          <aside className="desktop-before-start" aria-labelledby="before-start-heading">
            <p className="section-label">Before you start</p>
            <h2 id="before-start-heading">You can use this service to</h2>
            <ul>
              <li>Submit a location for official review.</li>
              <li>Check whether an address code is published.</li>
              <li>Track a request without exposing private identity details.</li>
            </ul>
          </aside>
        </div>

        <section className="service-start-workflow" aria-labelledby="workflow-heading">
          <p className="section-label"><LocalizedText k="workflow" /></p>
          <h2 id="workflow-heading"><LocalizedText k="homeWorkflowTitle" /></h2>
          <ol>
            {operatingStages.map((stage, index) => (
              <li key={stage}>
                <span>{index + 1}</span>
                <LocalizedText k={stage} />
              </li>
            ))}
          </ol>
        </section>

        <section className="service-start-staff" aria-labelledby="staff-services-heading">
          <div>
            <p className="section-label">Staff services</p>
            <h2 id="staff-services-heading">Staff sign-in</h2>
          </div>
          <a className="button button-secondary" href="/login">Sign in</a>
        </section>
      </section>
    </SiteChrome>
  );
}
