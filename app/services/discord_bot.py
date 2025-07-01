import discord
from discord.ext import commands
from datetime import datetime, timezone
import requests
import asyncio
import re

from app.core.config import settings
from app.utils.logger import logger
from app.services.message_handler import handle_discord_message_for_bot

# 봇 구현 코드
# 메시지 처리 로직
# 알림 전송 로직
# 봇 시작 및 종료 로직
# 봇 인텐트 설정
# 봇 명령어 설정
# 봇 이벤트 설정
# 봇 오류 처리

class DiscordBot:
    def __init__(self):
        # 봇 인텐트 설정
        #인텐트 : 봇이 디스코드 서버에 연결할 때 필요한 권한을 설정하는 객체
        # 메시지 내용 읽기 권한 활성화
        intents = discord.Intents.default()
        intents.message_content = True  # 메시지 내용 읽기 권한
        
        # 봇 인스턴스 생성
        # 명령어 접두사 설정
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        self.start_time = datetime.now(timezone.utc)
        
        # 이벤트 설정
        self.setup_events()
    
    # 이벤트 처리 함수
    def setup_events(self):

        # 봇이 준비되었을 때 실행되는 이벤트
        @self.bot.event
        async def on_ready():
            logger.info(f'{self.bot.user}가 디스코드에 연결되었습니다!')
            logger.info(f'봇이 {len(self.bot.guilds)}개의 서버에 참여 중입니다.')
        
        # 메시지가 수신되었을 때 실행되는 이벤트
        @self.bot.event
        async def on_message(message):
            # 봇 자신의 메시지는 무시
            # 봇이 자신의 메시지를 처리하지 않도록 함
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

            # 명령어 목록(명령어: 설명)
            command_list = {
                "!도움말": "현재 봇의 명령어 목록을 확인합니다.",
                "!안녕": "현재 봇의 업타임을 확인합니다.",
                "!로그인": "현재 봇이 로그인합니다.",
                "!로그아웃": "현재 봇이 로그아웃합니다.",
                "!오늘 일정": "현재 봇이 오늘 일정을 확인합니다.",
                "!내일 일정": "현재 봇이 내일 일정을 확인합니다.",
                "!이번주 일정": "현재 봇이 이번주 일정을 확인합니다.",
                "!이번달 일정": "현재 봇이 이번달 일정을 확인합니다.",
            }
            try:
                # 봇이 명령어를 처리하도록 함
                if message.content.strip() in command_list:
                    if message.content.strip() == "!안녕":
                        response = await self.handle_greeting()
                        await message.channel.send(response)
                    elif message.content.strip() == "!도움말":
                        response = await self.handle_help(command_list)
                        await message.channel.send(response)
                    elif message.content.strip() == "!로그인":
                        response = await self.handle_login(message)
                        await message.channel.send(response)
                    elif message.content.strip() == "!로그아웃":
                        response = await self.handle_logout()
                        await message.channel.send(response)
                    elif message.content.strip() == "!오늘 일정":
                        response = await self.handle_today_schedule()
                        await message.channel.send(response)
                    elif message.content.strip() == "!내일 일정":
                        response = await self.handle_tomorrow_schedule()
                        await message.channel.send(response)
                    elif message.content.strip() == "!이번주 일정":
                        response = await self.handle_this_week_schedule()
                        await message.channel.send(response)
                    elif message.content.strip() == "!이번달 일정":
                        response = await self.handle_this_month_schedule()
                        await message.channel.send(response)
                    return
                
                # 다른 메시지는 백엔드로 전달
                result = await handle_discord_message_for_bot(payload)
                
                if result and "response" in result:
                    await message.channel.send(result["response"])
                    
            except Exception as e:
                logger.error(f"메시지 처리 중 오류 발생: {e}")
                await message.channel.send("죄송합니다. 메시지 처리 중 오류가 발생했습니다.")


    # !안녕 명령어 처리 함수
    async def handle_greeting(self):
        """봇의 업타임을 확인합니다."""
        # 봇 시작 시간 계산
        uptime_delta = datetime.now(timezone.utc) - self.start_time
        
        # 업타임 계산
        total_seconds = int(uptime_delta.total_seconds())
        days = total_seconds // (24 * 3600)
        total_seconds %= 24 * 3600
        hours = total_seconds // 3600
        total_seconds %= 3600
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        # 업타임 문자열 생성
        uptime_parts = []
        if days > 0:
            uptime_parts.append(f"{days}일")
        if hours > 0:
            uptime_parts.append(f"{hours}시간")
        if minutes > 0:
            uptime_parts.append(f"{minutes}분")
        uptime_parts.append(f"{seconds}초")
        
        uptime_str = " ".join(uptime_parts)
        return f"안녕하세요! 봇의 업타임은 {uptime_str}입니다."
    
    # !도움말 명령어 처리 함수
    async def handle_help(self, command_list: dict):
        """봇의 명령어 목록을 확인합니다."""
        # 명령어 목록 문자열 생성
        command_list_str = "\n".join([f"!{command}: {description}" for command, description in command_list.items()])
        return f"봇의 명령어 목록을 확인합니다.\n{command_list_str}"
    
    # !로그인 명령어 처리 함수
    # 백엔드 로그인 요청 방식 : POST
    # 백엔드 로그인 요청 파라미터 : {
    #     "user_id": user_id,
    # }
    # 백엔드 로그인 요청 헤더 : {
    #     "Content-Type": "application/json"
    # }
    # 백엔드 로그인 요청 바디 : {
    #     "user_id": user_id,
    #     "email": email
    # }
    # 백엔드 로그인 요청 반환 값 : {
    #     "message" : "로그인 성공" or "로그인 실패",
    #     "url" : 구글 로그인 페이지 주소
    # }
    async def handle_login(self, message):
        """봇이 로그인합니다."""
        try:            
            # 사용자 id 가져오기
            user_id = message.author.id

            # 1단계 : 이메일 요청
            await message.channel.send("구글 이메일을 입력해주세요.")

            def check(m):
                return m.author.id == user_id and m.channel.id == message.channel.id
            
            # 2단계 : 이메일 요청 대기
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30)
                email = msg.content.strip()
                if not email:
                    return "구글 이메일을 입력해주세요."
                if not re.match(r"[^@]+@gmail\.com", email):
                    return "올바른 구글 이메일 형식이 아닙니다."
                
                # 3단계 : 이메일 요청 처리
                post_url = f"{settings.backend_url}/api/v1/auth/login"
                post_data = {
                    "user_id": str(user_id),
                    "user_email": str(email)
                }
                post_headers = {
                    "Content-Type": "application/json"
                }
                post_response = requests.post(post_url, headers=post_headers, json=post_data)
                response = post_response.json()
                if response.get("message") == "유효한 토큰":
                    return "토큰이 유효한 계정입니다."
                elif response.get("message") == "유효하지 않은 토큰":
                    url = response.get("login_url")
                    return f"토큰이 유효하지 않습니다. 구글 로그인 페이지로 이동합니다. {url}"
                else:
                    return "로그인 처리 중 오류가 발생했습니다."
            except asyncio.TimeoutError:
                return "응답 시간이 초과되었습니다. 다시 '!로그인' 명령어를 입력해주세요."


            post_url = f"{settings.backend_url}/api/v1/auth/login"
            post_data = {
                "user_id": user_id
            }
            post_headers = {
                "Content-Type": "application/json"
            }
            post_response = requests.post(post_url, headers=post_headers, json=post_data)
            response = post_response.json()
            if response.get("message") == "로그인 성공":
                return "이미 로그인 되어있습니다."
            elif response.get("message") == "로그인 실패":
                return response.get("url")
            else:
                return "로그인 처리 중 오류가 발생했습니다."
        except Exception as e:
            logger.error(f"로그인 처리 중 오류 발생: {e}")
            return "로그인 처리 중 오류가 발생했습니다."

    
    # !로그아웃 명령어 처리 함수
    async def handle_logout(self):
        """봇이 로그아웃합니다."""
        return "봇이 로그아웃합니다."
    
    # !오늘 일정 명령어 처리 함수
    async def handle_today_schedule(self):
        """봇이 오늘 일정을 확인합니다."""
        return "봇이 오늘 일정을 확인합니다."
    
    # !내일 일정 명령어 처리 함수
    async def handle_tomorrow_schedule(self):
        """봇이 내일 일정을 확인합니다."""
        return "봇이 내일 일정을 확인합니다."
    
    # !이번주 일정 명령어 처리 함수
    async def handle_this_week_schedule(self):
        """봇이 이번주 일정을 확인합니다."""
        return "봇이 이번주 일정을 확인합니다."
    
    # !이번달 일정 명령어 처리 함수
    async def handle_this_month_schedule(self):
        """봇이 이번달 일정을 확인합니다."""
        return "봇이 이번달 일정을 확인합니다."
    
    # 알림 전송 함수
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