from typing import Generator, Optional
from pydantic import BaseModel

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from jose import jwt, JWTError

from app.models import User
from app.core.config import settings
from app.core.auth import oauth2_schema
from app.db.session import SessionLocal


class TokenData(BaseModel):
    username: Optional[str] = None


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_schema),
) -> User:
    credential_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token=token,
            key=settings.JWT_SECRET,
            algorithms=settings.JWT_ALGORITHM,
            options={"verify_aud": False},
        )
        username = payload.get("sub")
        if username is None:
            raise credential_exceptions
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exceptions
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credential_exceptions
    return user
