"""Safe request-correlation identifier generation and validation."""

import re
from typing import NewType
from uuid import uuid4

RequestId = NewType("RequestId", str)

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def new_request_id() -> RequestId:
    """Generate an opaque request identifier."""
    return RequestId(f"req_{uuid4().hex}")


def resolve_request_id(inbound_request_id: str | None) -> RequestId:
    """Accept a safe inbound identifier or replace it with an opaque value."""
    if inbound_request_id and _REQUEST_ID_PATTERN.fullmatch(inbound_request_id):
        return RequestId(inbound_request_id)
    return new_request_id()
