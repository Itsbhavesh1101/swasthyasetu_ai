const CONTRACT_VERSION = "synthetic-mental-health-presentation.v1" as const;
const POLICY_ID = "syn_mh_policy_fixture" as const;
const POLICY_VERSION = "engineering.v1" as const;
const MAX_AGE_MS = 60_000;

const LOCAL_TEST = new Set(["LOCAL", "TEST"]);
const ROUTES = new Set([
  "SYNTHETIC_ROUTE_ALPHA",
  "SYNTHETIC_ROUTE_BETA",
  "SYNTHETIC_ROUTE_GAMMA",
  "SYNTHETIC_CLARIFICATION_REQUIRED",
  "SYNTHETIC_DEGRADED_SAFE_FALLBACK",
]);
const REASON =
  /^SYN_MH_(?:POLICY_REASON_(?:ALPHA|BETA|GAMMA|DELTA)|POLICY_(?:UNAVAILABLE|INVALID|NOT_EFFECTIVE|EXPIRED|SUSPENDED|NO_MATCH|WINNER_CONFLICT)|EVIDENCE_CONFLICT)$/;
const UTC = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/;
const SHA256 = /^[a-f0-9]{64}$/;
const DECISION_ID = /^syn_mh_policy_decision_(alpha|beta|gamma|delta)$/;
const EVALUATION_ID = /^syn_mh_policy_evaluation_(alpha|beta|gamma|delta)$/;

export type MentalHealthPresentationState =
  | Readonly<{
      contract_version: typeof CONTRACT_VERSION;
      kind: "NOT_AVAILABLE";
      code: "POLICY_UNAPPROVED_OR_UNAVAILABLE";
    }>
  | Readonly<{
      contract_version: typeof CONTRACT_VERSION;
      kind: "DEGRADED";
      code: "INVALID_OR_INCOMPATIBLE_RESULT";
    }>
  | Readonly<{
      contract_version: typeof CONTRACT_VERSION;
      kind: "ENGINEERING_SYNTHETIC_PREVIEW";
      classification: "ENGINEERING_ONLY";
      route: string;
      reason_codes: readonly string[];
    }>;

const NOT_AVAILABLE = Object.freeze({
  contract_version: CONTRACT_VERSION,
  kind: "NOT_AVAILABLE" as const,
  code: "POLICY_UNAPPROVED_OR_UNAVAILABLE" as const,
});
const DEGRADED = Object.freeze({
  contract_version: CONTRACT_VERSION,
  kind: "DEGRADED" as const,
  code: "INVALID_OR_INCOMPATIBLE_RESULT" as const,
});

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exactKeys(value: Record<string, unknown>, expected: readonly string[]): boolean {
  const keys = Reflect.ownKeys(value);
  return (
    keys.length === expected.length &&
    keys.every((key) => typeof key === "string" && expected.includes(key))
  );
}

function timestamp(value: unknown, observedAt: Date): value is string {
  if (typeof value !== "string" || !UTC.test(value)) return false;
  const parsed = Date.parse(value);
  const now = observedAt.getTime();
  if (!Number.isFinite(parsed) || !Number.isFinite(now)) return false;
  const canonical = new Date(parsed).toISOString();
  if (value !== (value.includes(".") ? canonical : canonical.replace(".000Z", "Z"))) return false;
  return now >= parsed && now - parsed <= MAX_AGE_MS;
}

function reasons(value: unknown): value is [string] {
  if (!Array.isArray(value) || value.length !== 1 || !Object.hasOwn(value, 0)) return false;
  return typeof value[0] === "string" && REASON.test(value[0]);
}

function routeMatchesReason(route: string, reason: string): boolean {
  if (route === "SYNTHETIC_ROUTE_ALPHA") return reason === "SYN_MH_POLICY_REASON_ALPHA";
  if (route === "SYNTHETIC_ROUTE_BETA") return reason === "SYN_MH_POLICY_REASON_BETA";
  if (route === "SYNTHETIC_ROUTE_GAMMA") return reason === "SYN_MH_POLICY_REASON_DELTA";
  if (route === "SYNTHETIC_CLARIFICATION_REQUIRED") return reason === "SYN_MH_POLICY_REASON_GAMMA";
  return !reason.startsWith("SYN_MH_POLICY_REASON_");
}

/** Projects only exact fresh P14 toy states; protected environments read no untrusted decision. */
export function projectSyntheticMentalHealthPresentation(
  input: Readonly<{ environment: unknown; decision: unknown; observedAt: Date }>,
): MentalHealthPresentationState {
  if (typeof input.environment !== "string" || !LOCAL_TEST.has(input.environment))
    return NOT_AVAILABLE;
  try {
    const value = input.decision;
    if (
      !record(value) ||
      !exactKeys(value, [
        "decision_id",
        "evaluation_id",
        "evaluation_fingerprint",
        "route",
        "reason_codes",
        "policy_reference",
        "decided_at",
        "authority",
        "classification",
        "verification",
      ])
    )
      return DEGRADED;
    if (
      typeof value.route !== "string" ||
      !ROUTES.has(value.route) ||
      !reasons(value.reason_codes) ||
      !routeMatchesReason(value.route, value.reason_codes[0]) ||
      !timestamp(value.decided_at, input.observedAt)
    )
      return DEGRADED;
    if (
      value.authority !== "ENGINEERING_ONLY" ||
      value.classification !== "ENGINEERING_SYNTHETIC" ||
      value.verification !== "UNVERIFIED"
    )
      return DEGRADED;
    if (
      typeof value.decision_id !== "string" ||
      typeof value.evaluation_id !== "string" ||
      !DECISION_ID.test(value.decision_id) ||
      !EVALUATION_ID.test(value.evaluation_id) ||
      value.decision_id.slice("syn_mh_policy_decision_".length) !==
        value.evaluation_id.slice("syn_mh_policy_evaluation_".length) ||
      typeof value.evaluation_fingerprint !== "string" ||
      !SHA256.test(value.evaluation_fingerprint)
    )
      return DEGRADED;
    if (
      !record(value.policy_reference) ||
      !exactKeys(value.policy_reference, ["policy_id", "policy_version", "content_hash"]) ||
      value.policy_reference.policy_id !== POLICY_ID ||
      value.policy_reference.policy_version !== POLICY_VERSION ||
      typeof value.policy_reference.content_hash !== "string" ||
      !SHA256.test(value.policy_reference.content_hash)
    )
      return DEGRADED;
    return Object.freeze({
      contract_version: CONTRACT_VERSION,
      kind: "ENGINEERING_SYNTHETIC_PREVIEW" as const,
      classification: "ENGINEERING_ONLY" as const,
      route: value.route,
      reason_codes: Object.freeze([...value.reason_codes]),
    });
  } catch {
    return DEGRADED;
  }
}
