import time
from generator_jwt import generate_jwt
from token_validate_utils import validate_token  # gunakan fungsi validasi yang Anda punya

def handle_grab(query, user_id, tz_name, user_requests, user_blocked, user_timezone, token_usage, last_token, update, context):
    if check_limit(update, context, tz_name, user_id, user_requests, user_blocked, user_timezone):
        if not last_token:
            # User belum punya token → generate baru
            token = generate_jwt()
            is_valid, status_msg = validate_token(token)
            if is_valid:
                query.edit_message_text(f"✅ Selamat, Anda mendapat token aktif!\n{status_msg}\n\nToken: {token}", parse_mode="Markdown")
                last_token = {"service": "Grab", "time": datetime.datetime.now().isoformat(), "token": token}
            else:
                query.edit_message_text(f"⚠️ Token baru gagal validasi.\n{status_msg}", parse_mode="Markdown")
        else:
            # User sudah punya token → cek status token lama
            old_token = last_token.get("token")
            is_valid, status_msg = validate_token(old_token)
            if is_valid:
                # Token lama masih aktif → kirim token lama
                query.edit_message_text(f"ℹ️ Token lama Anda masih aktif.\n{status_msg}\n\nToken: {old_token}", parse_mode="Markdown")
            else:
                # Token lama revoke → buat token baru
                query.edit_message_text(f"⚠️ Token lama Anda sudah revoke.\nBot akan membuatkan yang baru...", parse_mode="Markdown")
                time.sleep(2)  # jeda 2 detik
                token = generate_jwt()
                is_valid, status_msg = validate_token(token)
                if is_valid:
                    query.edit_message_text(f"✅ Token baru berhasil dibuat!\n{status_msg}\n\nToken: {token}", parse_mode="Markdown")
                    last_token = {"service": "Grab", "time": datetime.datetime.now().isoformat(), "token": token}
                else:
                    query.edit_message_text(f"⚠️ Token baru gagal validasi.\n{status_msg}", parse_mode="Markdown")

    save_tmp(user_id, user_requests, user_blocked, user_timezone, token_usage, last_token)
    return last_token
