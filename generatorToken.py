from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from zoneinfo import ZoneInfo
from token_utils import check_limit, fetch_tokens, user_timezone, save_tmp, load_tmp

def token_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Grab", callback_data="grab"),
         InlineKeyboardButton("Gojek", callback_data="gojek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("📌 Pilih token:", reply_markup=reply_markup)

def button_handler(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data in ["grab", "gojek"]:
        load_tmp()
        if user_id not in user_timezone:
            keyboard = [[InlineKeyboardButton("Set Timezone", callback_data="set_timezone")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text("⚠️ Anda belum set timezone. Silakan pilih:", reply_markup=reply_markup)
            return
        tz_name = user_timezone[user_id]
        if data == "grab":
            if check_limit(update, context, tz_name):
                tokens = fetch_tokens("https://gist.githubusercontent.com/.../Grab")
                query.edit_message_text(f"=== Token Grab ===\n```{tokens[0]}```", parse_mode="Markdown")
        else:
            if check_limit(update, context, tz_name):
                tokens = fetch_tokens("https://gist.githubusercontent.com/.../Gojek")
                query.edit_message_text(f"=== Token Gojek ===\n```{tokens[0]}```", parse_mode="Markdown")

    elif data == "set_timezone":
        query.edit_message_text("🕒 Kirim timezone Anda, contoh: `Asia/Jayapura`")

def set_timezone(update, context):
    user_id = update.effective_user.id
    tz_name = update.message.text.strip()
    try:
        ZoneInfo(tz_name)  # validasi
        load_tmp()
        user_timezone[user_id] = tz_name
        save_tmp()
        update.message.reply_text(f"✅ Timezone Anda diset ke {tz_name}. Sekarang bisa request token.")
    except Exception:
        update.message.reply_text("❌ Timezone tidak valid. Gunakan format seperti `Asia/Jakarta`.")

def register_token_menu(dp):
    dp.add_handler(CommandHandler("token", token_menu))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, set_timezone))

# Alias agar bot.py tetap bisa pakai nama lama
def register_token_handlers(dp):
    register_token_menu(dp)
