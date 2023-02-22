from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from storage_app.articles.controllers.db_article_controller import DBArticleController
from storage_app.users.controllers.db_user_controller import DBUserController
from storage_app.logger_config import logger
from storage_app.users.models.api_users import UserCreate, UserPatch


class APIUserController:
    @staticmethod
    async def create_user(user: UserCreate, db: AsyncSession):
        if await DBUserController.get_user_by_username(username=user.username, db=db):
            logger.error(f"User with username {user.username} already exists")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username {user.username} already exists")
        try:
            new_user = await DBUserController.create_user(user=user, db=db)
        except Exception:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Repeat request later")
        return new_user

    @staticmethod
    async def get_user(user_id: int, db: AsyncSession):
        user = await DBUserController.get_user_by_id(user_id=user_id, db=db)
        if not user:
            logger.error(f"Attempt to get nonexistent user with id {user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
        return user

    @staticmethod
    async def get_user_articles(user_id: int, db: AsyncSession):
        user = await DBUserController.get_user_by_id(user_id=user_id, db=db)
        if not user:
            logger.error(f"Attempt to get nonexistent user with id {user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
        user_articles = await DBArticleController.get_user_articles(user_id=user_id, db=db)
        return user_articles

    @staticmethod
    async def get_users(db: AsyncSession):
        return await DBUserController.get_users(db=db)

    @staticmethod
    async def delete_user(user_id: int, db: AsyncSession):
        if not await DBUserController.get_user_by_id(user_id=user_id, db=db):
            logger.error(f"Attempt to get nonexistent user with id {user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
        await DBUserController.delete_user(user_id=user_id, db=db)
        return {'deleted'}

    @staticmethod
    async def update_user(user: UserPatch, user_id: int, db: AsyncSession):
        user_db = await DBUserController.get_user_by_id(user_id=user_id, db=db)
        if not user_db:
            logger.error(f"Attempt to update nonexistent user with id {user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
        if user.username:
            if await DBUserController.get_user_by_username(username=user.username, db=db):
                logger.error(f"User with username {user.username} already exists")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username {user.username} already exists")
        try:
            updated_user = await DBUserController.update_user(user=user, user_id=user_id, db=db)
        except Exception:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Repeat request later")
        return updated_user

