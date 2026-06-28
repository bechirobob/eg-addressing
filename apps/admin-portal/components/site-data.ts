export type OperatorRole = 'guest' | 'viewer' | 'editor' | 'admin';

type NavItem = {
  href: string;
  label: string;
  visibleTo: OperatorRole[];
  priorityFor: OperatorRole[];
};

type RouteRule = {
  path: string;
  allowedRoles: OperatorRole[];
};

export const navItems: NavItem[] = [
  {
    href: '/',
    label: 'Platform overview',
    visibleTo: ['guest', 'viewer', 'editor', 'admin'],
    priorityFor: ['guest', 'viewer'],
  },
  {
    href: '/login',
    label: 'Admin sign-in',
    visibleTo: ['guest'],
    priorityFor: ['guest'],
  },
  {
    href: '/reports',
    label: 'Reporting dashboard',
    visibleTo: ['guest', 'viewer', 'editor', 'admin'],
    priorityFor: ['guest', 'viewer', 'editor', 'admin'],
  },
  {
    href: '/verify',
    label: 'Verification portal',
    visibleTo: ['editor', 'admin'],
    priorityFor: ['admin'],
  },
  {
    href: '/field',
    label: 'Field operations',
    visibleTo: ['editor', 'admin'],
    priorityFor: ['editor'],
  },
  {
    href: '/registry',
    label: 'Registry core',
    visibleTo: ['editor', 'admin'],
    priorityFor: ['editor', 'admin'],
  },
  {
    href: '/territories',
    label: 'Territory registry',
    visibleTo: ['editor', 'admin'],
    priorityFor: ['editor'],
  },
  {
    href: '/exports',
    label: 'Publication ops',
    visibleTo: ['admin'],
    priorityFor: ['admin'],
  },
];

export const statusHighlights = [
  'National digital public infrastructure posture',
  'Restrained state identity and trusted institutional presentation',
  'Operational service surfaces for registry, field, and verification work',
];

const routeRules: RouteRule[] = [
  { path: '/', allowedRoles: ['guest', 'viewer', 'editor', 'admin'] },
  { path: '/login', allowedRoles: ['guest', 'viewer', 'editor', 'admin'] },
  { path: '/reports', allowedRoles: ['guest', 'viewer', 'editor', 'admin'] },
  { path: '/verify', allowedRoles: ['editor', 'admin'] },
  { path: '/field', allowedRoles: ['editor', 'admin'] },
  { path: '/registry', allowedRoles: ['editor', 'admin'] },
  { path: '/territories', allowedRoles: ['editor', 'admin'] },
  { path: '/exports', allowedRoles: ['admin'] },
];

export function defaultRouteForRole(role: OperatorRole): string {
  if (role === 'admin') return '/verify';
  if (role === 'editor') return '/registry';
  return '/reports';
}

export function isRouteAccessible(pathname: string, role: OperatorRole): boolean {
  const rule = routeRules.find((item) => item.path === pathname);
  if (!rule) {
    return true;
  }
  return rule.allowedRoles.includes(role);
}

export function routeNeedsResolvedSession(pathname: string): boolean {
  const rule = routeRules.find((item) => item.path === pathname);
  if (!rule) {
    return false;
  }
  return !rule.allowedRoles.includes('guest');
}
