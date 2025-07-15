import logging
import os
import requests
import asyncio
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import settings

load_dotenv()
TOKEN = os.getenv("TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ASK_USER_NAME = 1
user_selection = {}

SELECT_USER, SELECT_SESSION = range(2)


# /start command - create messenger and base user
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    messenger_user_payload = {"messenger_id": telegram_user_id}
    user_payload = {
        "name": first_name,
        "created_by": telegram_user_id,
        "default_hezb": None,
    }

    try:
        create_messenger_user_response = requests.post(
            f"{settings.API_BASE_URL}/messenger-user/", json=messenger_user_payload
        )

        if create_messenger_user_response.status_code in [200, 201]:
            await asyncio.sleep(1)
            create_user_response = requests.post(
                f"{settings.API_BASE_URL}/user/", json=user_payload
            )

            if create_user_response.status_code == 201:
                await update.message.reply_text(
                    settings.START_HELLO_MESSAGE.format(name=first_name)
                )
            else:
                await update.message.reply_text(
                    settings.ERROR_IN_REGISTER_MESSAGE.format(
                        error=create_user_response.text
                    )
                )
                return
        else:
            await update.message.reply_text(
                settings.ERROR_IN_REGISTER_MESSAGE.format(
                    error=create_messenger_user_response.text
                )
            )
            return

    except Exception as e:
        logger.error(settings.ERROR_IN_API_CALL_MESSAGE.format(error=e))
        await update.message.reply_text(
            settings.ERROR_IN_API_CALL_MESSAGE.format(error=e)
        )
        return

    reply_keyboard = [
        [settings.CREATE_NEW_USER_BUTTON, settings.SUBSCRIBE_TO_COURSE_BUTTON]
    ]
    await update.message.reply_text(
        settings.WHAT_DO_YOU_WANT_TO_DO_MESSAGE,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )


# مرحله: ساخت کاربر جدید
async def create_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 لطفاً نام کاربر جدید را وارد کن:")
    return ASK_USER_NAME


async def receive_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    telegram_user_id = update.effective_user.id

    payload = {"name": name, "created_by": telegram_user_id, "default_hezb": None}

    try:
        response = requests.post(f"{settings.API_BASE_URL}/user/", json=payload)
        if response.status_code == 201:
            await update.message.reply_text(f"✅ کاربر '{name}' با موفقیت ایجاد شد.")
        else:
            await update.message.reply_text(f"❌ خطا در ایجاد کاربر: {response.text}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا: {str(e)}")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END


# نمایش جلسات و ثبت‌نام
async def show_session_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    url = f"{settings.API_BASE_URL}/session/"
    response = requests.get(url)

    if response.status_code == 200:
        sessions = response.json()
        keyboard = [
            [
                InlineKeyboardButton(
                    f"ID: {s['id']} - شروع: {s['start_time']} - پایان: {s['end_time']}",
                    callback_data=f"session_{s['id']}",
                )
            ]
            for s in sessions
        ]
        await update.message.reply_text(
            "لطفاً یک جلسه انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("مشکلی در دریافت جلسات پیش آمد.")

async def show_users_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    telegram_user_id = update.effective_user.id
    url = f"{settings.API_BASE_URL}/messenger-user/{telegram_user_id}/users/"
    response = requests.get(url)

    if response.status_code == 200:
        users = response.json()
        keyboard = [
            [InlineKeyboardButton(f"{user['name']}", callback_data="noop")]
            for user in users
        ]
        if not users:
            await update.message.reply_text("❗️هیچ کاربری یافت نشد.")
            return ConversationHandler.END
        await update.message.reply_text(
            "list your users:",  reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("مشکلی در دریافت جلسات پیش آمد.")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "noop":
        return
    selected_session_id = query.data.split("_")[1]
    user_selection[update.effective_user.id] = selected_session_id
    await query.edit_message_text(f"✅ شما جلسه {selected_session_id} را انتخاب کردید.")
    await register_participant(update, selected_session_id)


async def register_participant(update: Update, selected_session_id: str) -> None:
    user_id = update.effective_user.id
    payload = {"user": user_id, "session": selected_session_id, "hezb": None}
    try:
        response = requests.post(f"{settings.API_BASE_URL}/participant/", json=payload)
        if response.status_code == 201:
            await update.message.reply_text(
                f"✅ با موفقیت در جلسه {selected_session_id} ثبت‌نام شدید."
            )
        else:
            await update.message.reply_text(f"❌ خطا در ثبت‌نام: {response.text}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا در ارتباط با سرور: {str(e)}")


async def subscribe_session_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user_id = update.effective_user.id
    url = f"{settings.API_BASE_URL}/messenger-user/{telegram_user_id}/users/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            users = response.json()
            if not users:
                await update.message.reply_text("❗️هیچ کاربری یافت نشد.")
                return ConversationHandler.END

            # ذخیره کاربران برای استفاده در مرحله بعد
            context.user_data["users"] = {str(u["id"]): u["name"] for u in users}

            keyboard = [
                [InlineKeyboardButton(u["name"], callback_data=f"user_{u['id']}")]
                for u in users
            ]
            await update.message.reply_text(
                "👤 لطفاً یکی از کاربران را انتخاب کن:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return SELECT_USER
        else:
            await update.message.reply_text("❗️خطا در دریافت کاربران.")
            return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا در ارتباط: {e}")
        return ConversationHandler.END


async def select_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.data.split("_")[1]
    context.user_data["selected_user_id"] = user_id

    url = f"{settings.API_BASE_URL}/session/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            sessions = response.json()
            if not sessions:
                await query.edit_message_text("هیچ جلسه‌ای یافت نشد.")
                return ConversationHandler.END

            keyboard = [
                [
                    InlineKeyboardButton(
                        f"ID: {s['id']} - شروع: {s['start_time'].split('T')[0]}",
                        callback_data=f"session_{s['id']}",
                    )
                ]
                for s in sessions
            ]

            await query.edit_message_text(
                "📅 لطفاً یک جلسه را انتخاب کن:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return SELECT_SESSION
        else:
            await query.edit_message_text("❗️خطا در دریافت جلسات.")
            return ConversationHandler.END
    except Exception as e:
        await query.edit_message_text(f"⚠️ خطا در ارتباط با سرور: {e}")
        return ConversationHandler.END


async def select_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    session_id = query.data.split("_")[1]
    user_id = context.user_data.get("selected_user_id")

    payload = {"user": user_id, "session": session_id, "hezb": None}
    try:
        response = requests.post(f"{settings.API_BASE_URL}/participant/", json=payload)
        if response.status_code == 201:
            await query.edit_message_text(
                f"✅ کاربر با موفقیت در جلسه {session_id} ثبت‌نام شد."
            )
        else:
            await query.edit_message_text(f"❌ خطا در ثبت‌نام: {response.text}")
    except Exception as e:
        await query.edit_message_text(f"⚠️ خطا در ارتباط با سرور: {e}")

    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    user_create_conv = ConversationHandler(
        entry_points=[CommandHandler("create_user", create_user_command)],
        states={
            ASK_USER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_name)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    subscribe_session_conv = ConversationHandler(
        entry_points=[
            CommandHandler("session_subscription", subscribe_session_command)
        ],
        states={
            SELECT_USER: [CallbackQueryHandler(select_user, pattern=r"^user_\d+$")],
            SELECT_SESSION: [
                CallbackQueryHandler(select_session, pattern=r"^session_\d+$")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(user_create_conv)
    application.add_handler(subscribe_session_conv)
    application.add_handler(CommandHandler("show_users", show_users_command))
    application.add_handler(CommandHandler("show_sessions", show_session_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
