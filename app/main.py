from fastapi import FastAPI
from app.routes import webhook
from datetime import datetime, timezone

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.state.start_time = datetime.now(timezone.utc)

app.include_router(webhook.router)