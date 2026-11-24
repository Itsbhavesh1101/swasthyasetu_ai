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
  aadhaarNumber: string;
  pregnancyStatus: string;
  genderIdentity?: string;
  locationContext?: string;
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
    aadhaarNumber: "",
    pregnancyStatus: demographics?.pregnancyStatus ?? "",
  };
}

export function maskedAadhaar(lastFour: string | null | undefined): string {
  if (!lastFour || !/^[0-9]{4}$/.test(lastFour)) return "";
  return `•••• •••• ${lastFour}`;
}

export function formatProfileDate(value: string | null | undefined): string {
  if (!value || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return "—";
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function nullable(value: string | undefined | null) {
  if (!value) return null;
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
      genderIdentity: null,
      pregnancyStatus:
        draft.administrativeSex === "female" ? nullable(draft.pregnancyStatus) : null,
      locationContext: null,
      heightCm: Number(draft.heightCm),
      weightKg: Number(draft.weightKg),
      mobileNumber: nullable(draft.mobileNumber),
      bloodGroup: draft.bloodGroup || null,
      aadhaarNumber: nullable(draft.aadhaarNumber),
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
