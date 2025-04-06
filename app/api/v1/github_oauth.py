from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import RedirectResponse
import os, requests
router = APIRouter()

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/api/v1/oauth/callback")

# Temporary storage (use session/db in real app)
pending_verifications = {}  # {"session_id": "claimed_username"}

@router.get("/start-verification/{username}")
async def start_verification(username: str):
    pending_verifications["demo"] = username
    return RedirectResponse(f"/api/v1/oauth/login", status_code=302)

@router.get("/login")
async def github_login():
    # Redirect to GitHub OAuth page
    print(f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope=read:user")
    return RedirectResponse(
        url=f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope=read:user"
    )

@router.get("/callback")
async def github_callback(code: str):
    # Exchange code for access token
    # TODO: Implement token exchange
    return {"status": "success", "code": code}