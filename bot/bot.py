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
SELECTING_USERS = 2
SELECT_USER = 3

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
        return SELECT_USER
    else:
        await update.message.reply_text("مشکلی در دریافت جلسات پیش آمد.")


async def show_users_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    telegram_user_id = update.effective_user.id
    print(telegram_user_id)
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


def send_register_participant(user_ids, session_id) -> None:
    for user_id in user_ids:
        payload = {"user": user_id, "session": session_id, "hezb": None}
        r = requests.post(f"{settings.API_BASE_URL}/participant/", json=payload)


async def join_session_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await send_session_selection(chat_id, context)
    return SELECT_USER


async def show_user_selection_menu(query, context):
    selected = context.user_data.get("selected_users", set())
    users = context.user_data["all_users"]

    keyboard = []
    for user in users:
        user_id = str(user['id'])
        is_selected = user_id in selected
        prefix = "✅ " if is_selected else ""
        keyboard.append([
            InlineKeyboardButton(f"{prefix}{user['name']}", callback_data=f"user_{user_id}")
        ])

    keyboard.append([InlineKeyboardButton("✅ تأیید انتخاب‌ها", callback_data="confirm_selection")])

    await query.message.edit_text(
        "کاربران مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def select_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    session_id = query.data.split("_")[1]
    context.user_data["session_id"] = session_id
    context.user_data["selected_users"] = set()

    telegram_user_id = update.effective_user.id
    url = f"{settings.API_BASE_URL}/messenger-user/{telegram_user_id}/users/"
    response = requests.get(url)

    if response.status_code == 200:
        users = response.json()
        context.user_data["all_users"] = users  # ذخیره لیست کامل برای استفاده در مراحل بعد

        if not users:
            await query.message.reply_text("❗️هیچ کاربری یافت نشد.")
            return ConversationHandler.END

        await show_user_selection_menu(query, context)
        return SELECTING_USERS
    else:
        await query.message.reply_text("مشکلی در دریافت جلسات پیش آمد.")
        return ConversationHandler.END


async def handle_user_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("user_"):
        user_id = data.split("_")[1]
        selected = context.user_data.setdefault("selected_users", set())
        if user_id in selected:
            selected.remove(user_id)
        else:
            selected.add(user_id)

        await show_user_selection_menu(query, context)
        return SELECTING_USERS

    elif data == "confirm_selection":
        selected_ids = context.user_data.get("selected_users", set())
        selected_names = [
            user['name']
            for user in context.user_data["all_users"]
            if str(user['id']) in selected_ids
        ]
        await query.message.edit_text(
            f"✅ کاربران انتخاب‌شده:\n" + "\n".join(selected_names)
        )
        session_id = context.user_data.get("session_id")
        send_register_participant(selected_ids, session_id)
        await query.message.edit_text(
            f"✅ کاربران انتخاب‌شده:\n" + "\n".join(selected_names) +
            "\n\n✅ اطلاعات با موفقیت ارسال شد."
        )
        return ConversationHandler.END

async def send_session_selection(chat_id, context):
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
        await context.bot.send_message(
            chat_id=chat_id,
            text="لطفاً یک جلسه انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="مشکلی در دریافت جلسات پیش آمد."
        )

async def start_join_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    await send_session_selection(chat_id, context)
    return SELECT_USER

def run_bot() -> None:
    application = Application.builder().token(os.getenv("TOKEN")).build()

    user_create_conv = ConversationHandler(
        entry_points=[CommandHandler("create_user", create_user_command)],
        states={
            ASK_USER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_name)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    join_session_conv = ConversationHandler(
        entry_points=[
            CommandHandler("join_session", join_session_command),
            CallbackQueryHandler(start_join_session, pattern="^start_join_session$")
        ],
        states={
            SELECT_USER: [CallbackQueryHandler(select_user)],
            SELECTING_USERS: [
            CallbackQueryHandler(handle_user_selection, pattern="^(user_|confirm_selection$)")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(user_create_conv)
    application.add_handler(join_session_conv)
    application.add_handler(CommandHandler("show_users", show_users_command))
    application.add_handler(CommandHandler("show_sessions", show_session_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CallbackQueryHandler(start_join_session, pattern="^start_join_session$"))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
