'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import type { ReactNode } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { clearStoredToken } from './demoAuth';
import {
  defaultRouteForRole,
  isRouteAccessible,
  navItems,
  routeNeedsResolvedSession,
  type OperatorRole,
} from './site-data';
import { resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

type RoleAwareChromeProps = {
  apiBaseUrl: string;
  children: ReactNode;
};

function roleFromSession(role: 'viewer' | 'editor' | 'admin' | undefined, status: 'loading' | 'ready' | 'guest'): OperatorRole {
  if (status === 'guest' || !role) return 'guest';
  return role;
}

export function RoleAwareChrome({ apiBaseUrl, children }: RoleAwareChromeProps) {
  const router = useRouter();
  const pathname = usePathname();
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { sessionUser, sessionStatus, reloadSession } = useStoredSession(browserApiBaseUrl);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [forcedGuest, setForcedGuest] = useState(false);

  const effectiveSessionUser = forcedGuest ? null : sessionUser;
  const effectiveSessionStatus = forcedGuest ? 'guest' : sessionStatus;

  const role = roleFromSession(effectiveSessionUser?.role, effectiveSessionStatus);
  const currentRoute = pathname || '/';
  const waitingForAccessResolution = effectiveSessionStatus === 'loading' && routeNeedsResolvedSession(currentRoute);
  const accessAllowed = effectiveSessionStatus === 'loading' ? true : isRouteAccessible(currentRoute, role);

  const visibleItems = useMemo(
    () => navItems.filter((item) => item.visibleTo.includes(role)),
    [role],
  );

  const primaryItems = useMemo(
    () => visibleItems.filter((item) => item.priorityFor.includes(role) || item.href === currentRoute),
    [currentRoute, role, visibleItems],
  );

  const secondaryItems = useMemo(
    () => visibleItems.filter((item) => !primaryItems.some((primary) => primary.href === item.href)),
    [primaryItems, visibleItems],
  );

  useEffect(() => {
    if (effectiveSessionStatus === 'loading' || accessAllowed) {
      return;
    }

    router.replace(role === 'guest' ? '/login' : defaultRouteForRole(role));
  }, [accessAllowed, effectiveSessionStatus, role, router]);

  const handleLogout = useCallback(async () => {
    setIsLoggingOut(true);
    setForcedGuest(true);
    clearStoredToken();
    await reloadSession();
    router.replace('/login');
    router.refresh();
  }, [reloadSession, router]);

  const workspaceHref = defaultRouteForRole(role);

  return (
    <>
      <div className="chrome-shell">
        <div className="nav-cluster">
          <nav className="top-nav" aria-label="Surface navigation">
            {primaryItems.map((item) => {
              const isActive = item.href === currentRoute;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`nav-link ${isActive ? 'nav-link-active' : ''}`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          {secondaryItems.length ? (
            <div className="secondary-nav" aria-label="Additional surfaces">
              {secondaryItems.map((item) => {
                const isActive = item.href === currentRoute;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`secondary-nav-link ${isActive ? 'secondary-nav-link-active' : ''}`}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </div>
          ) : null}
        </div>

        <div className="chrome-session-card" aria-live="polite">
          {effectiveSessionStatus === 'ready' && effectiveSessionUser ? (
            <>
              <div>
                <strong>{effectiveSessionUser.full_name}</strong>
                <p>
                  Signed in as <span className="session-role">{effectiveSessionUser.role}</span> · @{effectiveSessionUser.username}
                </p>
              </div>
              <div className="chrome-session-actions">
                {currentRoute !== workspaceHref ? (
                  <Link href={workspaceHref} className="secondary-button chrome-link-button">
                    Return to workspace
                  </Link>
                ) : null}
                <button className="secondary-button" type="button" onClick={() => void handleLogout()} disabled={isLoggingOut}>
                  {isLoggingOut ? 'Signing out…' : 'Sign out'}
                </button>
              </div>
            </>
          ) : effectiveSessionStatus === 'loading' ? (
            <>
              <div>
                <strong>Checking session</strong>
                <p>Validating operator access and role boundaries.</p>
              </div>
            </>
          ) : (
            <>
              <div>
                <strong>Guest review mode</strong>
                <p>Browse overview and reporting surfaces, or sign in for protected registry operations.</p>
              </div>
              {currentRoute !== '/login' ? (
                <div className="chrome-session-actions">
                  <Link href="/login" className="secondary-button chrome-link-button">
                    Sign in
                  </Link>
                </div>
              ) : null}
            </>
          )}
        </div>
      </div>

      {waitingForAccessResolution ? (
        <section className="panel panel-state-grid">
          <div className="panel-state">
            <strong>Checking access</strong>
            <p>Resolving the operator session before loading this protected surface.</p>
          </div>
        </section>
      ) : !accessAllowed ? (
        <section className="panel panel-state-grid">
          <div className="panel-state">
            <strong>Redirecting to an allowed surface</strong>
            <p>
              This page is restricted for your current role. Redirecting to {role === 'guest' ? 'sign-in' : 'your workspace'} now.
            </p>
          </div>
        </section>
      ) : (
        children
      )}
    </>
  );
}
