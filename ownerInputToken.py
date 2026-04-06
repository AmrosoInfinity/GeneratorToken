import json
import os
import logging
import base64
import datetime
from telegram.ext import CommandHandler

logger = logging.getLogger(__name__)
CONFIG_FILE = os.path.join("config", "njwt_config.json")

def decode_jwt_payload(token: str):
    """Decode payload JWT tanpa verifikasi signature untuk ambil metadata."""
    try:
        parts = token.split('.')
        if len(parts) != 3: return None
        payload_b64 = parts[1]
        payload_b64 += '=' * (4 - len(payload_b64) % 4) if len(payload_b64) % 4 else ''
        return json.loads(base64.urlsafe_b64decode(payload_b64).decode('utf-8'))
    except Exception as e:
        logger.error(f"Error decoding payload: {e}")
        return None

def input_token(update, context):
    owner_id = context.bot_data.get("owner_id")
    if int(update.effective_user.id) != int(owner_id): return

    if not context.args:
        update.message.reply_text("⚠️ Gunakan: `/inputToken ey...`", parse_mode='Markdown')
        return

    njwt_string = "".join(context.args).strip()
    payload = decode_jwt_payload(njwt_string)

    if not payload or not all(k in payload for k in ('iat', 'exp', 'sub')):
        update.message.reply_text("❌ Token tidak valid (Missing iat/exp/sub).")
        return

    try:
        os.makedirs("config", exist_ok=True)
        data = {
            "njwt": njwt_string,
            "iat": payload['iat'],
            "exp": payload['exp'],
            "sub": payload['sub'],
            "updated_at": int(datetime.datetime.utcnow().timestamp())
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)
        
        exp_time = datetime.datetime.fromtimestamp(payload['exp']).strftime('%Y-%m-%d %H:%M:%S')
        update.message.reply_text(
            f"✅ **Token Synced!**\n👤 **Sub:** `{payload['sub']}`\n📅 **Exp:** `{exp_time}`",
            parse_mode='Markdown'
        )
    except Exception as e:
        update.message.reply_text(f"❌ Gagal simpan: {e}")

def register_input_token(dp, owner_id: int):
    dp.bot_data["owner_id"] = owner_id
    dp.add_handler(CommandHandler("inputToken", input_token))
