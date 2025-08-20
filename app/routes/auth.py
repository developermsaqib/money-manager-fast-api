from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi.util import get_remote_address
from slowapi import Limiter
from app.schemas.user import UserCreate, UserLogin, UserPublic
from app.schemas.auth import TokenOut
from app.schemas.common import Message
from app.services.users import create_user, authenticate, blacklist_token
from app.services.tokens import issue_access_token
from app.utils.deps import get_current_user
from app.core.config import settings
from app.core.security import decode_token

router = APIRouter()
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

@router.post("/register", response_model=UserPublic)
@limiter.limit("5/minute")
async def register(payload: UserCreate):
    try:
        user_id = await create_user(payload.email, payload.password)
    except Exception:
        raise HTTPException(status_code=400, detail="Email already registered")
    return UserPublic(id=user_id, email=payload.email.lower())

@router.post("/login", response_model=TokenOut)
@limiter.limit("10/minute")
async def login(payload: UserLogin):
    user_id = await authenticate(payload.email, payload.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token, jti, exp_ts = await issue_access_token(user_id)
    return TokenOut(access_token=token)

@router.post("/logout", response_model=Message)
async def logout(request: Request, current: UserPublic = Depends(get_current_user)):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Missing bearer token")
    token = auth.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid token")
    jti = payload.get("jti")
    exp_ts = payload.get("exp")
    if not jti or not exp_ts:
        raise HTTPException(status_code=400, detail="Invalid token payload")
    await blacklist_token(jti, exp_ts)
    return Message(message="logged out")

@router.get("/me", response_model=UserPublic)
async def me(current: UserPublic = Depends(get_current_user)):
    return current
