from uuid import UUID

from pydantic import BaseModel, Field


class ConnectRequest(BaseModel):
    token: str = Field(min_length=1)
    remember_me: bool = False


class ConnectResponse(BaseModel):
    user_id: UUID
    remember_me: bool
