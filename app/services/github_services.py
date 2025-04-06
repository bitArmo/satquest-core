import logging
import json
from typing import Dict, Any
from fastapi import HTTPException, status
from app.models.github_models import GitHubEvent

def handle_github_event(event: str, payload: dict):
    logging.info(f"Received event: {event}")
    github_event = GitHubEvent(**payload)
    logging.info(f"Payload: {github_event}")
    # Additional processing logic here
    return {"status": "Event processed successfully"}
