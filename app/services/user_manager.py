import typing
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.database import get_db, settings

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request: typing.Optional[Request] = None):
        print(f"User {user.id} has registered.")

async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
