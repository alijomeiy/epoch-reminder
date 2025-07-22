from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
from telegram.ext import ApplicationBuilder
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

app = FastAPI()

class BroadcastRequest(BaseModel):
    user_ids: list[int]

@app.post("/notify-new-session/")
async def send_message_to_users(data: BroadcastRequest):
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    if not application:
        raise HTTPException(status_code=503, detail="Bot is not running")

    keyboard = [
        [InlineKeyboardButton("مشاهده", callback_data="start_join_session")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    for user_id in data.user_ids:
        try:
            await application.bot.send_message(
                chat_id=user_id,
                text="دوره جدید اومده",
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Error sending message to {user_id}: {e}")

    return {"status": "success", "message": "Messages sent"}

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=9000)
