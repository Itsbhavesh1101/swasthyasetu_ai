import type { EngineeringABDMPreview } from "../lib/abdm-demo/contracts";
import { ActionLink, PageHeader, Panel, StatusBanner } from "./ui-primitives";

function readable(value: string) {
  return value.replaceAll("_", " ");
}

export function ABDMSyntheticPreview({ result }: Readonly<{ result: EngineeringABDMPreview }>) {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        eyebrow="College demonstration"
        title="Synthetic ABDM failure boundary"
        description="Fixed engineering tokens demonstrate a detached, zero-egress adapter boundary only."
      />
      <StatusBanner title="No ABHA identity or ABDM exchange occurred">
        <p>{result.notice}</p>
      </StatusBanner>
      <Panel>
        <h2>Scripted rejection</h2>
        <p>A known toy request returns the exact content-free rejection state.</p>
        <dl className="review-list">
          <div>
            <dt>Mode</dt>
            <dd>{readable(result.mode)}</dd>
          </div>
          <div>
            <dt>State</dt>
            <dd>{readable(result.scripted_state)}</dd>
          </div>
          <div>
            <dt>Issue</dt>
            <dd>{readable(result.scripted_issue)}</dd>
          </div>
        </dl>
      </Panel>
      <Panel>
        <h2>Unknown request</h2>
        <p>Unknown requests fail closed as unavailable; they never fall back to acceptance.</p>
        <dl className="review-list">
          <div>
            <dt>State</dt>
            <dd>{readable(result.unknown_state)}</dd>
          </div>
          <div>
            <dt>Issue</dt>
            <dd>{readable(result.unknown_issue)}</dd>
          </div>
          <div>
            <dt>Network egress</dt>
            <dd>None</dd>
          </div>
        </dl>
      </Panel>
      <p>
        The local intake path is not accessed or mutated. No identity, consent, upload, exchange,
        sandbox, retry, transport, or persistence controls exist.
      </p>
      <ActionLink href="/" variant="secondary">
        Return home
      </ActionLink>
    </div>
  );
}
