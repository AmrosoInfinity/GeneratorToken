import datetime
import logging
import random
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

# Import utils (Pastikan nama fungsi sinkron dengan utils/token_validate_utils.py)
from utils.token_validate_utils import check_limit, fetch_tokens, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message
from utils.button_ownership_utils import is_button_owner
from utils.chat_timer_utils import set_expire_timer
from utils.grab_handler_utils import handle_grab

logger = logging.getLogger(__name__)

# Mapping message_id -> {owner: user_id, expired: bool}
active_button_owner = {}

def token_menu(update, context):
    """Menampilkan menu utama Grab & Gojek."""
    keyboard = [
        [InlineKeyboardButton("Grab 🚦", callback_data="grab"),
         InlineKeyboardButton("Gojek 🚦", callback_data="gojek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = update.message.reply_text(string.TOKEN_MENU_TEXT, reply_markup=reply_markup)

    active_button_owner[msg.message_id] = {"owner": update.effective_user.id, "expired": False}
    set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)

def button_handler(update, context):
    """Handler utama untuk klik tombol."""
    query = update.callback_query
    chat = update.effective_chat
    user_id = query.from_user.id
    data = query.data
    message_id = query.message.message_id

    query.answer()

    # 1. Validasi Owner Tombol
    state = active_button_owner.get(message_id)
    if not is_button_owner(context, chat, user_id, state, query):
        return

    # 2. Load Data User (Selalu tangkap 5 variabel agar tidak crash)
    user_requests, user_blocked, user_timezone, token_usage, last_token = load_tmp(user_id)

    try:
        # --- LOGIKA LAYANAN ---
        if data in ["grab", "gojek"]:
            if chat.type not in ["group", "supergroup"]:
                send_group_only_message(update, "⚠️ Command ini hanya bisa digunakan di dalam grup.")
                return

            # Cek Timezone
            tz_name = user_timezone.get(str(user_id))
            if not tz_name:
                keyboard = [[InlineKeyboardButton("Set Timezone 🌍", callback_data="set_timezone")]]
                msg = query.edit_message_text(string.NEED_TIMEZONE_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
                active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
                set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)
                return

            # --- EKSEKUSI GRAB ---
            if data == "grab":
                # Biarkan Grab menggunakan handler bawaanmu
                last_token = handle_grab(query, user_id, tz_name, user_requests, user_blocked, user_timezone, token_usage, last_token, update, context)

            # --- EKSEKUSI GOJEK (Direct Fetch & Zero-Storage) ---
            elif data == "gojek":
                if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                    query.edit_message_text("📡 *Menghubungkan ke Gist...*", parse_mode="Markdown")
                    
                    url_gojek = "https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek"
                    tokens = fetch_tokens(url_gojek)
                    
                    if tokens:
                        chosen = random.choice(tokens).strip()
                        time.sleep(1) # Jeda singkat agar transisi mulus
                        
                        # Tampilkan token (pake format monospaced agar mudah di-copy)
                        try:
                            text = string.TOKEN_GOJEK.format(token=f"```{chosen}```")
                        except:
                            text = f"🚀 **Gojek Token:**\n\n```{chosen}```"
                        
                        query.edit_message_text(text, parse_mode="Markdown")
                        
                        # Simpan metadata ringan (Hanya waktu, tanpa isi token Gist)
                        meta_gojek = {"service": "Gojek", "time": datetime.datetime.now().isoformat()}
                        save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token=meta_gojek)

                        # Hapus otomatis pesan dalam 15 detik
                        context.job_queue.run_once(lambda ctx: ctx.bot.delete_message(chat.id, message_id), 15)
                    else:
                        query.edit_message_text("❌ Gagal: Token tidak ditemukan di Gist.")

            # Hapus antrian owner setelah diproses
            active_button_owner.pop(message_id, None)

        # --- LOGIKA TIMEZONE ---
        elif data == "set_timezone":
            keyboard = [
                [InlineKeyboardButton("WIB (Jakarta)", callback_data="tz_Asia/Jakarta")],
                [InlineKeyboardButton("WITA (Makassar)", callback_data="tz_Asia/Makassar")],
                [InlineKeyboardButton("WIT (Jayapura)", callback_data="tz_Asia/Jayapura")]
            ]
            query.edit_message_text(string.CHOOSE_TIMEZONE_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))

        elif data.startswith("tz_"):
            tz_selected = data.replace("tz_", "")
            user_timezone[str(user_id)] = tz_selected
            save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)
            query.edit_message_text(f"✅ Timezone diatur ke: `{tz_selected}`", parse_mode="Markdown")
            active_button_owner.pop(message_id, None)

    except Exception as e:
        logger.error(f"Error di button_handler: {e}", exc_info=True)
        query.edit_message_text(f"⚠️ **Error Internal:** `{str(e)}`", parse_mode="Markdown")

def register_token_handlers(dp):
    """Pendaftaran handler."""
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(button_handler, pattern=r"^(grab|gojek|set_timezone|tz_.*)$"))
