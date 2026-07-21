'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import type { ReactNode } from 'react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

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

type TranslationKey = Parameters<ReturnType<typeof useTranslation>['t']>[0];

function roleFromSession(role: Exclude<OperatorRole, 'guest'> | undefined, status: 'loading' | 'ready' | 'guest'): OperatorRole {
  if (status === 'guest' || !role) return 'guest';
  return role;
}

function navLabelKey(href: string) {
  const labels: Record<string, TranslationKey> = {
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
  const labels: Record<keyof typeof navGroupLabels, TranslationKey> = {
    public: 'navPublic',
    staff: 'navStaff',
    admin: 'navAdmin',
  };
  return labels[group];
}

function normalizedRoute(href: string) {
  return href.split(/[?#]/, 1)[0] || '/';
}

function routeIsActive(route: string, currentRoute: string) {
  return route === currentRoute || (route !== '/' && currentRoute.startsWith(`${route}/`));
}

function humanizeRole(role: string) {
  return role
    .split('_')
    .filter(Boolean)
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(' ');
}

const STAFF_SESSION_ROUTES = ['/field', '/registry', '/signage', '/reports', '/exports', '/territories', '/verify', '/records', '/admin/staff'] as const;

function isStaffSessionRoute(pathname: string) {
  return STAFF_SESSION_ROUTES.some((route) => pathname === route || pathname.startsWith(`${route}/`));
}

export function RoleAwareChrome({ apiBaseUrl, children, skipSessionLookup = false }: RoleAwareChromeProps) {
  const { t } = useTranslation();
  const router = useRouter();
  const pathname = usePathname();
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { sessionUser, sessionStatus, reloadSession } = useStoredSession(browserApiBaseUrl, { enabled: !skipSessionLookup });
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [forcedGuest, setForcedGuest] = useState(false);
  const [mobileNavigationOpen, setMobileNavigationOpen] = useState(false);
  const mobileMenuButtonRef = useRef<HTMLButtonElement>(null);
  const mobileNavigationRef = useRef<HTMLElement>(null);

  const effectiveSessionUser = forcedGuest ? null : sessionUser;
  const effectiveSessionStatus = forcedGuest ? 'guest' : sessionStatus;

  const role = roleFromSession(effectiveSessionUser?.role, effectiveSessionStatus);
  const currentRoute = pathname || '/';
  const waitingForAccessResolution = effectiveSessionStatus === 'loading' && routeNeedsResolvedSession(currentRoute);
  const accessAllowed = effectiveSessionStatus === 'loading' ? true : isRouteAccessible(currentRoute, role);
  const isProtectedWorkspace = role !== 'guest' && isStaffSessionRoute(currentRoute);

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
    setMobileNavigationOpen(false);
  }, [currentRoute]);

  useEffect(() => {
    if (!mobileNavigationOpen) return;

    const navigation = mobileNavigationRef.current;
    const focusable = Array.from(
      navigation?.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])') ?? [],
    );
    const firstFocusable = focusable[0];
    const lastFocusable = focusable[focusable.length - 1];
    const previousBodyOverflow = document.body.style.overflow;

    document.body.style.overflow = 'hidden';
    firstFocusable?.focus();

    function handleDrawerKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        event.preventDefault();
        setMobileNavigationOpen(false);
        mobileMenuButtonRef.current?.focus();
        return;
      }

      if (event.key !== 'Tab' || !firstFocusable || !lastFocusable) return;
      if (event.shiftKey && document.activeElement === firstFocusable) {
        event.preventDefault();
        lastFocusable.focus();
      } else if (!event.shiftKey && document.activeElement === lastFocusable) {
        event.preventDefault();
        firstFocusable.focus();
      }
    }

    document.addEventListener('keydown', handleDrawerKeyDown);
    return () => {
      document.removeEventListener('keydown', handleDrawerKeyDown);
      document.body.style.overflow = previousBodyOverflow;
    };
  }, [mobileNavigationOpen]);

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
  const staffSessionUser = effectiveSessionStatus === 'ready' && effectiveSessionUser && isStaffSessionRoute(currentRoute) ? effectiveSessionUser : null;
  const currentNavItem = visibleItems.find((item) => routeIsActive(normalizedRoute(item.href), currentRoute)) ?? null;
  const currentNavLabelKey = currentNavItem ? navLabelKey(normalizedRoute(currentNavItem.href)) : undefined;
  const currentSectionLabel = currentNavItem ? (currentNavLabelKey ? t(currentNavLabelKey) : currentNavItem.label) : t('navStaff');
  const controlNavItems: Array<{ href: string; labelKey: TranslationKey; iconClass: string }> = [
    { href: '/field', labelKey: 'navFieldWork', iconClass: 'queue' },
    { href: '/registry', labelKey: 'navAddressRegistry', iconClass: 'case-files' },
    { href: '/signage', labelKey: 'navLocationReview', iconClass: 'signage' },
    { href: '/reports', labelKey: 'navReports', iconClass: 'reports' },
    ...(role === 'admin' ? [{ href: '/admin/staff?from=mobile-staff-services', labelKey: 'navAdmin' as TranslationKey, iconClass: 'dashboard' }] : []),
  ].filter((item) => isRouteAccessible(item.href, role));

  const accessContent = waitingForAccessResolution ? (
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
  );

  function renderNavigation() {
    return (
      <nav className="top-nav grouped-top-nav" aria-label={t(role === 'guest' ? 'navPublic' : 'navStaff')}>
        {(Object.keys(navGroupLabels) as Array<keyof typeof navGroupLabels>).map((group) => {
          const items = groupedItems[group] ?? [];
          if (!items.length) return null;
          return (
            <section className="nav-group" key={group} aria-label={t(navGroupKey(group))}>
              <p className="nav-group-label">{t(navGroupKey(group))}</p>
              <div className="nav-group-links">
                {items.map((item) => {
                  const itemRoute = normalizedRoute(item.href);
                  const isActive = routeIsActive(itemRoute, currentRoute);
                  const labelKey = navLabelKey(itemRoute);
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
    );
  }

  if (isProtectedWorkspace) {
    return (
      <div className={`operator-workspace-shell chrome-role-${role}`}>
        <button
          ref={mobileMenuButtonRef}
          className="operator-mobile-menu"
          type="button"
          aria-expanded={mobileNavigationOpen}
          aria-controls="operator-primary-navigation"
          onClick={() => setMobileNavigationOpen((open) => !open)}
        >
          <span aria-hidden="true" />
          <strong>{currentSectionLabel}</strong>
        </button>

        <aside className="operator-sidebar operator-sidebar-desktop" aria-label={t('navStaff')}>
          <div className="operator-sidebar-identity">
            <Link href={workspaceHref} className="operator-platform-link">
              <span>{t('republic')}</span>
              <strong>{t('homeTitle')}</strong>
            </Link>
            {staffSessionUser ? (
              <div className="operator-role-context">
                <span>{t('signedInAs')}</span>
                <strong>{staffSessionUser.full_name}</strong>
                <small>{humanizeRole(staffSessionUser.role)}</small>
              </div>
            ) : null}
          </div>
          {renderNavigation()}
        </aside>

        <aside
          id="operator-primary-navigation"
          ref={mobileNavigationRef}
          className="operator-sidebar operator-sidebar-mobile"
          aria-label={t('navStaff')}
          hidden={!mobileNavigationOpen}
        >
          <div className="operator-sidebar-identity">
            <Link href={workspaceHref} className="operator-platform-link">
              <span>{t('republic')}</span>
              <strong>{t('homeTitle')}</strong>
            </Link>
            {staffSessionUser ? (
              <div className="operator-role-context">
                <span>{t('signedInAs')}</span>
                <strong>{staffSessionUser.full_name}</strong>
                <small>{humanizeRole(staffSessionUser.role)}</small>
              </div>
            ) : null}
          </div>
          {renderNavigation()}
        </aside>

        {mobileNavigationOpen ? (
          <button
            className="operator-navigation-scrim"
            type="button"
            aria-label={t('navStaff')}
            onClick={() => {
              setMobileNavigationOpen(false);
              mobileMenuButtonRef.current?.focus();
            }}
          />
        ) : null}

        <section className="operator-workspace-column" aria-label={currentSectionLabel}>
          <header className="operator-utility-bar">
            <div className="operator-location-context">
              <span>{t('navStaff')}</span>
              <strong>{currentSectionLabel}</strong>
            </div>
            {staffSessionUser ? (
              <div className="operator-session-utility" aria-live="polite">
                <span>{humanizeRole(staffSessionUser.role)}</span>
                <button type="button" onClick={() => void handleLogout()} disabled={isLoggingOut}>
                  {isLoggingOut ? t('signingOut') : t('signOut')}
                </button>
              </div>
            ) : null}
          </header>

          {accessContent}

          {controlNavItems.length ? (
            <nav
              className="mobile-control-nav"
              aria-label={t('navStaff')}
              style={{ gridTemplateColumns: `repeat(${controlNavItems.length}, minmax(0, 1fr))` }}
            >
              {controlNavItems.map((item) => {
                const itemRoute = normalizedRoute(item.href);
                const isActive = routeIsActive(itemRoute, currentRoute);
                return (
                  <Link key={item.href} href={item.href} className={`mobile-control-nav-link mobile-control-nav-${item.iconClass} ${isActive ? 'active' : ''}`} aria-current={isActive ? 'page' : undefined}>
                    <span aria-hidden="true" />
                    <strong>{t(item.labelKey)}</strong>
                  </Link>
                );
              })}
            </nav>
          ) : null}
        </section>
      </div>
    );
  }

  return (
    <>
      <div className={`chrome-shell chrome-role-${role}`}>
        <div className="nav-cluster grouped-nav-cluster">
          {currentRoute !== '/' ? (
            <Link href="/" className="platform-overview-link">
              <span className="platform-overview-title">{t('platformOverview')}</span>
            </Link>
          ) : null}
          {renderNavigation()}
        </div>

        {staffSessionUser ? (
          <div className="chrome-session-card chrome-session-utility" aria-live="polite">
            <span className="session-utility-role">{humanizeRole(staffSessionUser.role)}</span>
            <button className="session-utility-logout" type="button" onClick={() => void handleLogout()} disabled={isLoggingOut}>
              {isLoggingOut ? t('signingOut') : t('signOut')}
            </button>
          </div>
        ) : null}
      </div>

      {accessContent}
    </>
  );
}
