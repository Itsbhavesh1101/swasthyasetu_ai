import type { EngineeringMannSetuPreview } from "../lib/mannsetu-demo/contracts";
import { ActionLink, PageHeader, Panel, StatusBanner } from "./ui-primitives";

function readable(value: string) {
  return value.replaceAll("_", " ");
}

export function MannSetuSyntheticPreview({
  result,
}: Readonly<{ result: EngineeringMannSetuPreview }>) {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        eyebrow="College demonstration"
        title="MannSetu synthetic policy preview"
        description="Fixed nonmedical engineering symbols demonstrate deterministic precedence only."
      />
      <StatusBanner title="No mental-health assessment was performed">
        <p>{result.notice}</p>
      </StatusBanner>
      <Panel>
        <h2>Independent symbolic evidence</h2>
        <p>These tokens have no clinical, language, questionnaire, or patient meaning.</p>
        <dl className="review-list">
          <div>
            <dt>Extractor token</dt>
            <dd>{readable(result.extractor_signal)}</dd>
          </div>
          <div>
            <dt>Independent backstop token</dt>
            <dd>{readable(result.backstop_signal)}</dd>
          </div>
          <div>
            <dt>Verification</dt>
            <dd>{readable(result.verification)}</dd>
          </div>
        </dl>
      </Panel>
      <Panel>
        <h2>Deterministic precedence result</h2>
        <p>The toy override wins mechanically; the route token has no real-world interpretation.</p>
        <dl className="review-list">
          <div>
            <dt>Precedence</dt>
            <dd>{readable(result.precedence)}</dd>
          </div>
          <div>
            <dt>Route token</dt>
            <dd>{readable(result.route)}</dd>
          </div>
          <div>
            <dt>Reason token</dt>
            <dd>{readable(result.reason_code)}</dd>
          </div>
        </dl>
      </Panel>
      <Panel>
        <h2>Safety boundary</h2>
        <ul>
          <li>No conversation, screening, diagnosis, or treatment advice.</li>
          <li>No patient data, clinical meaning, verified resource, or contact information.</li>
          <li>No referral, sharing, notification, or external delivery.</li>
        </ul>
      </Panel>
      <p>No assessment, messaging, resource, referral, or clinical-action controls are enabled.</p>
      <ActionLink href="/" variant="secondary">
        Return home
      </ActionLink>
    </div>
  );
}
