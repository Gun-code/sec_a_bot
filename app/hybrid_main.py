import asyncio
import uvicorn
from fastapi import FastAPI
from threading import Thread

from app.routes import webhook, notification
from app.services.discord_bot import discord_bot
from app.utils.logger import logger


# FastAPI 앱 생성
app = FastAPI(title="Discord Bot with Notification API")

# 라우터 등록
app.include_router(webhook.router, tags=["webhook"])
app.include_router(notification.router, tags=["notification"])


@app.on_event("startup")
async def startup_event():
    """FastAPI 시작 시 실행"""
    logger.info("FastAPI 서버가 시작되었습니다.")


def run_fastapi():
    """FastAPI 서버를 별도 스레드에서 실행"""
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


async def run_discord_bot():
    """디스코드 봇 실행"""
    try:
        await discord_bot.start()
    except Exception as e:
        logger.error(f"디스코드 봇 실행 중 오류: {e}")


async def main():
    """메인 함수 - 봇과 API 서버를 동시 실행"""
    # FastAPI 서버를 별도 스레드에서 시작
    fastapi_thread = Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    logger.info("FastAPI 서버와 디스코드 봇을 동시에 시작합니다...")
    
    # 디스코드 봇 실행 (메인 스레드)
    await run_discord_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("서비스가 수동으로 중단되었습니다.")
    except Exception as e:
        logger.error(f"서비스 실행 중 오류: {e}") 