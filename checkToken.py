import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from utils.remove_token_user import remove_user_token_message
from utils.button_ownership_utils import is_checktoken_owner
from support.string import (
    CHECKTOKEN_VALID_MSG,
    CHECKTOKEN_INVALID_MSG,
    CHECKTOKEN_ERROR_MSG,
    CHECKTOKEN_PROMPT_MSG,
    CHECKTOKEN_NOT_A_TOKEN_MSG,
)

def checktoken_command(update, context):
    # simpan owner id
    context.user_data["checktoken_state"] = {"owner": update.effective_user.id, "expired": False}
    keyboard = [[InlineKeyboardButton("Masukkan Token", callback_data="checktoken")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(CHECKTOKEN_PROMPT_MSG, reply_markup=reply_markup)

def checktoken_button(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    chat = update.effective_chat
    state = context.user_data.get("checktoken_state")

    # cek ownership
    if not is_checktoken_owner(context, chat, user_id, state, query):
        return

    # kalau owner → hapus tombol setelah ditekan
    query.answer()
    query.edit_message_text("Silakan kirim token Anda di chat.")
    # hapus state agar tidak bisa dipakai lagi
    context.user_data.pop("checktoken_state", None)

def checktoken_handler(update, context):
    raw_text = update.message.text
    token = raw_text.replace("@AmrosolBot", "").replace("*", "").strip()
    token_length = len(token)

    if not token.startswith("ey"):
        update.message.reply_text(CHECKTOKEN_NOT_A_TOKEN_MSG)
        return

    lat = "-6.1901"
    lng = "106.8326"
    url = f"https://p.grabtaxi.com/api/passenger/v3/grabfood/content/restaurants?latlng={lat},{lng}"

    headers = {
        "Authorization": token,
        "X-Location": f"{lat},{lng}",
        "x-mts-ssid": token,
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Grab/5.397.0 (Android 15; Build 139598668)"
    }

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
    dp.add_handler(CallbackQueryHandler(checktoken_button, pattern="^checktoken$"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, checktoken_handler))
