'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

import { defaultRouteForRole } from './site-data';
import { clearStoredToken, setStoredToken } from './demoAuth';
import { resolveBrowserApiBaseUrl } from './sessionClient';

type LoginPanelProps = {
  apiBaseUrl: string;
};

export function LoginPanel({ apiBaseUrl }: LoginPanelProps) {
  const router = useRouter();
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/auth/login`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const payload = (await response.json()) as { token?: string; auth_mode?: string; user?: { role: string }; detail?: string };

      if (!response.ok) {
        setError(payload.detail ?? 'Login failed.');
        return;
      }

      if (payload.auth_mode === 'cookie_session') {
        clearStoredToken();
      } else if (payload.token) {
        setStoredToken(payload.token);
      } else {
        setError('Login failed: session token was not returned.');
        return;
      }
      const nextRoute = defaultRouteForRole((payload.user?.role as 'viewer' | 'editor' | 'admin' | undefined) ?? 'viewer');
      setNotice(`Signed in as ${username} (${payload.user?.role ?? 'unknown role'}). Opening your administration workspace…`);
      router.push(nextRoute);
      router.refresh();
    } catch {
      setError('Network error while signing in.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="section-grid single-column-grid">
      <article className="public-task-panel civic-panel-blue">
        <div className="panel-head">
          <p className="section-label">Platform access</p>
          <h3>Sign in to perform protected registry actions</h3>
        </div>

        <p className="institutional-note">
          Use an authorized operator account. Protected actions are role-controlled and recorded in the audit trail.
        </p>

        <form className="territory-form" onSubmit={handleSubmit}>
          <label className="territory-field" htmlFor="login-username">
            <span className="territory-label">Username</span>
            <input
              id="login-username"
              className="territory-input"
              name="username"
              autoComplete="username"
              autoCapitalize="none"
              autoCorrect="off"
              spellCheck={false}
              enterKeyHint="next"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>

          <label className="territory-field" htmlFor="login-password">
            <span className="territory-label">Password</span>
            <input
              id="login-password"
              className="territory-input"
              type="password"
              name="password"
              autoComplete="current-password"
              enterKeyHint="done"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          <div className="territory-form-actions">
            <button className="verification-button" type="submit" disabled={isSubmitting} aria-describedby="login-submit-help">
              {isSubmitting ? 'Signing in…' : 'Sign in'}
            </button>
            <p id="login-submit-help" className="institutional-note compact-note">
              Press Enter from the password field after entering your authorized operator credentials.
            </p>
          </div>

          {notice ? <p className="form-notice success">{notice}</p> : null}
          {error ? <p className="form-notice error">{error}</p> : null}
        </form>
      </article>
    </section>
  );
}
