from telegram.ext import CommandHandler, MessageHandler, Filters
from utils.block_user_utils import block_user, unblock_user, is_blocked

def block_command(update, context):
    # hanya owner yang boleh blokir
    if update.effective_user.id != context.bot_data.get("owner_id"):
        return
    try:
        target_id = int(context.args[0])
        block_user(target_id)
        update.message.reply_text(f"User {target_id} diblokir secara privat.")
    except Exception:
        update.message.reply_text("Format salah. Gunakan: /block <id_user>")

def unblock_command(update, context):
    if update.effective_user.id != context.bot_data.get("owner_id"):
        return
    try:
        target_id = int(context.args[0])
        unblock_user(target_id)
        update.message.reply_text(f"User {target_id} dihapus dari blokir.")
    except Exception:
        update.message.reply_text("Format salah. Gunakan: /unblock <id_user>")

def message_filter(update, context):
    # jika user diblokir, abaikan semua pesan/perintah
    if is_blocked(update.effective_user.id):
        return

def group_monitor(update, context):
    chat = update.effective_chat
    user = update.effective_user

    # jika user nakal ada di grup, bot kick
    if is_blocked(user.id) and chat.type in ["group", "supergroup"]:
        try:
            context.bot.kick_chat_member(chat.id, user.id)
        except Exception:
            pass

    # jika bot ditambahkan ke grup oleh user nakal, langsung keluar
    if chat.type in ["group", "supergroup"]:
        admins = context.bot.get_chat_administrators(chat.id)
        for admin in admins:
            if is_blocked(admin.user.id):
                try:
                    context.bot.leave_chat(chat.id)
                except Exception:
                    pass
                break

def register_block(dp, owner_id: int):
    dp.bot_data["owner_id"] = owner_id
    dp.add_handler(CommandHandler("block", block_command))
    dp.add_handler(CommandHandler("unblock", unblock_command))
    dp.add_handler(MessageHandler(Filters.all, message_filter), group=0)
    dp.add_handler(MessageHandler(Filters.status_update, group_monitor))
