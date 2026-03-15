import os
from telegram.ext import CommandHandler

# Fungsi untuk membaca file message.txt dan ambil balasan sesuai id
def get_message_by_id(message_id: str):
    try:
        with open("support/message.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    if key == message_id:
                        return value
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

# Handler untuk command /info (hanya di grup)
def info(update, context):
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        update.message.reply_text("Command /info hanya bisa digunakan di dalam grup.")
        return

    msg = get_message_by_id("info")
    if msg:
        update.message.reply_text(msg, parse_mode="Markdown")
    else:
        update.message.reply_text("Pesan untuk 'info' tidak ditemukan.")

def register_command_handlers(dp):
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("info", info))
