import pytest
from datetime import timedelta
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException

from app.core.security import create_access_token, get_current_user


@pytest.mark.asyncio
async def test_get_current_user_success():
    token = create_access_token({"sub": "7", "email": "x@y.z", "role": "admin", "is_active": True}, expires_delta=timedelta(minutes=1))
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = await get_current_user(creds)
    assert user["id"] == 7
    assert user["email"] == "x@y.z"
    assert user["role"] == "admin"
    assert user["is_active"] is True


@pytest.mark.asyncio
async def test_get_current_user_missing_sub_raises_401():
    token = create_access_token({"email": "no-sub@example.com", "role": "client"}, expires_delta=timedelta(minutes=1))
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as exc:
        await get_current_user(creds)
    assert exc.value.status_code == 401
