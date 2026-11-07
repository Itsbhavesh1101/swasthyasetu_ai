import type {
  BloodGroup,
  PatientProfile,
  PatientProfileSubmission,
} from "../lib/patient/contracts";

export const bloodGroupOptions: ReadonlyArray<{ label: string; value: BloodGroup }> = [
  { label: "A+", value: "A+" },
  { label: "A−", value: "A-" },
  { label: "B+", value: "B+" },
  { label: "B−", value: "B-" },
  { label: "AB+", value: "AB+" },
  { label: "AB−", value: "AB-" },
  { label: "O+", value: "O+" },
  { label: "O−", value: "O-" },
  { label: "Unknown", value: "UNKNOWN" },
];

export type ProfileDraft = {
  displayName: string;
  preferredLanguage: string;
  dateOfBirth: string;
  administrativeSex: string;
  heightCm: string;
  weightKg: string;
  mobileNumber: string;
  bloodGroup: BloodGroup | "";
  demoAadhaarReference: string;
  genderIdentity: string;
  pregnancyStatus: string;
  locationContext: string;
};

export function profileDraft(profile: PatientProfile): ProfileDraft {
  const demographics = profile.demographics;
  return {
    displayName: profile.displayName ?? "",
    preferredLanguage: profile.preferredLanguage ?? "",
    dateOfBirth: demographics?.dateOfBirth ?? "",
    administrativeSex: demographics?.administrativeSex ?? "",
    heightCm: String(demographics?.heightCm ?? ""),
    weightKg: String(demographics?.weightKg ?? ""),
    mobileNumber: demographics?.mobileNumber ?? "",
    bloodGroup: demographics?.bloodGroup ?? "",
    demoAadhaarReference: demographics?.demoAadhaarReference ?? "",
    genderIdentity: demographics?.genderIdentity ?? "",
    pregnancyStatus: demographics?.pregnancyStatus ?? "",
    locationContext: demographics?.locationContext ?? "",
  };
}

function nullable(value: string) {
  const trimmed = value.trim();
  return trimmed || null;
}

export function profileSubmission(
  profile: PatientProfile,
  draft: ProfileDraft,
): PatientProfileSubmission {
  return {
    expectedUpdatedAt: profile.updatedAt,
    displayName: draft.displayName.trim(),
    preferredLanguage: nullable(draft.preferredLanguage),
    demographics: {
      dateOfBirth: nullable(draft.dateOfBirth),
      administrativeSex: nullable(draft.administrativeSex),
      genderIdentity: nullable(draft.genderIdentity),
      pregnancyStatus: nullable(draft.pregnancyStatus),
      locationContext: nullable(draft.locationContext),
      heightCm: Number(draft.heightCm),
      weightKg: Number(draft.weightKg),
      mobileNumber: nullable(draft.mobileNumber),
      bloodGroup: draft.bloodGroup || null,
      demoAadhaarReference: nullable(draft.demoAadhaarReference),
    },
  };
}

export function calculatedAge(dateOfBirth: string, today = new Date()) {
  const birthDate = /^\d{4}-\d{2}-\d{2}$/.test(dateOfBirth)
    ? new Date(`${dateOfBirth}T00:00:00Z`)
    : null;
  if (!birthDate || Number.isNaN(birthDate.getTime())) return null;
  const age =
    today.getUTCFullYear() -
    birthDate.getUTCFullYear() -
    (today.getUTCMonth() < birthDate.getUTCMonth() ||
    (today.getUTCMonth() === birthDate.getUTCMonth() && today.getUTCDate() < birthDate.getUTCDate())
      ? 1
      : 0);
  return age >= 0 ? age : null;
}

export function calculatedBmi(heightCm: string, weightKg: string) {
  const height = Number(heightCm);
  const weight = Number(weightKg);
  return height >= 30 && weight >= 1 ? weight / (height / 100) ** 2 : null;
}
