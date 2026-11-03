export type HistoryFactType =
  "PROBLEM" | "MEDICATION" | "ALLERGY" | "PROCEDURE" | "OBSERVATION" | "INVESTIGATION";

export type HistoryItem = {
  factId: string;
  factType: HistoryFactType;
  label: string;
  status: string | null;
  effectiveTime: string | null;
  recordedAt: string;
  verificationState: "PATIENT_CONFIRMED" | "CLINICIAN_CONFIRMED" | "SUPERSEDED";
  supersededByFactId: string | null;
};

export type HistoryState =
  { state: "AUTHENTICATED"; items: HistoryItem[] } | { state: "ANONYMOUS" };

export type HistoryPayload = Record<string, string | null> & { fact_type: HistoryFactType };
