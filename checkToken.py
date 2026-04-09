import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from utils.remove_token_user import remove_user_token_message
from utils.button_ownership_utils import is_button_owner
from utils.token_validate_utils import validate_token
from utils.checktoken_abuse_utils import record_check, should_block, warn_or_suspect
from support.string import CHECKTOKEN_PROMPT_MSG

# --- FUNGSI BARU: MANAGEMENT LIST ---

def whitelist_check_command(update, context):
    user_id = update.effective_user.id
    owner_id = context.bot_data.get("owner_id")
    if user_id != owner_id: return

    if not context.args:
        update.message.reply_text("Format: `/whitelistCheck [user_id]`")
        return

    try:
        target_id = int(context.args[0])
        whitelist = context.bot_data.get("whitelist", [])
        if target_id not in whitelist:
            whitelist.append(target_id)
            context.bot_data["whitelist"] = whitelist
            update.message.reply_text(f"✅ ID `{target_id}` ditambahkan ke Whitelist.")
        else:
            update.message.reply_text("ℹ️ ID sudah ada di Whitelist.")
    except ValueError:
        update.message.reply_text("❌ ID harus berupa angka.")

def blacklist_check_command(update, context):
    user_id = update.effective_user.id
    owner_id = context.bot_data.get("owner_id")
    if user_id != owner_id: return

    if not context.args:
        update.message.reply_text("Format: `/blacklistCheck [user_id]`")
        return

    try:
        target_id = int(context.args[0])
        blacklist = context.bot_data.get("blacklist", [])
        if target_id not in blacklist:
            blacklist.append(target_id)
            context.bot_data["blacklist"] = blacklist
            update.message.reply_text(f"🚫 ID `{target_id}` berhasil di-Blacklist secara permanen.")
        else:
            update.message.reply_text("ℹ️ ID sudah ada di Blacklist.")
    except ValueError:
        update.message.reply_text("❌ ID harus berupa angka.")

# --- MODIFIKASI: LOGIKA CHECKTOKEN ---

def checktoken_command(update, context):
    user_id = update.effective_user.id
    owner_id = context.bot_data.get("owner_id")
    
    # Ambil data list
    whitelist = context.bot_data.get("whitelist", [])
    blacklist = context.bot_data.get("blacklist", [])

    # 1. CEK BLACKLIST (Prioritas Utama)
    if user_id in blacklist:
        update.message.reply_text("🚫 Akses Anda telah dilarang secara permanen oleh Owner.")
        return

    # 2. CEK PENGECUALIAN (Owner & Whitelist)
    if user_id == owner_id or user_id in whitelist:
        pass 
    else:
        # 3. LOGIKA AWAL (Antispam & Auto-Block)
        if should_block(user_id, owner_id):
            status = warn_or_suspect(user_id, owner_id, context.bot)
            if status == "warn":
                update.message.reply_text(
                    "⚠️ Anda terlalu sering melakukan pengecekan token. Tunggu 12 jam sebelum mencoba lagi."
                )
                return
            elif status == "suspect":
                update.message.reply_text("🚫 Akses checktoken Anda diblokir sementara.")
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

    # Sisa kode prompt tetap sama...
    sent = update.message.reply_text(
        CHECKTOKEN_PROMPT_MSG,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Masukkan Token", callback_data="checktoken")]]
        )
    )
    context.user_data["checktoken_state"] = {"owner": user_id, "prompt_id": sent.message_id, "expired": False}

    def expire_prompt():
        state = context.user_data.get("checktoken_state")
        if state and not state["expired"] and state["prompt_id"] == sent.message_id:
            try: context.bot.delete_message(update.effective_chat.id, sent.message_id)
            except: pass
            state["expired"] = True
            context.user_data.pop("checktoken_state", None)

    threading.Timer(30, expire_prompt).start()

# --- HANDLER LAINNYA TETAP SAMA ---
def checktoken_button(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    chat = update.effective_chat
    state = context.user_data.get("checktoken_state")
    if not is_button_owner(context, chat, user_id, state, query): return
    query.answer()
    query.edit_message_text("Silakan kirim token Anda di chat.")

def checktoken_handler(update, context):
    state = context.user_data.get("checktoken_state")
    if not state or state.get("expired"): return
    raw_text = update.message.text
    token = raw_text.replace("@AmrosolBot", "").replace("*", "").strip()
    is_valid, message = validate_token(token)
    update.message.reply_text(message)
    remove_user_token_message(context, update.message.chat_id, update.message.message_id)
    record_check(update.effective_user.id, is_valid)
    try: context.bot.delete_message(update.message.chat_id, state["prompt_id"])
    except: pass
    context.user_data.pop("checktoken_state", None)

def register_checktoken(dp, owner_id: int):
    dp.bot_data["owner_id"] = owner_id
    # Registrasi handler baru
    dp.add_handler(CommandHandler("whitelistCheck", whitelist_check_command))
    dp.add_handler(CommandHandler("blacklistCheck", blacklist_check_command))
    dp.add_handler(CommandHandler("checktoken", checktoken_command))
    dp.add_handler(CallbackQueryHandler(checktoken_button, pattern="^checktoken$"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, checktoken_handler))
