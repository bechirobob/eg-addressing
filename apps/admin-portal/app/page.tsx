import { SiteChrome } from '../components/SiteChrome';
import { LocalizedText } from '../components/i18n';

export const dynamic = 'force-dynamic';

const publicServices = [
  {
    href: '/geotag',
    labelKey: 'homeRegisterLabel',
    descriptionKey: 'homeRegisterDescription',
    actionKey: 'homeRegisterAction',
  },
  {
    href: '/issue',
    labelKey: 'homeCheckLabel',
    descriptionKey: 'homeCheckDescription',
    actionKey: 'homeCheckAction',
  },
  {
    href: '/track',
    labelKey: 'homeTrackLabel',
    descriptionKey: 'homeTrackDescription',
    actionKey: 'homeTrackAction',
  },
] as const;

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
      subtitle="A public entry point for registering locations, checking official address codes, and tracking review progress across the national addressing workflow."
      subtitleKey="homeSubtitle"
    >
      <section className="section-grid national-platform-grid">
        <article className="public-task-panel civic-panel-blue national-platform-overview">
          <div className="panel-head">
            <p className="section-label"><LocalizedText k="publicServices" /></p>
            <h3><LocalizedText k="chooseCorrectService" /></h3>
          </div>
          <p className="institutional-note">
            <LocalizedText k="homeIntro" />
          </p>
          <div className="summary-grid national-service-grid">
            {publicServices.map((service) => (
              <a className="national-service-card" href={service.href} key={service.href}>
                <strong><LocalizedText k={service.labelKey} /></strong>
                <span><LocalizedText k={service.descriptionKey} /></span>
                <em><LocalizedText k={service.actionKey} /></em>
              </a>
            ))}
          </div>
        </article>

        <article className="public-task-panel civic-panel-gold national-platform-workflow">
          <div className="panel-head">
            <p className="section-label"><LocalizedText k="workflow" /></p>
            <h3><LocalizedText k="homeWorkflowTitle" /></h3>
          </div>
          <ol className="program-list national-workflow-list">
            {operatingStages.map((stage, index) => (
              <li key={stage}>
                <span>{index + 1}. <LocalizedText k={stage} /></span>
              </li>
            ))}
          </ol>
          <details className="disclosure-panel">
            <summary><LocalizedText k="whatMakesOfficial" /></summary>
            <p>
              <LocalizedText k="officialRecordExplanation" />
            </p>
          </details>
        </article>
      </section>
    </SiteChrome>
  );
}
