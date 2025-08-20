from app.core.security import create_access_token

async def issue_access_token(user_id: str) -> tuple[str, str, int]:
    token, jti, exp_ts = create_access_token(subject=user_id)
    return token, jti, exp_ts
