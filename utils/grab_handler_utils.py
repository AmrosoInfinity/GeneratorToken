import time
import datetime
import logging
from double_jwt.generator_jwt import generate_jwt
from utils.token_validate_utils import check_grab_token_status, check_limit, save_tmp

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def handle_grab(query, user_id, tz_name, user_requests, user_blocked, user_timezone,
                token_usage, last_token, update, context):
    # Cek limit request user
    if not check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
        return last_token

    def send_and_delete(msg: str):
        """Helper untuk kirim pesan lalu hapus setelah 5 detik."""
        query.edit_message_text(msg, parse_mode="Markdown")
        context.job_queue.run_once(
            lambda ctx: ctx.bot.delete_message(query.message.chat_id, query.message.message_id),
            5
        )

    # Jika belum ada token tersimpan
    if not last_token:
        token = generate_jwt()
        logger.info(f"[GrabHandler] Token baru dibuat untuk user {user_id} pada {datetime.datetime.utcnow().isoformat()}")
        logger.debug(f"[GrabHandler] Token baru (awal 80 char): {token[:80]}...")
        is_valid, status_msg = check_grab_token_status(token)
        if is_valid:
            send_and_delete(f"✅ Selamat, Anda mendapat token aktif!\n{status_msg}\n\n```{token}```")
            last_token = {"service": "Grab", "time": datetime.datetime.now().isoformat(), "token": token}
        else:
            query.edit_message_text(f"⚠️ Token baru gagal validasi.\n{status_msg}", parse_mode="Markdown")
    else:
        old_token = last_token.get("token")
        logger.info(f"[GrabHandler] Mengecek token lama untuk user {user_id}")
        is_valid, status_msg = check_grab_token_status(old_token)
        if is_valid:
            send_and_delete(f"ℹ️ Token lama Anda masih aktif.\n{status_msg}\n\n```{old_token}```")
        else:
            query.edit_message_text("⚠️ Token lama sudah revoke.\nBot akan membuatkan yang baru...", parse_mode="Markdown")
            time.sleep(2)
            token = generate_jwt()
            logger.info(f"[GrabHandler] Token baru dibuat untuk user {user_id} pada {datetime.datetime.utcnow().isoformat()}")
            logger.debug(f"[GrabHandler] Token baru (awal 80 char): {token[:80]}...")
            is_valid, status_msg = check_grab_token_status(token)
            if is_valid:
                send_and_delete(f"✅ Token baru berhasil dibuat!\n{status_msg}\n\n```{token}```")
                last_token = {"service": "Grab", "time": datetime.datetime.now().isoformat(), "token": token}
            else:
                query.edit_message_text(f"⚠️ Token baru gagal validasi.\n{status_msg}", parse_mode="Markdown")

    # Simpan state user
    save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)
    return last_token
