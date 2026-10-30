export type SecurityHeader = Readonly<{ key: string; value: string }>;

const sharedHeaders: readonly SecurityHeader[] = [
  { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
  { key: "Cross-Origin-Resource-Policy", value: "same-origin" },
  {
    key: "Permissions-Policy",
    value: "camera=(), geolocation=(), microphone=(), payment=(), usb=()",
  },
  { key: "Referrer-Policy", value: "no-referrer" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
];

function contentSecurityPolicy(production: boolean): string {
  const scriptSource = production
    ? "script-src 'self' 'unsafe-inline'"
    : "script-src 'self' 'unsafe-inline' 'unsafe-eval'";
  const connectSource = production ? "connect-src 'self'" : "connect-src 'self' ws: wss:";
  return [
    "default-src 'self'",
    "base-uri 'self'",
    connectSource,
    "font-src 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "frame-src 'none'",
    "img-src 'self' data:",
    "manifest-src 'self'",
    "media-src 'none'",
    "object-src 'none'",
    scriptSource,
    "style-src 'self' 'unsafe-inline'",
    "worker-src 'self'",
    ...(production ? ["upgrade-insecure-requests"] : []),
  ].join("; ");
}

export function browserSecurityHeaders(production: boolean): readonly SecurityHeader[] {
  return [
    ...sharedHeaders,
    { key: "Content-Security-Policy", value: contentSecurityPolicy(production) },
    ...(production
      ? [
          {
            key: "Strict-Transport-Security",
            value: "max-age=31536000; includeSubDomains",
          },
        ]
      : []),
  ];
}
