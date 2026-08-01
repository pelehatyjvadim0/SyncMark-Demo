"""Create synthetic demo shipment storage.

Revision ID: 0001_create_shipments
Revises:
Create Date: 2026-08-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_create_shipments"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shipments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False, unique=True, index=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("items", sa.Text(), nullable=False),
        sa.Column("issues", sa.Text(), nullable=False),
        sa.Column("labels", sa.Text(), nullable=False),
        sa.Column("submitted_keys", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("shipments")
