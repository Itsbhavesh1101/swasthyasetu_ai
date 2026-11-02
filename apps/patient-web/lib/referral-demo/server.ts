import { NextResponse } from "next/server";

import type { EngineeringReferralDiscovery } from "./contracts";

const FIELDS = [
  "classification",
  "authority",
  "route_disposition",
  "route_reason",
  "service_code",
  "provider_display_name",
  "provider_service_code",
  "provider_verification",
  "resource_display_name",
  "resource_code",
  "resource_verification",
  "source_verification",
  "contacts_available",
  "provider_selected",
  "referral_state_model",
  "referral_created",
  "sharing_consent",
  "external_delivery",
  "notification_delivery",
  "notice",
];

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exactKeys(value: Record<string, unknown>): boolean {
  const actual = Object.keys(value).sort();
  const expected = [...FIELDS].sort();
  return actual.length === expected.length && actual.every((key, index) => key === expected[index]);
}

function backendUrl(): string | undefined {
  const value = process.env.SWASTHYASETU_BACKEND_URL?.trim();
  if (!value) return undefined;
  try {
    const parsed = new URL(value);
    const loopback = ["localhost", "127.0.0.1", "::1"].includes(parsed.hostname);
    if (
      !["http:", "https:"].includes(parsed.protocol) ||
      parsed.username ||
      parsed.password ||
      parsed.pathname !== "/" ||
      parsed.search ||
      parsed.hash ||
      (parsed.protocol === "http:" && !loopback)
    )
      return undefined;
    return parsed.origin;
  } catch {
    return undefined;
  }
}

export function validEngineeringReferralDiscovery(
  value: unknown,
): value is EngineeringReferralDiscovery {
  if (!record(value) || !exactKeys(value)) return false;
  if (
    value.classification !== "ENGINEERING_SYNTHETIC" ||
    value.authority !== "ENGINEERING_ONLY" ||
    value.route_disposition !== "SYMBOLIC_MATCH" ||
    value.route_reason !== "EXACT_SYMBOLIC_MATCH" ||
    value.service_code !== "syn_service_college_demo" ||
    value.provider_display_name !== "Synthetic College Demo Provider" ||
    value.provider_service_code !== "syn_service_college_demo" ||
    value.provider_verification !== "UNVERIFIED" ||
    value.resource_display_name !== "Synthetic College Demo Resource" ||
    value.resource_code !== "syn_resource_type_college_demo" ||
    value.resource_verification !== "UNVERIFIED" ||
    value.source_verification !== "UNVERIFIED" ||
    value.contacts_available !== false ||
    value.provider_selected !== false ||
    value.referral_state_model !== "OFFERED" ||
    value.referral_created !== false ||
    value.sharing_consent !== "NOT_REQUESTED" ||
    value.external_delivery !== false ||
    value.notification_delivery !== false ||
    typeof value.notice !== "string" ||
    value.notice.length === 0 ||
    value.notice.length > 256
  )
    return false;
  const notice = value.notice.toLowerCase();
  return [
    "synthetic",
    "unverified",
    "no provider is selected",
    "no referral is created",
    "no data is shared or delivered",
  ].every((token) => notice.includes(token));
}

export type EngineeringReferralOutcome =
  { ok: true; result: EngineeringReferralDiscovery } | { ok: false; status: number; code: string };

export async function loadEngineeringReferralDiscovery(): Promise<EngineeringReferralOutcome> {
  const base = backendUrl();
  if (!base) return { ok: false, status: 404, code: "FEATURE_DISABLED" };
  try {
    const response = await fetch(`${base}/api/v1/engineering-demo/referral-discovery`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(5_000),
    });
    const data: unknown = await response.json().catch(() => undefined);
    if (!response.ok || !validEngineeringReferralDiscovery(data))
      return {
        ok: false,
        status: response.ok ? 502 : response.status,
        code: "RESULT_UNAVAILABLE",
      };
    return { ok: true, result: data };
  } catch {
    return { ok: false, status: 503, code: "DEPENDENCY_UNAVAILABLE" };
  }
}

export async function readEngineeringReferralDiscovery(): Promise<NextResponse> {
  const outcome = await loadEngineeringReferralDiscovery();
  if (!outcome.ok)
    return NextResponse.json(
      { error: { code: outcome.code, message: "The engineering preview is unavailable." } },
      { status: outcome.status, headers: { "Cache-Control": "no-store" } },
    );
  return NextResponse.json(outcome.result, { headers: { "Cache-Control": "no-store" } });
}
