# import logging
# import requests
# from telegram import Update
# from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# # اطلاعات اولیه
# # API_TOKEN = ""  # ← توکن احراز هویت

# # فعال‌سازی لاگ‌ها
# logging.basicConfig(level=logging.INFO)

# # هندلر دستور /start
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     telegram_user_id = update.effective_user.id  # آی‌دی کاربر تلگرام
#     first_name = update.effective_user.first_name

#     # # ساختن داده‌ای که به سرور فرستاده می‌شود
#     # payload = {
#     #     "messenger_id": telegram_user_id
#     # }

#     # try:
#     #     response = requests.post(
#     #         f"{API_BASE_URL}/messenger-user/",
#     #         json=payload,
#     #     )

#     #     if response.status_code == 201:
#     #         await update.message.reply_text(f"سلام {first_name}! ثبت‌نام با موفقیت انجام شد.")
#     #     elif response.status_code == 200:
#     #         await update.message.reply_text(f"{first_name}، شما قبلاً ثبت شده‌اید.")
#     #     else:
#     #         await update.message.reply_text(f"خطا در ثبت‌نام: {response.status_code} - {response.text}")
#     # except Exception as e:
#     #     logging.error("خطا در ارتباط با API: %s", e)
#     #     await update.message.reply_text("مشکلی در برقراری ارتباط با سرور پیش آمد.")
#     print(f"DONE! userid{telegram_user_id}")
#     pass

# # راه‌اندازی ربات
# async def main():
#     app = ApplicationBuilder().token("").build()

#     app.add_handler(CommandHandler("start", start))

#     await app.run_polling()

# # اجرای برنامه
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())


#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import requests

import os
from dotenv import load_dotenv

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

API_BASE_URL = "http://192.168.21.70:8000/api"


load_dotenv()

TOKEN = os.getenv("TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    telegram_user_id = update.effective_user.id  # آی‌دی کاربر تلگرام
    first_name = update.effective_user.first_name

    # # ساختن داده‌ای که به سرور فرستاده می‌شود
    payload = {
        "messenger_id": telegram_user_id
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/messenger-user/",
            json=payload,
        )

        if response.status_code == 201:
            await update.message.reply_text(f"سلام {first_name}! ثبت‌نام با موفقیت انجام شد.")
        elif response.status_code == 200:
            await update.message.reply_text(f"{first_name}، شما قبلاً ثبت شده‌اید.")
        else:
            await update.message.reply_text(f"خطا در ثبت‌نام: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error("خطا در ارتباط با API: %s", e)
        await update.message.reply_text("مشکلی در برقراری ارتباط با سرور پیش آمد.")
    print(f"DONE - userid: {telegram_user_id} - first name: {first_name}")
    reply_keyboard = [["Boy", "Girl", "Other"]]

    await update.message.reply_text(
        "Hi! My name is Professor Bot. I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "Are you a boy or a girl?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?"
        ),
    )

    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "I see! Please send me a photo of yourself, "
        "so I know what you look like, or send /skip if you don't want to.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
    await update.message.reply_text(
        "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
    )

    return LOCATION


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    await update.message.reply_text(
        "I bet you look great! Now, send me your location please, or send /skip."
    )

    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    await update.message.reply_text(
        "Maybe I can visit you sometime! At last, tell me something about yourself."
    )

    return BIO


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    await update.message.reply_text(
        "You seem a bit paranoid! At last, tell me something about yourself."
    )

    return BIO


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Thank you! I hope we can talk again some day.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            LOCATION: [
                MessageHandler(filters.LOCATION, location),
                CommandHandler("skip", skip_location),
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()