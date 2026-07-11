export type OperatorRole = 'guest' | 'viewer' | 'editor' | 'admin' | 'agency_viewer';

export type NavGroup = 'public' | 'staff' | 'admin';

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
  admin: 'Admin area',
};

export const navItems: NavItem[] = [
  {
    href: '/geotag',
    label: 'Register location',
    visibleTo: ['guest', 'viewer', 'editor', 'admin', 'agency_viewer'],
    priorityFor: ['guest'],
    group: 'public',
  },
  {
    href: '/issue',
    label: 'Check address code',
    visibleTo: ['guest', 'viewer', 'editor', 'admin', 'agency_viewer'],
    priorityFor: ['viewer'],
    group: 'public',
  },
  {
    href: '/track',
    label: 'Track request',
    visibleTo: ['guest', 'viewer', 'editor', 'admin', 'agency_viewer'],
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
    visibleTo: ['viewer', 'editor', 'admin', 'agency_viewer'],
    priorityFor: ['guest', 'viewer', 'editor', 'admin', 'agency_viewer'],
    group: 'staff',
  },
  {
    href: '/exports',
    label: 'Publication & signage',
    visibleTo: [],
    priorityFor: ['admin'],
    group: 'staff',
  },
  {
    href: '/admin/staff?from=staff-services',
    label: 'Admin area',
    visibleTo: ['admin'],
    priorityFor: [],
    group: 'staff',
  },
  {
    href: '/admin/staff',
    label: 'Staff account control',
    visibleTo: ['admin'],
    priorityFor: ['admin'],
    group: 'admin',
  },
];

export const statusHighlights = [
  'Government-owned address records',
  'GPS-first citizen registration',
  'Operator review before public use',
];

const routeRules: RouteRule[] = [
  { path: '/', allowedRoles: ['guest', 'viewer', 'editor', 'admin', 'agency_viewer'] },
  { path: '/login', allowedRoles: ['guest', 'viewer', 'editor', 'admin', 'agency_viewer'] },
  { path: '/reports', allowedRoles: ['viewer', 'editor', 'admin', 'agency_viewer'] },
  { path: '/issue', allowedRoles: ['guest', 'viewer', 'editor', 'admin', 'agency_viewer'] },
  { path: '/track', allowedRoles: ['guest', 'viewer', 'editor', 'admin', 'agency_viewer'] },
  { path: '/geotag', allowedRoles: ['guest', 'viewer', 'editor', 'admin', 'agency_viewer'] },
  { path: '/verify', allowedRoles: ['editor', 'admin'] },
  { path: '/field', allowedRoles: ['editor', 'admin'] },
  { path: '/registry', allowedRoles: ['editor', 'admin'] },
  { path: '/records', allowedRoles: ['viewer', 'editor', 'admin'] },
  { path: '/territories', allowedRoles: ['editor', 'admin'] },
  { path: '/exports', allowedRoles: ['admin'] },
  { path: '/admin', allowedRoles: ['admin'] },
  { path: '/admin/staff', allowedRoles: ['admin'] },
  { path: '/signage', allowedRoles: ['editor', 'admin'] },
];

const PUBLIC_PREFIXES = ['/code/', '/proof/'];
const PROTECTED_PREFIXES = ['/admin', '/reports', '/exports', '/registry', '/verify', '/field', '/signage', '/records', '/territories'];

function normalizePathname(pathname: string): string {
  const [withoutQuery] = pathname.split(/[?#]/, 1);
  if (withoutQuery.length > 1 && withoutQuery.endsWith('/')) return withoutQuery.slice(0, -1);
  return withoutQuery || '/';
}

export function defaultRouteForRole(role: OperatorRole): string {
  if (role === 'admin') return '/field';
  if (role === 'editor') return '/registry';
  if (role === 'viewer' || role === 'agency_viewer') return '/reports';
  return '/';
}

export function isRouteAccessible(pathname: string, role: OperatorRole): boolean {
  const normalized = normalizePathname(pathname);
  const rule = routeRules.find((item) => item.path === normalized);
  if (rule) {
    return rule.allowedRoles.includes(role);
  }
  if (PUBLIC_PREFIXES.some((prefix) => normalized.startsWith(prefix))) {
    return true;
  }
  const protectedPrefix = PROTECTED_PREFIXES.find((prefix) => normalized === prefix || normalized.startsWith(`${prefix}/`));
  if (protectedPrefix) {
    const baseRule = routeRules.find((item) => item.path === protectedPrefix);
    return Boolean(baseRule?.allowedRoles.includes(role));
  }
  return true;
}

export function routeNeedsResolvedSession(pathname: string): boolean {
  const normalized = normalizePathname(pathname);
  const rule = routeRules.find((item) => item.path === normalized);
  if (rule) {
    return !rule.allowedRoles.includes('guest');
  }
  const protectedPrefix = PROTECTED_PREFIXES.find((prefix) => normalized === prefix || normalized.startsWith(`${prefix}/`));
  if (!protectedPrefix) {
    return false;
  }
  const baseRule = routeRules.find((item) => item.path === protectedPrefix);
  return Boolean(baseRule && !baseRule.allowedRoles.includes('guest'));
}
