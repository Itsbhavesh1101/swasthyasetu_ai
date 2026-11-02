import type { EngineeringSummaryResult } from "../lib/summary-demo/contracts";

function readable(value: string) {
  return value.replaceAll("_", " ");
}

export function EngineeringSummaryReview({
  result,
}: Readonly<{ result: EngineeringSummaryResult | null }>) {
  if (!result)
    return (
      <section className="state-panel" role="status">
        <div>
          <h2>Summary preview unavailable</h2>
          <p>No source-backed summary or clinician action has been enabled.</p>
        </div>
      </section>
    );
  return (
    <div className="page-stack page-stack--narrow">
      <section className="content-card" aria-labelledby="summary-heading">
        <p className="eyebrow">P10 offline engineering path</p>
        <h2 id="summary-heading">Synthetic source-backed summary draft</h2>
        <p>{result.notice}</p>
        <p>
          <strong>Draft only. Not signed clinical documentation. No review authority.</strong>
        </p>
        <dl className="review-list">
          <div>
            <dt>Draft status</dt>
            <dd>{result.status}</dd>
          </div>
          <div>
            <dt>Source comparison</dt>
            <dd>{result.freshness}</dd>
          </div>
          <div>
            <dt>Review state</dt>
            <dd>{readable(result.review_state)}</dd>
          </div>
          <div>
            <dt>Source access</dt>
            <dd>{readable(result.source_access)}</dd>
          </div>
        </dl>
      </section>

      <section className="content-card" aria-labelledby="drift-heading">
        <h2 id="drift-heading">Source drift check</h2>
        <p>
          A new synthetic HPI source was detected after the draft snapshot. The draft remains stale
          and cannot be confirmed.
        </p>
        <dl className="review-list">
          <div>
            <dt>Affected section</dt>
            <dd>{readable(result.affected_sections[0])}</dd>
          </div>
          <div>
            <dt>Reason</dt>
            <dd>{readable(result.drift_reasons[0])}</dd>
          </div>
        </dl>
      </section>

      <section className="content-card" aria-labelledby="sections-heading">
        <h2 id="sections-heading">Canonical summary sections</h2>
        <div className="summary-sections">
          {result.sections.map((section) => (
            <article key={section.section} className="summary-section">
              <h3>{readable(section.section)}</h3>
              <p>
                <strong>{section.readiness}</strong>
              </p>
              {section.assertions.length ? (
                <ul>
                  {section.assertions.map((assertion) => (
                    <li key={assertion}>
                      {readable(assertion)} · {readable(section.source_kinds.at(0) ?? "UNKNOWN")}
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No assertion supplied; absence is not a clinical finding.</p>
              )}
            </article>
          ))}
        </div>
        <p>Edit, confirm, and reject controls remain unavailable.</p>
      </section>
    </div>
  );
}
