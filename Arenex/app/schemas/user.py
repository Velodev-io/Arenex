from typing import Optional
from fastapi_users import schemas
from pydantic import ConfigDict

class UserRead(schemas.BaseUser[int]):
    model_config = ConfigDict(from_attributes=True)

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass
