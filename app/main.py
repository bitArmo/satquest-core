from fastapi import FastAPI
from .api.v1.github_webhook import router as github_webhook_router
from .api.v1.users import router as users_router
from .core.logging_config import setup_logging

# Setup logging
logger = setup_logging()

app = FastAPI()

# Include your routers for different routes
app.include_router(github_webhook_router, prefix="/api/v1/webhook", tags=["GitHub Webhook"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")
