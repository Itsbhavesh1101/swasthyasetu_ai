export interface LoadingStateProps {
  readonly label?: string;
}

export function LoadingState({ label = "Loading application" }: LoadingStateProps) {
  return (
    <section aria-busy="true" aria-live="polite" className="state-panel" role="status">
      <span aria-hidden="true" className="loading-indicator" />
      <p className="font-medium">{label}</p>
    </section>
  );
}
