from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import settings
from app.api.auth import router as auth_router
from app.api.agents import router as agents_router
from app.api.matches import router as matches_router
from app.api.ws import router as ws_router
from app.api.social import router as social_router

app = FastAPI(title="Arenex Platform", redirect_slashes=False)

# CORS configuration
allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Router
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)

# Feature Routers
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
