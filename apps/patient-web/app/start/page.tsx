import type { Metadata } from "next";

import { RouteUnavailable } from "../../components/route-unavailable";

export const metadata: Metadata = { title: "Start" };

export default function StartPage() {
  return (
    <RouteUnavailable
      availableIn="P6-B onboarding"
      description="A secure session and clear consent step must be connected before this journey can begin."
      title="Start your journey"
    />
  );
}
