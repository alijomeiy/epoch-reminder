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
    message: str

@app.post("/send-message/")
async def send_message_to_users(data: BroadcastRequest):
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    if not application:
        raise HTTPException(status_code=503, detail="Bot is not running")

    keyboard = [
        [InlineKeyboardButton("پیوستن به جلسه", callback_data="join_session")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    for user_id in data.user_ids:
        try:
            await application.bot.send_message(
                chat_id=user_id,
                text=data.message,
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Error sending message to {user_id}: {e}")

    return {"status": "success", "message": "Messages sent"}

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=9000)
