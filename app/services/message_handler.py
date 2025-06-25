import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from datetime import datetime, timezone

from app.core.config import settings
from app.utils.logger import logger


async def handle_discord_message(request: Request, payload: dict) -> Dict[str, Any]:
    """FastAPI 웹훅용 메시지 핸들러"""
    content = payload.get("content", "")
    author = payload.get("author", {}).get("username", "unknown")
    logger.info(f"Received message from {author}: {content}")

    if content == "!안녕":
        if not hasattr(request.app.state, "start_time"):
            raise HTTPException(
                status_code=500, detail="Server start time not available."
            )

        start_time: datetime = request.app.state.start_time
        uptime_delta = datetime.now(timezone.utc) - start_time

        total_seconds = int(uptime_delta.total_seconds())
        days = total_seconds // (24 * 3600)
        total_seconds %= 24 * 3600
        hours = total_seconds // 3600
        total_seconds %= 3600
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        uptime_parts = []
        if days > 0:
            uptime_parts.append(f"{days}일")
        if hours > 0:
            uptime_parts.append(f"{hours}시간")
        if minutes > 0:
            uptime_parts.append(f"{minutes}분")
        uptime_parts.append(f"{seconds}초")

        uptime_str = " ".join(uptime_parts)

        response_message = f"안녕하세요 uptime: {uptime_str}"
        logger.info(f"Responding to !안녕 command with: {response_message}")
        return {"response": response_message}

    return await _forward_to_backend(payload)


async def handle_discord_message_for_bot(payload: dict):
    """디스코드 봇용 메시지 핸들러"""
    content = payload.get("content", "")
    author = payload.get("author", {}).get("username", "unknown")
    logger.info(f"Bot received message from {author}: {content}")
    
    # 봇에서는 !안녕을 여기서 처리하지 않음 (discord_bot.py에서 처리)
    # 다른 메시지만 백엔드로 전달
    return await _forward_to_backend(payload)


async def _forward_to_backend(payload: dict) -> Optional[Dict[str, Any]]:
    """백엔드로 메시지 전달하는 공통 함수"""
    if not settings.backend_url:
        logger.error("BACKEND_URL is not set. Cannot forward message.")
        raise HTTPException(
            status_code=500, detail="Backend service is not configured."
        )

    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Forwarding message to {settings.backend_url}")
            response = await client.post(
                settings.backend_url, json=payload, timeout=5.0
            )
            response.raise_for_status()  # 2xx가 아닌 상태 코드에 대해 예외 발생
            logger.info(
                f"Successfully forwarded message. Backend response: {response.status_code}"
            )
            return response.json()
        except httpx.RequestError as exc:
            logger.error(f"Error while requesting {exc.request.url!r}: {exc}")
            # 봇용에서는 HTTPException 대신 None 반환
            if isinstance(exc, Exception):
                return None
            raise HTTPException(
                status_code=503, detail="Backend service is unavailable."
            )
        except httpx.HTTPStatusError as exc:
            logger.error(
                f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
            )
            # 봇용에서는 HTTPException 대신 None 반환  
            if isinstance(exc, Exception):
                return None
            raise HTTPException(
                status_code=502, detail="Bad response from backend service."
            )
