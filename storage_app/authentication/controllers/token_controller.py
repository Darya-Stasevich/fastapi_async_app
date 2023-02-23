from typing import Union
from datetime import datetime, timedelta

from jose import jwt, JWTError, ExpiredSignatureError

from storage_app.config import SETTINGS
from storage_app.logger_config import logger


class AccessTokenController:
    @staticmethod
    async def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        new_access_token = jwt.encode(to_encode, SETTINGS.SECRET_KEY, algorithm=SETTINGS.ALGORITHM)
        logger.info("new access token created")
        return new_access_token

    @staticmethod
    async def verify_access_token(access_token_cookie: str):
        try:
            payload = jwt.decode(access_token_cookie, SETTINGS.SECRET_KEY, algorithms=[SETTINGS.ALGORITHM])
            username: str = payload.get("sub")
        except ExpiredSignatureError:
            logger.warning("access token time expired")
            raise ExpiredSignatureError
        logger.info("access token successfully verified")
        return username


class RefreshTokenController:
    @staticmethod
    async def create_refresh_token(data: dict, expires_delta: Union[timedelta, None] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        new_refresh_token = jwt.encode(to_encode, SETTINGS.SECRET_KEY, algorithm=SETTINGS.ALGORITHM)
        logger.info("new refresh token created")
        return new_refresh_token

    @staticmethod
    async def verify_refresh_token(refresh_token_cookie: str):
        try:
            payload = jwt.decode(refresh_token_cookie, SETTINGS.SECRET_KEY,
                                 algorithms=[SETTINGS.ALGORITHM])
            logger.info("refresh token successfully verified")
            access_token_expires = timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expires = timedelta(minutes=SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES)
            access_token = await AccessTokenController.create_access_token(data={"sub": payload.get('sub')},
                                                                           expires_delta=access_token_expires)
            refresh_token = await RefreshTokenController.create_refresh_token(data={"sub": payload.get('sub')},
                                                                              expires_delta=refresh_token_expires)
        except JWTError:
            logger.warning("refresh token time expired")
            raise JWTError
        return {"access_token": access_token, "refresh_token": refresh_token, "username": payload.get('sub')}
