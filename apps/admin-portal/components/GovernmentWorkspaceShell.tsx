'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import type { ReactNode } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { clearStoredToken } from './demoAuth';
import { GovernmentIcon, type GovernmentIconName } from './GovernmentIcon';
import { isRouteAccessible, type OperatorRole } from './site-data';
import { resolveBrowserApiBaseUrl, sessionRequestInit, useStoredSession } from './sessionClient';

type GovernmentWorkspaceShellProps = {
  apiBaseUrl: string;
  attentionCount: number;
  sectionLabel?: string;
  workspaceTitle?: string;
  workContext?: string[];
  children: ReactNode;
};

type WorkspaceNavigationItem = {
  href: string;
  label: string;
  description: string;
  icon: GovernmentIconName;
};

const PRIMARY_NAVIGATION: WorkspaceNavigationItem[] = [
  { href: '/workspace', label: 'Home', description: 'Today’s work and national status', icon: 'home' },
  { href: '/field', label: 'Field Operations', description: 'Assignments, evidence, and capture', icon: 'field' },
  { href: '/registry', label: 'Registry', description: 'Authoritative address records', icon: 'registry' },
  { href: '/territories', label: 'Mapping', description: 'Territories and geographic scope', icon: 'mapping' },
  { href: '/verify', label: 'Verification', description: 'Evidence review and decisions', icon: 'verification' },
  { href: '/signage', label: 'Publication', description: 'Release control and signage', icon: 'publication' },
  { href: '/reports', label: 'Analytics', description: 'National reporting and readiness', icon: 'analytics' },
];

const CONTROL_NAVIGATION: WorkspaceNavigationItem[] = [
  { href: '/admin/staff', label: 'Administration', description: 'Personnel, access, and scope', icon: 'administration' },
  { href: '/exports', label: 'Publication Outputs', description: 'Controlled official outputs', icon: 'reports' },
];

function humanizeRole(role: string) {
  return role
    .split('_')
    .filter(Boolean)
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(' ');
}

function routeIsActive(href: string, pathname: string) {
  return href === pathname || (href !== '/workspace' && pathname.startsWith(`${href}/`));
}

export function GovernmentWorkspaceShell({
  apiBaseUrl,
  attentionCount,
  sectionLabel = 'Government workspace',
  workspaceTitle = 'National Operations',
  workContext,
  children,
}: GovernmentWorkspaceShellProps) {
  const router = useRouter();
  const pathname = usePathname() || '/workspace';
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { sessionUser, sessionStatus, reloadSession } = useStoredSession(browserApiBaseUrl);
  const [navigationOpen, setNavigationOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const role: OperatorRole = sessionStatus === 'ready' && sessionUser ? sessionUser.role : 'guest';
  const routeAccessible = sessionStatus === 'ready' && sessionUser
    ? isRouteAccessible(pathname, sessionUser.role)
    : false;
  const visiblePrimaryNavigation = useMemo(
    () => PRIMARY_NAVIGATION.filter((item) => isRouteAccessible(item.href, role)),
    [role],
  );
  const visibleControlNavigation = useMemo(
    () => CONTROL_NAVIGATION.filter((item) => isRouteAccessible(item.href, role)),
    [role],
  );
  const searchHref = isRouteAccessible('/registry', role) ? '/registry' : '/reports';
  const showReviewNotice = process.env.NEXT_PUBLIC_APP_ENV !== 'production';
  const resolvedContext = workContext?.length
    ? workContext
    : [
        'National scope',
        `Authority: ${sessionUser ? humanizeRole(sessionUser.role) : 'Resolving'}`,
        'Publication remains subject to official approval controls',
      ];

  useEffect(() => {
    if (sessionStatus === 'loading') return;
    if (sessionStatus === 'guest' || !sessionUser) {
      router.replace('/login');
      return;
    }
    if (!routeAccessible) router.replace('/workspace');
  }, [routeAccessible, router, sessionStatus, sessionUser]);

  const handleLogout = useCallback(async () => {
    setIsLoggingOut(true);
    try {
      const storedToken = typeof window === 'undefined' ? null : window.localStorage.getItem('egAddressingToken');
      await fetch(`${browserApiBaseUrl}/api/v1/auth/logout`, {
        method: 'POST',
        ...sessionRequestInit(storedToken),
      });
    } catch {
      // Local session cleanup remains authoritative for this browser when revoke is unavailable.
    }
    clearStoredToken();
    await reloadSession();
    router.replace('/login');
    router.refresh();
  }, [browserApiBaseUrl, reloadSession, router]);

  function renderNavigation(items: WorkspaceNavigationItem[]) {
    return items.map((item) => {
      const active = routeIsActive(item.href, pathname);
      return (
        <Link
          key={item.href}
          href={item.href}
          className={`government-navigation-link ${active ? 'active' : ''}`}
          aria-current={active ? 'page' : undefined}
          onClick={() => setNavigationOpen(false)}
        >
          <GovernmentIcon name={item.icon} className="government-navigation-icon" />
          <span className="government-navigation-copy">
            <strong>{item.label}</strong>
            <small>{item.description}</small>
          </span>
        </Link>
      );
    });
  }

  if (sessionStatus !== 'ready' || !sessionUser || !routeAccessible) {
    return (
      <main className="government-access-gate" aria-live="polite">
        <img src="/eg-coat-of-arms.svg" alt="Coat of arms of the Republic of Equatorial Guinea" />
        <p>Republic of Equatorial Guinea</p>
        <h1>National Addressing Platform</h1>
        <span>{sessionStatus === 'loading' ? 'Confirming protected workspace authority…' : 'Redirecting to the authorized service…'}</span>
      </main>
    );
  }

  return (
    <div className="government-workspace-root">
      <a className="government-skip-link" href="#government-workspace-content">Skip to workspace content</a>

      {showReviewNotice ? (
        <div className="government-review-notice">
          <strong>BECOREOPS INTERNAL REVIEW ENVIRONMENT</strong>
          <span>Illustrative or staging information must not be treated as an official published record.</span>
        </div>
      ) : null}

      <button
        className="government-mobile-menu"
        type="button"
        aria-expanded={navigationOpen}
        aria-controls="government-workspace-navigation"
        onClick={() => setNavigationOpen((open) => !open)}
      >
        <GovernmentIcon name="menu" />
        <span>National Addressing Platform</span>
      </button>

      <div className="government-workspace-layout">
        <aside
          id="government-workspace-navigation"
          className={`government-sidebar ${navigationOpen ? 'open' : ''}`}
          aria-label="Government workspace navigation"
        >
          <div className="government-identity">
            <img
              className="government-coat-of-arms"
              src="/eg-coat-of-arms.svg"
              alt="Coat of arms of the Republic of Equatorial Guinea"
            />
            <div>
              <p>Republic of Equatorial Guinea</p>
              <strong>National Addressing Platform</strong>
            </div>
          </div>

          <nav className="government-navigation" aria-label="National operations">
            <p className="government-navigation-label">National operations</p>
            {renderNavigation(visiblePrimaryNavigation)}
            {visibleControlNavigation.length ? (
              <>
                <p className="government-navigation-label government-navigation-label-secondary">Platform control</p>
                {renderNavigation(visibleControlNavigation)}
              </>
            ) : null}
          </nav>

          <div className="government-sidebar-footer">
            <span>Active authority</span>
            <strong>{humanizeRole(sessionUser.role)}</strong>
            <small>Access and territorial scope are enforced by the platform authority service.</small>
          </div>
        </aside>

        {navigationOpen ? (
          <button
            className="government-navigation-scrim"
            type="button"
            aria-label="Close workspace navigation"
            onClick={() => setNavigationOpen(false)}
          />
        ) : null}

        <section className="government-workspace-main" aria-label={`${workspaceTitle} workspace`}>
          <header className="government-topbar">
            <div className="government-topbar-title">
              <span>{sectionLabel}</span>
              <strong>{workspaceTitle}</strong>
            </div>

            <Link className="government-global-search" href={searchHref}>
              <GovernmentIcon name="search" />
              <span>Search official records</span>
              <small>{searchHref === '/registry' ? 'Open registry' : 'Open reporting'}</small>
            </Link>

            <div className="government-session">
              <div className="government-attention" aria-label={`${attentionCount} items require attention`}>
                <GovernmentIcon name="alert" />
                <span>{attentionCount}</span>
              </div>
              <div className="government-user-copy">
                <strong>{sessionUser.full_name}</strong>
                <span>{humanizeRole(sessionUser.role)}</span>
              </div>
              <button type="button" onClick={() => void handleLogout()} disabled={isLoggingOut}>
                <GovernmentIcon name="signout" />
                <span>{isLoggingOut ? 'Signing out' : 'Sign out'}</span>
              </button>
            </div>
          </header>

          <div className="government-work-context">
            {resolvedContext.map((item, index) => (
              <span key={`${item}-${index}`}>
                {index === 0 ? <GovernmentIcon name="territory" /> : null}
                {item}
              </span>
            ))}
          </div>

          <div id="government-workspace-content" className="government-workspace-content">
            {children}
          </div>

          <footer className="government-delivery-footer">
            <div>
              <strong>National Addressing Platform</strong>
              <span>Republic of Equatorial Guinea</span>
            </div>
            <p>Developed by BeCoreOps for the Government of the Republic of Equatorial Guinea</p>
          </footer>
        </section>
      </div>
    </div>
  );
}
