from typing import Optional

from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    username: EmailStr
    password: constr(min_length=5)


class UserOut(BaseModel):
    id: int
    username: EmailStr

    class Config:
        orm_mode = True


class UserPatch(BaseModel):
    username: Optional[EmailStr]
    password: Optional[str]


