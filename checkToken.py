import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters
from utils.remove_token_user import remove_user_token_message

def checktoken_command(update, context):
    # tampilkan tombol input agar user bisa paste token
    keyboard = [[InlineKeyboardButton("Masukkan Token", switch_inline_query_current_chat="")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Silakan tekan tombol di bawah lalu paste token Anda.\n"
        "Pesan token akan otomatis dihapus setelah dicek.",
        reply_markup=reply_markup
    )

def checktoken_handler(update, context):
    token = update.message.text.strip()
    url = "https://api.grab.com/grabid/v1/me/status"
    headers = {"Authorization": token}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            update.message.reply_text("✅ Token valid.")
        else:
            update.message.reply_text(f"❌ Token tidak valid. Status code: {resp.status_code}")
    except Exception as e:
        update.message.reply_text(f"⚠️ Error saat cek token: {e}")

    # hapus pesan token user
    remove_user_token_message(context, update.message.chat_id, update.message.message_id)

def register_checktoken(dp):
    dp.add_handler(CommandHandler("checktoken", checktoken_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, checktoken_handler))
