import { SiteChrome } from '../components/SiteChrome';

type ApiMeta = {
  platform: {
    name: string;
    mode: string;
  };
  stack: {
    backend: string;
    frontend: string;
    database: string;
    cache: string;
    storage: string;
  };
  modules: string[];
};

type Territory = {
  id: string;
  name: string;
  province: string;
  type: string;
  readiness: string;
};

export const dynamic = 'force-dynamic';

async function getApiMeta(): Promise<{ ok: boolean; data: ApiMeta | null }> {
  const baseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';

  try {
    const response = await fetch(`${baseUrl}/api/v1/meta`, { cache: 'no-store' });
    if (!response.ok) {
      return { ok: false, data: null };
    }
    const data = (await response.json()) as ApiMeta;
    return { ok: true, data };
  } catch {
    return { ok: false, data: null };
  }
}

async function getTerritories(): Promise<Territory[]> {
  const baseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';

  try {
    const response = await fetch(`${baseUrl}/api/v1/territories`, { cache: 'no-store' });
    if (!response.ok) {
      return [];
    }
    const payload = (await response.json()) as { items: Territory[] };
    return payload.items;
  } catch {
    return [];
  }
}

const programWorkstreams = [
  'National registry and verification authority',
  'Territory, road, building, and address governance',
  'Field capture, review, and quality assurance workflow',
  'Institutional interoperability for emergency, utility, and planning use',
];

const deliveryDisciplines = [
  'Official review and publication controls',
  'Institutional auditability and traceability',
  'National scaling logic and controlled rollout',
  'Secure service boundary across registry, field, and agency use',
];

export default async function HomePage() {
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const { ok, data } = await getApiMeta();
  const territories = await getTerritories();

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="National infrastructure program"
      title="National Digital Addressing Platform"
      subtitle="Official digital infrastructure for address registry, verification, territorial operations, and inter-agency coordination."
    >
      <section className="hero-card feature-hero">
        <div className="hero-copy-block">
          <span className="eyebrow">Platform overview</span>
          <h2>Built to feel official, trustworthy, and operationally serious.</h2>
          <p className="hero-copy">
            This control surface is the front-facing system shell for the national addressing programme. It is being shaped as public digital infrastructure with disciplined hierarchy, restrained symbolism, and clear operational trust signals.
          </p>
        </div>

        <div className="hero-grid">
          <article className="status-card primary-card">
            <span className={`status-pill ${ok ? 'ok' : 'warn'}`}>{ok ? 'Core platform reachable' : 'Core platform unavailable'}</span>
            <h3>{data?.platform.name ?? 'Backend status unavailable'}</h3>
            <dl className="facts-grid">
              <div>
                <dt>Operational phase</dt>
                <dd>{data?.platform.mode ?? 'unknown'}</dd>
              </div>
              <div>
                <dt>Role of this surface</dt>
                <dd>Administrative command and verification layer</dd>
              </div>
              <div>
                <dt>Identity posture</dt>
                <dd>National digital public infrastructure</dd>
              </div>
              <div>
                <dt>Service condition</dt>
                <dd>{ok ? 'Available for operator use' : 'Awaiting recovery'}</dd>
              </div>
            </dl>
          </article>

          <article className="status-card secondary-card">
            <span className="status-pill neutral">Current service stack</span>
            <ul className="stack-list">
              <li><strong>Frontend</strong><span>{data?.stack.frontend ?? 'Next.js'}</span></li>
              <li><strong>Backend</strong><span>{data?.stack.backend ?? 'FastAPI'}</span></li>
              <li><strong>Database</strong><span>{data?.stack.database ?? 'PostgreSQL + PostGIS'}</span></li>
              <li><strong>Cache</strong><span>{data?.stack.cache ?? 'Redis'}</span></li>
              <li><strong>Storage</strong><span>{data?.stack.storage ?? 'MinIO'}</span></li>
            </ul>
          </article>
        </div>
      </section>

      <section className="section-grid">
        <article className="panel panel-accent-blue">
          <div className="panel-head">
            <p className="section-label">Program workstreams</p>
            <h3>Institutional scope</h3>
          </div>
          <ul className="program-list">
            {programWorkstreams.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>

        <article className="panel panel-accent-green">
          <div className="panel-head">
            <p className="section-label">Operational discipline</p>
            <h3>Delivery standards</h3>
          </div>
          <ul className="program-list">
            {deliveryDisciplines.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>

      <section className="section-grid lower-grid">
        <article className="panel">
          <div className="panel-head">
            <p className="section-label">Platform modules</p>
            <h3>Core system domains</h3>
          </div>
          <div className="tag-grid">
            {(data?.modules ?? []).map((module) => (
              <span key={module} className="tag">
                {module.replace('-', ' ')}
              </span>
            ))}
          </div>
        </article>

        <article className="panel panel-accent-gold">
          <div className="panel-head">
            <p className="section-label">Priority territories</p>
            <h3>Current registry footprint</h3>
          </div>
          <ul className="program-list">
            {territories.map((territory) => (
              <li key={territory.id}>
                <span>
                  <strong>{territory.name}</strong>
                  <br />
                  {territory.province} · {territory.type}
                </span>
                <span>{territory.readiness}</span>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </SiteChrome>
  );
}
