import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from utils.token_validate_utils import check_limit, fetch_tokens, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message
from utils.button_ownership_utils import is_button_owner
from utils.chat_timer_utils import set_expire_timer
from utils.captureTraffic import get_x_token

# mapping message_id -> {owner: user_id, expired: bool}
active_button_owner = {}

def token_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Grab", callback_data="grab"),
         InlineKeyboardButton("Gojek", callback_data="gojek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = update.message.reply_text(string.TOKEN_MENU_TEXT, reply_markup=reply_markup)

    active_button_owner[msg.message_id] = {"owner": update.effective_user.id, "expired": False}
    set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)


def handle_grab(query, tz_name, user_id, user_requests, user_blocked, user_timezone, update, context):
    if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
        token = get_x_token(
            file_path="playload/disini/grab_payload.bin",   # payload hasil capture di repo
            prev_token="isi_token_lama_dari_response",     # token lama dari response sebelumnya
            batch_id="954a7e43-aaa1-4726-a280-c1b4451d0577",
            event_count=122,
            batch_timestamp=1774808569291
        )
        if token:
            query.edit_message_text(string.TOKEN_GRAB.format(token=token), parse_mode="Markdown")
        else:
            query.edit_message_text(string.TOKEN_NOT_FOUND.format(service="Grab"), parse_mode="Markdown")
    save_tmp(user_id, user_requests, user_blocked, user_timezone)


def handle_gojek(query, tz_name, user_id, user_requests, user_blocked, user_timezone, update, context):
    if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
        tokens = fetch_tokens("https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek")
        if tokens:
            chosen = random.choice(tokens)
            query.edit_message_text(string.TOKEN_GOJEK.format(token=chosen), parse_mode="Markdown")
        else:
            query.edit_message_text(string.TOKEN_NOT_FOUND.format(service="Gojek"), parse_mode="Markdown")
    save_tmp(user_id, user_requests, user_blocked, user_timezone)


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
        if data == "grab":
            handle_grab(query, tz_name, user_id, user_requests, user_blocked, user_timezone, update, context)
        elif data == "gojek":
            handle_gojek(query, tz_name, user_id, user_requests, user_blocked, user_timezone, update, context)

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


def register_token_menu(dp):
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(button_handler))


def register_token_handlers(dp):
    register_token_menu(dp)
