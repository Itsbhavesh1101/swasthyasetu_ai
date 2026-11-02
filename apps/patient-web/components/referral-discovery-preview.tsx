import type { EngineeringReferralDiscovery } from "../lib/referral-demo/contracts";
import { ActionLink, PageHeader, Panel, StatusBanner } from "./ui-primitives";

function readable(value: string) {
  return value.replaceAll("_", " ");
}

export function ReferralDiscoveryPreview({
  result,
}: Readonly<{ result: EngineeringReferralDiscovery }>) {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        eyebrow="College demonstration"
        title="Synthetic referral discovery"
        description="Offline engineering evidence only. This is not provider advice or a referral."
      />
      <StatusBanner title="No referral or sharing occurred">
        <p>{result.notice}</p>
      </StatusBanner>
      <Panel>
        <h2>Symbolic routing contract</h2>
        <p>A fixed nonmedical engineering symbol produced one exact service token.</p>
        <dl className="review-list">
          <div>
            <dt>Disposition</dt>
            <dd>{readable(result.route_disposition)}</dd>
          </div>
          <div>
            <dt>Service token</dt>
            <dd>{readable(result.service_code)}</dd>
          </div>
        </dl>
      </Panel>
      <Panel>
        <h2>Detached directory fixtures</h2>
        <p>These records are not selected, verified, contactable, ranked, or recommended.</p>
        <div className="feature-grid">
          <section aria-labelledby="provider-fixture-heading">
            <h3 id="provider-fixture-heading">{result.provider_display_name}</h3>
            <p>{result.provider_verification} · no contact data</p>
          </section>
          <section aria-labelledby="resource-fixture-heading">
            <h3 id="resource-fixture-heading">{result.resource_display_name}</h3>
            <p>{result.resource_verification} · no contact data</p>
          </section>
        </div>
      </Panel>
      <Panel>
        <h2>Referral state model</h2>
        <dl className="review-list">
          <div>
            <dt>Detached state token</dt>
            <dd>{result.referral_state_model}</dd>
          </div>
          <div>
            <dt>Referral created</dt>
            <dd>No</dd>
          </div>
          <div>
            <dt>Referral-sharing consent</dt>
            <dd>{readable(result.sharing_consent)}</dd>
          </div>
          <div>
            <dt>External or notification delivery</dt>
            <dd>None</dd>
          </div>
        </dl>
      </Panel>
      <p>
        No provider-selection, contact, booking, send, consent, or referral controls are enabled.
      </p>
      <ActionLink href="/" variant="secondary">
        Return home
      </ActionLink>
    </div>
  );
}
