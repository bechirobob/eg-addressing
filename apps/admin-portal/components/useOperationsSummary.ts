'use client';

import { useEffect, useState } from 'react';
import type { GovernmentReadinessSummary, GovernmentReportingSummary } from '../lib/governmentWorkspaceData';
import { sessionRequestInit, type SessionStatus } from './sessionClient';

type Snapshot = {
  summary: GovernmentReportingSummary | null;
  readiness: GovernmentReadinessSummary | null;
  loading: boolean;
  updatedAt: string | null;
};
const empty: Snapshot = { summary: null, readiness: null, loading: true, updatedAt: null };
const validCount = (value: unknown): value is number => typeof value === 'number' && Number.isSafeInteger(value) && value >= 0;

function reporting(value: GovernmentReportingSummary) {
  const totals = value?.totals;
  if (!totals || !['territories', 'submissions', 'review_queue', 'published_addresses', 'correction_queue']
    .every((key) => validCount(totals[key as keyof typeof totals])) ||
    (totals.geotag_queue !== undefined && !validCount(totals.geotag_queue))) throw new Error('Invalid summary');
  return value;
}
function readiness(value: GovernmentReadinessSummary) {
  if (!value || !validCount(value.passed_gates) || !validCount(value.total_gates) ||
    value.passed_gates > value.total_gates || !Array.isArray(value.gates) ||
    !value.gates.every((gate) => gate && ['name', 'status', 'evidence', 'next_step']
      .every((key) => typeof gate[key as keyof typeof gate] === 'string'))) throw new Error('Invalid readiness');
  return value;
}

export function useOperationsSummary(baseUrl: string, token: string | null, status: SessionStatus, userId?: string) {
  const [snapshot, setSnapshot] = useState<Snapshot>(empty);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    setSnapshot(empty);
    if (status !== 'ready') return;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    let active = true;
    async function request<T>(path: string, validate: (value: T) => T) {
      const response = await fetch(`${baseUrl}/api/v1/${path}`, {
        ...sessionRequestInit(token), cache: 'no-store', signal: controller.signal,
      });
      if (!response.ok) throw new Error('Summary unavailable');
      return validate(await response.json());
    }
    void Promise.allSettled([
      request('reporting/summary', reporting), request('pilot-readiness/summary', readiness),
    ]).then(([report, pilot]) => {
      if (!active) return;
      const summary = report.status === 'fulfilled' ? report.value : null;
      const readiness = pilot.status === 'fulfilled' ? pilot.value : null;
      setSnapshot({ summary, readiness, loading: false, updatedAt: summary || readiness ? new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : null });
    }).finally(() => clearTimeout(timeout));
    return () => { active = false; clearTimeout(timeout); controller.abort(); };
  }, [baseUrl, token, status, userId, revision]);
  return { ...snapshot, refresh: () => setRevision((value) => value + 1) };
}
