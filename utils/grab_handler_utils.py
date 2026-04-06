import time
import datetime
import logging
from double_jwt.generator_jwt import generate_jwt
from utils.token_validate_utils import check_grab_token_status, check_limit, save_tmp

logger = logging.getLogger(__name__)

def handle_grab(query, user_id, tz_name, user_requests, user_blocked, user_timezone,
                token_usage, last_token, update, context):
    
    if not check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
        return last_token

    def send_and_delete(msg: str):
        query.edit_message_text(msg, parse_mode="Markdown")
        context.job_queue.run_once(
            lambda ctx: ctx.bot.delete_message(query.message.chat_id, query.message.message_id), 10
        )

    # Pengecekan Validitas Token
    need_new = False
    if not last_token or "token" not in last_token:
        need_new = True
    else:
        is_valid, status_msg = check_grab_token_status(last_token["token"])
        if is_valid:
            send_and_delete(f"ℹ️ **Token Aktif**\n{status_msg}\n\n```{last_token['token']}```")
            return last_token
        need_new = True

    if need_new:
        try:
            query.edit_message_text("🔄 Sedang memproses token baru...", parse_mode="Markdown")
            new_jwt = generate_jwt()
            is_valid, status_msg = check_grab_token_status(new_jwt)
            
            if is_valid:
                send_and_delete(f"✅ **Token Berhasil Dibuat**\n{status_msg}\n\n```{new_jwt}```")
                last_token = {"service": "Grab", "time": datetime.datetime.now().isoformat(), "token": new_jwt}
            else:
                query.edit_message_text(f"❌ **Validasi Gagal**\n{status_msg}", parse_mode="Markdown")
        except Exception as e:
            query.edit_message_text(f"⚠️ **Error:** `{str(e)}`", parse_mode="Markdown")

    save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)
    return last_token
