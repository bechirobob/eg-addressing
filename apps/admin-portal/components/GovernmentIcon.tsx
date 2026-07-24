import type { ReactNode, SVGProps } from 'react';

export type GovernmentIconName =
  | 'home'
  | 'operations'
  | 'registry'
  | 'mapping'
  | 'field'
  | 'verification'
  | 'publication'
  | 'agencies'
  | 'analytics'
  | 'administration'
  | 'system'
  | 'reports'
  | 'search'
  | 'menu'
  | 'signout'
  | 'territory'
  | 'alert'
  | 'published'
  | 'corrections'
  | 'readiness'
  | 'records';

type GovernmentIconProps = Omit<SVGProps<SVGSVGElement>, 'children'> & {
  name: GovernmentIconName;
  title?: string;
};

function iconPaths(name: GovernmentIconName): ReactNode {
  switch (name) {
    case 'home':
      return <><path d="M3 10.5 12 3l9 7.5" /><path d="M5 9.5V21h14V9.5" /><path d="M9 21v-7h6v7" /></>;
    case 'operations':
      return <><path d="M5 5h14v14H5z" /><path d="M8 9h8M8 13h8M8 17h5" /><path d="m3 8 1.5 1.5L7 7" /></>;
    case 'registry':
      return <><ellipse cx="12" cy="5" rx="7" ry="3" /><path d="M5 5v6c0 1.7 3.1 3 7 3s7-1.3 7-3V5" /><path d="M5 11v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6" /></>;
    case 'mapping':
      return <><path d="m3 6 5-2 8 3 5-2v13l-5 2-8-3-5 2z" /><path d="M8 4v13M16 7v13" /></>;
    case 'field':
      return <><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" /><circle cx="12" cy="10" r="2.5" /><path d="m8.5 15.5 2 2 4-4" /></>;
    case 'verification':
      return <><path d="M8 4h8l2 3v14H6V7z" /><path d="M9 4V2h6v2" /><path d="m9 13 2 2 4-5" /></>;
    case 'publication':
      return <><path d="M6 3h9l3 3v15H6z" /><path d="M15 3v4h4" /><path d="M9 11h6M9 15h4" /><circle cx="16.5" cy="17.5" r="3" /></>;
    case 'agencies':
      return <><path d="M3 21h18" /><path d="M5 21V9h14v12" /><path d="m4 9 8-5 8 5" /><path d="M8 13h2M14 13h2M8 17h2M14 17h2" /></>;
    case 'analytics':
    case 'reports':
      return <><path d="M4 20V10M10 20V4M16 20v-7M22 20H2" /><path d="m4 8 6-4 6 5 5-4" /></>;
    case 'administration':
      return <><circle cx="9" cy="8" r="3" /><path d="M3.5 20v-2.5A4.5 4.5 0 0 1 8 13h2a4.5 4.5 0 0 1 4.5 4.5V20" /><circle cx="18" cy="8" r="2" /><path d="M16 14h2.5a3 3 0 0 1 3 3V20" /></>;
    case 'system':
      return <><circle cx="12" cy="12" r="3" /><path d="M12 2v3M12 19v3M4.9 4.9 7 7M17 17l2.1 2.1M2 12h3M19 12h3M4.9 19.1 7 17M17 7l2.1-2.1" /></>;
    case 'search':
      return <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>;
    case 'menu':
      return <><path d="M4 7h16M4 12h16M4 17h16" /></>;
    case 'signout':
      return <><path d="M10 4H5v16h5" /><path d="M14 8l4 4-4 4M18 12H9" /></>;
    case 'territory':
      return <><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9S14.5 18.4 12 21c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3Z" /></>;
    case 'alert':
      return <><path d="M12 3 2.8 20h18.4z" /><path d="M12 9v5M12 17.5h.01" /></>;
    case 'published':
      return <><path d="M5 3h10l4 4v14H5z" /><path d="M15 3v5h5" /><path d="m8 15 2.3 2.3L16 11.5" /></>;
    case 'corrections':
      return <><path d="M4 7h11a5 5 0 0 1 0 10H8" /><path d="m8 13-4 4 4 4" /><path d="M20 7 17 4l-3 3" /></>;
    case 'readiness':
      return <><path d="M4 20h16" /><path d="M6 16v4M10 12v8M14 8v12M18 4v16" /><path d="m5 11 4-4 4 2 6-6" /></>;
    case 'records':
      return <><path d="M4 5h5l2 2h9v12H4z" /><path d="M8 11h8M8 15h6" /></>;
    default:
      return null;
  }
}

export function GovernmentIcon({ name, title, className, ...props }: GovernmentIconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      role={title ? 'img' : undefined}
      aria-hidden={title ? undefined : true}
      focusable="false"
      {...props}
    >
      {title ? <title>{title}</title> : null}
      {iconPaths(name)}
    </svg>
  );
}
