import random
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from utils.token_validate_utils import check_limit, fetch_tokens, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message
from utils.button_ownership_utils import is_button_owner
from utils.chat_timer_utils import set_expire_timer

# mapping message_id -> {owner: user_id, expired: bool}
active_button_owner = {}

# === Helper untuk hapus pesan ===
def delete_message(context):
    job = context.job
    chat_id = job.context["chat_id"]
    message_id = job.context["message_id"]
    try:
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"[DEBUG] Failed to delete message {message_id}: {e}")

# === Validasi token usage ===
def can_use_token(token, user_id, token_usage):
    """Return True jika token masih bisa dipakai, False kalau sudah limit."""
    users = set(token_usage.get(token, []))
    if len(users) >= 3:
        return False
    users.add(user_id)
    token_usage[token] = list(users)
    return True

def get_available_token(tokens, user_id, token_usage):
    """Cari token yang belum penuh 3 user."""
    random.shuffle(tokens)
    for token in tokens:
        if can_use_token(token, user_id, token_usage):
            return token
    return None

# === Menu utama token ===
def token_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Grab", callback_data="grab"),
         InlineKeyboardButton("Gojek", callback_data="gojek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = update.message.reply_text(string.TOKEN_MENU_TEXT, reply_markup=reply_markup)

    active_button_owner[msg.message_id] = {
        "owner": update.effective_user.id,
        "expired": False
    }
    set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)

# === Handler tombol ===
def button_handler(update, context):
    query = update.callback_query
    chat = update.effective_chat
    user_id = query.from_user.id
    data = query.data
    message_id = query.message.message_id

    state = active_button_owner.get(message_id)

    # cek kepemilikan tombol
    if not is_button_owner(context, chat, user_id, state, query):
        return

    user_requests, user_blocked, user_timezone, token_usage, last_token = load_tmp(user_id)

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

        # cek apakah user sudah punya token dalam 12 jam terakhir
        if last_token:
            last_time = datetime.datetime.fromisoformat(last_token.get("time"))
            if datetime.datetime.now() - last_time < datetime.timedelta(hours=12):
                query.edit_message_text("⚠️ Kamu sudah menerima token dalam 12 jam terakhir.", parse_mode="Markdown")
                return

        # === Grab ===
        if data == "grab":
            if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                tokens = fetch_tokens("https://gist.githubusercontent.com/AmrosoInfinity/5b19fdb53aa1bfcfa4fc3843165b9471/raw/Grab")
                if tokens:
                    chosen = get_available_token(tokens, user_id, token_usage)
                    if chosen:
                        msg = query.edit_message_text(string.TOKEN_GRAB.format(token=chosen), parse_mode="Markdown")
                        context.job_queue.run_once(delete_message, 20, context={"chat_id": msg.chat_id, "message_id": msg.message_id})
                        last_token = {"service": "Grab", "time": datetime.datetime.now().isoformat()}
                    else:
                        query.edit_message_text("⚠️ Semua token sudah dipakai oleh 3 user.", parse_mode="Markdown")
                else:
                    query.edit_message_text(string.TOKEN_NOT_FOUND.format(service="Grab"), parse_mode="Markdown")
            save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)

        # === Gojek ===
        elif data == "gojek":
            if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                tokens = fetch_tokens("https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek")
                if tokens:
                    chosen = get_available_token(tokens, user_id, token_usage)
                    if chosen:
                        msg = query.edit_message_text(string.TOKEN_GOJEK.format(token=chosen), parse_mode="Markdown")
                        context.job_queue.run_once(delete_message, 20, context={"chat_id": msg.chat_id, "message_id": msg.message_id})
                        last_token = {"service": "Gojek", "time": datetime.datetime.now().isoformat()}
                    else:
                        query.edit_message_text("⚠️ Semua token sudah dipakai oleh 3 user.", parse_mode="Markdown")
                else:
                    query.edit_message_text(string.TOKEN_NOT_FOUND.format(service="Gojek"), parse_mode="Markdown")
            save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)

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
        save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)
        query.edit_message_text(string.TIMEZONE_SET_SUCCESS.format(tz=tz_name), parse_mode="Markdown")
        if state:
            active_button_owner.pop(message_id, None)

# === Registrasi handler ===
def register_token_menu(dp):
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(button_handler))

def register_token_handlers(dp):
    register_token_menu(dp)
