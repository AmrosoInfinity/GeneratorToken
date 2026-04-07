import datetime
import logging
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from utils.token_validate_utils import check_limit, fetch_tokens, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message # Pakai ini buat arahin user
from utils.button_ownership_utils import is_button_owner
from utils.chat_timer_utils import set_expire_timer
from utils.grab_handler_utils import handle_grab

logger = logging.getLogger(__name__)

active_button_owner = {}

def token_menu(update, context):
    chat = update.effective_chat
    user_id = update.effective_user.id
    bot_owner_id = context.bot_data.get("owner_id")

    # 1. Cek apakah ini Supergroup & Verifikasi Owner
    is_valid_group = False
    if chat.type == "supergroup":
        try:
            admins = context.bot.get_chat_administrators(chat.id)
            group_owner = next((admin for admin in admins if admin.status == 'creator'), None)
            if group_owner and group_owner.user.id == bot_owner_id:
                is_valid_group = True
        except Exception as e:
            logger.error(f"Gagal verifikasi group owner: {e}")

    # 2. Jika tidak valid, kirim pesan arahan (tombol add to group/join)
    if not is_valid_group:
        text_warn = "⚠️ *Akses Ditolak!*\nPerintah ini hanya bisa digunakan di dalam *Supergroup Resmi* milik Owner Bot."
        send_group_only_message(update, text=text_warn)
        return

    # 3. Jika valid, tampilkan menu seperti biasa
    keyboard = [
        [InlineKeyboardButton("Grab 🚦", callback_data="grab"),
         InlineKeyboardButton("Gojek 🚦", callback_data="gojek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = update.message.reply_text(string.TOKEN_MENU_TEXT, reply_markup=reply_markup)

    active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
    set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)

def button_handler(update, context):
    query = update.callback_query
    chat = update.effective_chat
    user_id = query.from_user.id
    data = query.data
    message_id = query.message.message_id
    query.answer()

    state = active_button_owner.get(message_id)
    if not is_button_owner(context, chat, user_id, state, query):
        return

    tmp_data = load_tmp(user_id)
    if not tmp_data or len(tmp_data) < 5:
        user_requests, user_blocked, user_timezone, token_usage, last_token = {}, {}, {}, {}, {}
    else:
        user_requests, user_blocked, user_timezone, token_usage, last_token = tmp_data

    try:
        if data in ["grab", "gojek"]:
            # Proteksi tambahan di callback
            if chat.type != "supergroup":
                send_group_only_message(update, "⚠️ Hanya bisa di Supergroup resmi.")
                return

            if str(user_id) not in user_timezone:
                keyboard = [[InlineKeyboardButton("Set Timezone 🌍", callback_data="set_timezone")]]
                msg = query.edit_message_text(string.NEED_TIMEZONE_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
                active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
                set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)
                return

            tz_name = user_timezone.get(str(user_id))

            if data == "grab":
                last_token = handle_grab(query, user_id, tz_name, user_requests, user_blocked, user_timezone, token_usage, last_token, update, context)

            elif data == "gojek":
                if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                    url_gojek = "https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek"
                    tokens = fetch_tokens(url_gojek)
                    if tokens:
                        token = random.choice(tokens).strip()
                        pesan = f"**#### TOKEN GOJEK ####**\n\n```{token}```"
                        query.edit_message_text(pesan, parse_mode="Markdown")
                        
                        last_token = {"service": "Gojek", "time": datetime.datetime.now().isoformat()}
                        context.job_queue.run_once(lambda ctx: ctx.bot.delete_message(chat.id, message_id), 15)
                    else:
                        query.edit_message_text("❌ Token Gojek tidak ditemukan di Gist.", parse_mode="Markdown")
                
                save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)

            active_button_owner.pop(message_id, None)

        elif data == "set_timezone":
            keyboard = [[InlineKeyboardButton("WIB", callback_data="tz_Asia/Jakarta")],
                        [InlineKeyboardButton("WITA", callback_data="tz_Asia/Makassar")],
                        [InlineKeyboardButton("WIT", callback_data="tz_Asia/Jayapura")]]
            query.edit_message_text(string.CHOOSE_TIMEZONE_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))

        elif data.startswith("tz_"):
            tz_selected = data.replace("tz_", "")
            user_timezone[str(user_id)] = tz_selected
            save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)
            query.edit_message_text(f"✅ Timezone diatur ke: `{tz_selected}`", parse_mode="Markdown")
            active_button_owner.pop(message_id, None)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        try:
            query.edit_message_text(f"⚠️ Error Internal: {str(e)}")
        except:
            pass

def register_token_handlers(dp, owner_id):
    dp.bot_data["owner_id"] = owner_id
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(button_handler, pattern=r"^(grab|gojek|set_timezone|tz_.*)$"))
