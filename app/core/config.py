import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "FastAPI Discord Bot")
    api_key: str = os.getenv("API_KEY")
    port: int = int(os.getenv("PORT", 8000))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    discord_token: str = os.getenv("DISCORD_TOKEN")
    backend_url: str = os.getenv("BACKEND_URL")

settings = Settings()
