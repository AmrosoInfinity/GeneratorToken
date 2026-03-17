import os
from telegram.ext import CommandHandler
from button_utils import get_group_only_buttons   # utilitas tombol

def get_message_by_id(message_id: str):
    try:
        with open("support/message.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        capture = False
        buffer = []
        for line in lines:
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                if key == message_id:
                    buffer.append(value.strip())
                    capture = True
                else:
                    if capture:
                        break
            else:
                if capture:
                    buffer.append(line.rstrip())

        if buffer:
            return "\n".join(buffer).strip()
        return None
    except Exception as e:
        print("[DEBUG] Error membaca file:", e)
        return None

def start(update, context):
    msg = get_message_by_id("start")
    update.message.reply_text(msg or "Pesan untuk 'start' tidak ditemukan.", parse_mode="Markdown")

def help_command(update, context):
    msg = get_message_by_id("help")
    update.message.reply_text(msg or "Pesan untuk 'help' tidak ditemukan.", parse_mode="Markdown")

def about(update, context):
    msg = get_message_by_id("about")
    update.message.reply_text(msg or "Pesan untuk 'about' tidak ditemukan.", parse_mode="Markdown")

def info(update, context):
    chat = update.effective_chat
    msg = get_message_by_id("info")

    if not msg:
        update.message.reply_text("Pesan untuk 'info' tidak ditemukan.")
        return

    gif_path = os.path.join("support", "media1.gif")
    try:
        with open(gif_path, "rb") as gif_file:
            # jika private chat → tambahkan tombol
            if chat.type == "private":
                context.bot.send_animation(
                    chat_id=chat.id,
                    animation=gif_file,
                    caption=msg,
                    parse_mode="Markdown",
                    reply_markup=get_group_only_buttons()
                )
            else:
                # jika group/supergroup → kirim tanpa tombol
                context.bot.send_animation(
                    chat_id=chat.id,
                    animation=gif_file,
                    caption=msg,
                    parse_mode="Markdown"
                )
    except Exception as e:
        print("[DEBUG] Error kirim GIF:", e)
        if chat.type == "private":
            update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_group_only_buttons())
        else:
            update.message.reply_text(msg, parse_mode="Markdown")

def register_command_handlers(dp):
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("info", info))
