export type EngineeringSummarySection = {
  section:
    | "CHIEF_COMPLAINT"
    | "HPI"
    | "PAST_MEDICAL_HISTORY"
    | "PAST_SURGICAL_HISTORY"
    | "MEDICATIONS"
    | "ALLERGIES"
    | "FAMILY_HISTORY"
    | "PERSONAL_HISTORY"
    | "REVIEW_OF_SYSTEMS"
    | "PRIOR_INVESTIGATIONS";
  readiness: "UNKNOWN" | "UNVERIFIED";
  assertions: string[];
  source_kinds: string[];
  conflict_review_required: false;
};

export type EngineeringSummaryResult = {
  status: "DRAFT";
  classification: "ENGINEERING_ONLY";
  review_state: "REVIEW_REQUIRED";
  freshness: "STALE";
  affected_sections: ["HPI"];
  drift_reasons: ["NEW_SOURCE"];
  source_count: 1;
  sections: EngineeringSummarySection[];
  source_access: "NOT_AUTHORIZED";
  can_edit: false;
  can_confirm: false;
  can_reject: false;
  external_egress: false;
  notice: string;
};
