import asyncio
import signal
import sys

from app.services.discord_bot import discord_bot
from app.utils.logger import logger


async def main():
    """메인 함수"""
    try:
        await discord_bot.start()
    except KeyboardInterrupt:
        logger.info("봇이 수동으로 중단되었습니다.")
    except Exception as e:
        logger.error(f"봇 실행 중 오류 발생: {e}")
    finally:
        await discord_bot.close()


def signal_handler(signum, frame):
    """시그널 핸들러"""
    logger.info("종료 신호를 받았습니다. 봇을 안전하게 종료합니다...")
    sys.exit(0)


if __name__ == "__main__":
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 봇 실행
    asyncio.run(main()) 