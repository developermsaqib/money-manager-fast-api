from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.db.mongo import db
from app.core.security import decode_token
from app.schemas.user import UserPublic

security = HTTPBearer(auto_error=False)

async def get_db():
    return db()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    jti = payload.get("jti")
    user_id = payload.get("sub")
    if not jti or not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    d = db()
    # Check blacklist
    exists = await d.token_blacklist.find_one({"jti": jti})
    if exists:
        raise HTTPException(status_code=401, detail="Token revoked")

    user = await d.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return UserPublic(id=user["_id"], email=user["email"])
