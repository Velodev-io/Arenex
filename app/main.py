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

# Chrome Private Network Access — allow requests from localhost → LAN IP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class PrivateNetworkAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        return response

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            if request.method == "OPTIONS" and "access-control-request-private-network" in request.headers:
                from starlette.responses import Response
                response = Response(status_code=204, headers={
                    "Access-Control-Allow-Private-Network": "true",
                    "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                })
                await response(scope, receive, send)
                return
        await super().__call__(scope, receive, send)

app.add_middleware(PrivateNetworkAccessMiddleware)

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
