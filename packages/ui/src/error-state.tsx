export interface ErrorStateProps {
  readonly description?: string;
  readonly onRetry?: () => void;
  readonly title?: string;
}

export function ErrorState({
  description = "The application could not complete this request. Please try again.",
  onRetry,
  title = "Something went wrong",
}: ErrorStateProps) {
  return (
    <section aria-labelledby="error-state-title" className="state-panel" role="alert">
      <h2 className="text-xl font-semibold" id="error-state-title">
        {title}
      </h2>
      <p className="text-[var(--color-muted)]">{description}</p>
      {onRetry ? (
        <button className="primary-action" onClick={onRetry} type="button">
          Try again
        </button>
      ) : null}
    </section>
  );
}
