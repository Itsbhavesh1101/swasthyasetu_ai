"""P3-A persistence baseline.

Revision ID: p3a_0001
Revises: None
"""

from collections.abc import Sequence

revision: str = "p3a_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Establish migration lineage without creating application tables."""
    pass


def downgrade() -> None:
    """Return to the pre-migration baseline."""
    pass
