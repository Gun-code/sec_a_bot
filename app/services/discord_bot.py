import discord
from discord.ext import commands
from datetime import datetime, timezone
import asyncio

from app.core.config import settings
from app.utils.logger import logger
from app.services.message_handler import handle_discord_message_for_bot


class DiscordBot:
    def __init__(self):
        # 봇 인텐트 설정
        intents = discord.Intents.default()
        intents.message_content = True  # 메시지 내용 읽기 권한
        
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        self.start_time = datetime.now(timezone.utc)
        
        self.setup_events()
    
    def setup_events(self):
        @self.bot.event
        async def on_ready():
            logger.info(f'{self.bot.user}가 디스코드에 연결되었습니다!')
            logger.info(f'봇이 {len(self.bot.guilds)}개의 서버에 참여 중입니다.')
        
        @self.bot.event
        async def on_message(message):
            # 봇 자신의 메시지는 무시
            if message.author.bot:
                return
            
            # 메시지 페이로드 생성
            payload = {
                "content": message.content,
                "author": {
                    "username": message.author.name,
                    "id": str(message.author.id),
                    "discriminator": message.author.discriminator
                },
                "channel_id": str(message.channel.id),
                "guild_id": str(message.guild.id) if message.guild else None,
                "message_id": str(message.id),
                "timestamp": message.created_at.isoformat()
            }
            
            try:
                # !안녕 명령어는 봇에서 직접 처리
                if message.content.strip() == "!안녕":
                    response = await self.handle_greeting()
                    await message.channel.send(response)
                    return
                
                # 다른 메시지는 백엔드로 전달
                result = await handle_discord_message_for_bot(payload)
                
                if result and "response" in result:
                    await message.channel.send(result["response"])
                    
            except Exception as e:
                logger.error(f"메시지 처리 중 오류 발생: {e}")
                await message.channel.send("죄송합니다. 메시지 처리 중 오류가 발생했습니다.")
    
    async def handle_greeting(self):
        """!안녕 명령어 처리"""
        uptime_delta = datetime.now(timezone.utc) - self.start_time
        
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
        return f"안녕하세요! uptime: {uptime_str}"
    
    async def send_notification(self, channel_id: str, message: str):
        """백엔드에서 호출할 수 있는 알림 전송 메서드"""
        try:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                await channel.send(message)
                logger.info(f"알림을 채널 {channel_id}에 전송했습니다: {message}")
                return True
            else:
                logger.error(f"채널 {channel_id}를 찾을 수 없습니다.")
                return False
        except Exception as e:
            logger.error(f"알림 전송 중 오류 발생: {e}")
            return False
    
    async def start(self):
        """봇 시작"""
        if not settings.discord_token:
            raise ValueError("DISCORD_TOKEN이 설정되지 않았습니다.")
        
        logger.info("디스코드 봇을 시작합니다...")
        await self.bot.start(settings.discord_token)
    
    async def close(self):
        """봇 종료"""
        logger.info("디스코드 봇을 종료합니다...")
        await self.bot.close()


# 봇 인스턴스
discord_bot = DiscordBot() 