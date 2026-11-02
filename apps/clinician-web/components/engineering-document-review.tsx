import type { EngineeringDocumentResult } from "../lib/document-demo/contracts";

export function EngineeringDocumentReview({
  result,
}: Readonly<{ result: EngineeringDocumentResult | null }>) {
  if (!result)
    return (
      <section className="state-panel" role="status">
        <div>
          <h2>Engineering preview unavailable</h2>
          <p>No clinician workflow or document source access has been enabled.</p>
        </div>
      </section>
    );
  return (
    <div className="page-stack page-stack--narrow">
      <section className="content-card" aria-labelledby="boundary-heading">
        <p className="eyebrow">P11 offline engineering path</p>
        <h2 id="boundary-heading">Synthetic document review receipt</h2>
        <p>{result.notice}</p>
        <p>
          <strong>Not patient data. Not a medical result. Not approved source access.</strong>
        </p>
      </section>

      <section className="content-card" aria-labelledby="lifecycle-heading">
        <h2 id="lifecycle-heading">Guarded lifecycle</h2>
        <ol className="demo-lifecycle" aria-label="Synthetic document lifecycle">
          {result.lifecycle.map((state) => (
            <li key={state}>{state.replaceAll("_", " ")}</li>
          ))}
        </ol>
      </section>

      <section className="content-card" aria-labelledby="processing-heading">
        <h2 id="processing-heading">Offline processing contract</h2>
        <dl className="review-list">
          <div>
            <dt>Technical result</dt>
            <dd>{result.processing_status}</dd>
          </div>
          <div>
            <dt>External egress</dt>
            <dd>{result.external_egress ? "Enabled" : "None"}</dd>
          </div>
          <div>
            <dt>Declared synthetic type</dt>
            <dd>{result.document_type.replaceAll("_", " ")}</dd>
          </div>
          <div>
            <dt>Processor behavior</dt>
            <dd>{result.processor_disposition.replaceAll("_", " ")}</dd>
          </div>
        </dl>
      </section>

      <section className="content-card" aria-labelledby="candidate-heading">
        <h2 id="candidate-heading">Detached evidence state</h2>
        <dl className="review-list">
          <div>
            <dt>Candidate</dt>
            <dd>{result.candidate_disposition}</dd>
          </div>
          <div>
            <dt>Structural match</dt>
            <dd>{result.structural_match.replaceAll("_", " ")}</dd>
          </div>
          <div>
            <dt>Source access</dt>
            <dd>{result.source_access.replaceAll("_", " ")}</dd>
          </div>
          <div>
            <dt>Confidence</dt>
            <dd>{result.confidence}</dd>
          </div>
        </dl>
        <p>Review controls remain disabled because no clinical or source authority exists.</p>
      </section>
    </div>
  );
}
