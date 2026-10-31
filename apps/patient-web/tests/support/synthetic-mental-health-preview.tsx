import type { MentalHealthPresentationState } from "../../lib/mental-health/presentation";

/** Vitest-only harness; production code must never import this component. */
export function SyntheticMentalHealthPreview({
  state,
}: Readonly<{ state: MentalHealthPresentationState }>) {
  if (state.kind !== "ENGINEERING_SYNTHETIC_PREVIEW") {
    return (
      <section aria-labelledby="synthetic-mh-unavailable" role="status">
        <h2 id="synthetic-mh-unavailable">Mental-health result unavailable</h2>
        <p>No mental-health assessment has been performed.</p>
      </section>
    );
  }
  return (
    <section aria-labelledby="synthetic-mh-preview" role="status">
      <h2 id="synthetic-mh-preview">Synthetic mental-health preview</h2>
      <strong>Engineering test data only — not a medical assessment</strong>
      <code>{state.route}</code>
      <ul>
        {state.reason_codes.map((reason) => (
          <li key={reason}>
            <code>{reason}</code>
          </li>
        ))}
      </ul>
    </section>
  );
}
