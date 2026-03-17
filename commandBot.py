import os
from telegram.ext import CommandHandler
from button_utils import send_group_only_message   # utilitas tombol

# Fungsi untuk membaca file message.txt dan ambil balasan sesuai id (multiline)
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

# Handler untuk command /start
def start(update, context):
    msg = get_message_by_id("start")
    if msg:
        update.message.reply_text(msg, parse_mode="Markdown")
    else:
        update.message.reply_text("Pesan untuk 'start' tidak ditemukan.")

# Handler untuk command /help
def help_command(update, context):
    msg = get_message_by_id("help")
    if msg:
        update.message.reply_text(msg, parse_mode="Markdown")
    else:
        update.message.reply_text("Pesan untuk 'help' tidak ditemukan.")

# Handler untuk command /about
def about(update, context):
    msg = get_message_by_id("about")
    if msg:
        update.message.reply_text(msg, parse_mode="Markdown")
    else:
        update.message.reply_text("Pesan untuk 'about' tidak ditemukan.")

# Handler untuk command /info (hanya di grup, kalau private tampilkan tombol)
def info(update, context):
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        send_group_only_message(update, "⚠️ Command /info berisi instruksi permintaan token grab/gojek dan hanya bisa digunakan di dalam grup.")
        return

    msg = get_message_by_id("info")
    if msg:
        gif_path = os.path.join("support", "media1.gif")
        try:
            with open(gif_path, "rb") as gif_file:
                context.bot.send_animation(
                    chat_id=chat.id,
                    animation=gif_file,
                    caption=msg,
                    parse_mode="Markdown"
                )
        except Exception as e:
            print("[DEBUG] Error kirim GIF:", e)
            update.message.reply_text(msg, parse_mode="Markdown")
    else:
        update.message.reply_text("Pesan untuk 'info' tidak ditemukan.")

def register_command_handlers(dp):
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("info", info))
