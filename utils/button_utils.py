# button_utils.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Konfigurasi global
BOT_USERNAME = "AmrosolBot"   # tanpa @
MAIN_GROUP_LINK = "https://t.me/AmrosoCommunity"

def get_group_only_buttons():
    """Return InlineKeyboardMarkup dengan tombol add-to-group dan link grup utama."""
    keyboard = [
        [InlineKeyboardButton("➕ Tambahkan bot ke grup", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("🌐 Join grup utama", url=MAIN_GROUP_LINK)]
    ]
    return InlineKeyboardMarkup(keyboard)

def send_group_only_message(update, text="⚠️ Command ini hanya bisa digunakan di dalam grup."):
    """Kirim pesan dengan tombol add-to-group + link grup utama."""
    reply_markup = get_group_only_buttons()
    if update.message:
        update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.edit_message_text(text, reply_markup=reply_markup)
