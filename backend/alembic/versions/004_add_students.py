"""add students table

Revision ID: 004
Revises: 003
Create Date: 2026-08-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'students',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('academy_id', UUID(as_uuid=True), sa.ForeignKey('academies.id'), nullable=False),
        sa.Column('first_name', sa.String, nullable=False),
        sa.Column('last_name', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=False),
        sa.Column('identification_number', sa.String, nullable=False),
        sa.Column('phone_number', sa.String, nullable=False),
        sa.Column('address', sa.String, nullable=False),
        sa.Column('date_of_birth', sa.DateTime, nullable=False),
        sa.Column('allergies', sa.Text, server_default='N/A'),
        sa.Column('referral_source', sa.String, nullable=False),
        sa.Column('occupation', sa.String, nullable=False),
        sa.Column('status', sa.String, server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('academy_id', 'email', name='uq_student_academy_email'),
        sa.UniqueConstraint('academy_id', 'identification_number', name='uq_student_academy_identification'),
    )
    op.create_index('ix_students_academy_id', 'students', ['academy_id'])
    op.create_index('ix_students_status', 'students', ['status'])


def downgrade() -> None:
    op.drop_index('ix_students_status')
    op.drop_index('ix_students_academy_id')
    op.drop_table('students')
