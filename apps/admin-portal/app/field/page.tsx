import { SiteChrome } from '../../components/SiteChrome';
import { FieldWorkflowPanel } from '../../components/FieldWorkflowPanel';

export const dynamic = 'force-dynamic';

type Assignment = {
  assignment_id: string;
  territory_id: string;
  territory: string;
  task: string;
  team: string;
  priority: string;
};

type Submission = {
  id: string;
  assignment_id?: string | null;
  territory_id: string;
  territory_name: string;
  submission_type: 'road' | 'building' | 'address';
  candidate_name: string;
  candidate_status: string;
  notes: string;
  submitted_by: string;
  review_status: string;
  reviewer_note: string;
  registry_entity_id?: string | null;
};

type Territory = { id: string; name: string };

async function getAssignments(baseUrl: string): Promise<Assignment[]> {
  try {
    const response = await fetch(`${baseUrl}/api/v1/field/assignments`, { cache: 'no-store' });
    if (!response.ok) return [];
    const payload = (await response.json()) as { items: Assignment[] };
    return payload.items ?? [];
  } catch {
    return [];
  }
}

async function getSubmissions(baseUrl: string): Promise<Submission[]> {
  const bootstrapHeaders = { Authorization: ['Bearer', 'admin-bootstrap-token'].join(' ') };
  try {
    const response = await fetch(`${baseUrl}/api/v1/field/submissions`, {
      cache: 'no-store',
      headers: bootstrapHeaders,
    });
    if (!response.ok) return [];
    const payload = (await response.json()) as { items: Submission[] };
    return payload.items ?? [];
  } catch {
    return [];
  }
}

async function getTerritories(baseUrl: string): Promise<Territory[]> {
  try {
    const response = await fetch(`${baseUrl}/api/v1/territories`, { cache: 'no-store' });
    if (!response.ok) return [];
    const payload = (await response.json()) as { items: Territory[] };
    return payload.items ?? [];
  } catch {
    return [];
  }
}

export default async function FieldPage() {
  const apiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const [assignments, submissions, territories] = await Promise.all([
    getAssignments(apiBaseUrl),
    getSubmissions(apiBaseUrl),
    getTerritories(apiBaseUrl),
  ]);

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Field operations"
      title="Field Submission Workflow"
      subtitle="Operational intake for survey teams, route coordinators, and field officers feeding the national addressing verification queue."
    >
      <FieldWorkflowPanel
        assignments={assignments}
        submissions={submissions}
        territories={territories}
        apiBaseUrl={publicApiBaseUrl}
      />
    </SiteChrome>
  );
}
