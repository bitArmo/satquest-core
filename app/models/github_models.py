from pydantic import BaseModel

class GitHubEvent(BaseModel):
    action: str
    repository: dict
    sender: dict
