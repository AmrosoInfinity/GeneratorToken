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
    token = update.message.text
    token_length = len(token)

    url = "https://api.grab.com/grabid/v1/me/status"
    headers = {
        "Authorization": token  # sama persis dengan curl di Termux
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        status_code = resp.status_code
        response_text = resp.text

        if status_code == 200:
            reply = (
                "✅ Token valid.\n"
                f"🔢 Panjang token: {token_length} karakter\n"
                f"📡 Status code: {status_code}\n"
                f"📄 Cuplikan response:\n{response_text[:300]}..."
            )
        else:
            reply = (
                "❌ Token tidak valid.\n"
                f"🔢 Panjang token: {token_length} karakter\n"
                f"📡 Status code: {status_code}\n"
                f"📄 Response:\n{response_text[:200]}..."
            )

        update.message.reply_text(reply)

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
