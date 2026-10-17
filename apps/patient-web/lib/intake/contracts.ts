export type AnswerType =
  | "TEXT"
  | "SINGLE_CHOICE"
  | "MULTI_CHOICE"
  | "BOOLEAN"
  | "NUMBER"
  | "DATE"
  | "DURATION"
  | "SEVERITY_SCALE";

export type IntakeQuestion = {
  question_id: string;
  question_version: string;
  pack_id: string;
  pack_version: string;
  section: string;
  prompt: string;
  help_text: string | null;
  answer_type: AnswerType;
  requiredness: string;
  allow_unknown: boolean;
  allow_prefer_not_to_answer: boolean;
  allow_skip: boolean;
  constraints: Record<string, unknown>;
  options: { id: string; label: string }[];
};

export type IntakeAnswer = {
  answer_id: string;
  question_id: string;
  question_version: string;
  answer_type: AnswerType;
  value: string | number | boolean | null;
  selected_option_ids: string[] | null;
  unit: string | null;
  response_disposition: string;
  source_label: string;
};

export type IntakeView = {
  intake_id: string;
  encounter_id: string;
  status: "IN_PROGRESS" | "COMPLETED" | "ABANDONED";
  version: number;
  started_at: string;
  completed_at: string | null;
  pack_versions: { pack_id: string; pack_version: string }[];
  current_question: IntakeQuestion | null;
  engine_state: "NEXT_QUESTION" | "CLARIFICATION_REQUIRED" | "INCOMPLETE" | "COMPLETION_READY";
  completion_ready: boolean;
  answers: IntakeAnswer[];
  missing_information: {
    field_or_question_key: string;
    reason_code: string;
    requiredness: string;
  }[];
};

export type IntakeError = { error: { code: string; message: string } };
