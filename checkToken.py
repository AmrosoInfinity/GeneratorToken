import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters
from utils.remove_token_user import remove_user_token_message
from support.string import (
    CHECKTOKEN_VALID_MSG,
    CHECKTOKEN_INVALID_MSG,
    CHECKTOKEN_ERROR_MSG,
    CHECKTOKEN_PROMPT_MSG,
    CHECKTOKEN_NOT_A_TOKEN_MSG,
)

def checktoken_command(update, context):
    keyboard = [[InlineKeyboardButton("Masukkan Token", switch_inline_query_current_chat="")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(CHECKTOKEN_PROMPT_MSG, reply_markup=reply_markup)

def checktoken_handler(update, context):
    raw_text = update.message.text
    # Bersihkan mention, simbol, dan spasi
    token = raw_text.replace("@AmrosolBot", "").replace("*", "").strip()
    token_length = len(token)

    # Validasi awal: hanya token yang dimulai "ey"
    if not token.startswith("ey"):
        update.message.reply_text(CHECKTOKEN_NOT_A_TOKEN_MSG)
        return

    lat = "-6.1901"
    lng = "106.8326"
    url = f"https://p.grabtaxi.com/api/passenger/v3/grabfood/content/restaurants?latlng={lat},{lng}"

    headers = {"Authorization": token}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        status_code = resp.status_code

        if status_code == 200:
            reply = CHECKTOKEN_VALID_MSG.format(length=token_length, status=status_code)
        else:
            reply = CHECKTOKEN_INVALID_MSG.format(length=token_length, status=status_code)

        update.message.reply_text(reply)

    except Exception as e:
        update.message.reply_text(CHECKTOKEN_ERROR_MSG.format(error=e))

    remove_user_token_message(context, update.message.chat_id, update.message.message_id)

def register_checktoken(dp):
    dp.add_handler(CommandHandler("checktoken", checktoken_command))
    # Full filter: hanya teks biasa, bukan command
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, checktoken_handler))
