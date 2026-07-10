export type SessionUser = {
  id: string;
  username: string;
  full_name: string;
  role: 'viewer' | 'editor' | 'admin' | 'agency_viewer';
};

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.localStorage.getItem('egAddressingToken');
}

export function setStoredToken(token: string): void {
  if (typeof window === 'undefined') {
    return;
  }
  window.localStorage.setItem('egAddressingToken', token);
}

export function clearStoredToken(): void {
  if (typeof window === 'undefined') {
    return;
  }
  window.localStorage.removeItem('egAddressingToken');
}
