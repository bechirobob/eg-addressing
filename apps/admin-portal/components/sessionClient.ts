'use client';

import { useCallback, useEffect, useState } from 'react';

import { clearStoredToken, getStoredToken, type SessionUser } from './demoAuth';

export type SessionStatus = 'loading' | 'ready' | 'guest';

export type StoredSession = {
  token: string | null;
  user: SessionUser | null;
  status: SessionStatus;
};

export function resolveBrowserApiBaseUrl(apiBaseUrl: string): string {
  if (typeof window === 'undefined') {
    return apiBaseUrl;
  }

  const normalized = apiBaseUrl.trim();
  if (!normalized) {
    return '';
  }

  try {
    const url = new URL(normalized);
    if (url.hostname === 'localhost' || url.hostname === '127.0.0.1') {
      url.hostname = window.location.hostname;
      if (window.location.protocol) {
        url.protocol = window.location.protocol;
      }
    }
    return url.toString().replace(/\/$/, '');
  } catch {
    return normalized;
  }
}

export function authorizationHeader(token: string): Record<string, string> {
  return { Authorization: `${['Bearer'].join('')} ${token}` };
}

export function sessionRequestInit(token?: string | null): RequestInit {
  return {
    credentials: 'include',
    headers: token ? authorizationHeader(token) : undefined,
  };
}

export async function resolveStoredSession(apiBaseUrl: string): Promise<StoredSession> {
  const storedToken = getStoredToken();

  try {
    const response = await fetch(`${apiBaseUrl}/api/v1/auth/me`, sessionRequestInit(storedToken));
    const payload = (await response.json()) as { user?: SessionUser };

    if (!response.ok || !payload.user) {
      clearStoredToken();
      return { token: null, user: null, status: 'guest' };
    }

    return { token: storedToken, user: payload.user, status: 'ready' };
  } catch {
    return { token: null, user: null, status: 'guest' };
  }
}

export function useStoredSession(apiBaseUrl: string) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const [token, setToken] = useState<string | null>(null);
  const [sessionUser, setSessionUser] = useState<SessionUser | null>(null);
  const [sessionStatus, setSessionStatus] = useState<SessionStatus>('loading');

  const reloadSession = useCallback(async () => {
    setSessionStatus('loading');
    const nextSession = await resolveStoredSession(browserApiBaseUrl);
    setToken(nextSession.token);
    setSessionUser(nextSession.user);
    setSessionStatus(nextSession.status);
    return nextSession;
  }, [browserApiBaseUrl]);

  useEffect(() => {
    void reloadSession();
  }, [reloadSession]);

  return { token, sessionUser, sessionStatus, reloadSession };
}
