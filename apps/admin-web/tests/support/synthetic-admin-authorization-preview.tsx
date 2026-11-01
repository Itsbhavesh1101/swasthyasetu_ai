export type SyntheticAdminPresentationEnvironment =
  "LOCAL" | "TEST" | "STAGING" | "PILOT" | "PRODUCTION";

export type SyntheticAdminPresentationState =
  | "IDENTITY_UNAVAILABLE"
  | "MFA_REQUIRED"
  | "SCOPE_DENIED"
  | "SYNTHETIC_CONTRACT_MATCH"
  | "STALE_SNAPSHOT"
  | "PENDING_HUMAN_REVIEW";

export interface SyntheticAdminPresentation {
  readonly token: "UNAVAILABLE" | "MFA_REQUIRED" | "DENIED" | "MATCH_ONLY" | "STALE" | "PENDING";
  readonly heading: string;
  readonly detail: string;
}

const UNAVAILABLE = Object.freeze({
  detail: "Synthetic admin presentation is unavailable.",
  heading: "Unavailable",
  token: "UNAVAILABLE",
} satisfies SyntheticAdminPresentation);

const PRESENTATIONS = Object.freeze({
  IDENTITY_UNAVAILABLE: Object.freeze({
    detail: "No trusted synthetic identity is available.",
    heading: "Identity unavailable",
    token: "UNAVAILABLE",
  }),
  MFA_REQUIRED: Object.freeze({
    detail: "Synthetic MFA evidence is absent.",
    heading: "MFA required",
    token: "MFA_REQUIRED",
  }),
  PENDING_HUMAN_REVIEW: Object.freeze({
    detail: "Required human decisions remain pending.",
    heading: "Review pending",
    token: "PENDING",
  }),
  SCOPE_DENIED: Object.freeze({
    detail: "No exact synthetic scope match is available.",
    heading: "Scope denied",
    token: "DENIED",
  }),
  STALE_SNAPSHOT: Object.freeze({
    detail: "Synthetic authorization evidence is stale.",
    heading: "Snapshot stale",
    token: "STALE",
  }),
  SYNTHETIC_CONTRACT_MATCH: Object.freeze({
    detail: "A test-only synthetic contract matched. Runtime access is not granted.",
    heading: "Synthetic contract match",
    token: "MATCH_ONLY",
  }),
} satisfies Readonly<Record<SyntheticAdminPresentationState, SyntheticAdminPresentation>>);

function readField(input: object, field: string): unknown {
  try {
    return Reflect.get(input, field);
  } catch {
    return undefined;
  }
}

/** Test-only projection. It is not a runtime authorization decision. */
export function projectSyntheticAdminPresentation(input: unknown): SyntheticAdminPresentation {
  if (typeof input !== "object" || input === null || Array.isArray(input)) {
    return UNAVAILABLE;
  }
  const environment = readField(input, "environment");
  if (environment !== "LOCAL" && environment !== "TEST") {
    return UNAVAILABLE;
  }
  const state = readField(input, "state");
  if (typeof state !== "string" || !Object.hasOwn(PRESENTATIONS, state)) {
    return UNAVAILABLE;
  }
  return PRESENTATIONS[state as SyntheticAdminPresentationState];
}

/** Vitest-only fixture. Production code must never import this module. */
export function SyntheticAdminAuthorizationPreview(
  props: Readonly<{
    environment: SyntheticAdminPresentationEnvironment;
    state: SyntheticAdminPresentationState;
  }>,
) {
  const presentation = projectSyntheticAdminPresentation(props);

  return (
    <section
      aria-labelledby="synthetic-admin-authorization-preview"
      aria-live="polite"
      role="status"
    >
      <h2 id="synthetic-admin-authorization-preview">{presentation.heading}</h2>
      <strong>Engineering test fixture only - no admin authority</strong>
      <p>{presentation.detail}</p>
      <p>Read-only. No administrative action is available.</p>
    </section>
  );
}
