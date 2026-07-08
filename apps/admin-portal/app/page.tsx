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
      <section className="service-start-page" aria-labelledby="public-services-heading">
        <div className="service-start-actions" aria-label="Public addressing services">
          <a className="button button-primary service-start-primary" href="/geotag">
            <LocalizedText k="homeRegisterLabel" />
          </a>
          <div className="service-start-secondary-actions">
            <a className="button button-secondary" href="/issue">
              <LocalizedText k="homeCheckLabel" />
            </a>
            <a className="button button-secondary" href="/track">
              <LocalizedText k="homeTrackAction" />
            </a>
          </div>
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
