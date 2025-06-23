import logging
import sys

# 로거 설정
logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# 핸들러 설정 (콘솔 출력)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
