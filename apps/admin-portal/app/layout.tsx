import 'leaflet/dist/leaflet.css';
import './globals.css';
import './citizen-geotag-map.css';
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
