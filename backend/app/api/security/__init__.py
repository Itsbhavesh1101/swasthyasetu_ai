"""FastAPI security boundary helpers."""

from app.api.security.authorization import require_permission, require_self_subject

__all__ = ["require_permission", "require_self_subject"]
