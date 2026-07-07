'use client';

import { FormEvent, useMemo, useState } from 'react';

import { useTranslation } from './i18n';
import { resolveBrowserApiBaseUrl } from './sessionClient';

type PublicExtract = {
  query: string;
  match_status: string;
  public_code: string | null;
  address_label: string;
  jurisdiction: string;
  verification_status: string;
  publication_state: string;
  verification_note: string;
  issuance_method?: string;
  source?: string;
  latitude?: number | null;
  longitude?: number | null;
  accuracy_meters?: number | null;
  address_id?: string | null;
  document_title?: string;
  document_reference?: string;
  record_locator?: string | null;
  issued_for?: string;
  issuing_authority?: string;
  extract_status?: string;
};

type PublicIssuancePanelProps = {
  initialExtract: PublicExtract;
  apiBaseUrl: string;
};

export function PublicIssuancePanel({ initialExtract, apiBaseUrl }: PublicIssuancePanelProps) {
  const { t } = useTranslation();
  const browserApiBaseUrl = resolveBrowserApiBaseUrl(apiBaseUrl);
  const [query, setQuery] = useState(initialExtract.public_code ?? initialExtract.query);
  const [extract, setExtract] = useState(initialExtract);
  const [correctionType, setCorrectionType] = useState('record-update');
  const [reason, setReason] = useState('record details need review');
  const [note, setNote] = useState('');
  const [reporterName, setReporterName] = useState('');
  const [reporterContact, setReporterContact] = useState('');
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLookupLoading, setIsLookupLoading] = useState(false);
  const [isCorrectionSubmitting, setIsCorrectionSubmitting] = useState(false);

  const canPrint = useMemo(() => extract.match_status === 'verified' && extract.extract_status === 'ready', [extract]);
  const printDisabledReason = canPrint ? null : t('printAvailableAfterVerified');

  async function handleLookup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLookupLoading(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/public/issuance/${encodeURIComponent(query)}`);
      const payload = (await response.json()) as PublicExtract;
      setExtract(payload);
      if (!response.ok) {
        setError(t('unableRetrieveExtract'));
        return;
      }
      setNotice(payload.match_status === 'verified' ? t('officialExtractLoaded') : t('noPublishedRecordMatched'));
    } catch {
      setError(t('unableRetrieveExtract'));
    } finally {
      setIsLookupLoading(false);
    }
  }

  async function handleCorrection(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCorrectionSubmitting(true);
    setNotice(null);
    setError(null);

    try {
      const response = await fetch(`${browserApiBaseUrl}/api/v1/public/corrections`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: extract.public_code ?? query,
          public_code: extract.public_code,
          address_id: extract.address_id,
          correction_type: correctionType,
          reason,
          note,
          reporter_name: reporterName || null,
          reporter_contact: reporterContact || null,
        }),
      });
      const payload = (await response.json()) as { status?: string; detail?: string };
      if (!response.ok) {
        setError(payload.detail ?? t('unableSubmitCorrection'));
        return;
      }
      setNotice(t('correctionSubmitted'));
      setNote('');
      setReporterName('');
      setReporterContact('');
    } catch {
      setError(t('unableSubmitCorrection'));
    } finally {
      setIsCorrectionSubmitting(false);
    }
  }

  return (
    <>
      <section className="section-grid public-issuance-grid">
        <article className="public-task-panel civic-panel-blue">
          <div className="panel-head">
            <p className="section-label">{t('lookup')}</p>
            <h3>{t('searchPublicRegistry')}</h3>
          </div>
          <form className="territory-form" onSubmit={handleLookup}>
            <label className="territory-field territory-field-wide">
              <span className="territory-label">{t('publicCodeOrAddress')}</span>
              <input className="territory-input" value={query} onChange={(event) => setQuery(event.target.value)} required />
            </label>
            <div className="territory-form-actions">
              <button className="verification-button" type="submit" disabled={isLookupLoading}>
                {isLookupLoading ? t('checking') : t('loadOfficialExtract')}
              </button>
            </div>
          </form>
          <p className="institutional-note issuance-help-copy">
            {t('exampleOfficialCode')}: <strong>EG-BN-MALABO-001A</strong>
          </p>
        </article>

        <article className="public-task-panel civic-panel-gold issuance-panel">
          <div className="panel-head compact-panel-head">
            <p className="section-label">{t('registryExtract')}</p>
            <h3>{extract.document_title ?? t('officialAddressRegistryExtract')}</h3>
          </div>
          <details className="disclosure-panel issuance-summary-disclosure">
            <summary>
              <span className={`status-pill ${extract.match_status === 'verified' ? 'ok' : 'warn'}`}>
                {extract.extract_status ?? extract.match_status}
              </span>
              <span className="issuance-summary-title">{extract.address_label}</span>
              <span className="issuance-summary-meta">{extract.jurisdiction}</span>
            </summary>
            <div className="result-card issuance-result-card">
              <div className="issuance-result-copy">
                <p>{extract.verification_note}</p>
              </div>
              <div className="button-stack issuance-actions">
                <button className="secondary-button" type="button" onClick={() => window.print()} disabled={!canPrint}>
                  {printDisabledReason ?? t('printExtract')}
                </button>
              </div>
            </div>
            <dl className="facts-grid issuance-facts-grid">
            <div>
              <dt>{t('documentReference')}</dt>
              <dd>{extract.document_reference ?? t('pendingLookup')}</dd>
            </div>
            <div>
              <dt>{t('publicCode')}</dt>
              <dd>{extract.public_code ?? t('notAssigned')}</dd>
            </div>
            <div>
              <dt>{t('verificationLevel')}</dt>
              <dd>{extract.verification_status}</dd>
            </div>
            <div>
              <dt>{t('publicationState')}</dt>
              <dd>{extract.publication_state}</dd>
            </div>
            <div>
              <dt>{t('issuanceMethod')}</dt>
              <dd>{extract.issuance_method ?? t('notRecorded')}</dd>
            </div>
            <div>
              <dt>{t('registrySource')}</dt>
              <dd>{extract.source ?? t('notRecorded')}</dd>
            </div>
            <div>
              <dt>{t('coordinates')}</dt>
              <dd>
                {extract.latitude != null && extract.longitude != null
                  ? `${extract.latitude}, ${extract.longitude}`
                  : t('noPublicCoordinate')}
              </dd>
            </div>
            <div>
              <dt>{t('accuracy')}</dt>
              <dd>{extract.accuracy_meters != null ? `${extract.accuracy_meters} m` : t('notRecorded')}</dd>
            </div>
            <div className="issuance-facts-full">
              <dt>{t('issuingAuthority')}</dt>
              <dd>{extract.issuing_authority ?? `${t('republic')} · ${t('homeTitle')}`}</dd>
            </div>
            </dl>
          </details>
        </article>
      </section>

      <section className="section-grid public-issuance-grid">
        <article className="public-task-panel civic-panel-green">
          <div className="panel-head">
            <p className="section-label">{t('correctionReport')}</p>
            <h3>{t('reportNeedsReview')}</h3>
          </div>
          <details className="disclosure-panel">
            <summary>{t('openCorrectionForm')}</summary>
            <form className="territory-form" onSubmit={handleCorrection}>
            <label className="territory-field">
              <span className="territory-label">{t('correctionType')}</span>
              <input className="territory-input" value={correctionType} onChange={(event) => setCorrectionType(event.target.value)} required />
            </label>
            <label className="territory-field">
              <span className="territory-label">{t('reason')}</span>
              <input className="territory-input" value={reason} onChange={(event) => setReason(event.target.value)} required />
            </label>
            <label className="territory-field territory-field-wide">
              <span className="territory-label">{t('notes')}</span>
              <textarea className="territory-input territory-textarea" value={note} onChange={(event) => setNote(event.target.value)} rows={4} />
            </label>
            <div className="filter-grid">
              <label className="territory-field">
                <span className="territory-label">{t('yourName')}</span>
                <input className="territory-input" value={reporterName} onChange={(event) => setReporterName(event.target.value)} />
              </label>
              <label className="territory-field">
                <span className="territory-label">{t('contact')}</span>
                <input className="territory-input" value={reporterContact} onChange={(event) => setReporterContact(event.target.value)} />
              </label>
            </div>
            <div className="territory-form-actions">
              <button className="verification-button" type="submit" disabled={isCorrectionSubmitting}>
                {isCorrectionSubmitting ? t('submitting') : t('submitCorrectionReport')}
              </button>
            </div>
            </form>
          </details>
          {notice ? <p className="form-notice success">{notice}</p> : null}
          {error ? <p className="form-notice error">{error}</p> : null}
        </article>

        <article className="public-task-panel civic-panel-blue">
          <div className="panel-head">
            <p className="section-label">{t('extractMeaning')}</p>
            <h3>{t('publicConfirmationNotTitle')}</h3>
          </div>
          <details className="disclosure-panel">
            <summary>{t('readExtractGuidance')}</summary>
            <ul className="program-list">
            <li>
              <span>{t('extractGuide1')}</span>
            </li>
            <li>
              <span>{t('extractGuide2')}</span>
            </li>
            <li>
              <span>{t('extractGuide3')}</span>
            </li>
            <li>
              <span>{t('extractGuide4')}</span>
            </li>
            </ul>
          </details>
        </article>
      </section>
    </>
  );
}
