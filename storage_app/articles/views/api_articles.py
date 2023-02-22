from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from storage_app.articles.controllers.api_article_controller import APIArticleController
from storage_app.articles.models.api_article_models import ArticleCreate, ArticleOut, ArticlePatch
from storage_app.authentication.views.authentication_views import get_current_user
from storage_app.db_config import get_db
from storage_app.users.models.api_users import UserOut

router = APIRouter(
    prefix='/articles',
    tags=['articles'],
)


@router.post("/", response_model=ArticleOut, status_code=201)
async def create_new_article(article: ArticleCreate, db: AsyncSession = Depends(get_db),
                             user_id: int = Depends(get_current_user)):
    return await APIArticleController.create_article(article=article, db=db, user_id=user_id)


@router.get("/{article_id}", response_model=ArticleOut)
async def show_user(article_id: int, db: AsyncSession = Depends(get_db),
                    user_id: int = Depends(get_current_user)):
    return await APIArticleController.get_article(article_id=article_id, db=db)


@router.get("/", response_model=List[ArticleOut])
async def show_articles(db: AsyncSession = Depends(get_db), user_id: int= Depends(get_current_user)):
    return await APIArticleController.get_articles(db=db)


@router.patch("/{article_id}", response_model=ArticleOut)
async def update_article(article: ArticlePatch, article_id: int, db: AsyncSession = Depends(get_db),
                         user_id: int = Depends(get_current_user)):
    return await APIArticleController.update_article(article=article, article_id=article_id, db=db,
                                                     user_id=user_id)


@router.delete("/{article_id}", status_code=204)
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db),
                         user_id: int = Depends(get_current_user)):
    return await APIArticleController.delete_article(article_id=article_id, db=db, user_id=user_id)
