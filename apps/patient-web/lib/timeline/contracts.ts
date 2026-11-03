export type TimelineItem = Readonly<{
  entryId: string;
  entryType: "ENCOUNTER" | "CLINICAL_FACT";
  occurredAt: string;
  category: string;
  label: string;
  detail: string;
}>;

export type TimelineState =
  | Readonly<{ state: "ANONYMOUS" }>
  | Readonly<{
      state: "AUTHENTICATED";
      items: readonly TimelineItem[];
      nextCursor?: string;
    }>;
