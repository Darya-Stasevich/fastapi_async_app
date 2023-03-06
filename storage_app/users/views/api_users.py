from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from storage_app.articles.models.api_article_models import ArticleOut
from storage_app.authentication.views.authentication_views import get_current_user
from storage_app.db_config import get_db
from storage_app.users.controllers.api_user_controller import APIUserController
from storage_app.users.models.api_users import UserOut, UserCreate, UserPatch

router = APIRouter(
    prefix='/users',
    tags=['users'],
)


@router.post("/", response_model=UserOut, status_code=201)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await APIUserController.create_user(user=user, db=db)


@router.get("/{user_id}", response_model=UserOut)
async def show_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await APIUserController.get_user(user_id=user_id, db=db)


@router.get("/{user_id}/articles", response_model=List[ArticleOut])
async def show_user_articles(user_id: int, db: AsyncSession = Depends(get_db)):
    return await APIUserController.get_user_articles(user_id=user_id, db=db)


@router.get("/", response_model=List[UserOut])
async def show_users(db: AsyncSession = Depends(get_db)):
    return await APIUserController.get_users(db=db)


@router.patch("/{user_id}", status_code=202, response_model=UserOut)
async def update_user(user: UserPatch, user_id: int, db: AsyncSession = Depends(get_db),
                      user_token: UserOut = Depends(get_current_user)):
    return await APIUserController.update_user(user=user, user_id=user_id, db=db)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await APIUserController.delete_user(user_id=user_id, db=db)
