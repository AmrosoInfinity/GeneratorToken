import json
import os
import re
from telegram.ext import CommandHandler

CONFIG_FILE = os.path.join("config", "njwt_config.json")

def sanitize_token(raw: str) -> str:
    """Bersihkan string token dari karakter ilegal."""
    return re.sub(r"[^A-Za-z0-9\-\._]", "", raw.strip())

def input_token(update, context):
    owner_id = context.bot_data["owner_id"]  # selalu ada, wajib diisi dari bot.py
    user_id = update.effective_user.id

    if user_id != owner_id:
        update.message.reply_text("⚠️ Hanya owner bot yang bisa menggunakan perintah ini.")
        return

    if not context.args:
        update.message.reply_text("Gunakan format: /inputToken <njwt_string>")
        return

    njwt_string = sanitize_token(" ".join(context.args))
    os.makedirs("config", exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"njwt": njwt_string}, f)

    update.message.reply_text("✅ String njwt berhasil disimpan. Sekarang gunakan /token untuk generate JWT.")

def register_input_token(dp, owner_id: int):
    """Register handler /inputToken dan simpan owner_id ke bot_data."""
    dp.bot_data["owner_id"] = owner_id
    dp.add_handler(CommandHandler("inputToken", input_token))
