import os
from telegram.ext import CommandHandler

def add_fakegps(update, context):
    if not context.args:
        update.message.reply_text("Gunakan format: /add_fakegps <package>")
        return
    package = context.args[0]
    update.message.reply_text("⚠️ Perintah ini hanya berjalan di perangkat root dengan Termux root access.")
    os.system(f"appops set {package} android:mock_location allow")
    update.message.reply_text(f"Mock location diizinkan untuk {package}")

def deny_fakegps(update, context):
    if not context.args:
        update.message.reply_text("Gunakan format: /deny_fakegps <package>")
        return
    package = context.args[0]
    update.message.reply_text("⚠️ Perintah ini hanya berjalan di perangkat root dengan Termux root access.")
    os.system(f"appops set {package} android:mock_location deny")
    update.message.reply_text(f"Mock location ditolak untuk {package}")

def register_appops_handlers(dp):
    dp.add_handler(CommandHandler("add_fakegps", add_fakegps))
    dp.add_handler(CommandHandler("deny_fakegps", deny_fakegps))
