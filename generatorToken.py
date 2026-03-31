import os
import requests
import hashlib
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from utils.token_validate_utils import check_limit, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message
from utils.button_ownership_utils import is_button_owner
from utils.chat_timer_utils import set_expire_timer
from utils.token_utils import fetch_tokens_from_gist

active_button_owner = {}

# Gunakan FRONTEND_TOKEN untuk trigger workflow backend
GITHUB_API_URL = "https://api.github.com/repos/AmrosoInfinity/Amrosol_Backend-/actions/workflows/push-token.yml/dispatches"
GITHUB_TOKEN = os.getenv("FRONTEND_TOKEN")

def trigger_backend(service, user_id):
    """Trigger workflow backend via GitHub API dispatch"""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "ref": "main",
        "inputs": {
            "service": service,
            "userId": str(user_id)
        }
    }
    res = requests.post(GITHUB_API_URL, headers=headers, json=payload)
    return res.status_code == 204

def build_token_url(service, user_id, token_value):
    """Bangun URL rapi dengan hash token"""
    hash_token = hashlib.sha256(token_value.encode()).hexdigest()[:12]
    return f"https://amrosol.online/{service}/{user_id}/{hash_token}.html"

def token_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Grab", callback_data="grab"),
         InlineKeyboardButton("Gojek", callback_data="gojek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = update.message.reply_text(string.TOKEN_MENU_TEXT, reply_markup=reply_markup)
    active_button_owner[msg.message_id] = {"owner": update.effective_user.id, "expired": False}
    set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)

def button_handler(update, context):
    query = update.callback_query
    chat = update.effective_chat
    user_id = query.from_user.id
    data = query.data
    message_id = query.message.message_id

    state = active_button_owner.get(message_id)
    if not is_button_owner(context, chat, user_id, state, query):
        return

    user_requests, user_blocked, user_timezone = load_tmp(user_id)

    if data in ["grab", "gojek"]:
        if chat.type not in ["group", "supergroup"]:
            send_group_only_message(update, "⚠️ Command ini hanya bisa digunakan di dalam grup.")
            return

        if str(user_id) not in user_timezone:
            keyboard = [[InlineKeyboardButton("Set Timezone", callback_data="set_timezone")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            msg = query.edit_message_text(string.NEED_TIMEZONE_TEXT, reply_markup=reply_markup)
            active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
            set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)
            return

        tz_name = user_timezone.get(str(user_id))
        if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
            # Ambil token dari gist
            tokens = fetch_tokens_from_gist(data)
            if tokens:
                index = int(user_id) % len(tokens)
                token_value = tokens[index]

                if trigger_backend(data, user_id):
                    url = build_token_url(data, user_id, token_value)
                    keyboard = [[InlineKeyboardButton(f"Ambil Token {data.title()}", url=url)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    query.edit_message_text(string.TOKEN_READY.format(service=data.title()), reply_markup=reply_markup)
                else:
                    query.edit_message_text(string.TOKEN_NOT_FOUND.format(service=data.title()), parse_mode="Markdown")
            else:
                query.edit_message_text(string.TOKEN_NOT_FOUND.format(service=data.title()), parse_mode="Markdown")

        save_tmp(user_id, user_requests, user_blocked, user_timezone)
        if state:
            active_button_owner.pop(message_id, None)

    elif data == "set_timezone":
        keyboard = [
            [InlineKeyboardButton(string.TIMEZONE_WIB, callback_data="tz_Asia/Jakarta")],
            [InlineKeyboardButton(string.TIMEZONE_WITA, callback_data="tz_Asia/Makassar")],
            [InlineKeyboardButton(string.TIMEZONE_WIT, callback_data="tz_Asia/Jayapura")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = query.edit_message_text(string.CHOOSE_TIMEZONE_TEXT, reply_markup=reply_markup)
        active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
        set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)

    elif data.startswith("tz_"):
        tz_name = data.replace("tz_", "")
        user_timezone[str(user_id)] = tz_name
        save_tmp(user_id, user_requests, user_blocked, user_timezone)
        query.edit_message_text(string.TIMEZONE_SET_SUCCESS.format(tz=tz_name), parse_mode="Markdown")
        if state:
            active_button_owner.pop(message_id, None)

def register_token_handlers(dp):
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(button_handler))
