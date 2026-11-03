export type PatientDemographics = {
  dateOfBirth: string | null;
  administrativeSex: string | null;
  genderIdentity: string | null;
  pregnancyStatus: string | null;
  locationContext: string | null;
};

export type PatientProfile = {
  patientId: string;
  status: "ACTIVE" | "INACTIVE" | "MERGED" | "DELETED_PENDING";
  preferredLanguage: string | null;
  demographics: PatientDemographics | null;
  updatedAt: string;
};

export type PatientProfileState =
  { state: "AUTHENTICATED"; profile: PatientProfile } | { state: "ANONYMOUS" };

export type PatientProfileSubmission = {
  expectedUpdatedAt: string;
  preferredLanguage: string | null;
  demographics: PatientDemographics;
};
