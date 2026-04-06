import json
import os
import re
from telegram.ext import CommandHandler

CONFIG_FILE = "njwt_config.json"
OWNER_ID = int(os.environ.get("BOT_OWNER_ID", "0"))

def sanitize_token(raw: str) -> str:
    """Bersihkan token dari karakter yang tidak valid (Base64URL + titik)."""
    cleaned = raw.strip()
    return re.sub(r"[^A-Za-z0-9\-\._]", "", cleaned)

def input_token(update, context):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        update.message.reply_text("⚠️ Hanya owner bot yang bisa menggunakan perintah ini.")
        return

    if not context.args:
        update.message.reply_text("Gunakan format: /inputToken <njwt_string>")
        return

    raw_token = " ".join(context.args)
    njwt_string = sanitize_token(raw_token)

    # Simpan ke file config
    config = {"njwt": njwt_string}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

    update.message.reply_text("✅ String njwt berhasil disimpan.")

def load_njwt():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("njwt")
    return None

def register_input_token(dp):
    dp.add_handler(CommandHandler("inputToken", input_token))
