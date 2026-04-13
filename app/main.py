from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from app.models import User
from app.schemas.user import UserRead, UserCreate
from app.services.user_manager import get_user_manager
from app.core.auth import auth_backend

from fastapi.middleware.cors import CORSMiddleware
from app.database import settings

app = FastAPI(title="Arenex Platform")

# CORS configuration
allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
from app.api.matches import router as matches_router
from app.api.ws import router as ws_router
from app.api.social import router as social_router

app.include_router(
    agents_router,
    prefix="/agents",
    tags=["agents"]
)

app.include_router(
    matches_router,
    prefix="/matches",
    tags=["matches"]
)

app.include_router(
    ws_router,
    prefix="/ws/matches",
    tags=["websockets"]
)

app.include_router(
    social_router,
    prefix="/social",
    tags=["social"]
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "arenex-platform"}
