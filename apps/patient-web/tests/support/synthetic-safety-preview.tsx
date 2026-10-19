import type { SafetyPresentationState } from "../../lib/safety/presentation";

/** Vitest-only rendering harness. Production code must never import this module. */
export function SyntheticSafetyPreview({ state }: Readonly<{ state: SafetyPresentationState }>) {
  if (state.kind !== "ENGINEERING_SYNTHETIC_PREVIEW") {
    return (
      <section aria-labelledby="synthetic-safety-unavailable" role="status">
        <h2 id="synthetic-safety-unavailable">Safety result unavailable</h2>
        <p>No safety assessment has been performed.</p>
      </section>
    );
  }

  return (
    <section aria-labelledby="synthetic-safety-preview" role="status">
      <h2 id="synthetic-safety-preview">Synthetic safety preview</h2>
      <strong>Engineering test data only — not a medical assessment</strong>
      <dl>
        <div>
          <dt>Machine route token</dt>
          <dd>
            <code>{state.synthetic_decision.route}</code>
          </dd>
        </div>
        <div>
          <dt>Machine reason tokens</dt>
          <dd>
            <ul>
              {state.synthetic_decision.reason_codes.map((reason) => (
                <li key={reason}>
                  <code>{reason}</code>
                </li>
              ))}
            </ul>
          </dd>
        </div>
      </dl>
    </section>
  );
}
