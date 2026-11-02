import type { EngineeringSelfCarePreview } from "../lib/self-care-demo/contracts";
import { ActionLink, PageHeader, Panel, StatusBanner } from "./ui-primitives";

function readable(value: string) {
  return value.replaceAll("_", " ");
}

export function SelfCareSyntheticPreview({
  result,
}: Readonly<{ result: EngineeringSelfCarePreview }>) {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        eyebrow="College demonstration"
        title="Synthetic self-care safety preview"
        description="Fixed engineering symbols demonstrate safety-first eligibility mechanics only."
      />
      <StatusBanner title="No self-care guidance is displayed">
        <p>{result.notice}</p>
      </StatusBanner>
      <Panel>
        <h2>Unapproved knowledge placeholder</h2>
        <p>The placeholder contains no remedy, instruction, treatment, or readable guidance.</p>
        <dl className="review-list">
          <div>
            <dt>Placeholder token</dt>
            <dd>{readable(result.placeholder_token)}</dd>
          </div>
          <div>
            <dt>Pack state</dt>
            <dd>{readable(result.knowledge_pack_state)}</dd>
          </div>
          <div>
            <dt>Source verification</dt>
            <dd>{readable(result.source_verification)}</dd>
          </div>
        </dl>
      </Panel>
      <Panel>
        <h2>Exact symbolic candidate case</h2>
        <p>An engineering candidate reference is not clinical eligibility or display permission.</p>
        <dl className="review-list">
          <div>
            <dt>Outcome</dt>
            <dd>{readable(result.candidate_outcome)}</dd>
          </div>
          <div>
            <dt>Reason</dt>
            <dd>{readable(result.candidate_reason)}</dd>
          </div>
          <div>
            <dt>Display authorized</dt>
            <dd>No</dd>
          </div>
        </dl>
      </Panel>
      <Panel>
        <h2>Safety-block case</h2>
        <p>The upstream synthetic safety override removes every downstream candidate.</p>
        <dl className="review-list">
          <div>
            <dt>Outcome</dt>
            <dd>{readable(result.blocked_outcome)}</dd>
          </div>
          <div>
            <dt>Reason</dt>
            <dd>{readable(result.blocked_reason)}</dd>
          </div>
          <div>
            <dt>Remaining candidates</dt>
            <dd>{result.blocked_candidate_count}</dd>
          </div>
        </dl>
      </Panel>
      <p>
        No input, advice, retrieval, recommendation, consent, sharing, or delivery controls exist.
      </p>
      <ActionLink href="/" variant="secondary">
        Return home
      </ActionLink>
    </div>
  );
}
