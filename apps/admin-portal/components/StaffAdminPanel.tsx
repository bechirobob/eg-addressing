'use client';

import { FormEvent, useCallback, useEffect, useMemo, useState } from 'react';

import { resolveBrowserApiBaseUrl, sessionRequestInit } from './sessionClient';
import { getStoredToken } from './demoAuth';

type StaffRole = 'admin' | 'editor' | 'viewer' | 'agency_viewer';

type StaffUser = {
  id: string;
  username: string;
  full_name: string;
  role: StaffRole;
  is_active: boolean;
  created_at?: string | null;
  active_sessions: number;
};

type StaffUsersResponse = {
  items: StaffUser[];
  detail?: string;
};

type SessionResponse = {
  user?: {
    id: string;
    username: string;
    full_name: string;
    role: StaffRole;
  };
  detail?: string;
};

type ReadinessGate = {
  name: string;
  status: 'passed' | 'attention' | string;
  evidence?: string;
  next_step?: string;
};

type PilotReadinessSummary = {
  readiness_status: string;
  passed_gates: number;
  total_gates: number;
  gates?: ReadinessGate[];
  totals?: Record<string, number>;
  boundaries?: string[];
};

const staffRoles: Array<{ value: StaffRole; label: string }> = [
  { value: 'viewer', label: 'Viewer' },
  { value: 'agency_viewer', label: 'Agency reviewer' },
  { value: 'editor', label: 'Editor' },
  { value: 'admin', label: 'Admin' },
];

function storedToken() {
  return getStoredToken();
}

function roleLabel(role: StaffRole) {
  return staffRoles.find((item) => item.value === role)?.label ?? role;
}

function formatDate(value?: string | null) {
  if (!value) return 'Not recorded';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return 'Not recorded';
  return parsed.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

function readinessLabel(status: string) {
  if (status === 'pilot-ready') return 'Pilot ready';
  if (status === 'pilot-prep') return 'Pilot preparation';
  return status.replace(/-/g, ' ');
}

export function StaffAdminPanel({ apiBaseUrl }: { apiBaseUrl: string }) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const [users, setUsers] = useState<StaffUser[]>([]);
  const [readiness, setReadiness] = useState<PilotReadinessSummary | null>(null);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMutating, setIsMutating] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [newAccount, setNewAccount] = useState({ username: '', full_name: '', role: 'viewer' as StaffRole, password: '' });
  const [rowEdits, setRowEdits] = useState<Record<string, { full_name: string; role: StaffRole; password: string }>>({});

  const activeAdminCount = useMemo(() => users.filter((user) => user.role === 'admin' && user.is_active).length, [users]);

  const request = useCallback(async <T,>(path: string, init: RequestInit = {}): Promise<T> => {
    const token = storedToken();
    const response = await fetch(`${browserApiBaseUrl}${path}`, {
      ...init,
      credentials: 'include',
      headers: {
        ...(init.body ? { 'Content-Type': 'application/json' } : {}),
        ...sessionRequestInit(token).headers,
        ...(init.headers ?? {}),
      },
    });
    const text = await response.text();
    const payload = text ? JSON.parse(text) : null;
    if (!response.ok) {
      const detail = payload?.detail ?? `Request failed with ${response.status}`;
      throw new Error(detail);
    }
    return payload as T;
  }, [browserApiBaseUrl]);

  const loadUsers = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [session, staff, readinessSummary] = await Promise.all([
        request<SessionResponse>('/api/v1/auth/me'),
        request<StaffUsersResponse>('/api/v1/admin/users'),
        request<PilotReadinessSummary>('/api/v1/pilot-readiness/summary'),
      ]);
      setCurrentUserId(session.user?.id ?? null);
      setUsers(staff.items ?? []);
      setReadiness(readinessSummary);
      setRowEdits((previous) => {
        const next: Record<string, { full_name: string; role: StaffRole; password: string }> = {};
        for (const user of staff.items ?? []) {
          next[user.id] = previous[user.id] ?? { full_name: user.full_name, role: user.role, password: '' };
        }
        return next;
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load staff accounts.');
    } finally {
      setIsLoading(false);
    }
  }, [request]);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  async function mutate(action: () => Promise<void>, success: string) {
    setIsMutating(true);
    setNotice(null);
    setError(null);
    try {
      await action();
      setNotice(success);
      await loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to complete staff account action.');
    } finally {
      setIsMutating(false);
    }
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await mutate(async () => {
      await request<StaffUser>('/api/v1/admin/users', {
        method: 'POST',
        body: JSON.stringify(newAccount),
      });
      setNewAccount({ username: '', full_name: '', role: 'viewer', password: '' });
    }, 'Staff account created.');
  }

  async function handleSave(user: StaffUser) {
    const edit = rowEdits[user.id];
    await mutate(async () => {
      const payload: { full_name?: string; role?: StaffRole; password?: string } = {};
      if (edit.full_name.trim() !== user.full_name) payload.full_name = edit.full_name.trim();
      if (edit.role !== user.role) payload.role = edit.role;
      if (edit.password.trim()) payload.password = edit.password;
      await request<StaffUser>(`/api/v1/admin/users/${user.id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      });
    }, 'Staff account updated. Password rotations sign the user out everywhere automatically.');
  }

  async function handleDisable(user: StaffUser) {
    await mutate(async () => {
      await request<StaffUser>(`/api/v1/admin/users/${user.id}/disable`, { method: 'POST' });
    }, 'Staff account disabled and sessions revoked.');
  }

  async function handleRevoke(user: StaffUser) {
    await mutate(async () => {
      await request<{ revoked_sessions: number }>(`/api/v1/admin/users/${user.id}/revoke-sessions`, { method: 'POST' });
    }, 'User signed out everywhere.');
  }

  return (
    <section className="staff-admin-workspace section-grid single-column-grid" aria-labelledby="staff-admin-heading">
      <article className="public-task-panel staff-admin-intro">
        <div className="panel-head">
          <p className="section-label">Admin area</p>
          <h2 id="staff-admin-heading">Staff account control</h2>
        </div>
        <p className="institutional-note">
          This area is restricted to administrators. Editors, viewers, and agency reviewers can use their staff areas, but they cannot load or operate this account-management surface.
        </p>
        <div className="admin-readiness-summary" aria-label="System readiness summary">
          <div>
            <span>System readiness</span>
            <strong>{readiness ? readinessLabel(readiness.readiness_status) : 'Checking'}</strong>
          </div>
          <div>
            <span>Checks passed</span>
            <strong>{readiness ? `${readiness.passed_gates}/${readiness.total_gates}` : '—'}</strong>
          </div>
          <div>
            <span>Registry addresses</span>
            <strong>{readiness?.totals?.addresses ?? 0}</strong>
          </div>
          <p>{readiness?.boundaries?.[0] ?? 'Summary only. Full audit remains in the automated mission report.'}</p>
        </div>
        <details className="staff-admin-disclosure">
          <summary>Account safeguards</summary>
          <ul className="staff-admin-principles" aria-label="Staff account safeguards">
            <li>Password rotation signs the user out everywhere.</li>
            <li>Deactivating an account signs the user out everywhere.</li>
            <li>Current-admin and last-admin lockout protections remain enforced by the server.</li>
          </ul>
        </details>
      </article>

      <article className="public-task-panel staff-admin-create-panel">
        <div className="panel-head">
          <p className="section-label">Create account</p>
          <h3>Add authorized staff</h3>
        </div>
        <details className="staff-admin-disclosure staff-admin-create-disclosure">
          <summary>Open creation form</summary>
          <form className="territory-form staff-admin-create-form" onSubmit={handleCreate}>
            <label className="territory-field" htmlFor="staff-new-username">
              <span className="territory-label">Username</span>
              <input id="staff-new-username" className="territory-input" value={newAccount.username} autoComplete="username" autoCapitalize="none" autoCorrect="off" spellCheck={false} onChange={(event) => setNewAccount((value) => ({ ...value, username: event.target.value }))} required />
            </label>
            <label className="territory-field" htmlFor="staff-new-name">
              <span className="territory-label">Full name</span>
              <input id="staff-new-name" className="territory-input" value={newAccount.full_name} autoComplete="name" onChange={(event) => setNewAccount((value) => ({ ...value, full_name: event.target.value }))} required />
            </label>
            <label className="territory-field" htmlFor="staff-new-role">
              <span className="territory-label">Role</span>
              <select id="staff-new-role" className="territory-input" value={newAccount.role} onChange={(event) => setNewAccount((value) => ({ ...value, role: event.target.value as StaffRole }))}>
                {staffRoles.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}
              </select>
            </label>
            <label className="territory-field" htmlFor="staff-new-password">
              <span className="territory-label">Temporary password</span>
              <input id="staff-new-password" className="territory-input" type="password" value={newAccount.password} autoComplete="new-password" onChange={(event) => setNewAccount((value) => ({ ...value, password: event.target.value }))} required minLength={8} />
            </label>
            <div className="territory-form-actions">
              <button className="verification-button" type="submit" disabled={isMutating}>Create staff account</button>
            </div>
          </form>
        </details>
      </article>

      <article className="staff-admin-list-panel">
        <div className="panel-head staff-admin-list-head">
          <div>
            <p className="section-label">Account register</p>
            <h3>Authorized staff accounts</h3>
          </div>
          <button className="secondary-button" type="button" onClick={() => void loadUsers()} disabled={isLoading || isMutating}>Refresh</button>
        </div>

        {notice ? <p className="form-notice success" role="status">{notice}</p> : null}
        {error ? <p className="form-notice error" role="alert">{error}</p> : null}
        {isLoading ? <p className="institutional-note">Loading staff account register…</p> : null}

        <div className="staff-admin-table-wrap" aria-live="polite">
          <table className="staff-admin-table">
            <caption>Staff accounts, roles, session status, and account actions</caption>
            <thead>
              <tr>
                <th scope="col">Account</th>
                <th scope="col">Role</th>
                <th scope="col">Status</th>
                <th scope="col">Sessions</th>
                <th scope="col">Controlled actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => {
                const edit = rowEdits[user.id] ?? { full_name: user.full_name, role: user.role, password: '' };
                const isCurrentAdmin = user.id === currentUserId;
                const isLastActiveAdmin = user.role === 'admin' && user.is_active && activeAdminCount <= 1;
                const unsafeAdminAction = isCurrentAdmin || isLastActiveAdmin;
                return (
                  <tr key={user.id}>
                    <td data-label="Account">
                      <strong>{user.username}</strong>
                      <label className="staff-admin-inline-field" htmlFor={`staff-name-${user.id}`}>
                        <span>Full name</span>
                        <input id={`staff-name-${user.id}`} className="territory-input" value={edit.full_name} onChange={(event) => setRowEdits((value) => ({ ...value, [user.id]: { ...edit, full_name: event.target.value } }))} />
                      </label>
                      <small>Created {formatDate(user.created_at)}</small>
                    </td>
                    <td data-label="Role">
                      <label className="staff-admin-inline-field" htmlFor={`staff-role-${user.id}`}>
                        <span>Role</span>
                        <select id={`staff-role-${user.id}`} className="territory-input" value={edit.role} disabled={isCurrentAdmin} onChange={(event) => setRowEdits((value) => ({ ...value, [user.id]: { ...edit, role: event.target.value as StaffRole } }))}>
                          {staffRoles.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}
                        </select>
                      </label>
                      <small>{roleLabel(user.role)}</small>
                    </td>
                    <td data-label="Status">
                      <span className={`staff-admin-status ${user.is_active ? 'active' : 'disabled'}`}>{user.is_active ? 'Active' : 'Disabled'}</span>
                      {isCurrentAdmin ? <small>Current admin</small> : null}
                      {isLastActiveAdmin ? <small>Last active admin</small> : null}
                    </td>
                    <td data-label="Sessions">
                      <strong>{user.active_sessions}</strong>
                      <span>active</span>
                    </td>
                    <td data-label="Controlled actions">
                      <details className="staff-admin-disclosure staff-admin-action-disclosure">
                        <summary>Manage account</summary>
                        <label className="staff-admin-inline-field" htmlFor={`staff-password-${user.id}`}>
                          <span>New password</span>
                          <input id={`staff-password-${user.id}`} className="territory-input" type="password" value={edit.password} autoComplete="new-password" placeholder="Leave blank to keep current" onChange={(event) => setRowEdits((value) => ({ ...value, [user.id]: { ...edit, password: event.target.value } }))} />
                        </label>
                        <div className="staff-admin-actions">
                          <button className="secondary-button" type="button" onClick={() => void handleSave(user)} disabled={isMutating}>Save changes</button>
                          <button className="secondary-button" type="button" onClick={() => void handleRevoke(user)} disabled={isMutating || unsafeAdminAction || user.active_sessions === 0} aria-describedby={unsafeAdminAction ? `staff-admin-guard-${user.id}` : undefined}>Revoke sessions</button>
                          <button className="secondary-button danger-action" type="button" onClick={() => void handleDisable(user)} disabled={isMutating || !user.is_active || unsafeAdminAction} aria-describedby={unsafeAdminAction ? `staff-admin-guard-${user.id}` : undefined}>Disable</button>
                        </div>
                        {unsafeAdminAction ? <small id={`staff-admin-guard-${user.id}`}>Protected to prevent administrator lockout.</small> : null}
                      </details>
                    </td>
                  </tr>
                );
              })}
              {!users.length && !isLoading ? (
                <tr>
                  <td colSpan={5}>No staff accounts were returned.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}
