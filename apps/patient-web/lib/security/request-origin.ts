import type { NextRequest } from "next/server";

export type MutationOriginError = Readonly<{
  code: "ORIGIN_CONFIGURATION_INVALID" | "ORIGIN_REJECTED";
  message: string;
  status: 403 | 503;
}>;

function isLoopback(hostname: string): boolean {
  return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1";
}

function canonicalOrigin(value: string): string | undefined {
  try {
    const parsed = new URL(value);
    if (
      !["http:", "https:"].includes(parsed.protocol) ||
      parsed.username ||
      parsed.password ||
      parsed.pathname !== "/" ||
      parsed.search ||
      parsed.hash ||
      (parsed.protocol === "http:" && !isLoopback(parsed.hostname)) ||
      parsed.origin !== value
    ) {
      return undefined;
    }
    return parsed.origin;
  } catch {
    return undefined;
  }
}

function expectedOrigin(request: NextRequest): string | undefined {
  const configured = process.env.SWASTHYASETU_PUBLIC_ORIGIN?.trim();
  if (configured) return canonicalOrigin(configured);
  if (process.env.NODE_ENV === "production") return undefined;
  const host = request.headers.get("host");
  return canonicalOrigin(host ? `${request.nextUrl.protocol}//${host}` : request.nextUrl.origin);
}

export function validateMutationOrigin(request: NextRequest): MutationOriginError | undefined {
  const expected = expectedOrigin(request);
  if (!expected) {
    return {
      code: "ORIGIN_CONFIGURATION_INVALID",
      message: "The application origin is not configured.",
      status: 503,
    };
  }
  const supplied = request.headers.get("origin");
  if (!supplied || canonicalOrigin(supplied) !== expected) {
    return {
      code: "ORIGIN_REJECTED",
      message: "This request origin is not allowed.",
      status: 403,
    };
  }
  return undefined;
}
