import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from utils.remove_token_user import remove_user_token_message
from utils.button_ownership_utils import is_button_owner
from utils.token_validate_utils import validate_token
from utils.checktoken_abuse_utils import record_check, should_block, warn_or_suspect
from support.string import CHECKTOKEN_PROMPT_MSG

def checktoken_command(update, context):
    user_id = update.effective_user.id
    owner_id = context.bot_data.get("owner_id")

    # cek apakah user harus diblokir
    if should_block(user_id, owner_id):
        status = warn_or_suspect(user_id, owner_id, context.bot)
        if status == "warn":
            update.message.reply_text(
                "⚠️ Anda terlalu sering melakukan pengecekan token. Tunggu 12 jam sebelum mencoba lagi."
            )
            return
        elif status == "suspect":
            update.message.reply_text("🚫 Akses checktoken Anda diblokir sementara.")
            # jika user admin/owner grup → bot keluar
            chat = update.effective_chat
            if chat.type in ["group", "supergroup"]:
                admins = context.bot.get_chat_administrators(chat.id)
                for admin in admins:
                    if admin.user.id == user_id:
                        try:
                            context.bot.leave_chat(chat.id)
                        except Exception:
                            pass
                        break
            return

    sent = update.message.reply_text(
        CHECKTOKEN_PROMPT_MSG,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Masukkan Token", callback_data="checktoken")]]
        )
    )
    context.user_data["checktoken_state"] = {
        "owner": user_id,
        "prompt_id": sent.message_id,
        "expired": False
    }

    # Timer 30 detik untuk hapus prompt jika tidak ada interaksi
    def expire_prompt():
        state = context.user_data.get("checktoken_state")
        if state and not state["expired"] and state["prompt_id"] == sent.message_id:
            try:
                context.bot.delete_message(update.effective_chat.id, sent.message_id)
            except Exception:
                pass
            state["expired"] = True
            context.user_data.pop("checktoken_state", None)

    threading.Timer(30, expire_prompt).start()

def checktoken_button(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    chat = update.effective_chat
    state = context.user_data.get("checktoken_state")

    if not is_button_owner(context, chat, user_id, state, query):
        return

    query.answer()
    query.edit_message_text("Silakan kirim token Anda di chat.")

def checktoken_handler(update, context):
    state = context.user_data.get("checktoken_state")
    if not state or state.get("expired"):
        return

    raw_text = update.message.text
    token = raw_text.replace("@AmrosolBot", "").replace("*", "").strip()

    is_valid, message = validate_token(token)
    update.message.reply_text(message)

    # hapus pesan token user agar tidak tersimpan
    remove_user_token_message(context, update.message.chat_id, update.message.message_id)

    # catat aktivitas hanya kalau token valid dari bot
    record_check(update.effective_user.id, is_valid)

    # hapus prompt awal
    try:
        context.bot.delete_message(update.message.chat_id, state["prompt_id"])
    except Exception:
        pass

    context.user_data.pop("checktoken_state", None)

def register_checktoken(dp, owner_id: int):
    dp.bot_data["owner_id"] = owner_id
    dp.add_handler(CommandHandler("checktoken", checktoken_command))
    dp.add_handler(CallbackQueryHandler(checktoken_button, pattern="^checktoken$"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, checktoken_handler))
