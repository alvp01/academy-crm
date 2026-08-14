"""Remove identification_number from academies table.

Revision ID: 003
Revises: 002
Create Date: 2026-08-13
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the unique constraint first
    op.drop_constraint("uq_academy_identification", "academies", type_="unique")
    # Drop the column
    op.drop_column("academies", "identification_number")


def downgrade() -> None:
    # Add the column back (nullable initially for existing rows)
    op.add_column("academies", sa.Column("identification_number", sa.String, nullable=True))
    # Backfill existing rows with a placeholder value
    op.execute(
        "UPDATE academies SET identification_number = 'LEGACY-' || id::text WHERE identification_number IS NULL"
    )
    # Make the column NOT NULL
    op.alter_column("academies", "identification_number", nullable=False)
    # Re-add the unique constraint
    op.create_unique_constraint("uq_academy_identification", "academies", ["identification_number"])
