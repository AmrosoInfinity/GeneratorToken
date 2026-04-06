import datetime
import logging
import traceback
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

# Import utils
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
    """Menampilkan menu utama pilihan Grab atau Gojek."""
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

    # 2. Load Data User (Pastikan menangkap 5 variabel sesuai return load_tmp)
    try:
        loaded = load_tmp(user_id)
        if len(loaded) != 5:
            raise ValueError(f"Data tmp tidak valid (Expected 5, got {len(loaded)})")
        user_requests, user_blocked, user_timezone, token_usage, last_token = loaded
    except Exception as e:
        logger.error(f"Gagal load data: {e}")
        query.edit_message_text(f"⚠️ **Gagal Load Data:** `{str(e)}`", parse_mode="Markdown")
        return

    # 3. Logika Utama Berdasarkan Data Tombol
    try:
        # A. Kelompok Layanan (Grab/Gojek)
        if data in ["grab", "gojek"]:
            if chat.type not in ["group", "supergroup"]:
                send_group_only_message(update, "⚠️ Fitur ini hanya untuk di dalam grup.")
                return

            tz_name = user_timezone.get(str(user_id))
            if not tz_name:
                keyboard = [[InlineKeyboardButton("Set Timezone 🌍", callback_data="set_timezone")]]
                msg = query.edit_message_text(string.NEED_TIMEZONE_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))
                active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
                set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)
                return

            # --- EKSEKUSI GRAB ---
            if data == "grab":
                # Grab tetap menggunakan handler eksternal karena butuh sinkronisasi iat/exp
                last_token = handle_grab(query, user_id, tz_name, user_requests, user_blocked, user_timezone, token_usage, last_token, update, context)

            # --- EKSEKUSI GOJEK (Zero-Storage Fetch) ---
            elif data == "gojek":
                if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                    query.edit_message_text("📡 *Fetching Gist...*", parse_mode="Markdown")
                    
                    url_gojek = "https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek"
                    tokens = fetch_tokens(url_gojek)
                    
                    if tokens:
                        token_gist = tokens[0].strip()
                        
                        # Langsung tampilkan (Gunakan fallback jika string.py bermasalah)
                        try:
                            pesan = string.TOKEN_GOJEK.format(token=f"```{token_gist}```")
                        except:
                            pesan = f"🚀 **Token Gojek (Gist):**\n\n```{token_gist}```\n\n_Hapus otomatis 15 detik._"
                        
                        query.edit_message_text(pesan, parse_mode="Markdown")
                        
                        # Update metadata TANPA menyimpan isi token gist ke JSON
                        # Kita hanya simpan info kapan dia request terakhir
                        gojek_meta = {"service": "Gojek", "time": datetime.datetime.now().isoformat()}
                        save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token=gojek_meta)

                        # Auto-delete
                        context.job_queue.run_once(
                            lambda ctx: ctx.bot.delete_message(chat.id, message_id), 15
                        )
                    else:
                        query.edit_message_text("❌ Gagal: Gist kosong atau tidak dapat dijangkau.")

            # Bersihkan owner state
            active_button_owner.pop(message_id, None)

        # B. Logika Timezone
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
            query.edit_message_text(string.TIMEZONE_SET_SUCCESS.format(tz=tz_selected), parse_mode="Markdown")
            active_button_owner.pop(message_id, None)

    except Exception as e:
        # Menampilkan traceback lengkap di log GitHub dan pesan singkat di Telegram
        err_msg = traceback.format_exc()
        logger.error(f"CRITICAL ERROR: {err_msg}")
        
        # Kirim pesan error ke user agar tidak bingung
        try:
            query.edit_message_text(f"⚠️ **Internal Error:** `{str(e)}`", parse_mode="Markdown")
        except:
            pass

def register_token_handlers(dp):
    """Pendaftaran handler untuk bot.py"""
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(
        button_handler, 
        pattern=r"^(grab|gojek|set_timezone|tz_.*)$"
    ))
