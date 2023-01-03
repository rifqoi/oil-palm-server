from typing import Optional
from datetime import timedelta, datetime

from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app.models.user import User
from app.core.config import settings
from app.core.security import verify_password


oauth2_schema = OAuth2PasswordBearer(f"{settings.API_V1_STR}/auth/login")


def authenticate(
    *,
    username: str,
    password: str,
    db: Session,
) -> Optional[User]:
    user: Optional[User] = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


# TODO
def _create_token(
    token_type: str,
    lifetime: timedelta,
    sub: str,
) -> str:
    payload = {}

    payload["type"] = token_type

    # JWT Expiration Time
    expire = datetime.utcnow() + lifetime
    payload["exp"] = expire

    # JWT "iat" (issued at) claim identifies the issued date of the token
    payload["iat"] = datetime.utcnow()

    # JWT "sub" (subject) identifies the principal of the jwt
    # e.g user_id of the user or email of the user
    payload["sub"] = sub
    return jwt.encode(
        claims=payload,
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(*, sub: str) -> str:
    return _create_token(
        token_type="access_token",
        lifetime=timedelta(days=settings.JWT_TOKEN_EXPIRE_DAYS),
        sub=sub,
    )
