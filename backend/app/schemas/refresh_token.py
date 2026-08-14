import uuid
from datetime import datetime

from pydantic import BaseModel


class RefreshTokenCreate(BaseModel):
    academy_id: uuid.UUID
    token_hash: str
    jti: str
    expires_at: datetime
    user_agent: str | None = None
    ip_address: str | None = None


class RefreshTokenRead(BaseModel):
    id: uuid.UUID
    academy_id: uuid.UUID
    token_hash: str
    jti: str
    expires_at: datetime
    revoked_at: datetime | None = None
    user_agent: str | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
