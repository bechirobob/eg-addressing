# Equatorial Guinea National Identity UI Blueprint

> **For Hermes:** Apply this blueprint to every front-facing surface of the national addressing platform before calling the UI presentable.

**User goal and attention model**
- Primary users should immediately read this as an official national digital platform, not a generic startup dashboard.
- Attention should land in this order: state identity → platform purpose → operational trust/status → module/workflow overview.
- National symbols must support trust, not compete with the task layer.

**Relevant principles**
- **Gestalt:** use grouped cards and aligned sections so operational modules read as one coordinated government system.
- **Fitts:** key actions and state indicators should remain large and obvious without oversized decorative controls.
- **Cognitive load:** keep copy disciplined, remove MVP-template phrasing, and avoid ornamental clutter.
- **Feedback loops:** service status, environment readiness, and workflow readiness should be visible in restrained institutional badges.

**Visual system tokens**
- Core colors should come from the Equatorial Guinea flag in a mature, institutional palette:
  - deep green for trust/land/service continuity
  - muted red for national emphasis and alerts only
  - calm blue for structure, navigation, and government-system framing
  - ivory/off-white backgrounds instead of cold SaaS gray
  - restrained gold accents for ceremonial emphasis where needed
- Typography should feel official and readable: strong serif display for major headings paired with a clean sans for operational content.
- Controls should be softly squared, not playful-rounded.
- Shadows should be light and architectural, not glossy startup cards.

**Interaction and motion language**
- Motion should be minimal and respectful.
- Hover/focus states should rely on contrast, border, and elevation shifts more than animation.
- Respect `prefers-reduced-motion` by keeping transitions short and non-essential.

**Component map and data shape**
- Masthead / state banner with project label and subtle coat-of-arms placement.
- Hero section with national platform title, trust statement, and operational state summary.
- Operational summary cards with backend/frontend/data stack and platform readiness.
- Module/roadmap sections that feel like institutional program workstreams rather than SaaS feature chips.
- Reusable token classes should support future public pages using the same national identity system.

**Coat of arms usage rules**
- Use the coat of arms small-to-medium, preferably in the masthead or hero corner.
- Never let it dominate the page or repeat excessively.
- Keep it visible enough to signal official identity, but restrained so the interface still feels professional and task-first.
- Use a clean asset with enough whitespace and no gimmick effects.

**Critique checklist**
- If the page could be mistaken for a random startup admin template, the pass failed.
- If the coat of arms is loud, oversized, or repeated, the pass failed.
- If colors feel like pasted stripes instead of a system, the pass failed.
- If the page loses readability while becoming more patriotic, the pass failed.
- If mobile/desktop hierarchy gets weaker, the pass failed.
