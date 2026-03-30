import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters
from utils.remove_token_user import remove_user_token_message

def checktoken_command(update, context):
    """
    Handler untuk command /checktoken.
    Menampilkan tombol agar user bisa paste token.
    """
    keyboard = [[InlineKeyboardButton("Masukkan Token", switch_inline_query_current_chat="")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Silakan tekan tombol di bawah lalu paste token Anda.\n"
        "Pesan token akan otomatis dihapus setelah dicek.",
        reply_markup=reply_markup
    )

def checktoken_handler(update, context):
    """
    Handler untuk pesan token user.
    Bot akan cek ke Grab API lalu hapus pesan token.
    """
    token = update.message.text.strip()
    url = "https://api.grab.com/grabid/v1/me/status"

    # Samakan header dengan curl agar hasil identik
    headers = {
        "Authorization": token,          # tanpa Bearer karena pakai njwt
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "curl/7.68.0"      # sesuaikan dengan versi curl di Termux
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            update.message.reply_text("✅ Token valid.\nResponse:\n" + resp.text)
        else:
            update.message.reply_text(f"❌ Token tidak valid. Status code: {resp.status_code}")
    except Exception as e:
        update.message.reply_text(f"⚠️ Error saat cek token: {e}")

    # hapus pesan token user agar tidak tersisa di chat
    remove_user_token_message(context, update.message.chat_id, update.message.message_id)

def register_checktoken(dp):
    """
    Registrasi handler checktoken ke dispatcher utama.
    """
    dp.add_handler(CommandHandler("checktoken", checktoken_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, checktoken_handler))
