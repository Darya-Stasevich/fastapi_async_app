from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select, delete, update

from storage_app.articles.models.api_article_models import ArticleCreate, ArticlePatch
from storage_app.articles.models.db_article_models import Article

from storage_app.logger_config import logger
from storage_app.users.models.api_users import UserOut


class DBArticleController:
    @staticmethod
    async def create_article(article: ArticleCreate, db: AsyncSession, user_id: int):
        """Creation of article instance in DB"""
        try:
            logger.info(f"Creation of a new article started")
            new_article = Article(**article.dict(), user_id=user_id)
            db.add(new_article)
            await db.commit()
            await db.refresh(new_article)
            logger.info(f"Article {new_article.id} created")
            return new_article
        except exc.SQLAlchemyError as e:
            logger.error(f"User not saved. Error: {e._message()}")
            raise Exception

    @staticmethod
    async def get_article_by_id(article_id: int, db: AsyncSession):
        """Show article by id"""
        query = select(Article).where(Article.id == article_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_articles(user_id: int, db: AsyncSession):
        """Show user's articles"""
        query = select(Article).where(Article.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_articles(db: AsyncSession):
        """Show all articles"""
        result = await db.execute(select(Article))
        return result.scalars().all()

    @staticmethod
    async def delete_article(article_id: int, db: AsyncSession):
        """Delete article by id"""
        query = delete(Article).where(Article.id == article_id)
        await db.execute(query)
        await db.commit()
        logger.info(f"Article with {article_id} deleted")
        return {'Article deleted'}

    @staticmethod
    async def update_article(article: ArticlePatch, article_id: int, db: AsyncSession):
        """Partial update of article instance in DB"""
        try:
            update_data = article.dict(exclude_unset=True)
            updated_article = update(Article).where(Article.id == article_id).values(**update_data)
            await db.execute(updated_article)
            await db.commit()
            logger.info(f"Article {article_id} updated")
            result = await db.execute(select(Article).where(Article.id == article_id))  # !!!!!!!!!!!!!!!!
            return result.scalar_one_or_none()
        except exc.SQLAlchemyError as e:
            logger.error(f"Article not updated. Error: {e._message()}")
            raise Exception

