from typing import Sequence, Union

from alembic import op

revision: str = "0019"
down_revision: Union[str, None] = "0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE payment_gateways SET currency = 'RUB' WHERE type = 'HELEKET'")


def downgrade() -> None:
    op.execute("UPDATE payment_gateways SET currency = 'USD' WHERE type = 'HELEKET'")
