import datetime
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

# Import utils sesuai struktur proyek
from utils.token_validate_utils import check_limit, fetch_tokens, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message
from utils.button_ownership_utils import is_button_owner
from utils.chat_timer_utils import set_expire_timer

# Import handler Grab yang sudah kita sinkronkan iat/exp/sub
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

    # Registrasi owner tombol
    active_button_owner[msg.message_id] = {
        "owner": update.effective_user.id,
        "expired": False
    }
    
    # Set timer otomatis hapus pesan menu jika diabaikan
    set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)

def button_handler(update, context):
    """Handler utama untuk semua klik tombol di menu token."""
    query = update.callback_query
    chat = update.effective_chat
    user_id = query.from_user.id
    data = query.data
    message_id = query.message.message_id

    # Hilangkan icon loading di Telegram
    query.answer()

    state = active_button_owner.get(message_id)

    # 1. Cek kepemilikan tombol (Hanya yang panggil /token yang bisa klik)
    if not is_button_owner(context, chat, user_id, state, query):
        return

    # 2. Load data user secara aman
    tmp_data = load_tmp(user_id)
    if not tmp_data or len(tmp_data) < 5:
        user_requests, user_blocked, user_timezone, token_usage, last_token = {}, {}, {}, {}, {}
    else:
        user_requests, user_blocked, user_timezone, token_usage, last_token = tmp_data

    # 3. Logika Pilihan Layanan
    if data in ["grab", "gojek"]:
        # Pastikan hanya di grup
        if chat.type not in ["group", "supergroup"]:
            send_group_only_message(update, "⚠️ Command ini hanya bisa digunakan di dalam grup.")
            return

        # Cek apakah user sudah set timezone
        if str(user_id) not in user_timezone:
            keyboard = [[InlineKeyboardButton("Set Timezone 🌍", callback_data="set_timezone")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            msg = query.edit_message_text(string.NEED_TIMEZONE_TEXT, reply_markup=reply_markup)
            
            # Update state untuk tombol baru ini
            active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
            set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)
            return

        tz_name = user_timezone.get(str(user_id))

        # --- EKSEKUSI GRAB ---
        if data == "grab":
            last_token = handle_grab(
                query, user_id, tz_name,
                user_requests, user_blocked, user_timezone,
                token_usage, last_token, update, context
            )

        # --- EKSEKUSI GOJEK ---
        elif data == "gojek":
            if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                url_gojek = "https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek"
                tokens = fetch_tokens(url_gojek)
                if tokens:
                    token = tokens[0]
                    query.edit_message_text(
                        string.TOKEN_GOJEK.format(token=f"```{token}```"),
                        parse_mode="Markdown"
                    )
                    # Hapus pesan otomatis (10 detik)
                    context.job_queue.run_once(
                        lambda ctx: ctx.bot.delete_message(query.message.chat_id, query.message.message_id),
                        10
                    )
                    last_token = {
                        "service": "Gojek", 
                        "time": datetime.datetime.now().isoformat(), 
                        "token": token
                    }
                else:
                    query.edit_message_text(string.TOKEN_NOT_FOUND.format(service="Gojek"), parse_mode="Markdown")
            
            # Simpan state untuk Gojek
            save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)

        # Hapus state owner setelah eksekusi layanan selesai
        active_button_owner.pop(message_id, None)

    # --- LOGIKA SET TIMEZONE ---
    elif data == "set_timezone":
        keyboard = [
            [InlineKeyboardButton("WIB (Jakarta)", callback_data="tz_Asia/Jakarta")],
            [InlineKeyboardButton("WITA (Makassar)", callback_data="tz_Asia/Makassar")],
            [InlineKeyboardButton("WIT (Jayapura)", callback_data="tz_Asia/Jayapura")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = query.edit_message_text(string.CHOOSE_TIMEZONE_TEXT, reply_markup=reply_markup)
        
        active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
        set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)

    elif data.startswith("tz_"):
        tz_selected = data.replace("tz_", "")
        user_timezone[str(user_id)] = tz_selected
        
        # Simpan perubahan timezone
        save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)
        query.edit_message_text(string.TIMEZONE_SET_SUCCESS.format(tz=tz_selected), parse_mode="Markdown")
        
        # Bersihkan state
        active_button_owner.pop(message_id, None)

def register_token_handlers(dp):
    """Pendaftaran handler untuk bot.py"""
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(
        button_handler, 
        pattern=r"^(grab|gojek|set_timezone|tz_.*)$"
    ))
