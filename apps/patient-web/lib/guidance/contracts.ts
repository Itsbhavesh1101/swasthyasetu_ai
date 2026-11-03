export type GuidanceOutcome =
  "ANSWERED" | "OUT_OF_SCOPE" | "CONSENT_REQUIRED" | "UNAVAILABLE" | "REJECTED";

export type GuidanceCitation = Readonly<{ title: string; url: string }>;

export type GuidanceState =
  | Readonly<{ state: "ANONYMOUS" }>
  | Readonly<{
      state: "AUTHENTICATED";
      active: boolean;
      noticeVersion: "external-ai-v1";
      scope: readonly ["ayurvedic_guidance"];
    }>;

export type GuidanceResult = Readonly<{
  outcome: GuidanceOutcome;
  answer?: string;
  citations: readonly GuidanceCitation[];
  retrievedAt?: string;
}>;
