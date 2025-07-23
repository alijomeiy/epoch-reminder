from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import subprocess
import os
from telegram import InputFile
from telegram.ext import ApplicationBuilder
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from datetime import datetime
from docxtpl import DocxTemplate
from docx2pdf import convert
from typing import Dict
import json

app = FastAPI()

class BroadcastRequest(BaseModel):
    user_ids: list[int]

class Payload(BaseModel):
    telegram_id: int
    start_time: str
    end_time: str
    username: str
    hezb_days: Dict[str, int]

@app.post("/notify-new-session/")
async def send_message_to_users(data: BroadcastRequest):
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    if not application:
        raise HTTPException(status_code=503, detail="Bot is not running")

    keyboard = [
        [InlineKeyboardButton("مشاهده دوره", callback_data="start_join_session")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    for user_id in data.user_ids:
        try:
            await application.bot.send_message(
                chat_id=user_id,
                text="دوره جدید حزب قرآن آغاز شد",
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Error sending message to {payload.telegram_id}: {e}")

    return {"status": "success", "message": "Messages sent"}

@app.post("/notify-end-register/")
async def send_message_to_users(data: BroadcastRequest):
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    if not application:
        raise HTTPException(status_code=503, detail="Bot is not running")

    for user_id in data.user_ids:
        try:
            await application.bot.send_message(
                chat_id=user_id,
                text="""ثبت‌نام تموم شد!
ممنون از استقبال بی‌نظیرتون از دوره حزب قرآن 🌸
اگر ثبت‌نام کردید، منتظر شروع دوره باشید!""",
            )
        except Exception as e:
            print(f"Error sending message to {user_id}: {e}")

    return {"status": "success", "message": "Messages sent"}

@app.post("/send-info/")
async def receive_data(payload: Payload):
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    if not application:
        raise HTTPException(status_code=503, detail="Bot is not running")

    text = f"""
        username: {payload.username},
        start_time: {payload.start_time},
        end_time: {payload.end_time},
        hezb_days: {json.dumps(payload.hezb_days, ensure_ascii=False)}
    """

    doc = DocxTemplate("template.docx")
    docx_filename = f"{payload.username}.docx"
    pdf_filename = f"{payload.username}.pdf"
    context = {
        'username': payload.username,
        'start_time': payload.start_time,
        'end_time': payload.end_time,
        'hezb_days': payload.hezb_days
    }
    doc.render(context)
    doc.save(docx_filename)
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", ".",
        docx_filename
    ], check=True)
    print("PDF report generated successfully!")

    try:
        with open(pdf_filename, "rb") as file:
            await application.bot.send_document(
                chat_id=payload.telegram_id,
                document=InputFile(file, filename=pdf_filename),
                caption="📄 Your report is ready!"
            )
    except Exception as e:
        print(f"Error sending message to {user_id}: {e}")

    return {"status": "success", "message": "Messages sent"}



def run_api():
    uvicorn.run(app, host="0.0.0.0", port=9000)
