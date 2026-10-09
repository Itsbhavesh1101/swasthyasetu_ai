export interface EmptyStateProps {
  readonly description: string;
  readonly title: string;
}

export function EmptyState({ description, title }: EmptyStateProps) {
  return (
    <section aria-labelledby="empty-state-title" className="state-panel">
      <h2 className="text-xl font-semibold" id="empty-state-title">
        {title}
      </h2>
      <p className="max-w-2xl text-[var(--color-muted)]">{description}</p>
    </section>
  );
}
