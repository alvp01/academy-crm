import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        academy_id: uuid.UUID,
        token_hash: str,
        jti: str,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            academy_id=academy_id,
            token_hash=token_hash,
            jti=jti,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)
        return refresh_token

    async def get_by_jti(self, jti: str, academy_id: uuid.UUID) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.jti == jti,
                RefreshToken.academy_id == academy_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_jti_for_update(self, jti: str, academy_id: uuid.UUID) -> RefreshToken | None:
        """Get refresh token with SELECT FOR UPDATE to prevent race conditions during rotation."""
        result = await self.db.execute(
            select(RefreshToken)
            .where(
                RefreshToken.jti == jti,
                RefreshToken.academy_id == academy_id,
            )
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def revoke(self, jti: str, academy_id: uuid.UUID) -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.jti == jti,
                RefreshToken.academy_id == academy_id,
            )
            .values(revoked_at=now)
        )
        await self.db.commit()

    async def revoke_all_for_academy(self, academy_id: uuid.UUID) -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.academy_id == academy_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        await self.db.commit()

    async def cleanup_expired(self) -> int:
        """Bulk delete expired and old revoked tokens."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        result = await self.db.execute(
            delete(RefreshToken).where(
                (RefreshToken.expires_at < now)
                | ((RefreshToken.revoked_at.is_not(None)) & (RefreshToken.revoked_at < now))
            )
        )
        await self.db.commit()
        return result.rowcount
