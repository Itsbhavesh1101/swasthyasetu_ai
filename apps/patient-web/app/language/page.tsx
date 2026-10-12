import type { Metadata } from "next";

import { LanguageSelector } from "../../components/language-selector";
import { PageHeader } from "../../components/ui-primitives";

export const metadata: Metadata = { title: "Language" };

export default function LanguagePage() {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        title="Choose a language"
        description="This preference applies only to your temporary private session. The full experience is not yet translated."
      />
      <LanguageSelector />
    </div>
  );
}
