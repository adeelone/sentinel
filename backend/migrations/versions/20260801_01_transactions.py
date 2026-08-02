"""Create the transaction review store."""

from alembic import op
import sqlalchemy as sa

revision = "20260801_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("label", sa.String(length=24), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.Float(), nullable=False),
        sa.Column("transaction", sa.JSON(), nullable=False),
        sa.Column("contributions", sa.JSON()),
        sa.Column("note", sa.String(length=2000)),
    )
    op.create_index("ix_transactions_score", "transactions", ["score"])
    op.create_index("ix_transactions_label", "transactions", ["label"])
    op.create_index("ix_transactions_status", "transactions", ["status"])
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"])


def downgrade() -> None:
    op.drop_table("transactions")
