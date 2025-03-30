import os

class Settings:
    GITHUB_SECRET: str = os.getenv("GITHUB_SECRET", "your-github-secret")

settings = Settings()
