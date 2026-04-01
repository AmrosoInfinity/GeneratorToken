from telegram.ext import MessageHandler, Filters
from utils.suspect_user import record_token_request, is_suspect, get_all_suspects

def monitor_token_requests(update, context):
    user_id = update.effective_user.id
    text = update.message.text or ""

    # deteksi jika user minta token (misalnya mengandung kata 'token')
    if "token" in text.lower():
        record_token_request(user_id)

        if is_suspect(user_id):
            owner_id = context.bot_data.get("owner_id")
            suspects = get_all_suspects()
            if owner_id:
                try:
                    context.bot.send_message(
                        chat_id=owner_id,
                        text=f"⚠️ User mencurigakan terdeteksi:\n{suspects}"
                    )
                except Exception:
                    pass

def register_suspect(dp, owner_id: int):
    dp.bot_data["owner_id"] = owner_id
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, monitor_token_requests))
