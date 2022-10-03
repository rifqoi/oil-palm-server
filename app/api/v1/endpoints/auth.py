from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from app import schemas, crud, models
from app.api import deps
from app.core.auth import authenticate, create_access_token

router = APIRouter()


@router.post("/signup", response_model=schemas.User, status_code=201)
def create_user_signup(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    # Check whether username already exists in db.
    user = (
        db.query(models.User).filter(models.User.username == user_in.username).first()
    )

    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user = crud.user.create(db=db, obj_in=user_in)
    return user


@router.post("/login", status_code=200)
def login(
    *,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    user = authenticate(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid username or password",
        )
    return {
        "access_token": create_access_token(sub=user.username),
        "token_type": "bearer",
    }


@router.get("/me", status_code=200, response_model=schemas.User)
def get_user(current_user: models.User = Depends(deps.get_current_user)):
    user = current_user
    return user
