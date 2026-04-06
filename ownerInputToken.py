import json
import os
import re
import logging
from telegram.ext import CommandHandler

logger = logging.getLogger(__name__)
CONFIG_FILE = os.path.join("config", "njwt_config.json")

def sanitize_token(raw: str) -> str:
    """Membersihkan token dari spasi atau karakter ilegal."""
    return raw.strip()

def input_token(update, context):
    owner_id = context.bot_data.get("owner_id")
    user_id = update.effective_user.id

    # Validasi Owner (Integer comparison)
    if owner_id is None or int(user_id) != int(owner_id):
        update.message.reply_text("⚠️ Akses ditolak. Hanya owner yang bisa input token.")
        return

    # Validasi Argumen (Harus ada token setelah command)
    if not context.args:
        update.message.reply_text("❌ Format salah! Gunakan: `/inputToken ey....` ", parse_mode='Markdown')
        return

    # Menggabungkan argumen jika token terpisah spasi, lalu bersihkan
    njwt_string = sanitize_token(" ".join(context.args))
    
    try:
        os.makedirs("config", exist_ok=True)
        
        # LOGIKA REPLACE: Mode 'w' akan menghapus isi lama dan menulis yang baru
        with open(CONFIG_FILE, "w") as f:
            json.dump({"njwt": njwt_string}, f, indent=4)
        
        logger.info(f"Token njwt berhasil diperbarui oleh {user_id}")
        update.message.reply_text("✅ **Token Berhasil Digantikan!**\n\nData lama telah dihapus dan diganti dengan token baru. Gunakan `/token` untuk generate JWT.", parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Gagal menulis file config: {e}")
        update.message.reply_text(f"❌ Terjadi kesalahan sistem saat menyimpan token: {e}")

def register_input_token(dp, owner_id: int):
    """Mendaftarkan handler ke dispatcher."""
    dp.bot_data["owner_id"] = owner_id
    # Daftarkan variasi huruf besar/kecil agar lebih fleksibel
    dp.add_handler(CommandHandler("inputToken", input_token))
    dp.add_handler(CommandHandler("inputtoken", input_token))
