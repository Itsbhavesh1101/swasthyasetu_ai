const CONTRACT_VERSION = "safety-presentation.v1" as const;
const SYNTHETIC_POLICY_ID = "synthetic-physical-safety-metadata" as const;
const SYNTHETIC_POLICY_VERSION = "engineering.1" as const;
const MAX_REASON_CODES = 16;
const MAX_PREVIEW_AGE_MS = 60_000;

const LOCAL_TEST_ENVIRONMENTS = new Set(["LOCAL", "TEST"]);
const ROUTES = new Set([
  "EMERGENCY",
  "PRIORITY_REVIEW",
  "ROUTINE_CARE",
  "SUPPORTED_SELF_CARE",
  "CLARIFICATION_REQUIRED",
]);
const DECISION_KEYS = new Set([
  "route",
  "reason_codes",
  "policy_id",
  "policy_version",
  "requires_clarification",
  "blocks_self_care",
  "created_at",
]);
const REASON_CODE = /^SYNTHETIC_[A-Z0-9]+(?:_[A-Z0-9]+)*$/;
const UTC_TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/;

export type SyntheticSafetyRoute =
  | "EMERGENCY"
  | "PRIORITY_REVIEW"
  | "ROUTINE_CARE"
  | "SUPPORTED_SELF_CARE"
  | "CLARIFICATION_REQUIRED";

export type SyntheticSafetyDecisionView = Readonly<{
  route: SyntheticSafetyRoute;
  reason_codes: readonly string[];
  policy_id: typeof SYNTHETIC_POLICY_ID;
  policy_version: typeof SYNTHETIC_POLICY_VERSION;
  requires_clarification: boolean;
  blocks_self_care: boolean;
  created_at: string;
}>;

type UnavailableSafetyPresentation = Readonly<{
  contract_version: typeof CONTRACT_VERSION;
  kind: "NOT_AVAILABLE";
  blocks_self_care: true;
  code: "POLICY_UNAPPROVED_OR_UNAVAILABLE";
}>;

type DegradedSafetyPresentation = Readonly<{
  contract_version: typeof CONTRACT_VERSION;
  kind: "DEGRADED";
  blocks_self_care: true;
  code: "INVALID_OR_INCOMPATIBLE_RESULT";
}>;

type SyntheticPreviewSafetyPresentation = Readonly<{
  contract_version: typeof CONTRACT_VERSION;
  kind: "ENGINEERING_SYNTHETIC_PREVIEW";
  blocks_self_care: true;
  classification: "ENGINEERING_ONLY";
  synthetic_decision: SyntheticSafetyDecisionView;
}>;

export type SafetyPresentationState =
  UnavailableSafetyPresentation | DegradedSafetyPresentation | SyntheticPreviewSafetyPresentation;

export type SyntheticSafetyPresentationInput = Readonly<{
  environment: unknown;
  decision: unknown;
  observedAt: Date;
}>;

const NOT_AVAILABLE: UnavailableSafetyPresentation = Object.freeze({
  contract_version: CONTRACT_VERSION,
  kind: "NOT_AVAILABLE",
  blocks_self_care: true,
  code: "POLICY_UNAPPROVED_OR_UNAVAILABLE",
});

const DEGRADED: DegradedSafetyPresentation = Object.freeze({
  contract_version: CONTRACT_VERSION,
  kind: "DEGRADED",
  blocks_self_care: true,
  code: "INVALID_OR_INCOMPATIBLE_RESULT",
});

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasExactKeys(value: Record<string, unknown>): boolean {
  const keys = Reflect.ownKeys(value);
  if (keys.length !== DECISION_KEYS.size) return false;
  for (const key of keys) {
    if (typeof key !== "string" || !DECISION_KEYS.has(key)) return false;
  }
  return true;
}

function isReasonCodes(value: unknown): value is string[] {
  if (!Array.isArray(value) || value.length === 0 || value.length > MAX_REASON_CODES) return false;
  const seen = new Set<string>();
  let previous: string | undefined;
  for (let index = 0; index < value.length; index += 1) {
    if (!Object.hasOwn(value, index)) return false;
    const reason: unknown = value[index];
    if (
      typeof reason !== "string" ||
      reason.length > 64 ||
      !REASON_CODE.test(reason) ||
      seen.has(reason) ||
      (previous !== undefined && previous >= reason)
    ) {
      return false;
    }
    seen.add(reason);
    previous = reason;
  }
  return true;
}

function isValidTimestamp(value: unknown, observedAt: Date): value is string {
  if (typeof value !== "string" || !UTC_TIMESTAMP.test(value)) return false;
  const createdAtMs = Date.parse(value);
  const observedAtMs = observedAt.getTime();
  if (!Number.isFinite(createdAtMs) || !Number.isFinite(observedAtMs)) return false;
  const canonical = new Date(createdAtMs).toISOString();
  const expected = value.includes(".") ? canonical : canonical.replace(".000Z", "Z");
  if (value !== expected) return false;
  const ageMs = observedAtMs - createdAtMs;
  return ageMs >= 0 && ageMs <= MAX_PREVIEW_AGE_MS;
}

function flagsMatchRoute(
  route: SyntheticSafetyRoute,
  requiresClarification: boolean,
  blocksSelfCare: boolean,
): boolean {
  if (route === "CLARIFICATION_REQUIRED") return requiresClarification && blocksSelfCare;
  if (requiresClarification) return false;
  return route === "SUPPORTED_SELF_CARE" ? !blocksSelfCare : blocksSelfCare;
}

function parseSyntheticDecision(
  value: unknown,
  observedAt: Date,
): SyntheticSafetyDecisionView | null {
  if (!isRecord(value) || !hasExactKeys(value)) return null;
  const route = value.route;
  if (typeof route !== "string" || !ROUTES.has(route)) return null;
  const typedRoute = route as SyntheticSafetyRoute;
  if (
    !isReasonCodes(value.reason_codes) ||
    value.policy_id !== SYNTHETIC_POLICY_ID ||
    value.policy_version !== SYNTHETIC_POLICY_VERSION ||
    typeof value.requires_clarification !== "boolean" ||
    typeof value.blocks_self_care !== "boolean" ||
    !flagsMatchRoute(typedRoute, value.requires_clarification, value.blocks_self_care) ||
    !isValidTimestamp(value.created_at, observedAt)
  ) {
    return null;
  }

  const reasonCodes = Object.freeze([...value.reason_codes]);
  return Object.freeze({
    route: typedRoute,
    reason_codes: reasonCodes,
    policy_id: SYNTHETIC_POLICY_ID,
    policy_version: SYNTHETIC_POLICY_VERSION,
    requires_clarification: value.requires_clarification,
    blocks_self_care: value.blocks_self_care,
    created_at: value.created_at,
  });
}

/**
 * Projects only an exact, fresh P9-B toy decision into a non-actionable view state.
 * Protected or unknown environments return before inspecting untrusted decision data.
 */
export function projectSyntheticSafetyPresentation({
  decision,
  environment,
  observedAt,
}: SyntheticSafetyPresentationInput): SafetyPresentationState {
  if (typeof environment !== "string" || !LOCAL_TEST_ENVIRONMENTS.has(environment)) {
    return NOT_AVAILABLE;
  }

  try {
    const syntheticDecision = parseSyntheticDecision(decision, observedAt);
    if (syntheticDecision === null) return DEGRADED;
    return Object.freeze({
      contract_version: CONTRACT_VERSION,
      kind: "ENGINEERING_SYNTHETIC_PREVIEW",
      blocks_self_care: true,
      classification: "ENGINEERING_ONLY",
      synthetic_decision: syntheticDecision,
    });
  } catch {
    return DEGRADED;
  }
}
