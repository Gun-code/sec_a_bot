from fastapi import APIRouter, HTTPException
from app.models.discord import NotificationRequest, NotificationResponse
from app.services.discord_bot import discord_bot
from app.utils.logger import logger

router = APIRouter()

@router.post("/notify", response_model=NotificationResponse)
async def send_notification(request: NotificationRequest):
    """백엔드에서 디스코드 채널로 알림을 보내는 API"""
    try:
        success = await discord_bot.send_notification(
            channel_id=request.channel_id,
            message=request.message
        )
        
        if success:
            return NotificationResponse(
                success=True,
                message="알림이 성공적으로 전송되었습니다."
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail="채널을 찾을 수 없거나 알림 전송에 실패했습니다."
            )
            
    except Exception as e:
        logger.error(f"알림 API 처리 중 오류: {e}")
        raise HTTPException(
            status_code=500, 
            detail="서버 내부 오류가 발생했습니다."
        ) 