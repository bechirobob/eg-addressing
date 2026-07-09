# Desktop replication blueprint

Source: `national_addressing_desktop_replication_guide.pdf` uploaded 2026-07-09.

## 1. User goal and attention model
Desktop must feel like a calm government-funded administrative workspace, not a stretched mobile app or AI dashboard. Public users should quickly choose one service. Staff officers should search, compare, filter, review, and act from structured records and queues.

Attention order:
1. Official service identity and role-appropriate navigation.
2. Page title, description, and one primary action when applicable.
3. Main work area: table/search/queue/form task.
4. Right-side summary/detail panel for status, selected record, next action, or filters.
5. Secondary details behind disclosures or lower sections.

## 2. Principles
- Gestalt: desktop groups work by service and data table, not stacks of unrelated mobile cards.
- Fitts: primary actions remain visible near page headers or selected-row detail panels; table row actions stay clear.
- Cognitive load: metrics/status are summaries, not pill clouds; technical evidence remains collapsed or side-panel scoped.
- Feedback loops: statuses use text plus restrained badge treatment only where status identification helps; not every metric gets a badge.
- Government service fit: English-only, no command center/AI/smart/futuristic language, no decorative grids/glows.

## 3. Visual system tokens
- Background: warm off-white `#f7f4ec`.
- Surfaces: off-white/white `#fffef9`, muted `#f4f1e8`.
- Text: dark navy `#16324f`, muted `#667085`, soft `#8a94a3`.
- Borders: subtle gray `#d7dde5`, strong `#b9c3cf`.
- Semantic accents: blue, green, gold, red muted and restrained.
- Radius: cards/panels `12px`, controls `8px`.
- Container: `1120px–1280px`, target `1200px`.
- Desktop grid: 12 columns, 24–32px gap, main 8/9 cols, side 3/4 cols.
- Page padding: 32px desktop, 16px mobile.

## 4. Interaction and motion language
- Add skip link.
- Header navigation replaces huge repeated module grids.
- Desktop uses tables for registry records, field assignments, blockers, reports, and audit-style data.
- Right-side panels show selected row/status/filters/automation summaries.
- Mobile/tablet collapses back to stacked sections; wide tables remain horizontally scrollable where needed.
- No decorative motion; reduced-motion safe.

## 5. Component map and data shape
Shared system:
- Official header / service navigation / page header / desktop shell.
- 12-column grid helpers: main content + side panel.
- Filter/search bars, metric grid/list, data table, status badge, release panel, case/details panel.

Route patterns:
- `/`: public service start page; two-column intro + Before you start; service cards; four-step process; only homepage bottom Staff services sign-in remains allowed.
- `/field`: staff task screen; top summary; filters; assigned checks table with location, territory, status, required evidence, due date, assigned officer, action; right selected-assignment panel.
- `/registry`: search-first database workspace; large search, tabs, filters, data table, right record details panel.
- `/signage`: release gate; release status panel, summary metrics, blocked items table, signage batches/approver/date/notes.
- `/reports`: read-only reporting; filters, summary metrics, sections/tables/charts, Export report only.

## 6. Critique checklist
- Does any desktop route look like stretched mobile cards? If yes, convert to table/grid workspace.
- Is there a search promise without a visible search input? If yes, fail.
- Is there command center/AI/smart/futuristic language? If yes, remove.
- Are pills/chip clouds used for metrics or decoration? If yes, convert to plain text/table/status badge only when necessary.
- Are public and staff navigation separated correctly? If not, fix route-aware chrome.
- Are tables semantic and accessible? If not, add real table markup and headings.
- Are 1440, 1280, 1024, 768, and mobile verified live? If not, do not report done.
