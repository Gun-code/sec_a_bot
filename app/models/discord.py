from pydantic import BaseModel
from typing import Optional, Dict, Any


class DiscordAuthor(BaseModel):
    username: str
    id: Optional[str] = None
    discriminator: Optional[str] = None


class DiscordMessage(BaseModel):
    content: str
    author: DiscordAuthor
    channel_id: Optional[str] = None
    guild_id: Optional[str] = None
    message_id: Optional[str] = None
    timestamp: Optional[str] = None
    # 추가적인 필드들을 위한 확장성
    extra_data: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    response: str


class NotificationRequest(BaseModel):
    channel_id: str
    message: str


class NotificationResponse(BaseModel):
    success: bool
    message: str 