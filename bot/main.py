import threading
import bot
import api
import asyncio

def run_bot_thread():
    bot.run_bot()

def run_api_thread():
    api.run_api()

if __name__ == "__main__":
    threading.Thread(target=run_bot_thread, daemon=True).start()
    threading.Thread(target=run_api_thread, daemon=True).start()

    asyncio.get_event_loop().run_forever()
