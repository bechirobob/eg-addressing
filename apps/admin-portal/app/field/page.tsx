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

export default async function FieldPage() {
  const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
  const assignments: Assignment[] = [];
  const submissions: Submission[] = [];
  const territories: Territory[] = [];

  return (
    <SiteChrome
      apiBaseUrl={publicApiBaseUrl}
      eyebrow="Staff service"
      eyebrowKey="fieldEyebrow"
      title="Field work"
      titleKey="fieldTitle"
      subtitle="Complete assigned location checks and submit field evidence for review."
      subtitleKey="fieldSubtitle"
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
