import threading
import api
import bot
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_api_thread():
    logger.info("Starting FastAPI server...")
    api.run_api()

def main():
    api_thread = threading.Thread(target=run_api_thread, daemon=True)
    api_thread.start()

    logger.info("Starting Telegram bot in main thread...")
    bot.run_bot()

if __name__ == "__main__":
    main()
