export type BloodGroup = "A+" | "A-" | "B+" | "B-" | "AB+" | "AB-" | "O+" | "O-" | "UNKNOWN";

export type PatientDemographics = {
  dateOfBirth: string | null;
  administrativeSex: string | null;
  genderIdentity: string | null;
  pregnancyStatus: string | null;
  locationContext: string | null;
  heightCm: number | null;
  weightKg: number | null;
  bmi: number | null;
  mobileNumber: string | null;
  bloodGroup: BloodGroup | null;
  aadhaarLastFour: string | null;
};

export type PatientDemographicsSubmission = {
  dateOfBirth: string | null;
  administrativeSex: string | null;
  genderIdentity: string | null;
  pregnancyStatus: string | null;
  locationContext: string | null;
  heightCm: number | null;
  weightKg: number | null;
  mobileNumber: string | null;
  bloodGroup: BloodGroup | null;
  aadhaarNumber: string | null;
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
  demographics: PatientDemographicsSubmission;
};
