from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=6, max_length=128)


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    refresh_token: str


class TokenRoleOut(BaseModel):
    access_token: str
    refresh_token: str
    name: str
    role: str
    is_active: bool
