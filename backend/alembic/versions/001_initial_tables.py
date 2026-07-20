"""initial tables

Revision ID: 001
Revises: 
Create Date: 2026-07-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'academies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=False),
        sa.Column('identification_number', sa.String, nullable=False),
        sa.Column('password_hash', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.UniqueConstraint('email', name='uq_academy_email'),
        sa.UniqueConstraint('identification_number', name='uq_academy_identification'),
    )

    op.create_table(
        'headquarters',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('academy_id', UUID(as_uuid=True), sa.ForeignKey('academies.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.UniqueConstraint('academy_id', 'name', name='uq_hq_academy_name'),
    )

    op.create_table(
        'classrooms',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('headquarters_id', UUID(as_uuid=True), sa.ForeignKey('headquarters.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('classes_capacity', sa.Integer, nullable=False),
        sa.UniqueConstraint('headquarters_id', 'name', name='uq_classroom_hq_name'),
    )


def downgrade() -> None:
    op.drop_table('classrooms')
    op.drop_table('headquarters')
    op.drop_table('academies')
