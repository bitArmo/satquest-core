from fastapi import FastAPI
from .api.github_webhook import router as github_webhook_router
from .api.users import router as users_router
from .core.logging_config import setup_logging

# Setup logging
logger = setup_logging()

app = FastAPI()

# Include your routers for different routes
app.include_router(github_webhook_router, prefix="/webhook", tags=["GitHub Webhook"])
app.include_router(users_router, prefix="/users", tags=["Users"])

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")
