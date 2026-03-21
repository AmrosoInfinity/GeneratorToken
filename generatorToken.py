import time
import random
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from utils.token_validate_utils import check_limit, fetch_tokens, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message

# mapping message_id -> {owner: user_id, expired: bool}
active_button_owner = {}

def set_expire_timer(context, chat_id, message_id):
    def expire_button():
        time.sleep(60)
        state = active_button_owner.get(message_id)
        if state and not state["expired"]:
            try:
                context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=string.NO_SELECTION_MSG,   # "Anda tidak memilih apapun 🙄"
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            state["expired"] = True
    threading.Thread(target=expire_button, daemon=True).start()

def token_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Grab", callback_data="grab"),
         InlineKeyboardButton("Gojek", callback_data="gojek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = update.message.reply_text(string.TOKEN_MENU_TEXT, reply_markup=reply_markup)

    # catat owner tombol baru
    active_button_owner[msg.message_id] = {
        "owner": update.effective_user.id,
        "expired": False
    }
    set_expire_timer(context, msg.chat_id, msg.message_id)

def button_handler(update, context):
    query = update.callback_query
    chat = update.effective_chat
    user_id = query.from_user.id
    data = query.data
    message_id = query.message.message_id

    state = active_button_owner.get(message_id)

    # cek kepemilikan tombol
    if state:
        if state["owner"] != user_id:
            # ambil daftar admin untuk cek anonymous
            admins = context.bot.get_chat_administrators(chat.id)
            anon_ids = [admin.user.id for admin in admins if getattr(admin, "is_anonymous", False)]
            if user_id not in anon_ids:
                query.answer(string.NOT_YOUR_BUTTON_MSG, show_alert=True)  # "Token ini bukan untukmu🥱"
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
            # catat owner tombol baru
            active_button_owner[msg.message_id] = {
                "owner": user_id,
                "expired": False
            }
            set_expire_timer(context, msg.chat_id, msg.message_id)
            return

        tz_name = user_timezone.get(str(user_id))
        if data == "grab":
            if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                tokens = fetch_tokens("https://gist.githubusercontent.com/AmrosoInfinity/5b19fdb53aa1bfcfa4fc3843165b9471/raw/Grab")
                if tokens:
                    chosen = random.choice(tokens)
                    time.sleep(2)
                    query.edit_message_text(string.TOKEN_GRAB.format(token=chosen), parse_mode="Markdown")
                else:
                    query.edit_message_text(string.TOKEN_NOT_FOUND.format(service="Grab"), parse_mode="Markdown")
            save_tmp(user_id, user_requests, user_blocked, user_timezone)

        elif data == "gojek":
            if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                tokens = fetch_tokens("https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek")
                if tokens:
                    chosen = random.choice(tokens)
                    time.sleep(2)
                    query.edit_message_text(string.TOKEN_GOJEK.format(token=chosen), parse_mode="Markdown")
                else:
                    query.edit_message_text(string.TOKEN_NOT_FOUND.format(service="Gojek"), parse_mode="Markdown")
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
        # catat owner tombol baru
        active_button_owner[msg.message_id] = {
            "owner": user_id,
            "expired": False
        }
        set_expire_timer(context, msg.chat_id, msg.message_id)

    elif data.startswith("tz_"):
        tz_name = data.replace("tz_", "")
        user_timezone[str(user_id)] = tz_name
        save_tmp(user_id, user_requests, user_blocked, user_timezone)
        query.edit_message_text(string.TIMEZONE_SET_SUCCESS.format(tz=tz_name), parse_mode="Markdown")
        if state:
            active_button_owner.pop(message_id, None)

def register_token_menu(dp):
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(button_handler))

def register_token_handlers(dp):
    register_token_menu(dp)
