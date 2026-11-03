export type AccountState =
  | {
      state: "AUTHENTICATED";
      displayName?: string | null;
      patientId?: string;
      profileComplete: boolean;
    }
  | { state: "ANONYMOUS" };

export type AccountSubmission = {
  email: string;
  password: string;
};
