from typing import Union
from datetime import datetime, timedelta

from jose import jwt

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
        encoded_jwt = jwt.encode(to_encode, SETTINGS.SECRET_KEY, algorithm=SETTINGS.ALGORITHM)
        logger.info("New token created")
        return encoded_jwt
