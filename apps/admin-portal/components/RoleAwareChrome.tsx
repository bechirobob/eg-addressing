'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import type { ReactNode } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { clearStoredToken } from './demoAuth';
import { useTranslation } from './i18n';
import {
  defaultRouteForRole,
  isRouteAccessible,
  navGroupLabels,
  navItems,
  routeNeedsResolvedSession,
  type OperatorRole,
} from './site-data';
import { resolveBrowserApiBaseUrl, sessionRequestInit, useStoredSession } from './sessionClient';

type RoleAwareChromeProps = {
  apiBaseUrl: string;
  children: ReactNode;
  skipSessionLookup?: boolean;
};

function roleFromSession(role: Exclude<OperatorRole, 'guest'> | undefined, status: 'loading' | 'ready' | 'guest'): OperatorRole {
  if (status === 'guest' || !role) return 'guest';
  return role;
}

function navLabelKey(href: string) {
  const labels: Record<string, Parameters<ReturnType<typeof useTranslation>['t']>[0]> = {
    '/': 'navNationalPlatform',
    '/geotag': 'navRegisterLocation',
    '/issue': 'navVerifyAddress',
    '/track': 'navTrackRequest',
    '/login': 'navSignIn',
    '/signage': 'navLocationReview',
    '/field': 'navFieldWork',
    '/registry': 'navAddressRegistry',
    '/reports': 'navReports',
    '/admin/staff': 'navStaffAccounts',
  };
  return labels[href];
}

function navGroupKey(group: keyof typeof navGroupLabels) {
  const labels: Record<keyof typeof navGroupLabels, Parameters<ReturnType<typeof useTranslation>['t']>[0]> = {
    public: 'navPublic',
    staff: 'navStaff',
    admin: 'navAdmin',
  };
  return labels[group];
}

const STAFF_SESSION_ROUTES = new Set(['/field', '/registry', '/signage', '/reports', '/exports', '/territories', '/verify', '/records', '/admin/staff']);

export function RoleAwareChrome({ apiBaseUrl, children, skipSessionLookup = false }: RoleAwareChromeProps) {
  const { t } = useTranslation();
  const router = useRouter();
  const pathname = usePathname();
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { sessionUser, sessionStatus, reloadSession } = useStoredSession(browserApiBaseUrl, { enabled: !skipSessionLookup });
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [forcedGuest, setForcedGuest] = useState(false);

  const effectiveSessionUser = forcedGuest ? null : sessionUser;
  const effectiveSessionStatus = forcedGuest ? 'guest' : sessionStatus;

  const role = roleFromSession(effectiveSessionUser?.role, effectiveSessionStatus);
  const currentRoute = pathname || '/';
  const waitingForAccessResolution = effectiveSessionStatus === 'loading' && routeNeedsResolvedSession(currentRoute);
  const accessAllowed = effectiveSessionStatus === 'loading' ? true : isRouteAccessible(currentRoute, role);

  const visibleItems = useMemo(
    () => navItems.filter((item) => item.visibleTo.includes(role) && (role === 'guest' ? item.group === 'public' : item.group !== 'public')),
    [role],
  );

  const groupedItems = useMemo(() => {
    return visibleItems.reduce<Record<string, typeof visibleItems>>((groups, item) => {
      if (!groups[item.group]) groups[item.group] = [];
      groups[item.group].push(item);
      return groups;
    }, {});
  }, [visibleItems]);

  useEffect(() => {
    if (effectiveSessionStatus === 'loading' || accessAllowed) {
      return;
    }

    router.replace(role === 'guest' ? '/login' : defaultRouteForRole(role));
  }, [accessAllowed, effectiveSessionStatus, role, router]);

  const handleLogout = useCallback(async () => {
    setIsLoggingOut(true);
    setForcedGuest(true);
    try {
      const storedToken = typeof window === 'undefined' ? null : window.localStorage.getItem('egAddressingToken');
      await fetch(`${browserApiBaseUrl}/api/v1/auth/logout`, {
        method: 'POST',
        ...sessionRequestInit(storedToken),
      });
    } catch {
      // Best-effort revoke; local cleanup still proceeds.
    }
    clearStoredToken();
    await reloadSession();
    router.replace('/login');
    router.refresh();
  }, [browserApiBaseUrl, reloadSession, router]);

  const workspaceHref = defaultRouteForRole(role);
  const staffSessionUser = effectiveSessionStatus === 'ready' && effectiveSessionUser && STAFF_SESSION_ROUTES.has(currentRoute) ? effectiveSessionUser : null;
  const controlNavItems = [
    { href: '/field', label: 'Field', iconClass: 'queue' },
    { href: '/registry', label: 'Registry', iconClass: 'case-files' },
    { href: '/signage', label: 'Signage', iconClass: 'signage' },
    { href: '/reports', label: 'Reports', iconClass: 'reports' },
  ].filter((item) => isRouteAccessible(item.href, role));

  return (
    <>
      <div className={`chrome-shell chrome-role-${role}`}>
        <div className="nav-cluster grouped-nav-cluster">
          {currentRoute !== '/' ? (
            <Link href="/" className="platform-overview-link">
              <span className="platform-overview-title">Home</span>
            </Link>
          ) : null}
          <nav className="top-nav grouped-top-nav" aria-label="Main platform navigation">
            {(Object.keys(navGroupLabels) as Array<keyof typeof navGroupLabels>).map((group) => {
              const items = groupedItems[group] ?? [];
              if (!items.length) return null;
              return (
                <section className="nav-group" key={group} aria-labelledby={`nav-group-${group}`}>
                  <p className="nav-group-label" id={`nav-group-${group}`}>{t(navGroupKey(group))}</p>
                  <div className="nav-group-links">
                    {items.map((item) => {
                      const isActive = item.href === currentRoute;
                      const labelKey = navLabelKey(item.href);
                      return (
                        <Link
                          key={item.href}
                          href={item.href}
                          className={`nav-link ${isActive ? 'nav-link-active' : ''}`}
                          aria-current={isActive ? 'page' : undefined}
                        >
                          {item.href === '/login' ? (
                            <>
                              <span className="nav-link-title">{t('navAccount')}</span>
                              <span className="nav-link-subtitle">{labelKey ? t(labelKey) : item.label}</span>
                            </>
                          ) : (
                            <span className="nav-link-title">{labelKey ? t(labelKey) : item.label}</span>
                          )}
                        </Link>
                      );
                    })}
                  </div>
                </section>
              );
            })}
          </nav>
        </div>

        {staffSessionUser ? (
          <div className="chrome-session-card chrome-session-utility" aria-live="polite">
            <span className="session-utility-role">{staffSessionUser.role}</span>
            <button className="session-utility-logout" type="button" onClick={() => void handleLogout()} disabled={isLoggingOut}>
              {isLoggingOut ? t('signingOut') : t('signOut')}
            </button>
          </div>
        ) : null}
      </div>

      {role !== 'guest' && ['/field', '/registry', '/signage', '/reports', '/exports', '/territories', '/verify'].includes(currentRoute) && controlNavItems.length ? (
        <nav className="mobile-control-nav" aria-label="Operator control navigation">
          {controlNavItems.map((item) => {
            const isActive = currentRoute === item.href;
            return (
              <Link key={item.href} href={item.href} className={`mobile-control-nav-link mobile-control-nav-${item.iconClass} ${isActive ? 'active' : ''}`} aria-current={isActive ? 'page' : undefined}>
                <span aria-hidden="true" />
                <strong>{item.label}</strong>
              </Link>
            );
          })}
        </nav>
      ) : null}

      {waitingForAccessResolution ? (
        <section className="panel panel-state-grid">
          <div className="panel-state">
            <strong>{t('checkingAccess')}</strong>
            <p>{t('checkingAccessCopy')}</p>
          </div>
        </section>
      ) : !accessAllowed ? (
        <section className="panel panel-state-grid">
          <div className="panel-state">
            <strong>{t('redirecting')}</strong>
            <p>{t('redirectingCopy')}</p>
          </div>
        </section>
      ) : (
        children
      )}
    </>
  );
}
