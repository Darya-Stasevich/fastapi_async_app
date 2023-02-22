from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from storage_app.authentication.controllers.password_controller import PasswordController
from storage_app.users.models.api_users import UserCreate, UserPatch
from storage_app.users.models.db_users import User
from sqlalchemy import exc, select, delete, update

from storage_app.logger_config import logger


class DBUserController:
    @staticmethod
    async def create_user(user: UserCreate, db: AsyncSession):
        """Creation of user instance in DB"""
        try:
            hashed_password = PasswordController.generate_hashed_password(user.password)
            new_user = User(username=user.username, password=hashed_password)
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            logger.info(f"User {new_user.username} registered")
            return new_user
        except exc.SQLAlchemyError as e:
            logger.error(f"User not saved. Error: {e._message()}")
            raise Exception

    @staticmethod
    async def get_user_by_username(username: EmailStr, db: AsyncSession):
        """Show user by username"""
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(user_id: int, db: AsyncSession):
        """Show user by id"""
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_users(db: AsyncSession):
        """Show all users"""
        result = await db.execute(select(User))
        return result.scalars().all()

    @staticmethod
    async def delete_user(user_id: int, db: AsyncSession):
        """Delete user by id"""
        query = delete(User).where(User.id == user_id)
        await db.execute(query)
        await db.commit()
        logger.info(f"User with {user_id} deleted")
        return {'deleted'}

    @staticmethod
    async def update_user(user: UserPatch, user_id: int, db: AsyncSession):
        """Partial update of user instance in DB"""
        try:
            update_data = user.dict(exclude_unset=True)
            if update_data.get('password'):
                update_data['password'] = PasswordController.generate_hashed_password(user.password)
            updated_user = update(User).where(User.id == user_id).values(**update_data)
            await db.execute(updated_user)
            await db.commit()
            logger.info(f"User {user_id} updated")
            result = await db.execute(select(User).where(User.id == user_id))  # !!!!!!!!!!!!!!!!
            return result.scalar_one_or_none()
        except exc.SQLAlchemyError as e:
            logger.error(f"User not updated. Error: {e._message()}")
            raise Exception
