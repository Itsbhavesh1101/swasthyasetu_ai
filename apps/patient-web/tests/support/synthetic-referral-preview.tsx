export type SyntheticReferralPreviewState = "UNAVAILABLE" | "UNKNOWN" | "FAILED";

function stateMessage(state: SyntheticReferralPreviewState): string {
  switch (state) {
    case "UNKNOWN":
      return "Referral status is unknown in this fixture.";
    case "FAILED":
      return "A simulated referral operation failed. No delivery is claimed.";
    case "UNAVAILABLE":
    default:
      return "Referral services are unavailable in this fixture.";
  }
}

/** Vitest-only fixture. Production code must never import this module. */
export function SyntheticReferralPreview({
  state,
}: Readonly<{ state: SyntheticReferralPreviewState }>) {
  return (
    <section aria-labelledby="synthetic-referral-preview" aria-live="polite" role="status">
      <h2 id="synthetic-referral-preview">Synthetic referral preview</h2>
      <strong>Engineering test fixture only — no referral has been created or sent</strong>
      <p>{stateMessage(state)}</p>
      <p>Synthetic source only — not verified provider or resource data.</p>
    </section>
  );
}
