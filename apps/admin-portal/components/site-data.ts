export type OperatorRole = 'guest' | 'viewer' | 'editor' | 'admin';

export type NavGroup = 'public' | 'staff';

type NavItem = {
  href: string;
  label: string;
  visibleTo: OperatorRole[];
  priorityFor: OperatorRole[];
  group: NavGroup;
};

type RouteRule = {
  path: string;
  allowedRoles: OperatorRole[];
};

export const navGroupLabels: Record<NavGroup, string> = {
  public: 'Public',
  staff: 'Staff services',
};

export const navItems: NavItem[] = [
  {
    href: '/geotag',
    label: 'Register location',
    visibleTo: ['guest', 'viewer', 'editor', 'admin'],
    priorityFor: ['guest'],
    group: 'public',
  },
  {
    href: '/issue',
    label: 'Check address code',
    visibleTo: ['guest', 'viewer', 'editor', 'admin'],
    priorityFor: ['viewer'],
    group: 'public',
  },
  {
    href: '/track',
    label: 'Track request',
    visibleTo: ['guest', 'viewer', 'editor', 'admin'],
    priorityFor: ['guest', 'viewer'],
    group: 'public',
  },
  {
    href: '/login',
    label: 'Sign in',
    visibleTo: [],
    priorityFor: [],
    group: 'public',
  },
  {
    href: '/signage',
    label: 'Publication & signage',
    visibleTo: ['editor', 'admin'],
    priorityFor: ['admin', 'editor'],
    group: 'staff',
  },
  {
    href: '/verify',
    label: 'Review queue',
    visibleTo: [],
    priorityFor: ['admin'],
    group: 'staff',
  },
  {
    href: '/field',
    label: 'Field work',
    visibleTo: ['editor', 'admin'],
    priorityFor: ['editor'],
    group: 'staff',
  },
  {
    href: '/registry',
    label: 'Address registry',
    visibleTo: ['editor', 'admin'],
    priorityFor: ['editor', 'admin'],
    group: 'staff',
  },
  {
    href: '/records',
    label: 'Case files',
    visibleTo: [],
    priorityFor: ['viewer', 'editor', 'admin'],
    group: 'staff',
  },
  {
    href: '/territories',
    label: 'Territories',
    visibleTo: [],
    priorityFor: ['editor'],
    group: 'staff',
  },
  {
    href: '/reports',
    label: 'Reports',
    visibleTo: ['guest', 'viewer', 'editor', 'admin'],
    priorityFor: ['guest', 'viewer', 'editor', 'admin'],
    group: 'staff',
  },
  {
    href: '/exports',
    label: 'Publication & signage',
    visibleTo: [],
    priorityFor: ['admin'],
    group: 'staff',
  },
];

export const statusHighlights = [
  'Government-owned address records',
  'GPS-first citizen registration',
  'Operator review before public use',
];

const routeRules: RouteRule[] = [
  { path: '/', allowedRoles: ['guest', 'viewer', 'editor', 'admin'] },
  { path: '/login', allowedRoles: ['guest', 'viewer', 'editor', 'admin'] },
  { path: '/reports', allowedRoles: ['guest', 'viewer', 'editor', 'admin'] },
  { path: '/issue', allowedRoles: ['guest', 'viewer', 'editor', 'admin'] },
  { path: '/track', allowedRoles: ['guest', 'viewer', 'editor', 'admin'] },
  { path: '/geotag', allowedRoles: ['guest', 'viewer', 'editor', 'admin'] },
  { path: '/verify', allowedRoles: ['editor', 'admin'] },
  { path: '/field', allowedRoles: ['editor', 'admin'] },
  { path: '/registry', allowedRoles: ['editor', 'admin'] },
  { path: '/records', allowedRoles: ['viewer', 'editor', 'admin'] },
  { path: '/territories', allowedRoles: ['editor', 'admin'] },
  { path: '/exports', allowedRoles: ['admin'] },
  { path: '/signage', allowedRoles: ['editor', 'admin'] },
];

export function defaultRouteForRole(role: OperatorRole): string {
  if (role === 'admin') return '/field';
  if (role === 'editor') return '/registry';
  if (role === 'viewer') return '/reports';
  return '/';
}

export function isRouteAccessible(pathname: string, role: OperatorRole): boolean {
  const rule = routeRules.find((item) => item.path === pathname || pathname.startsWith('/code/'));
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
