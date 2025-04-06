from fastapi import APIRouter, Request
from app.services.github_services import handle_github_event

router = APIRouter()

@router.post("/")
async def github_webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")
    return handle_github_event(event, payload)
