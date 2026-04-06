import datetime
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

# Import utils sesuai struktur proyekmu
from utils.token_validate_utils import check_limit, fetch_tokens, save_tmp, load_tmp
from support import string
from utils.button_group_utils import send_group_only_message
from utils.button_ownership_utils import is_button_owner
from utils.chat_timer_utils import set_expire_timer

# Import handler Grab yang sudah kita sinkronkan iat/exp/sub-nya
from utils.grab_handler_utils import handle_grab

logger = logging.getLogger(__name__)

# Mapping message_id -> {owner: user_id, expired: bool}
active_button_owner = {}

# === Menu Utama Token ===
def token_menu(update, context):
    """Menampilkan pilihan Grab atau Gojek."""
    keyboard = [
        [InlineKeyboardButton("Grab 🟢", callback_data="btn_grab"),
         InlineKeyboardButton("Gojek 🚀", callback_data="btn_gojek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Kirim menu
    msg = update.message.reply_text(string.TOKEN_MENU_TEXT, reply_markup=reply_markup)

    # Registrasi owner tombol agar tidak diklik orang lain
    active_button_owner[msg.message_id] = {
        "owner": update.effective_user.id,
        "expired": False
    }
    
    # Set timer agar pesan otomatis terhapus jika diabaikan
    set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)

# === Handler Tombol (Callback) ===
def button_handler(update, context):
    query = update.callback_query
    chat = update.effective_chat
    user_id = query.from_user.id
    data = query.data
    message_id = query.message.message_id

    # 1. Pastikan query dijawab agar loading di HP user hilang
    query.answer()

    # 2. Cek Kepemilikan Tombol
    state = active_button_owner.get(message_id)
    if not is_button_owner(context, chat, user_id, state, query):
        return

    # 3. Safe Loading Data User
    # Pastikan unpacking tidak error jika load_tmp return None
    tmp_data = load_tmp(user_id)
    if not tmp_data or len(tmp_data) < 5:
        user_requests, user_blocked, user_timezone, token_usage, last_token = {}, {}, {}, {}, {}
    else:
        user_requests, user_blocked, user_timezone, token_usage, last_token = tmp_data

    # --- LOGIKA GRAB & GOJEK ---
    if data in ["btn_grab", "btn_gojek"]:
        if chat.type not in ["group", "supergroup"]:
            send_group_only_message(update, "⚠️ Command ini hanya bisa digunakan di dalam grup.")
            return

        # Cek Timezone
        if str(user_id) not in user_timezone:
            keyboard = [[InlineKeyboardButton("Set Timezone 🌍", callback_data="set_timezone")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            msg = query.edit_message_text(string.NEED_TIMEZONE_TEXT, reply_markup=reply_markup)
            
            active_button_owner[msg.message_id] = {"owner": user_id, "expired": False}
            set_expire_timer(context, msg.chat_id, msg.message_id, active_button_owner)
            return

        tz_name = user_timezone.get(str(user_id))

        # === EKSEKUSI GRAB (Double Layer JWT) ===
        if data == "btn_grab":
            last_token = handle_grab(
                query, user_id, tz_name,
                user_requests, user_blocked, user_timezone,
                token_usage, last_token, update, context
            )

        # === EKSEKUSI GOJEK (Gist Based) ===
        elif data == "btn_gojek":
            if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                # URL Gist Gojek kamu
                url_gojek = "https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek"
                tokens = fetch_tokens(url_gojek)
                
                if tokens:
                    token = tokens[0]
                    query.edit_message_text(
                        string.TOKEN_GOJEK.format(token=f"```{token}```"),
                        parse_mode="Markdown"
                    )
                    # Hapus pesan otomatis setelah 10 detik agar sempat copy
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
            
            # Simpan hasil ke .tmp
            save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)

        # Hapus owner state jika proses selesai
        active_button_owner.pop(message_id, None)

    # --- LOGIKA SET TIMEZONE ---
    elif data == "set_timezone":
        keyboard = [
            [InlineKeyboardButton("WIB (Jakarta)", callback_data="tz_Asia/Jakarta")],
            [InlineKeyboardButton("WITA (Makassar)", callback_data="tz_Asia/Makassar")],
            [InlineKeyboardButton("WIT (Jayapura)", callback_data="tz_Asia/Jayapura")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(string.CHOOSE_TIMEZONE_TEXT, reply_markup=reply_markup)

    elif data.startswith("tz_"):
        tz_selected = data.replace("tz_", "")
        user_timezone[str(user_id)] = tz_selected
        
        save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)
        query.edit_message_text(string.TIMEZONE_SET_SUCCESS.format(tz=tz_selected), parse_mode="Markdown")
        
        # Hapus state
        active_button_owner.pop(message_id, None)

# === Registrasi Handler ===
def register_token_handlers(dp):
    """Mendaftarkan handler ke dispatcher bot utama."""
    dp.add_handler(CommandHandler("token", token_menu))
    
    # Gunakan Regex Pattern agar Callback ini HANYA merespon tombol menu token
    dp.add_handler(CallbackQueryHandler(
        button_handler, 
        pattern=r"^(btn_grab|btn_gojek|set_timezone|tz_.*)$"
    ))
        # === Grab ===
        if data == "grab":
            last_token = handle_grab(
                query, user_id, tz_name,
                user_requests, user_blocked, user_timezone,
                token_usage, last_token, update, context
            )

        # === Gojek ===
        elif data == "gojek":
            if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
                tokens = fetch_tokens("https://gist.githubusercontent.com/AmrosoInfinity/aebd0ba65e12a20b062c291c68714d8a/raw/Gojek")
                if tokens:
                    token = tokens[0]
                    query.edit_message_text(
                        string.TOKEN_GOJEK.format(token=f"```{token}```"),
                        parse_mode="Markdown"
                    )
                    # Hapus pesan setelah 5 detik
                    context.job_queue.run_once(
                        lambda ctx: ctx.bot.delete_message(query.message.chat_id, query.message.message_id),
                        5
                    )
                    last_token = {"service": "Gojek", "time": datetime.datetime.now().isoformat(), "token": token}
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
