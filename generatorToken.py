import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from utils.token_validate_utils import check_limit, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message
from utils.button_ownership_utils import is_button_owner
from utils.chat_timer_utils import set_expire_timer

# State untuk owner tombol
active_button_owner = {}

# Ambil URL backend dari environment agar fleksibel
BACKEND_URL = os.getenv("BACKEND_URL", "https://raw.githubusercontent.com/AmrosoInfinity/Amrosol_Backend-/main/generate")

def token_menu(update, context):
    """Menu awal untuk memilih service token"""
    keyboard = [
        [InlineKeyboardButton("Grab", callback_data="grab"),
         InlineKeyboardButton("Gojek", callback_data="gojek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = update.message.reply_text(string.TOKEN_MENU_TEXT, reply_markup=reply_markup)

    active_button_owner[msg.message_id] = {"owner": update.effective_user.id, "expired": False}
    set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)

def button_handler(update, context):
    """Handler untuk semua tombol callback"""
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
        # Hanya boleh di grup
        if chat.type not in ["group", "supergroup"]:
            send_group_only_message(update, "⚠️ Command ini hanya bisa digunakan di dalam grup.")
            return

        # Pastikan timezone sudah di-set
        if str(user_id) not in user_timezone:
            keyboard = [[InlineKeyboardButton("Set Timezone", callback_data="set_timezone")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            msg = query.edit_message_text(string.NEED_TIMEZONE_TEXT, reply_markup=reply_markup)
            active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
            set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)
            return

        tz_name = user_timezone.get(str(user_id))
        if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
            try:
                payload = {"service": data, "userId": user_id}
                res = requests.post(BACKEND_URL, json=payload, timeout=10)

                if res.ok:
                    backend_data = res.json()
                    url = backend_data.get("url")
                    if url:
                        keyboard = [[InlineKeyboardButton(f"Ambil Token {data.title()}", url=url)]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        query.edit_message_text(string.TOKEN_READY.format(service=data.title()), reply_markup=reply_markup)
                    else:
                        query.edit_message_text(string.TOKEN_NOT_FOUND.format(service=data.title()), parse_mode="Markdown")
                else:
                    query.edit_message_text(string.TOKEN_NOT_FOUND.format(service=data.title()), parse_mode="Markdown")

            except Exception as e:
                query.edit_message_text(f"❌ Error komunikasi dengan backend: {e}")

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
    """Register semua handler terkait token"""
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(button_handler))
