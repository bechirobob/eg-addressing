from pathlib import Path

OUT = Path('/home/ubuntu/national-addressing-proposal')
OUT.mkdir(parents=True, exist_ok=True)

CSS = '''
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  color: #162032;
  font-family: "Inter", "Segoe UI", Arial, sans-serif;
  background: #f4f7fb;
  line-height: 1.45;
}
.page {
  width: 210mm;
  min-height: 297mm;
  margin: 0 auto 18px;
  background: #fff;
  padding: 22mm 18mm 18mm;
  position: relative;
  overflow: hidden;
  page-break-after: always;
}
.page:last-of-type { page-break-after: auto; }
.cover {
  background: radial-gradient(circle at 85% 12%, rgba(214, 32, 45, 0.18), transparent 28%),
              linear-gradient(135deg, #07182e 0%, #0a315e 58%, #123d70 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.cover:before {
  content: "";
  position: absolute;
  inset: auto -60mm -70mm auto;
  width: 160mm;
  height: 160mm;
  border-radius: 50%;
  border: 28mm solid rgba(255,255,255,.055);
}
.letter-cover {
  background: linear-gradient(180deg, #fbfcff 0%, #f5f8fc 100%);
}
.flagline { display: flex; gap: 5px; margin-bottom: 22mm; }
.flagline span { height: 6px; width: 42px; border-radius: 999px; display:block; }
.green { background:#3c9c4a; } .white { background:#fff; } .red { background:#d6202d; } .blue { background:#2b66b1; }
h1 { font-size: 42px; line-height: 1.04; margin: 0 0 14px; letter-spacing: -1.3px; }
.cover h1 { max-width: 155mm; font-size: 44px; }
.subtitle { font-size: 18px; max-width: 155mm; color: #dbeafe; }
.letter-cover .subtitle { color: #31445f; }
.kicker { text-transform: uppercase; letter-spacing: 1.7px; font-size: 12px; font-weight: 800; color: #83c5ff; margin-bottom: 10px; }
.letter-cover .kicker { color: #0b315f; }
.cover-meta { border-left: 4px solid #d6202d; padding-left: 16px; color: #eef6ff; font-size: 14px; max-width: 145mm; }
.letter-meta { border-left: 4px solid #d6202d; padding-left: 16px; color: #31445f; font-size: 14px; max-width: 150mm; }
h2 { font-size: 28px; margin: 0 0 12px; color:#0b315f; letter-spacing: -0.6px; }
h3 { font-size: 16px; margin: 18px 0 8px; color:#0c3a6d; }
p { margin: 0 0 10px; }
.lead { font-size: 17px; color:#26384f; }
.muted { color:#64748b; }
.small { font-size: 11px; color:#64748b; }
.section-tag { display:inline-block; color:#d6202d; font-weight: 800; font-size: 11px; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 8px; }
.grid { display:grid; gap: 12px; }
.grid-2 { grid-template-columns: 1fr 1fr; }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.card { background:#f8fafc; border:1px solid #dce6f2; border-radius: 14px; padding: 14px; }
.card.dark { background:#0b315f; color:#fff; border:0; }
.card.dark h3 { color:#fff; }
.stat { font-size: 29px; font-weight: 900; color:#0b315f; line-height:1.05; }
.statlabel { font-size: 11px; text-transform: uppercase; letter-spacing:.7px; color:#64748b; margin-top:5px; }
.dark .stat, .dark .statlabel { color:#fff; }
ul { margin: 8px 0 0 20px; padding: 0; }
li { margin-bottom: 6px; }
.callout { border-left: 5px solid #d6202d; background:#f8fbff; padding: 14px 16px; border-radius: 12px; margin: 14px 0; }
.quote { font-size: 21px; line-height: 1.3; color:#0b315f; font-weight: 800; }
.timeline { display:grid; gap:10px; margin-top: 12px; }
.phase { display:grid; grid-template-columns: 35mm 1fr 42mm; gap: 10px; align-items:start; padding: 12px; border:1px solid #dce6f2; border-radius: 12px; background:#fbfdff; }
.phase strong { color:#0b315f; }
.price { font-size: 17px; font-weight:900; color:#d6202d; text-align:right; }
table { width:100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }
th { background:#0b315f; color:#fff; text-align:left; padding:9px; }
td { border-bottom:1px solid #dce6f2; padding:8px 9px; vertical-align: top; }
.footer { position:absolute; bottom: 9mm; left:18mm; right:18mm; display:flex; justify-content:space-between; color:#8a97a8; font-size:10px; border-top:1px solid #e2e8f0; padding-top:6px; }
.footer span:last-child { display: none; }
.signature { margin-top: 24px; padding-top: 12px; border-top: 1px solid #dce6f2; }
.tight li { margin-bottom: 4px; }
.letter-body { font-size: 15px; color:#24354f; }
.letter-body p { margin-bottom: 14px; }
.letter-body .recipient { margin-bottom: 18px; }
@media print {
  body { background: #fff; }
  .page { width: 210mm; min-height: 297mm; margin: 0; page-break-after: always; break-after: page; }
  .page:last-of-type { page-break-after: auto; break-after: auto; }
}
'''

CONTENT = {
    'en': {
        'proposal_filename': 'equatorial-guinea-national-digital-addressing-proposal-en.html',
        'cover_filename': 'equatorial-guinea-national-digital-addressing-cover-letter-en.html',
        'title': 'National Digital Addressing System Proposal',
        'kicker': 'Confidential discussion proposal',
        'subtitle': 'A government-owned national addressing infrastructure program for Equatorial Guinea — giving every home, building, business, institution, and service point an official physical and digital address.',
        'prepared_for': 'Prepared for the Ministry of Transportation at the request of the Vice President',
        'purpose': 'Purpose: to establish a national address registry and geospatial service layer that supports postal delivery, emergency response, planning, logistics, utilities, digital public services, and national modernization.',
        'prepared_by': 'Prepared by: Benjamin Bob Bechiro<br/>Project Initiator<br/>Phone: +240 555 605 331<br/>Email: bechirobob@gmail.com<br/>Date: June 2026',
        'founder_tag': 'Founder’s note',
        'founder_title': 'A patriotic infrastructure proposal for national order, visibility, and service delivery',
        'founder_lead': 'Every serious modern state needs a trusted way to identify places. Without a reliable address system, homes stay difficult to find, services stay hard to deliver, and national planning remains slower, more manual, and less accountable than it should be.',
        'founder_quote': 'Roads, homes, public buildings, businesses, and future cities already exist. What is missing is a shared national location language that government, citizens, emergency teams, couriers, utilities, and investors can all trust and use.',
        'founder_p1': 'This proposal is not about street signs alone. It is about building a national operating layer for location identity: one authoritative system for house numbering, street naming, building registration, geolocation, postal coding, and searchable address verification.',
        'founder_p2': 'A country that wants stronger logistics, better emergency response, cleaner records, more efficient public services, and a more investment-ready business environment should not leave addresses informal or fragmented. Addressing is foundational infrastructure.',
        'founder_p3': 'Equatorial Guinea has the opportunity to do this with dignity and discipline: start with a controlled pilot, define standards correctly, keep government ownership of the registry, and scale in phases with auditability and operational realism.',
        'profile': 'Project initiator profile: Benjamin Bob Bechiro completed junior and senior high school at Archimedes International College in Accra, Ghana, where he served as Head of the Science Department in his senior year. He holds a Diploma in Software Engineering from the University of Staffordshire and an Honorary Bachelor’s Degree in Software Engineering from Coventry University in the United Kingdom. His private technology work includes completed platform projects for Joscol and Martínez Hermanos, covering practical digital commerce, operations, workflow, and service-delivery systems.',
        'signature': 'Respectfully submitted,',
        'signature_body': 'Benjamin Bob Bechiro<br/>Project Initiator<br/>Phone: +240 555 605 331<br/>Email: bechirobob@gmail.com',
        'summary_tag': 'Executive summary',
        'summary_title': 'Not a map project — a national address operating layer',
        'summary_lead': 'The recommended program is a phased National Digital Addressing System led by government and designed to become the authoritative source of location identity across Equatorial Guinea.',
        'summary_cards': [
            ('For citizens', ['Know and share a clear official address.', 'Receive deliveries, utility visits, and emergency response more reliably.', 'Verify and correct address records through a controlled channel.']),
            ('For ministries and municipalities', ['Maintain one trusted registry instead of fragmented local lists.', 'Track coverage, verification, gaps, and field progress.', 'Connect addressing to permits, taxation, census, land, and service workflows.']),
            ('For logistics and utilities', ['Reduce failed deliveries and service visits.', 'Plan routes, zones, and dispatch with verified coordinates.', 'Integrate approved address APIs into operations over time.']),
            ('For national leadership', ['Create measurable visibility into territorial coverage.', 'Support urban planning, infrastructure decisions, and public-service readiness.', 'Strengthen digital sovereignty through a government-owned registry.'])
        ],
        'core_proposal': 'Core proposal: approve a 9-month pilot covering standards, field capture, registry build, and public-service integration in priority zones of Malabo, then scale into a 3-year phased national rollout across Bata, Oyala/Ciudad de la Paz, and all provinces.',
        'why_tag': 'Why now',
        'why_title': 'The country needs a trusted way to identify places',
        'why_intro': 'Addressing affects far more than mail. A weak address system slows almost every service that depends on finding people, properties, or facilities correctly.',
        'stats': [
            ('Public services', 'Need location certainty for permits, inspections, notices, and response.'),
            ('Emergency response', 'Needs fast, unambiguous building and route identification.'),
            ('Utilities', 'Need precise service points for installation, meter records, and maintenance.'),
            ('Commerce and logistics', 'Need trusted addresses for dispatch, delivery, and reconciliation.'),
            ('Planning and census', 'Need consistent territorial units and verified building records.'),
            ('Future cities', 'Should not inherit paper-first address confusion.')
        ],
        'numbers_mean': 'What this means',
        'numbers_points': [
            'If addressing remains informal, every digital service built on top of it becomes weaker and more expensive to operate.',
            'A national address registry should be treated as foundational infrastructure, like roads, cadastral records, and public-service directories.',
            'A mobile-first field workflow is mandatory because verification will happen on the territory, not only in offices.',
            'Data governance and verification rules matter as much as software. A bad registry at scale becomes a national headache.'
        ],
        'opportunity_tag': 'National opportunity',
        'opportunity_title': 'Oyala / Ciudad de la Paz should be born address-ready',
        'opportunity_lead': 'A future-facing administrative capital should not depend on vague directions, improvised landmarks, and disconnected local records. It should open with a formal location identity model already designed into its operations.',
        'opportunity_quote': 'If a new capital represents the future of the nation, then every plot, building, road, ministry site, and service point inside it should already be identifiable, searchable, and service-ready by design.',
        'opportunity_cards': [
            ('Digital-by-default public administration', 'Permits, inspections, public notices, and inter-ministry coordination work better when locations are formally identified.'),
            ('Emergency and security readiness', 'Response teams need precise building references, route logic, and zone awareness, especially in expanding administrative districts.'),
            ('Utility and infrastructure delivery', 'Water, power, telecom, roads, sanitation, and maintenance operations benefit immediately from address-ready records.'),
            ('Investor and resident confidence', 'A city that is easy to navigate, verify, and service projects seriousness and administrative maturity.')
        ],
        'platform_tag': 'Platform model',
        'platform_title': 'What the national system should contain',
        'platform_rows': [
            ('National address registry', 'Authoritative building, plot, street, and zone records with administrative hierarchy and verification state.', 'Provides a single national source of truth.'),
            ('Geospatial map layer', 'Interactive map of roads, districts, buildings, parcels, landmarks, and service points.', 'Makes the registry usable in the field and in planning offices.'),
            ('Field capture application', 'Mobile/tablet workflow for enumerators to capture buildings, photos, coordinates, naming proposals, and validation status.', 'Supports structured territorial rollout and offline collection.'),
            ('Address code engine', 'Generates official address formats, short codes, printable labels, and signage references.', 'Keeps standards consistent across ministries and municipalities.'),
            ('Operations dashboard', 'Coverage metrics, approval queues, duplicate detection, team productivity, verification backlog, and reporting.', 'Gives leadership visibility and operational control.'),
            ('Citizen and agency access', 'Search, verify, request correction, print proof of address, and approved API access for service operators.', 'Drives real-world adoption beyond the registry itself.'),
            ('Integration gateway', 'Controlled interfaces for postal, utilities, emergency response, tax, land, planning, and logistics systems.', 'Prevents the address system from becoming an isolated database.')
        ],
        'benefits_tag': 'National advantages',
        'benefits_title': 'Why the whole country benefits',
        'benefits_lead': 'A good address system is quiet infrastructure: when it works, everything above it becomes easier to find, route, verify, inspect, deliver, and improve.',
        'benefits_cards': [
            ('Better public-service delivery', 'Agencies can issue, inspect, route, and follow up with clearer location identity.'),
            ('Faster emergency response', 'Ambulance, police, and fire services gain a more reliable operational reference model.'),
            ('Stronger economic activity', 'Businesses, delivery operators, and suppliers spend less time failing to locate people and places.'),
            ('Cleaner national records', 'Property, land, permits, service accounts, and census work gain a shared address backbone.'),
            ('Tourism and navigation', 'Visitors understand how to reach hotels, offices, venues, and services with less friction.'),
            ('Digital sovereignty', 'Government retains ownership and control of a strategic national dataset.')
        ],
        'roadmap_tag': 'Delivery roadmap',
        'roadmap_title': 'Recommended phased rollout',
        'timeline': [
            ('Phase 1', 'Standards + pilot design', '3 months', 'Define address standards, governance model, data schema, signage rules, pilot zones, field methodology, and ministry operating model.'),
            ('Phase 2', 'Pilot field capture + registry build', '6 months', 'Capture streets and buildings in pilot zones, verify naming/numbering, launch registry, and connect first government workflows.'),
            ('Phase 3', 'Malabo + Bata scale-up', '9-12 months', 'Expand to priority urban districts, strengthen dashboards, and onboard utilities, emergency services, and postal workflows.'),
            ('Phase 4', 'National expansion', '12-24 months', 'Roll out province by province with contractor control, QA, training, and approved integrations.'),
            ('Phase 5', 'Long-term operations', 'Ongoing', 'Maintain the registry, govern updates, support new developments, and evolve agency integrations.')
        ],
        'governance_tag': 'Governance and security',
        'governance_title': 'This must be run as national trust infrastructure',
        'gov_cards': [
            ('Government ownership of the registry', ['The core address database should remain under formal government control.', 'External vendors may support delivery, but not own the national source of truth.']),
            ('Cross-ministry steering model', ['Transport, interior/local administration, planning, lands, postal, telecom, emergency response, and municipalities should align standards early.', 'One lead sponsor is necessary, but the system serves many institutions.']),
            ('Verification before publication', ['No building record should become authoritative without defined validation rules.', 'Duplicates, naming conflicts, and unverified coordinates must be controlled operationally.']),
            ('Security and auditability', ['Role-based access, change logs, backups, incident handling, and approval history are mandatory.', 'Strategic location data should not drift into unmanaged personal spreadsheets or contractor silos.'])
        ],
        'pilot_tag': 'Pilot model',
        'pilot_title': 'What the first pilot should prove',
        'pilot_points': [
            'Government can define and approve one usable national address standard.',
            'Field teams can capture roads, buildings, and coordinates in a repeatable workflow.',
            'The registry can search, verify, and print official address records reliably.',
            'At least one ministry workflow, one emergency-response use case, and one utility/logistics use case can operate against the pilot data.',
            'Leadership can see measurable coverage, verification rate, backlog, and rollout cost signals before national expansion.'
        ],
        'pilot_callout': 'Recommended pilot geography: priority zones of Malabo, one government-service-heavy district, one fast-growing urban area, and one controlled zone in Oyala/Ciudad de la Paz to prove future-city readiness.',
        'legal_tag': 'Legal and regulatory framework',
        'legal_title': 'The registry needs legal force, not only software',
        'legal_cards': [
            ('National authority model', 'The State should designate the lead authority that approves address standards, naming rules, numbering policy, and inter-agency usage obligations.'),
            ('Municipal execution boundaries', 'Municipalities should participate in street naming, local validation, and maintenance reporting under a common national standard rather than inventing incompatible local systems.'),
            ('Proof-of-address status', 'The program should define when an address record becomes valid for residence proof, utility onboarding, inspection, delivery, and administrative correspondence.'),
            ('Appeals and corrections', 'A formal process should exist for disputes over names, numbering, duplicates, parcel conflicts, and resident correction requests.')
        ],
        'legal_points': [
            'A decree, regulation, or equivalent mandate should define ownership of the standard, approval authority, update rights, and institutional obligations to use the registry.',
            'Street naming, building numbering, and district zoning rules should be documented with version control and publication discipline.',
            'The legal layer should clarify how the address registry interacts with cadastral, land, tax, census, and municipal records.',
            'No national rollout should happen without a clear rulebook for authority, appeal, and update responsibility.'
        ],
        'signage_tag': 'Physical rollout and signage',
        'signage_title': 'The physical layer must be operationally real',
        'signage_cards': [
            ('Street and district signage', 'The program should define sign formats, reflectivity, materials, installation standards, maintenance cycles, and replacement workflow for damaged or missing signage.'),
            ('Building numbering operations', 'Number assignment rules should handle compounds, corner plots, apartment blocks, commercial floors, informal clusters, and future subdivisions without collapsing into inconsistency.'),
            ('Pilot-to-scale installation model', 'Digital registry launch can precede full national signage completion, but physical rollout sequencing should still be planned by zone, contractor, and inspection batch.'),
            ('Field QA and acceptance', 'Every installed sign and numbered building cluster should be auditable against approved records, photo evidence, and field acceptance reports.')
        ],
        'signage_points': [
            'Fabrication specifications should be standardized nationally to avoid fragmented designs and inconsistent quality.',
            'Installation contractors should work against survey-ready zone packets rather than ad hoc instructions.',
            'A replacement and vandalism-response workflow should be planned from the beginning, not after loss starts accumulating.',
            'Physical signage inventory should stay linked to registry IDs for traceability and future maintenance.'
        ],
        'integration_tag': 'Detailed integration model',
        'integration_title': 'The address system must plug into real operations',
        'integration_cards': [
            ('Postal transformation', 'Postal workflows should move from vague routing toward address-backed sorting, route planning, delivery confirmation, and service-coverage improvement.'),
            ('Emergency dispatch', 'Police, fire, and ambulance teams should receive searchable address references, zone logic, and dispatch-grade location identifiers in their operational tools.'),
            ('Utilities and field maintenance', 'Electricity, water, sanitation, telecom, and meter teams should link service points to verified address records to reduce failed visits and orphan records.'),
            ('Land, tax, and planning systems', 'Cadastral, permitting, taxation, and planning workflows should reconcile parcels and buildings against the address backbone rather than maintaining separate place identities.'),
            ('Citizen channels', 'Call centers, service counters, web lookup, printed proofs, SMS/WhatsApp notices, and assisted verification channels should all reference the same official record.'),
            ('Private-sector enablement', 'Approved APIs and data-access contracts should support logistics, banks, insurers, e-commerce operators, and large employers without compromising registry control.')
        ],
        'operations_tag': 'National operating model',
        'operations_title': 'Software alone will not run the system',
        'operations_cards': [
            ('Field workforce model', 'Enumerators, supervisors, QA leads, municipal validators, and central registry operators should each have defined responsibilities, escalation paths, and daily reporting structure.'),
            ('Training and certification', 'Field and office users should be trained on capture standards, verification rules, exception handling, and safe use of devices and data.'),
            ('Zone-based rollout command', 'The country should be divided into manageable operational zones with clear readiness gates, progress reporting, and acceptance sign-off before scale expansion.'),
            ('Service desk and registry operations', 'A national service desk should manage correction requests, duplicate investigations, access provisioning, support incidents, and controlled record updates.')
        ],
        'operations_points': [
            'Device inventories, SIM/data plans, transport planning, and supervision ratios should be budgeted as operating realities, not hidden assumptions.',
            'A daily and weekly reporting cadence should measure capture volume, validation quality, exceptions, and blocked zones.',
            'Field teams should work from approved basemaps, task packs, and naming/numbering rules rather than informal personal judgment.',
            'The operating model should support both pilot execution and long-term national maintenance after rollout.'
        ],
        'quality_tag': 'Data quality and lifecycle control',
        'quality_title': 'Bad records at scale become a national liability',
        'quality_cards': [
            ('Confidence and verification states', 'Every record should carry status markers such as captured, pending review, approved, disputed, corrected, retired, or superseded.'),
            ('Duplicate and conflict handling', 'The platform should flag overlapping coordinates, conflicting names, suspicious numbering gaps, and disputed parcel/building relationships before publication.'),
            ('Update governance', 'New developments, demolitions, rezoning, and administrative renaming events should feed a controlled update pipeline with audit history.'),
            ('Revalidation cycle', 'The system should include periodic re-checks for fast-changing urban areas so address records stay useful instead of becoming stale after first launch.')
        ],
        'quality_points': [
            'Quality assurance should use scorecards, photo review, sampling, and supervisor spot checks.',
            'Each province or city batch should clear acceptance thresholds before being declared operational.',
            'A national correction log should prevent quiet data drift and unmanaged local edits.',
            'Version history should support legal defensibility and operational trust.'
        ],
        'hosting_tag': 'Infrastructure and continuity posture',
        'hosting_title': 'A sovereign registry needs continuity planning',
        'hosting_cards': [
            ('Hosting model choice', 'Government should choose deliberately between sovereign hosting, trusted local data-center operation, hybrid cloud, or another approved model based on control, resilience, and procurement reality.'),
            ('Disaster recovery', 'Backups are not enough. The program should define recovery objectives, failover procedures, secure restore drills, and continuity responsibilities.'),
            ('Access control and security hardening', 'Authentication, role boundaries, encryption, key custody, endpoint management, and logging policy should be treated as essential infrastructure controls.'),
            ('Monitoring and audit readiness', 'System health, sync failures, suspicious edits, API usage, field-upload backlog, and outage events should be observable in near real time.')
        ],
        'hosting_points': [
            'The registry should not depend on unmanaged contractor laptops, private spreadsheets, or undocumented exports.',
            'Business continuity planning should cover both digital outages and field-operations disruption.',
            'Security review should include administrative abuse, API misuse, device loss, and unauthorized record manipulation.',
            'Operations should be measurable enough for ministerial oversight and future audits.'
        ],
        'risk_tag': 'Program risks and mitigation',
        'risk_title': 'The hard parts should be named early',
        'risk_cards': [
            ('Institutional fragmentation', 'Risk: ministries or municipalities create parallel address lists. Mitigation: one national standard, formal mandate, and integration obligations.'),
            ('Poor field consistency', 'Risk: teams capture inconsistent names, numbering, or coordinates. Mitigation: strong training, QA sampling, approval gates, and zone supervision.'),
            ('Political or community disputes', 'Risk: contested street names, district boundaries, or numbering decisions delay adoption. Mitigation: defined appeal process and staged validation.'),
            ('Stale registry after launch', 'Risk: records decay if no maintenance workflow exists. Mitigation: permanent operating model, change pipeline, and annual update funding.')
        ],
        'investment_tag': 'Investment model',
        'investment_title': 'Indicative planning budget for discussion',
        'investment_rows': [
            ('Program discovery + standards', 'Legal/administrative model, address standard, data schema, pilot governance, operational blueprint.', '$500,000 - $800,000'),
            ('Platform architecture + registry build', 'Core registry, map layer, dashboard, search, verification workflow, and hosting foundation.', '$1,200,000 - $1,800,000'),
            ('Field capture tools + operations', 'Enumerator app, offline capture, devices/process readiness, QA workflow, team management.', '$800,000 - $1,200,000'),
            ('Pilot field execution', 'Pilot-zone survey, verification, signage planning data, and controlled rollout support.', '$1,800,000 - $2,800,000'),
            ('Integrations + agency onboarding', 'Postal, emergency, utility, planning, and reporting workflow onboarding for the pilot stage.', '$500,000 - $900,000'),
            ('Security, training, and stabilization', 'Role security, backups, monitoring, training, documentation, and initial support.', '$400,000 - $700,000'),
            ('Indicative 9-month pilot envelope', 'Discussion budget before formal field survey and procurement refinement.', '$5,200,000 - $8,200,000')
        ],
        'budget_note': 'These figures reflect a top-band sovereign-infrastructure pricing posture for a serious government pilot, not a final procurement quote. Final cost depends on pilot geography, field-team size, existing base maps, hardware approach, signage scope, hosting/security posture, procurement structure, political delivery model, and ministry integration depth.',
        'commercial_tag': 'Commercial structure',
        'commercial_title': 'Suggested engagement structure',
        'commercial_cards': [
            ('Option A — Strategic design + pilot leadership', 'Lead standards, architecture, product design, vendor orchestration, and pilot operating model while government controls implementation approvals.'),
            ('Option B — Build + pilot execution support', 'Deliver the platform, coordinate the pilot system rollout, train teams, and support first agency integrations under a defined mandate.'),
            ('Option C — Government task-force advisory', 'Support a ministry-led or presidency-backed task force with technical direction, scope definition, procurement shaping, and architecture review.')
        ],
        'assumptions_tag': 'Assumptions and boundaries',
        'assumptions_title': 'What this proposal assumes',
        'assumptions': [
            'Government remains the owner of the national address registry and policy standards.',
            'Final administrative authority for naming and numbering must be defined clearly before large-scale rollout.',
            'Existing municipal, cadastral, or utility records may be incomplete and should be treated as inputs to verify, not truth to copy blindly.',
            'National signage manufacture and installation can be phased separately from digital registry launch if needed.',
            'This proposal does not assume that all agencies integrate on day one; the system should launch in controlled layers.',
            'Final procurement, legal review, and territorial policy decisions remain with government.'
        ],
        'next_tag': 'Recommendation',
        'next_title': 'Recommended next step',
        'next_text': 'Approve a structured discovery and pilot-design mandate first. The immediate objective should not be a premature nationwide rollout. It should be to define standards properly, choose pilot territories intelligently, build the national registry foundation, prove operational value in the field, and create evidence for scaled expansion with government confidence.',
        'next_quote': 'The right first win is not “we launched a map.” The right first win is “government can now identify, verify, search, and use addresses in real operations with confidence.”',
        'footer_brand': 'National Digital Addressing System Proposal',
        'table_headers': ('Layer', 'Capability', 'National value'),
        'investment_headers': ('Workstream', 'Coverage', 'Budget range'),
        'cover_letter': {
            'kicker': 'Confidential forwarding letter',
            'title': 'Cover Letter',
            'subtitle': 'Submission of the National Digital Addressing System Proposal for Equatorial Guinea',
            'meta': 'Prepared by Benjamin Bob Bechiro<br/>Phone: +240 555 605 331<br/>Email: bechirobob@gmail.com<br/>Date: June 2026',
            'recipient': 'To: The Ministry of Transportation, Republic of Equatorial Guinea',
            'subject': 'Subject: Submission of proposal for a National Digital Addressing System',
            'body': [
                'At the request of the Vice President, I respectfully submit the attached proposal to the Ministry of Transportation for consideration.',
                'The purpose of this submission is to present a serious, government-owned path for creating a national address registry, geospatial service layer, field-capture model, and operational rollout structure that can support public administration, emergency response, utilities, logistics, planning, and long-term digital modernization.',
                'This proposal is intentionally framed as national infrastructure rather than a narrow software product. It is designed to help the State define standards correctly, prove value through a disciplined pilot, and build the institutional and operational foundations required for trusted nationwide expansion.',
                'I would be honored to present the proposal formally, clarify the recommended pilot scope, and support any next-stage discussion concerning standards, governance, implementation structure, or national rollout planning.',
                'Thank you for your time, consideration, and service to the Republic of Equatorial Guinea.'
            ],
            'signoff': 'Respectfully,',
            'signature': 'Benjamin Bob Bechiro<br/>Project Initiator'
        }
    },
    'es': {
        'proposal_filename': 'equatorial-guinea-national-digital-addressing-proposal-es.html',
        'cover_filename': 'equatorial-guinea-national-digital-addressing-cover-letter-es.html',
        'title': 'Propuesta del Sistema Nacional de Direcciones Digitales',
        'kicker': 'Propuesta confidencial de discusión',
        'subtitle': 'Un programa nacional de infraestructura de direcciones, propiedad del Estado, para Guinea Ecuatorial — otorgando a cada vivienda, edificio, empresa, institución y punto de servicio una dirección física y digital oficial.',
        'prepared_for': 'Preparado para el Ministerio de Transportes por solicitud del Vicepresidente',
        'purpose': 'Objetivo: establecer un registro nacional de direcciones y una capa geoespacial de servicio que apoye la distribución postal, la respuesta de emergencia, la planificación, la logística, los servicios públicos, los servicios digitales del Estado y la modernización nacional.',
        'prepared_by': 'Preparado por: Benjamin Bob Bechiro<br/>Iniciador del proyecto<br/>Teléfono: +240 555 605 331<br/>Correo: bechirobob@gmail.com<br/>Fecha: junio de 2026',
        'founder_tag': 'Nota del autor',
        'founder_title': 'Una propuesta patriótica de infraestructura para el orden nacional, la visibilidad y la prestación de servicios',
        'founder_lead': 'Todo Estado moderno y serio necesita una forma confiable de identificar lugares. Sin un sistema de direcciones fiable, las viviendas siguen siendo difíciles de localizar, los servicios siguen siendo difíciles de prestar y la planificación nacional permanece más lenta, más manual y menos controlable de lo que debería.',
        'founder_quote': 'Carreteras, viviendas, edificios públicos, empresas y futuras ciudades ya existen. Lo que falta es un lenguaje nacional compartido de localización en el que puedan confiar y que puedan utilizar el gobierno, los ciudadanos, los equipos de emergencia, los mensajeros, los servicios públicos y los inversores.',
        'founder_p1': 'Esta propuesta no trata solo de colocar placas en las calles. Trata de construir una capa nacional de identidad de ubicación: un sistema autoritativo para la numeración de viviendas, la denominación de calles, el registro de edificios, la geolocalización, la codificación postal y la verificación buscable de direcciones.',
        'founder_p2': 'Un país que desea una logística más fuerte, una mejor respuesta de emergencia, registros más limpios, servicios públicos más eficientes y un entorno empresarial más preparado para la inversión no debe dejar las direcciones en un estado informal o fragmentado. La dirección es infraestructura fundamental.',
        'founder_p3': 'Guinea Ecuatorial tiene la oportunidad de hacerlo con dignidad y disciplina: empezar con un piloto controlado, definir correctamente los estándares, mantener la propiedad gubernamental del registro y escalar por fases con trazabilidad y realismo operativo.',
        'profile': 'Perfil del iniciador del proyecto: Benjamin Bob Bechiro cursó la educación secundaria en Archimedes International College en Accra, Ghana, donde fue Jefe del Departamento de Ciencias en su último año. Posee un Diploma en Ingeniería de Software por la University of Staffordshire y una Licenciatura Honorífica en Ingeniería de Software por Coventry University en el Reino Unido. Su trabajo tecnológico privado incluye plataformas terminadas para Joscol y Martínez Hermanos, enfocadas en comercio digital, operaciones, flujos de trabajo y sistemas de prestación de servicios.',
        'signature': 'Respetuosamente presentado,',
        'signature_body': 'Benjamin Bob Bechiro<br/>Iniciador del proyecto<br/>Teléfono: +240 555 605 331<br/>Correo: bechirobob@gmail.com',
        'summary_tag': 'Resumen ejecutivo',
        'summary_title': 'No es un proyecto de mapa: es una capa operativa nacional de direcciones',
        'summary_lead': 'El programa recomendado es un Sistema Nacional de Direcciones Digitales por fases, liderado por el Estado y diseñado para convertirse en la fuente autoritativa de identidad de localización en toda Guinea Ecuatorial.',
        'summary_cards': [
            ('Para los ciudadanos', ['Conocer y compartir una dirección oficial clara.', 'Recibir entregas, visitas de servicios públicos y respuesta de emergencia con mayor fiabilidad.', 'Verificar y corregir registros de dirección mediante un canal controlado.']),
            ('Para ministerios y municipios', ['Mantener un solo registro confiable en lugar de listas locales fragmentadas.', 'Supervisar cobertura, verificación, vacíos y avance de campo.', 'Conectar las direcciones con permisos, impuestos, censo, tierras y flujos de servicio.']),
            ('Para logística y servicios públicos', ['Reducir entregas y visitas fallidas.', 'Planificar rutas, zonas y despacho con coordenadas verificadas.', 'Integrar APIs de direcciones aprobadas en las operaciones con el tiempo.']),
            ('Para el liderazgo nacional', ['Crear visibilidad medible sobre la cobertura territorial.', 'Apoyar la planificación urbana, las decisiones de infraestructura y la preparación de servicios públicos.', 'Reforzar la soberanía digital mediante un registro propiedad del Estado.'])
        ],
        'core_proposal': 'Propuesta central: aprobar un piloto de 9 meses que cubra estándares, captura de campo, construcción del registro e integración inicial de servicios públicos en zonas prioritarias de Malabo, y después escalar hacia un despliegue nacional por fases de 3 años en Bata, Oyala/Ciudad de la Paz y todas las provincias.',
        'why_tag': 'Por qué ahora',
        'why_title': 'El país necesita una forma confiable de identificar lugares',
        'why_intro': 'Las direcciones afectan mucho más que el correo. Un sistema débil ralentiza casi todos los servicios que dependen de encontrar correctamente a personas, propiedades o instalaciones.',
        'stats': [
            ('Servicios públicos', 'Necesitan certeza de ubicación para permisos, inspecciones, notificaciones y respuesta.'),
            ('Respuesta de emergencia', 'Necesita identificación rápida y sin ambigüedad de edificios y rutas.'),
            ('Servicios públicos básicos', 'Necesitan puntos de servicio precisos para instalación, registros de medidores y mantenimiento.'),
            ('Comercio y logística', 'Necesitan direcciones confiables para despacho, entrega y conciliación.'),
            ('Planificación y censo', 'Necesitan unidades territoriales consistentes y registros verificados de edificios.'),
            ('Ciudades futuras', 'No deben heredar confusión de direcciones basada en papel.')
        ],
        'numbers_mean': 'Qué significa esto',
        'numbers_points': [
            'Si las direcciones siguen siendo informales, todos los servicios digitales construidos sobre ellas serán más débiles y más costosos de operar.',
            'Un registro nacional de direcciones debe tratarse como infraestructura fundamental, al mismo nivel que carreteras, catastro y directorios de servicio público.',
            'Un flujo de trabajo móvil para el terreno es obligatorio porque la verificación ocurre en el territorio, no solo en oficinas.',
            'La gobernanza de datos y las reglas de verificación importan tanto como el software. Un mal registro a gran escala se convierte en un problema nacional.'
        ],
        'opportunity_tag': 'Oportunidad nacional',
        'opportunity_title': 'Oyala / Ciudad de la Paz debe nacer preparada para direcciones formales',
        'opportunity_lead': 'Una capital administrativa orientada al futuro no debe depender de indicaciones vagas, puntos de referencia improvisados y registros locales desconectados. Debe abrir con un modelo formal de identidad de localización ya integrado en sus operaciones.',
        'opportunity_quote': 'Si una nueva capital representa el futuro de la nación, entonces cada parcela, edificio, carretera, sede ministerial y punto de servicio dentro de ella debe ser identificable, buscable y preparado para el servicio desde el diseño.',
        'opportunity_cards': [
            ('Administración pública digital por defecto', 'Permisos, inspecciones, notificaciones públicas y coordinación interministerial funcionan mejor cuando las ubicaciones están formalmente identificadas.'),
            ('Preparación para emergencia y seguridad', 'Los equipos de respuesta necesitan referencias precisas de edificios, lógica de rutas y conocimiento de zonas, especialmente en distritos administrativos en expansión.'),
            ('Prestación de infraestructuras y servicios', 'Agua, electricidad, telecomunicaciones, carreteras, saneamiento y mantenimiento se benefician inmediatamente de registros listos para el servicio.'),
            ('Confianza de inversores y residentes', 'Una ciudad fácil de navegar, verificar y atender proyecta seriedad y madurez administrativa.')
        ],
        'platform_tag': 'Modelo de plataforma',
        'platform_title': 'Qué debe contener el sistema nacional',
        'platform_rows': [
            ('Registro nacional de direcciones', 'Registros autoritativos de edificios, parcelas, calles y zonas con jerarquía administrativa y estado de verificación.', 'Aporta una sola fuente nacional de verdad.'),
            ('Capa geoespacial', 'Mapa interactivo de carreteras, distritos, edificios, parcelas, puntos de referencia y puntos de servicio.', 'Hace utilizable el registro tanto en campo como en oficinas de planificación.'),
            ('Aplicación de captura de campo', 'Flujo móvil/tableta para que los enumeradores capturen edificios, fotos, coordenadas, propuestas de nombres y estado de validación.', 'Permite un despliegue territorial estructurado y captura offline.'),
            ('Motor de códigos de dirección', 'Genera formatos oficiales de dirección, códigos cortos, etiquetas imprimibles y referencias de señalización.', 'Mantiene estándares consistentes entre ministerios y municipios.'),
            ('Panel de operaciones', 'Métricas de cobertura, colas de aprobación, detección de duplicados, productividad de equipos, retrasos de verificación e informes.', 'Da visibilidad y control operativo al liderazgo.'),
            ('Acceso ciudadano e institucional', 'Búsqueda, verificación, solicitud de corrección, impresión de comprobantes y acceso API aprobado para operadores de servicios.', 'Impulsa adopción real más allá del registro mismo.'),
            ('Pasarela de integración', 'Interfaces controladas para correos, servicios básicos, emergencias, impuestos, tierras, planificación y logística.', 'Evita que el sistema de direcciones se convierta en una base de datos aislada.')
        ],
        'benefits_tag': 'Ventajas nacionales',
        'benefits_title': 'Por qué beneficia a todo el país',
        'benefits_lead': 'Un buen sistema de direcciones es una infraestructura silenciosa: cuando funciona, todo lo que está encima se vuelve más fácil de encontrar, enrutar, verificar, inspeccionar, entregar y mejorar.',
        'benefits_cards': [
            ('Mejor prestación de servicios públicos', 'Las agencias pueden emitir, inspeccionar, enrutar y dar seguimiento con una identidad de localización más clara.'),
            ('Respuesta de emergencia más rápida', 'Ambulancias, policía y bomberos obtienen un modelo operativo de referencia más fiable.'),
            ('Actividad económica más fuerte', 'Empresas, repartidores y proveedores pierden menos tiempo intentando localizar personas y lugares.'),
            ('Registros nacionales más limpios', 'Propiedad, tierras, permisos, cuentas de servicio y censo obtienen una columna vertebral común de direcciones.'),
            ('Turismo y navegación', 'Los visitantes entienden mejor cómo llegar a hoteles, oficinas, eventos y servicios con menos fricción.'),
            ('Soberanía digital', 'El Estado mantiene la propiedad y control de un conjunto de datos nacionales estratégicos.')
        ],
        'roadmap_tag': 'Hoja de ruta',
        'roadmap_title': 'Despliegue por fases recomendado',
        'timeline': [
            ('Fase 1', 'Estándares + diseño del piloto', '3 meses', 'Definir estándares de dirección, modelo de gobernanza, esquema de datos, reglas de señalización, zonas piloto, metodología de campo y modelo operativo ministerial.'),
            ('Fase 2', 'Captura piloto + construcción del registro', '6 meses', 'Capturar calles y edificios en zonas piloto, verificar nombres/números, lanzar el registro y conectar primeros flujos de trabajo gubernamentales.'),
            ('Fase 3', 'Escala Malabo + Bata', '9-12 meses', 'Expandir a distritos urbanos prioritarios, reforzar paneles e incorporar servicios públicos, respuesta de emergencia y flujos postales.'),
            ('Fase 4', 'Expansión nacional', '12-24 meses', 'Desplegar provincia por provincia con control de contratistas, QA, capacitación e integraciones aprobadas.'),
            ('Fase 5', 'Operación de largo plazo', 'Continuo', 'Mantener el registro, gobernar actualizaciones, soportar nuevos desarrollos y evolucionar integraciones institucionales.')
        ],
        'governance_tag': 'Gobernanza y seguridad',
        'governance_title': 'Esto debe tratarse como infraestructura nacional de confianza',
        'gov_cards': [
            ('Propiedad estatal del registro', ['La base de datos central de direcciones debe permanecer bajo control formal del Estado.', 'Los proveedores externos pueden apoyar la ejecución, pero no deben poseer la fuente nacional de verdad.']),
            ('Modelo de dirección interministerial', ['Transporte, interior/administración local, planificación, tierras, correos, telecomunicaciones, emergencias y municipios deben alinear estándares desde el inicio.', 'Es necesario un patrocinador principal, pero el sistema sirve a muchas instituciones.']),
            ('Verificación antes de publicar', ['Ningún registro de edificio debe considerarse autoritativo sin reglas definidas de validación.', 'Duplicados, conflictos de nombres y coordenadas no verificadas deben controlarse operativamente.']),
            ('Seguridad y trazabilidad', ['Acceso por roles, bitácoras de cambios, copias de seguridad, manejo de incidentes e historial de aprobaciones son obligatorios.', 'Los datos estratégicos de localización no deben dispersarse en hojas de cálculo personales o silos de contratistas.'])
        ],
        'pilot_tag': 'Modelo piloto',
        'pilot_title': 'Qué debe demostrar el primer piloto',
        'pilot_points': [
            'Que el gobierno puede definir y aprobar un estándar nacional de dirección utilizable.',
            'Que los equipos de campo pueden capturar carreteras, edificios y coordenadas con un flujo repetible.',
            'Que el registro puede buscar, verificar e imprimir direcciones oficiales de forma fiable.',
            'Que al menos un flujo ministerial, un caso de uso de emergencia y un caso de utilidad/logística pueden operar sobre los datos piloto.',
            'Que el liderazgo puede ver cobertura medible, tasa de verificación, atrasos y señales de coste antes de la expansión nacional.'
        ],
        'pilot_callout': 'Geografía piloto recomendada: zonas prioritarias de Malabo, un distrito con alta concentración de servicios públicos, un área urbana en crecimiento y una zona controlada en Oyala/Ciudad de la Paz para demostrar preparación de ciudad futura.',
        'legal_tag': 'Marco legal y regulatorio',
        'legal_title': 'El registro necesita fuerza legal, no solo software',
        'legal_cards': [
            ('Modelo de autoridad nacional', 'El Estado debe designar la autoridad principal que aprueba los estándares de dirección, las reglas de denominación, la política de numeración y las obligaciones de uso interinstitucional.'),
            ('Límites de ejecución municipal', 'Los municipios deben participar en la denominación de calles, la validación local y el reporte de mantenimiento bajo un estándar nacional común, no inventando sistemas incompatibles.'),
            ('Valor oficial del comprobante de dirección', 'El programa debe definir cuándo un registro de dirección se considera válido para residencia, contratación de servicios, inspecciones, entregas y correspondencia administrativa.'),
            ('Apelaciones y correcciones', 'Debe existir un proceso formal para disputas sobre nombres, numeración, duplicados, conflictos parcelarios y solicitudes de corrección de residentes.')
        ],
        'legal_points': [
            'Un decreto, reglamento o mandato equivalente debe definir la propiedad del estándar, la autoridad de aprobación, los derechos de actualización y las obligaciones institucionales de uso del registro.',
            'La denominación de calles, la numeración de edificios y las reglas de zonificación distrital deben documentarse con control de versiones y disciplina de publicación.',
            'La capa legal debe aclarar cómo interactúa el registro de direcciones con catastro, tierras, impuestos, censo y registros municipales.',
            'No debe haber despliegue nacional sin un reglamento claro sobre autoridad, apelación y responsabilidad de actualización.'
        ],
        'signage_tag': 'Despliegue físico y señalización',
        'signage_title': 'La capa física debe ser operativamente real',
        'signage_cards': [
            ('Señalización de calles y distritos', 'El programa debe definir formatos, reflectividad, materiales, estándares de instalación, ciclos de mantenimiento y flujo de reposición para señalización dañada o ausente.'),
            ('Operación de numeración de edificios', 'Las reglas de asignación deben manejar recintos, esquinas, bloques de apartamentos, plantas comerciales, agrupaciones informales y futuras subdivisiones sin caer en inconsistencia.'),
            ('Modelo de instalación del piloto a la escala', 'El lanzamiento del registro digital puede preceder a la finalización total de la señalización nacional, pero la secuencia física igualmente debe planificarse por zona, contratista y lote de inspección.'),
            ('QA de campo y aceptación', 'Cada señal instalada y cada grupo numerado de edificios debe poder auditarse contra registros aprobados, evidencia fotográfica e informes de aceptación de campo.')
        ],
        'signage_points': [
            'Las especificaciones de fabricación deben estandarizarse a nivel nacional para evitar diseños fragmentados y calidad inconsistente.',
            'Los contratistas de instalación deben trabajar con paquetes zonales listos para levantamiento, no con instrucciones improvisadas.',
            'Debe planificarse desde el principio un flujo de reposición y respuesta ante vandalismo.',
            'El inventario físico de señalización debe permanecer vinculado a los IDs del registro para trazabilidad y mantenimiento futuro.'
        ],
        'integration_tag': 'Modelo detallado de integración',
        'integration_title': 'El sistema de direcciones debe conectarse con operaciones reales',
        'integration_cards': [
            ('Transformación postal', 'Los flujos postales deben pasar de rutas vagas a clasificación, planeamiento de ruta, confirmación de entrega y mejora de cobertura apoyados en direcciones.'),
            ('Despacho de emergencias', 'Policía, bomberos y ambulancias deben recibir referencias buscables, lógica de zonas e identificadores de localización aptos para despacho dentro de sus herramientas operativas.'),
            ('Servicios públicos y mantenimiento de campo', 'Electricidad, agua, saneamiento, telecomunicaciones y equipos de medición deben vincular puntos de servicio con registros verificados para reducir visitas fallidas y registros huérfanos.'),
            ('Tierras, impuestos y planificación', 'Catastro, permisos, tributación y planificación deben reconciliar parcelas y edificios con la columna vertebral de direcciones en lugar de mantener identidades de lugar separadas.'),
            ('Canales al ciudadano', 'Centros de llamadas, ventanillas, búsqueda web, comprobantes impresos, avisos por SMS/WhatsApp y canales asistidos de verificación deben referenciar el mismo registro oficial.'),
            ('Habilitación del sector privado', 'APIs aprobadas y contratos de acceso a datos deben apoyar logística, bancos, aseguradoras, comercio electrónico y grandes empleadores sin perder el control estatal del registro.')
        ],
        'operations_tag': 'Modelo operativo nacional',
        'operations_title': 'El software por sí solo no operará el sistema',
        'operations_cards': [
            ('Modelo de fuerza de campo', 'Enumeradores, supervisores, líderes de QA, validadores municipales y operadores centrales del registro deben tener responsabilidades definidas, rutas de escalado y estructura diaria de reporte.'),
            ('Formación y certificación', 'Usuarios de campo y de oficina deben formarse en estándares de captura, reglas de verificación, manejo de excepciones y uso seguro de dispositivos y datos.'),
            ('Comando de despliegue por zonas', 'El país debe dividirse en zonas operables con puertas de preparación, reporte de avance y aceptación firmada antes de expandirse.'),
            ('Mesa de servicio y operación del registro', 'Una mesa de servicio nacional debe gestionar correcciones, investigaciones de duplicados, provisión de accesos, incidencias de soporte y actualizaciones controladas.')
        ],
        'operations_points': [
            'Inventario de dispositivos, planes de datos/SIM, transporte y ratios de supervisión deben presupuestarse como realidades operativas, no como supuestos ocultos.',
            'Un ritmo diario y semanal de informes debe medir volumen de captura, calidad de validación, excepciones y zonas bloqueadas.',
            'Los equipos de campo deben trabajar desde mapas base aprobados, paquetes de tareas y reglas de denominación/numeración, no desde juicio informal personal.',
            'El modelo operativo debe sostener tanto la ejecución piloto como el mantenimiento nacional de largo plazo.'
        ],
        'quality_tag': 'Calidad de datos y control de ciclo de vida',
        'quality_title': 'Los malos registros a escala se convierten en una responsabilidad nacional',
        'quality_cards': [
            ('Estados de confianza y verificación', 'Cada registro debe llevar estados como capturado, pendiente de revisión, aprobado, en disputa, corregido, retirado o sustituido.'),
            ('Manejo de duplicados y conflictos', 'La plataforma debe señalar coordenadas superpuestas, nombres conflictivos, huecos sospechosos de numeración y relaciones disputadas entre parcela y edificio antes de publicar.'),
            ('Gobernanza de actualizaciones', 'Nuevos desarrollos, demoliciones, rezonificación y cambios administrativos de nombre deben alimentar una canalización controlada de actualización con historial auditable.'),
            ('Ciclo de revalidación', 'El sistema debe incluir revisiones periódicas en áreas urbanas de cambio rápido para que los registros sigan siendo útiles y no queden obsoletos tras el primer lanzamiento.')
        ],
        'quality_points': [
            'La garantía de calidad debe usar scorecards, revisión fotográfica, muestreo y controles puntuales de supervisores.',
            'Cada lote provincial o urbano debe superar umbrales de aceptación antes de declararse operativo.',
            'Un registro nacional de correcciones debe impedir deriva silenciosa de datos y ediciones locales sin control.',
            'El historial de versiones debe apoyar la defensa legal y la confianza operativa.'
        ],
        'hosting_tag': 'Infraestructura y continuidad',
        'hosting_title': 'Un registro soberano necesita planificación de continuidad',
        'hosting_cards': [
            ('Elección del modelo de hosting', 'El gobierno debe elegir deliberadamente entre hosting soberano, centro de datos local confiable, nube híbrida u otro modelo aprobado según control, resiliencia y realidad de contratación.'),
            ('Recuperación ante desastres', 'Los backups no bastan. El programa debe definir objetivos de recuperación, procedimientos de failover, pruebas seguras de restauración y responsabilidades de continuidad.'),
            ('Control de acceso y endurecimiento de seguridad', 'Autenticación, límites por rol, cifrado, custodia de claves, gestión de endpoints y política de logs deben tratarse como controles esenciales de infraestructura.'),
            ('Monitoreo y preparación para auditoría', 'La salud del sistema, fallos de sincronización, ediciones sospechosas, uso de API, retrasos de carga de campo y eventos de caída deben ser observables casi en tiempo real.')
        ],
        'hosting_points': [
            'El registro no debe depender de portátiles no gestionados, hojas de cálculo privadas o exportaciones sin documentación.',
            'La continuidad de negocio debe cubrir tanto caídas digitales como interrupciones de operación de campo.',
            'La revisión de seguridad debe incluir abuso administrativo, mal uso de API, pérdida de dispositivos y manipulación no autorizada de registros.',
            'La operación debe ser medible al nivel que exige la supervisión ministerial y futuras auditorías.'
        ],
        'risk_tag': 'Riesgos del programa y mitigación',
        'risk_title': 'Las partes difíciles deben nombrarse desde el inicio',
        'risk_cards': [
            ('Fragmentación institucional', 'Riesgo: ministerios o municipios crean listas paralelas. Mitigación: estándar nacional único, mandato formal y obligaciones de integración.'),
            ('Baja consistencia de campo', 'Riesgo: los equipos capturan nombres, numeración o coordenadas inconsistentes. Mitigación: formación fuerte, muestreo QA, puertas de aprobación y supervisión zonal.'),
            ('Disputas políticas o comunitarias', 'Riesgo: conflictos sobre nombres de calles, límites distritales o numeración retrasan la adopción. Mitigación: proceso definido de apelación y validación escalonada.'),
            ('Registro obsoleto tras el lanzamiento', 'Riesgo: los datos se degradan si no existe flujo de mantenimiento. Mitigación: modelo operativo permanente, canal de cambios y financiación anual de actualización.')
        ],
        'investment_tag': 'Modelo de inversión',
        'investment_title': 'Presupuesto indicativo de planificación para discusión',
        'investment_rows': [
            ('Descubrimiento del programa + estándares', 'Modelo legal/administrativo, estándar de dirección, esquema de datos, gobernanza piloto y plano operativo.', '$500,000 - $800,000'),
            ('Arquitectura de plataforma + construcción del registro', 'Registro central, capa cartográfica, panel, búsqueda, verificación y base de hosting.', '$1,200,000 - $1,800,000'),
            ('Herramientas de campo + operaciones', 'App de enumeradores, captura offline, preparación de dispositivos/procesos, QA y gestión de equipos.', '$800,000 - $1,200,000'),
            ('Ejecución del piloto', 'Levantamiento en zonas piloto, verificación, datos para señalización y soporte al despliegue controlado.', '$1,800,000 - $2,800,000'),
            ('Integraciones + incorporación institucional', 'Correos, emergencias, servicios básicos, planificación e incorporación de informes para la etapa piloto.', '$500,000 - $900,000'),
            ('Seguridad, capacitación y estabilización', 'Seguridad por roles, backups, monitoreo, formación, documentación y soporte inicial.', '$400,000 - $700,000'),
            ('Envolvente indicativa del piloto de 9 meses', 'Presupuesto de discusión antes del afinamiento formal de campo y contratación.', '$5,200,000 - $8,200,000')
        ],
        'budget_note': 'Estas cifras reflejan una postura de precio de banda alta para infraestructura soberana en un piloto gubernamental serio, no una cotización final de contratación. El coste final depende de la geografía del piloto, el tamaño de los equipos de campo, la calidad cartográfica existente, el enfoque de hardware, el alcance de la señalización, la postura de hosting/seguridad, la estructura de contratación, el modelo político de ejecución y la profundidad de integración ministerial.',
        'commercial_tag': 'Estructura de colaboración',
        'commercial_title': 'Modalidad sugerida de compromiso',
        'commercial_cards': [
            ('Opción A — Diseño estratégico + liderazgo del piloto', 'Dirigir estándares, arquitectura, diseño de producto, orquestación de proveedores y modelo operativo piloto mientras el gobierno controla aprobaciones de implementación.'),
            ('Opción B — Construcción + apoyo a la ejecución del piloto', 'Entregar la plataforma, coordinar el despliegue del sistema piloto, formar equipos y apoyar las primeras integraciones institucionales bajo un mandato definido.'),
            ('Opción C — Asesoría a una comisión gubernamental', 'Apoyar una comisión liderada por el ministerio o respaldada por la Presidencia con dirección técnica, definición de alcance, estructuración de contratación y revisión de arquitectura.')
        ],
        'assumptions_tag': 'Supuestos y límites',
        'assumptions_title': 'Qué asume esta propuesta',
        'assumptions': [
            'El gobierno sigue siendo propietario del registro nacional de direcciones y de los estándares de política.',
            'La autoridad administrativa final para nombrar y numerar debe definirse claramente antes del despliegue a gran escala.',
            'Los registros municipales, catastrales o de servicios existentes pueden estar incompletos y deben tratarse como insumos a verificar, no como verdad para copiar ciegamente.',
            'La fabricación e instalación nacional de señalización puede desarrollarse por separado del lanzamiento del registro digital si es necesario.',
            'Esta propuesta no supone que todas las instituciones se integren el día uno; el sistema debe lanzarse por capas controladas.',
            'La contratación final, la revisión legal y las decisiones de política territorial corresponden al gobierno.'
        ],
        'next_tag': 'Recomendación',
        'next_title': 'Siguiente paso recomendado',
        'next_text': 'Aprobar primero un mandato estructurado de descubrimiento y diseño del piloto. El objetivo inmediato no debe ser un despliegue nacional prematuro. Debe ser definir bien los estándares, elegir inteligentemente los territorios piloto, construir la base del registro nacional, demostrar valor operativo en el terreno y generar evidencia para una expansión escalada con confianza gubernamental.',
        'next_quote': 'La primera victoria correcta no es “lanzamos un mapa”. La primera victoria correcta es “el gobierno ya puede identificar, verificar, buscar y usar direcciones en operaciones reales con confianza”.',
        'footer_brand': 'Propuesta del Sistema Nacional de Direcciones Digitales',
        'table_headers': ('Capa', 'Capacidad', 'Valor nacional'),
        'investment_headers': ('Área de trabajo', 'Cobertura', 'Rango presupuestario'),
        'cover_letter': {
            'kicker': 'Carta confidencial de remisión',
            'title': 'Carta de Presentación',
            'subtitle': 'Remisión de la propuesta del Sistema Nacional de Direcciones Digitales para Guinea Ecuatorial',
            'meta': 'Preparado por Benjamin Bob Bechiro<br/>Teléfono: +240 555 605 331<br/>Correo: bechirobob@gmail.com<br/>Fecha: junio de 2026',
            'recipient': 'A: El Ministerio de Transportes de la República de Guinea Ecuatorial',
            'subject': 'Asunto: Remisión de propuesta para un Sistema Nacional de Direcciones Digitales',
            'body': [
                'Por solicitud del Vicepresidente, someto respetuosamente la propuesta adjunta al Ministerio de Transportes para su consideración.',
                'El objetivo de esta remisión es presentar una vía seria, de propiedad estatal, para crear un registro nacional de direcciones, una capa geoespacial de servicio, un modelo de captura de campo y una estructura operativa de despliegue que pueda apoyar la administración pública, la respuesta de emergencia, los servicios públicos, la logística, la planificación y la modernización digital de largo plazo.',
                'Esta propuesta está planteada deliberadamente como infraestructura nacional y no como un producto de software estrecho. Está diseñada para ayudar al Estado a definir correctamente los estándares, demostrar valor mediante un piloto disciplinado y construir las bases institucionales y operativas necesarias para una expansión nacional confiable.',
                'Sería un honor poder presentar formalmente la propuesta, aclarar el alcance recomendado del piloto y apoyar cualquier conversación posterior relacionada con estándares, gobernanza, estructura de implementación o planificación del despliegue nacional.',
                'Gracias por su tiempo, su consideración y su servicio a la República de Guinea Ecuatorial.'
            ],
            'signoff': 'Respetuosamente,',
            'signature': 'Benjamin Bob Bechiro<br/>Iniciador del proyecto'
        }
    }
}


def list_html(items):
    return ''.join(f'<li>{item}</li>' for item in items)


def list_paragraphs(items):
    return ''.join(f'<p>{item}</p>' for item in items)


def summary_cards(cards):
    return ''.join(f'<div class="card"><h3>{title}</h3><ul>{list_html(items)}</ul></div>' for title, items in cards)


def generic_cards(cards):
    return ''.join(f'<div class="card"><h3>{title}</h3><p>{body}</p></div>' for title, body in cards)


def governance_cards(cards):
    return ''.join(f'<div class="card"><h3>{title}</h3><ul>{list_html(bullets)}</ul></div>' for title, bullets in cards)


def stat_cards(stats):
    return ''.join(f'<div class="card"><div class="stat">{title}</div><div class="statlabel">{body}</div></div>' for title, body in stats)


def investment_rows(rows):
    out = []
    for title, coverage, cost in rows[:-1]:
        out.append(f'<tr><td>{title}</td><td>{coverage}</td><td>{cost}</td></tr>')
    total = rows[-1]
    out.append(f'<tr><td><strong>{total[0]}</strong></td><td><strong>{total[1]}</strong></td><td><strong>{total[2]}</strong></td></tr>')
    return ''.join(out)


def timeline_rows(rows):
    return ''.join(
        f'<div class="phase"><strong>{phase}</strong><div><strong>{title}</strong><br>{body}</div><div class="price">{duration}</div></div>'
        for phase, title, duration, body in rows
    )


def platform_rows(rows):
    return ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in rows)


def render_proposal(lang: str) -> str:
    c = CONTENT[lang]
    h1, h2, h3 = c['table_headers']
    ih1, ih2, ih3 = c['investment_headers']
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{c['title']}</title>
<link rel="icon" href="data:," />
<style>{CSS}</style>
</head>
<body>
<section class="page cover">
  <div>
    <div class="flagline"><span class="green"></span><span class="white"></span><span class="red"></span><span class="blue"></span></div>
    <div class="kicker">{c['kicker']}</div>
    <h1>{c['title']}</h1>
    <p class="subtitle">{c['subtitle']}</p>
  </div>
  <div class="cover-meta">
    <p><strong>{c['prepared_for']}</strong></p>
    <p>{c['purpose']}</p>
    <p>{c['prepared_by']}</p>
  </div>
</section>
<section class="page">
  <span class="section-tag">{c['founder_tag']}</span>
  <h2>{c['founder_title']}</h2>
  <p class="lead">{c['founder_lead']}</p>
  <div class="callout"><p class="quote">{c['founder_quote']}</p></div>
  <p>{c['founder_p1']}</p>
  <p>{c['founder_p2']}</p>
  <p>{c['founder_p3']}</p>
  <div class="callout"><p><strong>{c['profile']}</strong></p></div>
  <div class="signature"><p><strong>{c['signature']}</strong></p><p>{c['signature_body']}</p></div>
  <div class="footer"><span>{c['footer_brand']}</span><span>2</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['summary_tag']}</span>
  <h2>{c['summary_title']}</h2>
  <p class="lead">{c['summary_lead']}</p>
  <div class="grid grid-2">{summary_cards(c['summary_cards'])}</div>
  <div class="callout"><p><strong>{c['core_proposal']}</strong></p></div>
  <div class="footer"><span>{c['summary_tag']}</span><span>3</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['why_tag']}</span>
  <h2>{c['why_title']}</h2>
  <p>{c['why_intro']}</p>
  <div class="grid grid-3">{stat_cards(c['stats'])}</div>
  <h3>{c['numbers_mean']}</h3>
  <ul>{list_html(c['numbers_points'])}</ul>
  <div class="footer"><span>{c['why_tag']}</span><span>4</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['opportunity_tag']}</span>
  <h2>{c['opportunity_title']}</h2>
  <p class="lead">{c['opportunity_lead']}</p>
  <div class="callout"><p class="quote">{c['opportunity_quote']}</p></div>
  <div class="grid grid-2">{generic_cards(c['opportunity_cards'])}</div>
  <div class="footer"><span>{c['opportunity_tag']}</span><span>5</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['platform_tag']}</span>
  <h2>{c['platform_title']}</h2>
  <table>
    <thead><tr><th>{h1}</th><th>{h2}</th><th>{h3}</th></tr></thead>
    <tbody>{platform_rows(c['platform_rows'])}</tbody>
  </table>
  <div class="footer"><span>{c['platform_tag']}</span><span>6</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['benefits_tag']}</span>
  <h2>{c['benefits_title']}</h2>
  <p class="lead">{c['benefits_lead']}</p>
  <div class="grid grid-2">{generic_cards(c['benefits_cards'])}</div>
  <div class="footer"><span>{c['benefits_tag']}</span><span>7</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['roadmap_tag']}</span>
  <h2>{c['roadmap_title']}</h2>
  <div class="timeline">{timeline_rows(c['timeline'])}</div>
  <div class="footer"><span>{c['roadmap_tag']}</span><span>8</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['governance_tag']}</span>
  <h2>{c['governance_title']}</h2>
  <div class="grid grid-2">{governance_cards(c['gov_cards'])}</div>
  <h2 style="margin-top:18px">{c['pilot_tag']}: {c['pilot_title']}</h2>
  <ul>{list_html(c['pilot_points'])}</ul>
  <div class="callout"><p>{c['pilot_callout']}</p></div>
  <div class="footer"><span>{c['governance_tag']}</span><span>9</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['legal_tag']}</span>
  <h2>{c['legal_title']}</h2>
  <div class="grid grid-2">{generic_cards(c['legal_cards'])}</div>
  <ul>{list_html(c['legal_points'])}</ul>
  <div class="footer"><span>{c['legal_tag']}</span><span>10</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['signage_tag']}</span>
  <h2>{c['signage_title']}</h2>
  <div class="grid grid-2">{generic_cards(c['signage_cards'])}</div>
  <ul>{list_html(c['signage_points'])}</ul>
  <div class="footer"><span>{c['signage_tag']}</span><span>11</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['integration_tag']}</span>
  <h2>{c['integration_title']}</h2>
  <div class="grid grid-2">{generic_cards(c['integration_cards'])}</div>
  <div class="footer"><span>{c['integration_tag']}</span><span>12</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['operations_tag']}</span>
  <h2>{c['operations_title']}</h2>
  <div class="grid grid-2">{generic_cards(c['operations_cards'])}</div>
  <ul>{list_html(c['operations_points'])}</ul>
  <div class="footer"><span>{c['operations_tag']}</span><span>13</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['quality_tag']}</span>
  <h2>{c['quality_title']}</h2>
  <div class="grid grid-2">{generic_cards(c['quality_cards'])}</div>
  <ul>{list_html(c['quality_points'])}</ul>
  <div class="footer"><span>{c['quality_tag']}</span><span>14</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['hosting_tag']}</span>
  <h2>{c['hosting_title']}</h2>
  <div class="grid grid-2">{generic_cards(c['hosting_cards'])}</div>
  <ul>{list_html(c['hosting_points'])}</ul>
  <div class="footer"><span>{c['hosting_tag']}</span><span>15</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['risk_tag']}</span>
  <h2>{c['risk_title']}</h2>
  <div class="grid grid-2">{generic_cards(c['risk_cards'])}</div>
  <div class="footer"><span>{c['risk_tag']}</span><span>16</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['investment_tag']}</span>
  <h2>{c['investment_title']}</h2>
  <table>
    <thead><tr><th>{ih1}</th><th>{ih2}</th><th>{ih3}</th></tr></thead>
    <tbody>{investment_rows(c['investment_rows'])}</tbody>
  </table>
  <p class="small">{c['budget_note']}</p>
  <div class="footer"><span>{c['investment_tag']}</span><span>17</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['commercial_tag']}</span>
  <h2>{c['commercial_title']}</h2>
  <div class="grid grid-3">{generic_cards(c['commercial_cards'])}</div>
  <h2 style="margin-top:18px">{c['assumptions_tag']}</h2>
  <div class="card tight"><ul>{list_html(c['assumptions'])}</ul></div>
  <div class="footer"><span>{c['commercial_tag']}</span><span>18</span></div>
</section>
<section class="page">
  <span class="section-tag">{c['next_tag']}</span>
  <h2>{c['next_title']}</h2>
  <p class="lead">{c['next_text']}</p>
  <div class="callout"><p class="quote">{c['next_quote']}</p></div>
  <div class="footer"><span>{c['next_tag']}</span><span>19</span></div>
</section>
</body>
</html>'''


def render_cover_letter(lang: str) -> str:
    c = CONTENT[lang]['cover_letter']
    parent = CONTENT[lang]
    section_tag = 'Formal forwarding note' if lang == 'en' else 'Nota formal de remisión'
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{c['title']}</title>
<link rel="icon" href="data:," />
<style>{CSS}</style>
</head>
<body>
<section class="page">
  <div class="flagline"><span class="green"></span><span class="white"></span><span class="red"></span><span class="blue"></span></div>
  <div class="kicker" style="color:#0b315f;">{c['kicker']}</div>
  <h1 style="color:#0b315f; max-width:160mm; margin-bottom:10px;">{c['title']}</h1>
  <p class="subtitle" style="color:#31445f; margin-bottom:12px;">{c['subtitle']}</p>
  <div class="letter-meta" style="margin-bottom:20px;"><p>{c['meta']}</p></div>
  <span class="section-tag">{section_tag}</span>
  <div class="letter-body">
    <p class="recipient"><strong>{c['recipient']}</strong></p>
    <p><strong>{c['subject']}</strong></p>
    {list_paragraphs(c['body'])}
    <div class="signature">
      <p><strong>{c['signoff']}</strong></p>
      <p>{c['signature']}<br/>Phone: +240 555 605 331<br/>Email: bechirobob@gmail.com</p>
    </div>
  </div>
  <div class="footer"><span>{parent['footer_brand']}</span><span>1</span></div>
</section>
</body>
</html>'''


for lang in ('en', 'es'):
    proposal_path = OUT / CONTENT[lang]['proposal_filename']
    cover_path = OUT / CONTENT[lang]['cover_filename']
    proposal_path.write_text(render_proposal(lang), encoding='utf-8')
    cover_path.write_text(render_cover_letter(lang), encoding='utf-8')
    print(proposal_path)
    print(cover_path)
