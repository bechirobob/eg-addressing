export type SessionUser = {
  id: string;
  username: string;
  full_name: string;
  role: 'viewer' | 'editor' | 'admin';
};

export const demoCredentials = [
  { role: 'admin', username: 'admin', password: 'admin123', label: 'Platform administrator' },
  { role: 'editor', username: 'editor', password: 'editor123', label: 'Registry editor' },
  { role: 'viewer', username: 'viewer', password: 'viewer123', label: 'Program viewer' },
] as const;

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
