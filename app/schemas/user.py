from typing import Optional

from pydantic import BaseModel, Field, validator
from fastapi import HTTPException


class UserBase(BaseModel):
    username: Optional[str]
    name: Optional[str]


class UserCreate(UserBase):
    username: str
    name: str
    password: str = Field(min_length=8)

    @validator("password")
    def validate_password(cls, value):
        special_characters = list("!@#$%^&*()_+{}|:\"\<\>?[]\\;',./`~")
        rules = [
            lambda s: any(x.isupper() for x in s),  # must have at least one uppercase
            lambda s: any(x.islower() for x in s),  # must have at least one lowercase
            lambda s: any(x.isdigit() for x in s),  # must have at least one digit
            lambda s: any(x in special_characters for x in s),
        ]
        if not all(rule(value) for rule in rules):
            raise HTTPException(
                status_code=429,
                detail="Password must contains at least 1 upper case, numeric, and special characters.",
            )
        return value


class UserUpdate(UserBase):
    ...


class UserInDBBase(UserBase):
    id: Optional[int]

    class Config:
        orm_mode = True


class UserInDB(UserInDBBase):
    hashed_password: str


class User(UserInDBBase):
    ...
