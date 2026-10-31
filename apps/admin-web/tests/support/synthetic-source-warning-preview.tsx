export type SyntheticSourceWarningState =
  "SOURCE_UNAVAILABLE" | "SOURCE_UNVERIFIED" | "SOURCE_STALE" | "SOURCE_REVOKED";

function stateMessage(state: SyntheticSourceWarningState): string {
  switch (state) {
    case "SOURCE_UNVERIFIED":
      return "Synthetic source evidence is unverified.";
    case "SOURCE_STALE":
      return "Synthetic source evidence is stale.";
    case "SOURCE_REVOKED":
      return "Synthetic source evidence is revoked.";
    case "SOURCE_UNAVAILABLE":
    default:
      return "Synthetic source evidence is unavailable.";
  }
}

/** Vitest-only fixture. Production code must never import this module. */
export function SyntheticSourceWarningPreview({
  state,
}: Readonly<{ state: SyntheticSourceWarningState }>) {
  return (
    <section aria-labelledby="synthetic-source-warning-preview" aria-live="polite" role="status">
      <h2 id="synthetic-source-warning-preview">Synthetic source warning preview</h2>
      <strong>Engineering test fixture only — no source authority</strong>
      <p>{stateMessage(state)}</p>
      <p>Read-only. No moderation action is available.</p>
    </section>
  );
}
