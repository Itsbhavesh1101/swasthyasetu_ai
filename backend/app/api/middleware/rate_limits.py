"""Layered application rate limits for the FastAPI boundary."""

from __future__ import annotations

import hashlib
import hmac
import math
import secrets

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.api.errors.models import build_error_response
from app.api.security.bearer import parse_bearer
from app.config import RateLimitSettings
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.rate_limits import RateLimiter, RateLimitRule, RateLimitSubject

_MUTATION_METHODS = frozenset({"DELETE", "PATCH", "POST", "PUT"})


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply privacy-bounded global, peer, and credential limits."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        limiter: RateLimiter,
        settings: RateLimitSettings,
        api_v1_prefix: str,
        fingerprint_key: bytes | None = None,
    ) -> None:
        super().__init__(app)
        self._limiter = limiter
        self._api_v1_prefix = api_v1_prefix
        self._fingerprint_key = (
            fingerprint_key if fingerprint_key is not None else secrets.token_bytes(32)
        )
        if len(self._fingerprint_key) < 32:
            raise ValueError("rate-limit fingerprint key must contain at least 32 bytes")
        window = float(settings.window_seconds)
        self._rules = {
            "process": RateLimitRule("process", settings.process_requests, window),
            "peer": RateLimitRule("peer", settings.peer_requests, window),
            "credential": RateLimitRule("credential", settings.credential_requests, window),
            "mutation_peer": RateLimitRule(
                "mutation_peer", settings.mutation_peer_requests, window
            ),
            "mutation_credential": RateLimitRule(
                "mutation_credential", settings.mutation_credential_requests, window
            ),
            "session_creation_peer": RateLimitRule(
                "session_creation_peer", settings.session_creation_peer_requests, window
            ),
        }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self._is_api_path(request.url.path):
            return await call_next(request)

        decision = await self._limiter.check(self._subjects(request))
        if decision.allowed:
            return await call_next(request)

        retry_after = math.ceil(decision.retry_after_seconds or 1.0)
        response = build_error_response(
            status_code=429,
            code=ErrorCode.RATE_LIMITED,
            message="Too many requests.",
            request_id=str(getattr(request.state, "request_id", "unavailable")),
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["Retry-After"] = str(max(retry_after, 1))
        return response

    def _is_api_path(self, path: str) -> bool:
        return path == self._api_v1_prefix or path.startswith(f"{self._api_v1_prefix}/")

    def _subjects(self, request: Request) -> tuple[RateLimitSubject, ...]:
        peer_key = request.client.host if request.client is not None else "unknown"
        credential_key = self._credential_fingerprint(request.headers.get("authorization"))
        subjects = [
            RateLimitSubject(rule=self._rules["process"], key="all"),
            RateLimitSubject(rule=self._rules["peer"], key=peer_key),
        ]
        if credential_key is not None:
            subjects.append(RateLimitSubject(rule=self._rules["credential"], key=credential_key))
        if request.method in _MUTATION_METHODS:
            subjects.append(RateLimitSubject(rule=self._rules["mutation_peer"], key=peer_key))
            if credential_key is not None:
                subjects.append(
                    RateLimitSubject(rule=self._rules["mutation_credential"], key=credential_key)
                )
        if request.method == "POST" and request.url.path == f"{self._api_v1_prefix}/sessions":
            subjects.append(
                RateLimitSubject(rule=self._rules["session_creation_peer"], key=peer_key)
            )
        return tuple(subjects)

    def _credential_fingerprint(self, authorization: str | None) -> str | None:
        try:
            credential = parse_bearer(authorization)
        except ApplicationError:
            return None
        return hmac.new(
            self._fingerprint_key,
            credential.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
