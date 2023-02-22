from pydantic import BaseModel, EmailStr


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class AccessTokenData(BaseModel):
    username: EmailStr
