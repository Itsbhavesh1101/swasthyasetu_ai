export type DemoSection = {
  section_id: string;
  readiness: string;
  labels: string[];
  review_required: boolean;
};

export type DemoSafetyDecision = {
  route: string;
  reason_codes: string[];
  policy_id: string;
  policy_version: string;
  requires_clarification: boolean;
  blocks_self_care: boolean;
  created_at: string;
};

export type EngineeringDemoResult = {
  intake_id: string;
  encounter_id: string;
  status: "SYNTHETIC_PREVIEW" | "ABSTAINED";
  classification: "ENGINEERING_ONLY";
  extracted_label: string | null;
  verification_state: "AI_EXTRACTED_UNCONFIRMED" | null;
  safety_decision: DemoSafetyDecision | null;
  summary_sections: DemoSection[];
  notice: string;
};
