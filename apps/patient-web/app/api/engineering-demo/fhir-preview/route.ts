import { readEngineeringFHIRPreview } from "../../../../lib/fhir-demo/server";

export const dynamic = "force-dynamic";

export async function GET() {
  return readEngineeringFHIRPreview();
}
