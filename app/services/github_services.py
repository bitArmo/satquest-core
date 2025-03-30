import logging
import json

def handle_github_event(event: str, payload: dict):
    logging.info(f"Received event: {event}")
    logging.info(f"Payload: {json.dumps(payload, indent=2)}")
    # Additional processing logic here
    return {"status": "Event processed successfully"}
