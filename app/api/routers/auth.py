import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    new_refresh_jti,
    hash_jti,
    refresh_expires_at,
)
from app.db.session import get_session
from app.models.refresh_token import RefreshToken
from app.repos.refresh_token_repo import RefreshTokenRepo
from app.repos.user_repo import UserRepo
from app.schemas.auth import LoginIn, RefreshIn, LogoutIn, TokenRoleOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _decode(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])


@router.post("/login", response_model=TokenRoleOut)
async def login(data: LoginIn, session: AsyncSession = Depends(get_session)):
    user = await UserRepo(session).get_by_name(data.name)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    access = create_access_token(sub=str(user.id), role=user.role.value)

    jti = new_refresh_jti()
    refresh = create_refresh_token(sub=str(user.id), jti=jti)

    await RefreshTokenRepo(session).create(
        RefreshToken(
            user_id=user.id,
            jti_hash=hash_jti(jti),
            expires_at=refresh_expires_at(),
            revoked_at=None,
        )
    )
    await session.commit()

    return TokenRoleOut(access_token=access, refresh_token=refresh, name=user.name, role=user.role, is_active=user.is_active)


@router.post("/refresh", response_model=TokenRoleOut)
async def refresh_tokens(data: RefreshIn, session: AsyncSession = Depends(get_session)):
    try:
        payload = _decode(data.refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    sub = payload.get("sub")
    jti = payload.get("jti")
    if not sub or not jti:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        user_id = uuid.UUID(sub)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    repo = RefreshTokenRepo(session)
    rt = await repo.get_by_jti_hash(hash_jti(jti))
    if not rt:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if rt.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Refresh token revoked")
    if rt.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = await UserRepo(session).get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    # rotation
    repo.revoke(rt)

    new_jti = new_refresh_jti()
    new_refresh = create_refresh_token(sub=str(user.id), jti=new_jti)
    await repo.create(
        RefreshToken(
            user_id=user.id,
            jti_hash=hash_jti(new_jti),
            expires_at=refresh_expires_at(),
            revoked_at=None,
        )
    )

    access = create_access_token(sub=str(user.id), role=user.role.value)

    await session.commit()
    return TokenRoleOut(access_token=access, refresh_token=new_refresh, name=user.name, role=user.role, is_active=user.is_active)


@router.post("/logout")
async def logout(data: LogoutIn, session: AsyncSession = Depends(get_session)):
    try:
        payload = _decode(data.refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    repo = RefreshTokenRepo(session)
    rt = await repo.get_by_jti_hash(hash_jti(jti))
    if not rt:
        return {"ok": True}  # не раскрываем, существует ли токен
    if rt.revoked_at is None:
        repo.revoke(rt)
        await session.commit()

    return {"ok": True}
