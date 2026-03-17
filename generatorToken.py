import time
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from utils.token_validate_utils import check_limit, fetch_tokens, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message

def token_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Grab", callback_data="grab"),
         InlineKeyboardButton("Gojek", callback_data="gojek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(string.TOKEN_MENU_TEXT, reply_markup=reply_markup)

def button_handler(update, context):
    query = update.callback_query
    chat = update.effective_chat
    user_id = query.from_user.id
    data = query.data

    # selalu load data user dari tmp
    user_requests, user_blocked, user_timezone = load_tmp(user_id)

    if data in ["grab", "gojek"]:
        # cek group only
        if chat.type not in ["group", "supergroup"]:
            send_group_only_message(update, "⚠️ Command ini hanya bisa digunakan di dalam grup.")
            return

        # cek timezone
        if str(user_id) not in user_timezone:
            keyboard = [[InlineKeyboardButton("Set Timezone", callback_data="set_timezone")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(string.NEED_TIMEZONE_TEXT, reply_markup=reply_markup)
            return

        tz_name = user_timezone[str(user_id)]
        if data == "grab":
            if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                tokens = fetch_tokens("https://gist.githubusercontent.com/AmrosoInfinity/5b19fdb53aa1bfcfa4fc3843165b9471/raw/Grab")
                if tokens:
                    chosen = random.choice(tokens)
                    time.sleep(2)
                    query.edit_message_text(string.TOKEN_GRAB.format(token=chosen), parse_mode="Markdown")
                else:
                    query.edit_message_text(string.TOKEN_NOT_FOUND.format(service="Grab"))
            # simpan setiap interaksi
            save_tmp(user_id, user_requests, user_blocked, user_timezone)

        elif data == "gojek":
            if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                tokens = fetch_tokens("https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek")
                if tokens:
                    chosen = random.choice(tokens)
                    time.sleep(2)
                    query.edit_message_text(string.TOKEN_GOJEK.format(token=chosen), parse_mode="Markdown")
                else:
                    query.edit_message_text(string.TOKEN_NOT_FOUND.format(service="Gojek"))
            # simpan setiap interaksi
            save_tmp(user_id, user_requests, user_blocked, user_timezone)

    elif data == "set_timezone":
        keyboard = [
            [InlineKeyboardButton(string.TIMEZONE_WIB, callback_data="tz_Asia/Jakarta")],
            [InlineKeyboardButton(string.TIMEZONE_WITA, callback_data="tz_Asia/Makassar")],
            [InlineKeyboardButton(string.TIMEZONE_WIT, callback_data="tz_Asia/Jayapura")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(string.CHOOSE_TIMEZONE_TEXT, reply_markup=reply_markup)

    elif data.startswith("tz_"):
        tz_name = data.replace("tz_", "")
        user_timezone[str(user_id)] = tz_name
        save_tmp(user_id, user_requests, user_blocked, user_timezone)
        query.edit_message_text(string.TIMEZONE_SET_SUCCESS.format(tz=tz_name))

def register_token_menu(dp):
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(button_handler))

def register_token_handlers(dp):
    register_token_menu(dp)
