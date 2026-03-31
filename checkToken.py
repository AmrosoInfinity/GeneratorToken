from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from utils.remove_token_user import remove_user_token_message
from utils.button_ownership_utils import is_button_owner
from utils.token_validate_utils import validate_token
from support.string import CHECKTOKEN_PROMPT_MSG

def checktoken_command(update, context):
    sent = update.message.reply_text(
        CHECKTOKEN_PROMPT_MSG,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Masukkan Token", callback_data="checktoken")]]
        )
    )
    context.user_data["checktoken_state"] = {
        "owner": update.effective_user.id,
        "prompt_id": sent.message_id,
    }

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
    # hanya jalan kalau user memang sedang dalam state checktoken
    if "checktoken_state" not in context.user_data:
        return

    raw_text = update.message.text
    token = raw_text.replace("@AmrosolBot", "").replace("*", "").strip()

    is_valid, message = validate_token(token)
    update.message.reply_text(message)

    remove_user_token_message(context, update.message.chat_id, update.message.message_id)

    state = context.user_data.get("checktoken_state")
    if state and "prompt_id" in state:
        try:
            context.bot.delete_message(update.message.chat_id, state["prompt_id"])
        except Exception:
            pass

    # bersihkan state supaya tidak tangkap chat lain
    context.user_data.pop("checktoken_state", None)

def register_checktoken(dp):
    dp.add_handler(CommandHandler("checktoken", checktoken_command))
    dp.add_handler(CallbackQueryHandler(checktoken_button, pattern="^checktoken$"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, checktoken_handler))
