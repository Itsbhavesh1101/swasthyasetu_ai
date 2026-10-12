import { ActionLink, PageHeader, UnavailableState } from "./ui-primitives";

export function RouteUnavailable({
  availableIn,
  description,
  title,
}: Readonly<{ availableIn: string; description: string; title: string }>) {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader title={title} description="This page is part of the planned patient journey." />
      <UnavailableState
        availableIn={availableIn}
        description={description}
        title="This step is paused"
      />
      <ActionLink href="/" variant="secondary">
        Return home
      </ActionLink>
    </div>
  );
}
