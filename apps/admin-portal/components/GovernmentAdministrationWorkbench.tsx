'use client';

import type { FormEvent } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { GovernmentIcon } from './GovernmentIcon';
import { authorizationHeader, csrfHeader, resolveBrowserApiBaseUrl, useStoredSession } from './sessionClient';

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

type ReadinessGate = {
  name: string;
  status: string;
  evidence?: string;
  next_step?: string;
};

type ReadinessSummary = {
  readiness_status: string;
  passed_gates: number;
  total_gates: number;
  gates?: ReadinessGate[];
  totals?: Record<string, number>;
  boundaries?: string[];
};

const ROLE_OPTIONS: Array<{ value: StaffRole; label: string; authority: string }> = [
  { value: 'viewer', label: 'Viewer', authority: 'Read-only internal reporting and permitted case files' },
  { value: 'agency_viewer', label: 'Agency reviewer', authority: 'Read-only institutional reporting within approved agency scope' },
  { value: 'editor', label: 'Editor', authority: 'Field, registry, verification, and publication-preparation operations' },
  { value: 'admin', label: 'Administrator', authority: 'Personnel, access, release controls, and all editor operations' },
];

function roleLabel(role: StaffRole) {
  return ROLE_OPTIONS.find((item) => item.value === role)?.label ?? role;
}

function plainStatus(value?: string | null) {
  return (value || 'unknown').replaceAll('-', ' ').replaceAll('_', ' ');
}

function formatDate(value?: string | null) {
  if (!value) return 'Not recorded';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return 'Not recorded';
  return parsed.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

export function GovernmentAdministrationWorkbench({ apiBaseUrl }: { apiBaseUrl: string }) {
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const { token, sessionUser, sessionStatus } = useStoredSession(browserApiBaseUrl);
  const [users, setUsers] = useState<StaffUser[]>([]);
  const [readiness, setReadiness] = useState<ReadinessSummary | null>(null);
  const [selectedId, setSelectedId] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('active');
  const [edit, setEdit] = useState({ full_name: '', role: 'viewer' as StaffRole, password: '' });
  const [newAccount, setNewAccount] = useState({ username: '', full_name: '', role: 'viewer' as StaffRole, password: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canAdminister = sessionUser?.role === 'admin';

  function requestHeaders(withJson = false) {
    return {
      ...(withJson ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? authorizationHeader(token) : csrfHeader()),
    };
  }

  const request = useCallback(async <T,>(path: string, init: RequestInit = {}): Promise<T> => {
    const response = await fetch(`${browserApiBaseUrl}${path}`, {
      ...init,
      credentials: 'include',
      headers: {
        ...(init.body ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? authorizationHeader(token) : csrfHeader()),
        ...(init.headers ?? {}),
      },
    });
    const text = await response.text();
    const payload = text ? JSON.parse(text) : null;
    if (!response.ok) throw new Error(payload?.detail ?? `Administration request failed with ${response.status}.`);
    return payload as T;
  }, [browserApiBaseUrl, token]);

  const reload = useCallback(async () => {
    if (sessionStatus !== 'ready') return;
    setIsLoading(true);
    setError(null);
    try {
      const [staffPayload, readinessPayload] = await Promise.all([
        request<{ items?: StaffUser[] }>('/api/v1/admin/users'),
        request<ReadinessSummary>('/api/v1/pilot-readiness/summary'),
      ]);
      const nextUsers = staffPayload.items ?? [];
      setUsers(nextUsers);
      setReadiness(readinessPayload);
      setSelectedId((current) => nextUsers.some((user) => user.id === current) ? current : nextUsers[0]?.id ?? '');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Staff accounts could not be loaded.');
    } finally {
      setIsLoading(false);
    }
  }, [request, sessionStatus]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const normalizedSearch = searchQuery.trim().toLowerCase();
  const visibleUsers = useMemo(() => users.filter((user) => {
    if (roleFilter !== 'all' && user.role !== roleFilter) return false;
    if (statusFilter === 'active' && !user.is_active) return false;
    if (statusFilter === 'inactive' && user.is_active) return false;
    if (!normalizedSearch) return true;
    return [user.username, user.full_name, user.role, user.id].some((value) => value.toLowerCase().includes(normalizedSearch));
  }), [normalizedSearch, roleFilter, statusFilter, users]);

  useEffect(() => {
    if (!visibleUsers.length) {
      setSelectedId('');
      return;
    }
    if (!visibleUsers.some((user) => user.id === selectedId)) setSelectedId(visibleUsers[0].id);
  }, [selectedId, visibleUsers]);

  const selectedUser = users.find((user) => user.id === selectedId) ?? visibleUsers[0] ?? null;
  const activeAdminCount = users.filter((user) => user.role === 'admin' && user.is_active).length;
  const activeUsers = users.filter((user) => user.is_active);
  const activeSessionCount = users.reduce((total, user) => total + user.active_sessions, 0);
  const readinessAttention = readiness?.gates?.filter((gate) => gate.status !== 'passed') ?? [];
  const isCurrentUser = selectedUser?.id === sessionUser?.id;
  const isLastActiveAdmin = Boolean(selectedUser?.role === 'admin' && selectedUser.is_active && activeAdminCount <= 1);
  const disableBlockedReason = isCurrentUser
    ? 'Current administrator cannot disable this session account'
    : isLastActiveAdmin
      ? 'Last active administrator cannot be disabled'
      : null;

  useEffect(() => {
    if (!selectedUser) {
      setEdit({ full_name: '', role: 'viewer', password: '' });
      return;
    }
    setEdit({ full_name: selectedUser.full_name, role: selectedUser.role, password: '' });
  }, [selectedUser?.id, selectedUser?.full_name, selectedUser?.role]);

  async function mutate(action: () => Promise<void>, success: string) {
    if (!canAdminister) {
      setError('Administrator authority is required for personnel and access changes.');
      return;
    }
    setBusyAction(success);
    setNotice(null);
    setError(null);
    try {
      await action();
      setNotice(success);
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The administration action could not be completed.');
    } finally {
      setBusyAction(null);
    }
  }

  async function createAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await mutate(async () => {
      await request<StaffUser>('/api/v1/admin/users', { method: 'POST', body: JSON.stringify(newAccount), headers: requestHeaders(true) });
      setNewAccount({ username: '', full_name: '', role: 'viewer', password: '' });
    }, 'Staff account created.');
  }

  async function saveSelected() {
    if (!selectedUser) return;
    const payload: { full_name?: string; role?: StaffRole; password?: string } = {};
    if (edit.full_name.trim() !== selectedUser.full_name) payload.full_name = edit.full_name.trim();
    if (edit.role !== selectedUser.role) payload.role = edit.role;
    if (edit.password.trim()) payload.password = edit.password;
    if (!Object.keys(payload).length) {
      setNotice('No account change is pending.');
      return;
    }
    await mutate(async () => {
      await request<StaffUser>(`/api/v1/admin/users/${encodeURIComponent(selectedUser.id)}`, { method: 'PATCH', body: JSON.stringify(payload), headers: requestHeaders(true) });
    }, edit.password.trim() ? 'Staff account updated and active sessions revoked after password rotation.' : 'Staff account updated.');
  }

  async function revokeSelected() {
    if (!selectedUser) return;
    await mutate(async () => {
      await request<{ revoked_sessions: number }>(`/api/v1/admin/users/${encodeURIComponent(selectedUser.id)}/revoke-sessions`, { method: 'POST', headers: requestHeaders() });
    }, `${selectedUser.full_name} signed out everywhere.`);
  }

  async function disableSelected() {
    if (!selectedUser || disableBlockedReason) {
      setError(disableBlockedReason || 'Select an active staff account.');
      return;
    }
    await mutate(async () => {
      await request<StaffUser>(`/api/v1/admin/users/${encodeURIComponent(selectedUser.id)}/disable`, { method: 'POST', headers: requestHeaders() });
    }, `${selectedUser.full_name} disabled and all sessions revoked.`);
  }

  return (
    <section className="government-operation-page government-administration-workbench" aria-labelledby="administration-workbench-title">
      <header className="government-operation-header">
        <div>
          <p>Personnel and access authority</p>
          <h1 id="administration-workbench-title">Administration</h1>
          <span>Manage authorized personnel, roles, account state, and active sessions from one protected personnel register.</span>
        </div>
        <div className="government-operation-header-actions">
          <button type="button" onClick={() => void reload()} disabled={isLoading}><GovernmentIcon name="operations" />{isLoading ? 'Refreshing' : 'Refresh personnel'}</button>
        </div>
      </header>

      <dl className="government-operation-summary" aria-label="Administration summary">
        <div><dt>Active personnel</dt><dd>{activeUsers.length}</dd><span>Authorized staff accounts</span></div>
        <div><dt>Administrators</dt><dd>{activeUsers.filter((user) => user.role === 'admin').length}</dd><span>Platform-control authority</span></div>
        <div><dt>Editors</dt><dd>{activeUsers.filter((user) => user.role === 'editor').length}</dd><span>Operational write authority</span></div>
        <div><dt>Agency access</dt><dd>{activeUsers.filter((user) => user.role === 'agency_viewer').length}</dd><span>Read-only institutional access</span></div>
        <div><dt>Active sessions</dt><dd>{activeSessionCount}</dd><span>{readinessAttention.length} readiness item(s) need attention</span></div>
      </dl>

      <div className="government-command-bar government-administration-command-bar" aria-label="Personnel register filters">
        <label className="government-search-field"><GovernmentIcon name="search" /><span className="sr-only">Search personnel</span><input type="search" value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Search name, username, role, or staff ID" /></label>
        <label><span>Role</span><select value={roleFilter} onChange={(event) => setRoleFilter(event.target.value)}><option value="all">All roles</option>{ROLE_OPTIONS.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}</select></label>
        <label><span>Account state</span><select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="all">All accounts</option><option value="active">Active</option><option value="inactive">Inactive</option></select></label>
        <div className="government-command-note"><GovernmentIcon name="alert" /><span>Password rotation and account disablement revoke active sessions automatically.</span></div>
      </div>

      {sessionStatus === 'loading' ? <p className="government-inline-state">Resolving administrator authority and loading personnel…</p> : null}
      {notice ? <p className="government-inline-state success" role="status">{notice}</p> : null}
      {error ? <p className="government-inline-state error" role="alert">{error}</p> : null}

      <div className="government-three-pane-workbench">
        <aside className="government-queue-pane" aria-label="Authorized personnel register">
          <div className="government-pane-heading"><div><p>Personnel register</p><h2>Authorized accounts</h2></div><span>{visibleUsers.length} shown</span></div>
          <div className="government-record-queue">
            {visibleUsers.length ? visibleUsers.map((user) => (
              <button key={user.id} className={selectedUser?.id === user.id ? 'active' : ''} type="button" onClick={() => setSelectedId(user.id)}>
                <span className="government-queue-record-title">{user.full_name}</span>
                <code>{user.username} · {user.id}</code>
                <span>{roleLabel(user.role)} · {user.active_sessions} active session{user.active_sessions === 1 ? '' : 's'}</span>
                <small className={`government-record-state ${user.is_active ? 'success' : 'warning'}`}>{user.is_active ? 'Active' : 'Inactive'}</small>
              </button>
            )) : <div className="government-pane-empty"><GovernmentIcon name="administration" /><strong>No matching personnel</strong><span>Change the filters or create an authorized account.</span></div>}
          </div>
        </aside>

        <article className="government-record-pane" aria-label="Selected staff account">
          {selectedUser ? (
            <>
              <header className="government-selected-record-header"><div><p>Government personnel account</p><h2>{selectedUser.full_name}</h2><code>{selectedUser.username} · {selectedUser.id}</code></div><span className={`government-record-state ${selectedUser.is_active ? 'success' : 'warning'}`}>{selectedUser.is_active ? 'Active' : 'Inactive'}</span></header>
              <nav className="government-record-tabs" aria-label="Personnel record sections"><span className="active">Identity</span><span>Authority</span><span>Sessions</span><span>Safeguards</span></nav>
              <div className="government-record-body">
                <section><div className="government-record-section-heading"><h3>Personnel and account identity</h3><span>Protected administration service</span></div>
                  <dl className="government-record-facts">
                    <div><dt>Full name</dt><dd>{selectedUser.full_name}</dd></div>
                    <div><dt>Username</dt><dd>{selectedUser.username}</dd></div>
                    <div><dt>Role</dt><dd>{roleLabel(selectedUser.role)}</dd></div>
                    <div><dt>Account state</dt><dd>{selectedUser.is_active ? 'Active' : 'Inactive'}</dd></div>
                    <div><dt>Created</dt><dd>{formatDate(selectedUser.created_at)}</dd></div>
                    <div><dt>Active sessions</dt><dd>{selectedUser.active_sessions}</dd></div>
                  </dl>
                </section>
                <section><div className="government-record-section-heading"><h3>Role authority</h3><span>Route and action permissions remain enforced by platform services</span></div>
                  <div className="government-role-authority"><GovernmentIcon name="administration" /><div><strong>{roleLabel(selectedUser.role)}</strong><span>{ROLE_OPTIONS.find((role) => role.value === selectedUser.role)?.authority}</span></div></div>
                </section>
                <section><div className="government-record-section-heading"><h3>Controlled account update</h3><span>Changes are audit-tracked by the existing administration API</span></div>
                  <div className="government-edit-grid government-administration-edit-grid">
                    <label><span>Full name</span><input value={edit.full_name} onChange={(event) => setEdit((current) => ({ ...current, full_name: event.target.value }))} /></label>
                    <label><span>Role</span><select value={edit.role} onChange={(event) => setEdit((current) => ({ ...current, role: event.target.value as StaffRole }))}>{ROLE_OPTIONS.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}</select></label>
                    <label className="government-wide-field"><span>New password</span><input type="password" autoComplete="new-password" minLength={8} value={edit.password} onChange={(event) => setEdit((current) => ({ ...current, password: event.target.value }))} placeholder="Leave blank to keep current password" /></label>
                  </div>
                </section>
                <section><div className="government-record-section-heading"><h3>Account safeguards</h3><span>Server authority is final</span></div>
                  <ul className="government-safeguard-list"><li>Current-admin and last-active-admin lockout protections remain enforced.</li><li>Password rotation revokes all sessions.</li><li>Account disablement revokes all sessions and removes operational access.</li><li>Inactive accounts remain visible for audit and personnel history.</li></ul>
                </section>
              </div>
            </>
          ) : <div className="government-pane-empty large"><GovernmentIcon name="administration" /><strong>Select a staff account</strong><span>Personnel identity, authority, sessions, and valid controls will appear here.</span></div>}
        </article>

        <aside className="government-decision-pane" aria-label="Personnel account actions">
          <div className="government-pane-heading"><div><p>Access control</p><h2>Valid next actions</h2></div><span>{canAdminister ? 'Administrator authority' : 'Read only'}</span></div>
          <div className="government-decision-body">
            <section><h3>Selected account</h3><div className="government-action-stack"><button className="primary" type="button" onClick={() => void saveSelected()} disabled={!selectedUser || !canAdminister || Boolean(busyAction) || !selectedUser.is_active}>{!canAdminister ? 'Administrator required' : busyAction ? 'Working…' : 'Save account update'}</button><button type="button" onClick={() => void revokeSelected()} disabled={!selectedUser || !canAdminister || Boolean(busyAction) || selectedUser.active_sessions <= 0}>Sign out everywhere</button><button className="danger" type="button" onClick={() => void disableSelected()} disabled={!selectedUser || !selectedUser.is_active || !canAdminister || Boolean(busyAction) || Boolean(disableBlockedReason)}>{disableBlockedReason ?? (selectedUser?.is_active ? 'Disable account' : 'Account already inactive')}</button></div></section>

            <section><h3>Create authorized account</h3><form className="government-create-form government-administration-create-form" onSubmit={createAccount}><label><span>Username</span><input required autoCapitalize="none" autoCorrect="off" spellCheck={false} value={newAccount.username} onChange={(event) => setNewAccount((current) => ({ ...current, username: event.target.value }))} /></label><label><span>Full name</span><input required value={newAccount.full_name} onChange={(event) => setNewAccount((current) => ({ ...current, full_name: event.target.value }))} /></label><label><span>Role</span><select value={newAccount.role} onChange={(event) => setNewAccount((current) => ({ ...current, role: event.target.value as StaffRole }))}>{ROLE_OPTIONS.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}</select></label><label><span>Temporary password</span><input required type="password" autoComplete="new-password" minLength={8} value={newAccount.password} onChange={(event) => setNewAccount((current) => ({ ...current, password: event.target.value }))} /></label><button type="submit" disabled={!canAdminister || Boolean(busyAction)}>{!canAdminister ? 'Administrator required' : busyAction ? 'Working…' : 'Create staff account'}</button></form></section>

            {readiness ? <section><h3>Platform readiness</h3><div className="government-readiness-ledger"><strong>{plainStatus(readiness.readiness_status)}</strong><span>{readiness.passed_gates}/{readiness.total_gates} controls passed</span></div>{readinessAttention.length ? <ul className="government-overdue-list">{readinessAttention.slice(0, 5).map((gate) => <li key={gate.name}><strong>{gate.name}</strong><span>{plainStatus(gate.status)}</span><small>{gate.next_step || gate.evidence || 'Administrative attention required'}</small></li>)}</ul> : <p className="government-record-copy">No readiness exceptions were returned.</p>}</section> : null}

            <section className="government-authority-note"><GovernmentIcon name="alert" /><div><strong>Least privilege remains the default</strong><span>Grant only the role required for assigned duties. Publication release still requires separate administrator authority and an active institutional release flag.</span></div></section>
          </div>
        </aside>
      </div>
    </section>
  );
}
