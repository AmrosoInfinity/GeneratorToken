import time
import datetime
from double_jwt.generator_jwt import generate_jwt
from utils.token_validate_utils import validate_token, check_limit, save_tmp

def handle_grab(query, user_id, tz_name, user_requests, user_blocked, user_timezone,
                token_usage, last_token, update, context):
    if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
        if not last_token:
            token = generate_jwt()
            is_valid, status_msg = validate_token(token)
            if is_valid:
                query.edit_message_text(
                    f"✅ Selamat, Anda mendapat token aktif!\n{status_msg}\n\n```{token}```",
                    parse_mode="Markdown"
                )
                # Hapus pesan setelah 5 detik
                context.job_queue.run_once(
                    lambda ctx: ctx.bot.delete_message(query.message.chat_id, query.message.message_id),
                    5
                )
                last_token = {"service": "Grab", "time": datetime.datetime.now().isoformat(), "token": token}
            else:
                query.edit_message_text(f"⚠️ Token baru gagal validasi.\n{status_msg}", parse_mode="Markdown")
        else:
            old_token = last_token.get("token")
            is_valid, status_msg = validate_token(old_token)
            if is_valid:
                query.edit_message_text(
                    f"ℹ️ Token lama Anda masih aktif.\n{status_msg}\n\n```{old_token}```",
                    parse_mode="Markdown"
                )
                context.job_queue.run_once(
                    lambda ctx: ctx.bot.delete_message(query.message.chat_id, query.message.message_id),
                    5
                )
            else:
                query.edit_message_text(
                    f"⚠️ Token lama Anda sudah revoke.\nBot akan membuatkan yang baru...",
                    parse_mode="Markdown"
                )
                time.sleep(2)
                token = generate_jwt()
                is_valid, status_msg = validate_token(token)
                if is_valid:
                    query.edit_message_text(
                        f"✅ Token baru berhasil dibuat!\n{status_msg}\n\n```{token}```",
                        parse_mode="Markdown"
                    )
                    context.job_queue.run_once(
                        lambda ctx: ctx.bot.delete_message(query.message.chat_id, query.message.message_id),
                        5
                    )
                    last_token = {"service": "Grab", "time": datetime.datetime.now().isoformat(), "token": token}
                else:
                    query.edit_message_text(f"⚠️ Token baru gagal validasi.\n{status_msg}", parse_mode="Markdown")

    save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)
    return last_token
