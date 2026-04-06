import datetime
import logging
import traceback
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

# Import tetap dibutuhkan untuk limit dan timezone, tapi tidak untuk token Gojek
from utils.token_validate_utils import check_limit, fetch_tokens, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message
from utils.button_ownership_utils import is_button_owner
from utils.chat_timer_utils import set_expire_timer
from utils.grab_handler_utils import handle_grab

logger = logging.getLogger(__name__)
active_button_owner = {}

def token_menu(update, context):
    keyboard = [[InlineKeyboardButton("Grab 🚦", callback_data="grab"),
                 InlineKeyboardButton("Gojek 🚦", callback_data="gojek")]]
    msg = update.message.reply_text(string.TOKEN_MENU_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
    active_button_owner[msg.message_id] = {"owner": update.effective_user.id, "expired": False}
    set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)

def button_handler(update, context):
    query = update.callback_query
    chat = update.effective_chat
    user_id = query.from_user.id
    data = query.data
    message_id = query.message.message_id

    query.answer()

    # 1. Cek Owner
    state = active_button_owner.get(message_id)
    if not is_button_owner(context, chat, user_id, state, query):
        return

    # 2. Ambil data HANYA untuk keperluan Timezone & Limit
    user_requests, user_blocked, user_timezone, token_usage, last_token = load_tmp(user_id)

    try:
        if data == "gojek":
            # Cek Timezone dulu (karena limit butuh info waktu lokal)
            tz_name = user_timezone.get(str(user_id))
            if not tz_name:
                keyboard = [[InlineKeyboardButton("Set Timezone 🌍", callback_data="set_timezone")]]
                query.edit_message_text(string.NEED_TIMEZONE_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
                return

            # Jalankan Limit Checker
            if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                # --- PROSES DIRECT FETCH (Tanpa Load/Save Token) ---
                query.edit_message_text("📡 *Fetching Gist...*", parse_mode="Markdown")
                
                url_gojek = "https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek"
                tokens = fetch_tokens(url_gojek) # Ini fungsi yang sudah ada retry logic
                
                if tokens:
                    # Ambil satu secara acak agar adil
                    import random
                    token_hasil = random.choice(tokens).strip()
                    
                    # Langsung kirim ke user
                    try:
                        pesan = string.TOKEN_GOJEK.format(token=f"```{token_hasil}```")
                    except:
                        pesan = f"🚀 **Gojek Token:**\n\n```{token_hasil}```"
                    
                    query.edit_message_text(pesan, parse_mode="Markdown")
                    
                    # Update jumlah request saja ke database tmp (tanpa simpan tokennya)
                    save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)

                    # Hapus otomatis pesan token dalam 15 detik
                    context.job_queue.run_once(lambda ctx: ctx.bot.delete_message(chat.id, message_id), 15)
                else:
                    query.edit_message_text("❌ Gagal mengambil data dari Gist.")

        elif data == "grab":
            # Grab tetap pakai handler lama karena butuh sinkronisasi khusus
            tz_name = user_timezone.get(str(user_id))
            if tz_name:
                handle_grab(query, user_id, tz_name, user_requests, user_blocked, user_timezone, token_usage, last_token, update, context)

        # Logika Timezone tetap sama...
        elif data == "set_timezone" or data.startswith("tz_"):
            # (Logika set_timezone kamu di sini)
            pass

    except Exception as e:
        logger.error(f"Error: {traceback.format_exc()}")
        query.edit_message_text(f"⚠️ **Error:** `{str(e)}`", parse_mode="Markdown")

def register_token_handlers(dp):
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(button_handler, pattern=r"^(grab|gojek|set_timezone|tz_.*)$"))
