from fastapi import APIRouter, Request, HTTPException
from app.services.message_handler import handle_discord_message
from app.utils.logger import logger
from app.models.discord import DiscordMessage, MessageResponse

router = APIRouter()

@router.post("/webhook", response_model=MessageResponse)
async def receive_message(request: Request, message: DiscordMessage):
    try:
        # Pydantic 모델을 dict로 변환
        payload = message.model_dump()
        logger.info(f"Received payload: {payload}")
        return await handle_discord_message(request, payload)
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=400, detail="Invalid request payload.")
