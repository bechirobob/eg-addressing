import 'leaflet/dist/leaflet.css';
import './globals.css';
import './government-design-tokens.css';
import './operator-shell.css';
import './operator-workspace-redesign.css';
import './operator-workspace-authoritative.css';
import './operator-workspace-overflow.css';
import './operator-presentation-polish.css';
import './operator-presentation-final.css';
import './operator-presentation-last-mile.css';
import './operator-presentation-field-fix.css';
import './operator-presentation-field-stack.css';
import './operator-presentation-field-label.css';
import './operator-presentation-nav-cleanup.css';
import './government-workspace.css';
import './government-operations-workbench.css';
import type { Metadata } from 'next';
import type { ReactNode } from 'react';

export const metadata: Metadata = {
  title: 'Equatorial Guinea National Addressing Platform',
  description: 'National digital addressing platform for official registry, verification, field operations, and institutional coordination.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
