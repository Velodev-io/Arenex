from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from app.models import User
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.services.user_manager import get_user_manager
from app.core.auth import auth_backend

app = FastAPI(title="Arenex Platform")

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Optional: Users router for self-management
# app.include_router(
#     fastapi_users.get_users_router(UserRead, UserUpdate),
#     prefix="/users",
#     tags=["users"],
# )

from app.api.agents import router as agents_router

app.include_router(
    agents_router,
    prefix="/agents",
    tags=["agents"]
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "arenex-platform"}
