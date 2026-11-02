import type { EngineeringFHIRPreview } from "../lib/fhir-demo/contracts";
import { ActionLink, PageHeader, Panel, StatusBanner } from "./ui-primitives";

function readable(value: string) {
  return value.replaceAll("_", " ");
}

export function FHIRSyntheticPreview({ result }: Readonly<{ result: EngineeringFHIRPreview }>) {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        eyebrow="College demonstration"
        title="Synthetic FHIR boundary preview"
        description="Fixed engineering metadata demonstrates mapping and validation boundaries only."
      />
      <StatusBanner title="No FHIR exchange or conformance claim occurred">
        <p>{result.notice}</p>
      </StatusBanner>
      <Panel>
        <h2>Symbolic mapping projection</h2>
        <p>
          No resource fields, identifiers, clinical values, narrative, or terminology are present.
        </p>
        <dl className="review-list">
          <div>
            <dt>FHIR version</dt>
            <dd>{result.fhir_version}</dd>
          </div>
          <div>
            <dt>Resource label</dt>
            <dd>{result.resource_type}</dd>
          </div>
          <div>
            <dt>Projection state</dt>
            <dd>{readable(result.mapping_state)}</dd>
          </div>
        </dl>
      </Panel>
      <Panel>
        <h2>Validation boundary</h2>
        <p>Structural mechanics pass for the toy metadata; profile validation fails closed.</p>
        <dl className="review-list">
          <div>
            <dt>Structural result</dt>
            <dd>{readable(result.structural_validation)}</dd>
          </div>
          <div>
            <dt>Profile result</dt>
            <dd>{readable(result.profile_validation)}</dd>
          </div>
          <div>
            <dt>Profile reason</dt>
            <dd>{readable(result.profile_issue)}</dd>
          </div>
        </dl>
      </Panel>
      <p>
        No upload, input, export, import, consent, exchange, transport, ABDM, or persistence
        controls exist.
      </p>
      <ActionLink href="/" variant="secondary">
        Return home
      </ActionLink>
    </div>
  );
}
