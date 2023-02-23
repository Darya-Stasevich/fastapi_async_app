from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, ExpiredSignatureError

from sqlalchemy.ext.asyncio import AsyncSession

from storage_app.authentication.models.token import Token
from storage_app.authentication.controllers.token_controller import AccessTokenController, RefreshTokenController
from storage_app.authentication.controllers.password_controller import PasswordController
from storage_app.config import SETTINGS
from storage_app.db_config import get_db
from storage_app.users.controllers.db_user_controller import DBUserController
from storage_app.users.models.api_users import UserCreate
from storage_app.logger_config import logger

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


async def get_current_user(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """Get user from access token if found"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    access_token_cookie: str = request.cookies.get('access_token')
    if not access_token_cookie:
        raise HTTPException(status_code=401)
    try:
        username = await AccessTokenController.verify_access_token(access_token_cookie=access_token_cookie)
    except ExpiredSignatureError:
        refresh_token_cookie: str = request.cookies.get('refresh_token')
        if not request.cookies.get('refresh_token'):
            raise HTTPException(status_code=401)
        try:
            data: dict = await RefreshTokenController.verify_refresh_token(refresh_token_cookie=refresh_token_cookie)
            username = data.get("username")
            response.set_cookie(key="access_token", value=data.get("access_token"), httponly=True)
            response.set_cookie(key="refresh_token", value=data.get("refresh_token"), httponly=True)
        except JWTError:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await DBUserController.get_user_by_username(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user.id


@router.post("/login", response_model=Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    """User log-in route"""
    user_form = UserCreate(username=form_data.username, password=form_data.password)
    user = await authenticate_user(user_form, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = await AccessTokenController.create_access_token(data={"sub": user_form.username},
                                                                   expires_delta=access_token_expires)
    refresh_token = await RefreshTokenController.create_refresh_token(data={"sub": user_form.username},
                                                                      expires_delta=refresh_token_expires)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    logger.info("user logged-in")
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    logger.info("User logged-out")
    return {"detail": "User logged-out"}


@router.get("/dasha")
async def dasha(user: int = Depends(get_current_user)):
    return {'detail': 'dasha'}
