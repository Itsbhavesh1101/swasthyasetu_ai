export type AccountState =
  { state: "AUTHENTICATED"; displayName?: string; patientId?: string } | { state: "ANONYMOUS" };

export type AccountSubmission = {
  email: string;
  password: string;
  name?: string;
};
