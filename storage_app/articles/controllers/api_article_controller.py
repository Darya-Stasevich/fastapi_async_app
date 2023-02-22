from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from storage_app.articles.controllers.db_article_controller import DBArticleController
from storage_app.articles.models.api_article_models import ArticleCreate, ArticlePatch
from storage_app.logger_config import logger
from storage_app.users.models.api_users import UserOut


class APIArticleController:
    @staticmethod
    async def create_article(article: ArticleCreate, db: AsyncSession, user_id: int):
        try:
            new_article = await DBArticleController.create_article(article=article, db=db, user_id=user_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Repeat request later")
        return new_article

    @staticmethod
    async def get_article(article_id: int, db: AsyncSession):
        article = await DBArticleController.get_article_by_id(article_id=article_id, db=db)
        if not article:
            logger.error(f"Attempt to get nonexistent article with id {article_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
        return article

    @staticmethod
    async def get_articles(db: AsyncSession):
        return await DBArticleController.get_articles(db=db)

    @staticmethod
    async def delete_article(article_id: int, db: AsyncSession, user_id: int):
        article_db = await DBArticleController.get_article_by_id(article_id=article_id, db=db)
        if not article_db:
            logger.error(f"Attempt to get nonexistent article with id {article_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Article {article_id} not found")
        if article_db.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You are not allowed to perform this action')
        await DBArticleController.delete_article(article_id=article_id, db=db)
        return {'deleted'}

    @staticmethod
    async def update_article(article: ArticlePatch, article_id: int, db: AsyncSession, user_id: int):
        article_db = await DBArticleController.get_article_by_id(article_id=article_id, db=db)
        if not article_db:
            logger.error(f"Attempt to update nonexistent article with id {article_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Article {article_id} not found")
        if article_db.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You are not allowed to perform this action')
        try:
            updated_article = await DBArticleController.update_article(article=article, article_id=article_id, db=db)
        except Exception:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Something's wrong. Repeat request later")
        return updated_article


