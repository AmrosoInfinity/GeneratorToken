import json
import os
import re
from telegram.ext import CommandHandler

# Simpan config di root/config/
CONFIG_FILE = os.path.join("config", "njwt_config.json")

def sanitize_token(raw: str) -> str:
    cleaned = raw.strip()
    return re.sub(r"[^A-Za-z0-9\-\._]", "", cleaned)

def input_token(update, context):
    owner_id = context.bot_data.get("owner_id", 0)
    user_id = update.effective_user.id

    if user_id != owner_id:
        update.message.reply_text("⚠️ Hanya owner bot yang bisa menggunakan perintah ini.")
        return

    if not context.args:
        update.message.reply_text("Gunakan format: /inputToken <njwt_string>")
        return

    raw_token = " ".join(context.args)
    njwt_string = sanitize_token(raw_token)

    config = {"njwt": njwt_string}
    os.makedirs("config", exist_ok=True)  # pastikan folder config ada
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

    update.message.reply_text("✅ String njwt berhasil disimpan.")

def load_njwt():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("njwt")
    return None

def register_input_token(dp, owner_id=None):
    if owner_id is not None:
        dp.bot_data["owner_id"] = owner_id
    dp.add_handler(CommandHandler("inputToken", input_token))
