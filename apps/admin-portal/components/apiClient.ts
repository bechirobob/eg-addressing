'use client';

import { authorizationHeader } from './sessionClient';
import type { ApiPath } from './apiTypes';

export type ApiRequestOptions = RequestInit & {
  token?: string | null;
};

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function apiJson<T>(url: string | URL, options: ApiRequestOptions = {}): Promise<T> {
  const { token, headers, ...request } = options;
  const response = await fetch(url, {
    credentials: 'include',
    ...request,
    headers: {
      ...(headers ?? {}),
      ...(token ? authorizationHeader(token) : {}),
    },
  });

  const payload = (await response.json().catch(() => null)) as T | { detail?: string } | null;
  if (!response.ok) {
    const detail = payload && typeof payload === 'object' && 'detail' in payload ? payload.detail : null;
    throw new ApiError(detail || `Request failed with status ${response.status}`, response.status);
  }

  return payload as T;
}

export function apiPath(path: ApiPath): ApiPath {
  return path;
}
