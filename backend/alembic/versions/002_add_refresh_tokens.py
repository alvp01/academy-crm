"""add refresh tokens

Revision ID: 002
Revises: 001
Create Date: 2026-07-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'refresh_tokens',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('academy_id', UUID(as_uuid=True), sa.ForeignKey('academies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String, nullable=False),
        sa.Column('jti', sa.String, nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('revoked_at', sa.DateTime, nullable=True),
        sa.Column('user_agent', sa.String, nullable=True),
        sa.Column('ip_address', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_refresh_tokens_academy_jti', 'refresh_tokens', ['academy_id', 'jti'], unique=True)
    op.create_index('ix_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])


def downgrade() -> None:
    op.drop_index('ix_refresh_tokens_expires_at', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_academy_jti', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
