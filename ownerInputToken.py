import json
import os
import logging
import base64
import datetime
from telegram.ext import CommandHandler

logger = logging.getLogger(__name__)
CONFIG_FILE = os.path.join("config", "njwt_config.json")

def decode_jwt_payload(token: str):
    """Decode payload JWT tanpa verifikasi signature."""
    try:
        parts = token.split('.')
        if len(parts) != 3: return None
        
        payload_b64 = parts[1]
        # Fix padding base64
        payload_b64 += '=' * (4 - len(payload_b64) % 4) if len(payload_b64) % 4 else ''
        
        payload_json = base64.urlsafe_b64decode(payload_b64).decode('utf-8')
        return json.loads(payload_json)
    except Exception as e:
        logger.error(f"Gagal decode payload: {e}")
        return None

def input_token(update, context):
    owner_id = context.bot_data.get("owner_id")
    if int(update.effective_user.id) != int(owner_id): return

    if not context.args:
        update.message.reply_text("❌ Mana tokennya? Format: `/inputToken ey...`", parse_mode='Markdown')
        return

    njwt_string = "".join(context.args).strip()
    payload = decode_jwt_payload(njwt_string)

    # Validasi field wajib
    if not payload or not all(k in payload for k in ('iat', 'exp', 'sub')):
        update.message.reply_text("❌ Token tidak valid! Field `iat`, `exp`, atau `sub` tidak ditemukan.", parse_mode='Markdown')
        return

    try:
        os.makedirs("config", exist_ok=True)
        data_to_save = {
            "njwt": njwt_string,
            "iat": payload['iat'],
            "exp": payload['exp'],
            "sub": payload['sub'], # <--- Sinkronisasi SUB
            "updated_at": int(datetime.datetime.utcnow().timestamp())
        }
        
        with open(CONFIG_FILE, "w") as f:
            json.dump(data_to_save, f, indent=4)
        
        expired_dt = datetime.datetime.fromtimestamp(payload['exp']).strftime('%Y-%m-%d %H:%M:%S')
        update.message.reply_text(
            f"✅ **Double Layer Synced!**\n\n"
            f"👤 **Sub:** `{payload['sub']}`\n"
            f"📅 **Exp:** `{expired_dt}`\n"
            f"🛠 **Status:** Ready to Generate.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Gagal simpan config: {e}")
        update.message.reply_text(f"❌ Gagal tulis file: {e}")

def register_input_token(dp, owner_id: int):
    dp.bot_data["owner_id"] = owner_id
    dp.add_handler(CommandHandler("inputToken", input_token))
