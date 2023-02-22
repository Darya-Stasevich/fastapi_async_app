from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

from sqlalchemy.ext.asyncio import AsyncSession

from storage_app.authentication.models.token import AccessToken, AccessTokenData
from storage_app.authentication.controllers.token_controller import AccessTokenController
from storage_app.authentication.controllers.password_controller import PasswordController
from storage_app.config import SETTINGS
from storage_app.db_config import get_db
from storage_app.users.controllers.db_user_controller import DBUserController
from storage_app.users.models.api_users import UserCreate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(
    prefix='/auth',
    tags=['authentication']
)


async def authenticate_user(user_form: UserCreate, db: AsyncSession):
    user = await DBUserController.get_user_by_username(username=user_form.username, db=db)
    if not user:
        return False
    if not PasswordController.verify_password(user_form.password, user.password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """Get user from access token if found"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SETTINGS.SECRET_KEY, algorithms=[SETTINGS.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = AccessTokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await DBUserController.get_user_by_username(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user.id


@router.post("/login", response_model=AccessToken)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """User log-in function"""
    user_form = UserCreate(username=form_data.username, password=form_data.password)
    user = await authenticate_user(user_form, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await AccessTokenController.create_access_token(data={"sub": user_form.username},
                                                                   expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
