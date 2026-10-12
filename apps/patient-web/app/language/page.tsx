import type { Metadata } from "next";

import { RouteUnavailable } from "../../components/route-unavailable";

export const metadata: Metadata = { title: "Language" };

export default function LanguagePage() {
  return (
    <RouteUnavailable
      availableIn="P6-B language selection"
      description="Language choices are not active in this build, and no preference is stored."
      title="Choose a language"
    />
  );
}
