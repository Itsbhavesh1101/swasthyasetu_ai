import type { Metadata } from "next";
import { DocumentVault } from "../../components/document-vault";
import { PageHeader } from "../../components/ui-primitives";

export const metadata: Metadata = { title: "Documents" };

export default function DocumentsPage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Private vault"
        title="Health documents"
        description="Keep reports and prescriptions with your health record."
      />
      <DocumentVault />
    </div>
  );
}
