from fastapi import FastAPI
from contextlib import asynccontextmanager
from .api.v1.github_webhook import router as github_webhook_router
from .api.v1.users import router as users_router
from .api.v1.github_oauth import router as github_oauth_router
from .core.logging_config import setup_logging

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "SatQuest Core API"}

# Include your routers for different routes
app.include_router(github_webhook_router, prefix="/api/v1/webhook", tags=["GitHub Webhook"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(github_oauth_router, prefix="/api/v1/oauth", tags=["GitHub OAuth"])
