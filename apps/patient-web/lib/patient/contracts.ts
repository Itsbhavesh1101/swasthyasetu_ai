export type PatientDemographics = {
  dateOfBirth: string | null;
  administrativeSex: string | null;
  genderIdentity: string | null;
  pregnancyStatus: string | null;
  locationContext: string | null;
  heightCm: number | null;
  weightKg: number | null;
  bmi: number | null;
};

export type PatientProfile = {
  patientId: string;
  status: "ACTIVE" | "INACTIVE" | "MERGED" | "DELETED_PENDING";
  preferredLanguage: string | null;
  displayName: string | null;
  profileComplete: boolean;
  demographics: PatientDemographics | null;
  updatedAt: string;
};

export type PatientProfileState =
  { state: "AUTHENTICATED"; profile: PatientProfile } | { state: "ANONYMOUS" };

export type PatientProfileSubmission = {
  expectedUpdatedAt: string;
  preferredLanguage: string | null;
  displayName: string;
  demographics: Omit<PatientDemographics, "bmi">;
};
