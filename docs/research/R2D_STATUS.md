# R2-D Status

**Status:** COMPLETE — research/pre-technical-spike.

Current direction:

- Keycloak preferred authenticated IdP candidate; pseudonymous sessions stay internal.
- SeaweedFS preferred self-hosted object-store candidate; storage remains provider-neutral.
- PostgreSQL outbox + Procrastinate candidate for initial durable background work.
- Valkey is optional/ephemeral; NATS is future-only distributed messaging.
- OpenBao preferred self-hosted secrets candidate; Infisical is the main alternative.
- OpenTelemetry + Prometheus, Grafana optional, dedicated log backend deferred.
- Trivy + Gitleaks are recommended CI security controls.

Production adoption remains technical-spike and security-review gated.
