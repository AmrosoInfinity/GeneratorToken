import os
from telegram.ext import CommandHandler

def add_fakegps(update, context):
    if not context.args:
        update.message.reply_text("Gunakan format: /add_fakegps <package1>,<package2>,...")
        return

    # Gabungkan semua argumen jadi satu string, lalu split dengan koma
    packages = " ".join(context.args).split(",")
    update.message.reply_text("⚠️ Perintah ini hanya berjalan di perangkat root dengan Termux root access.")

    results = []
    for pkg in packages:
        pkg = pkg.strip()
        if pkg:
            os.system(f"appops set {pkg} android:mock_location allow")
            results.append(f"✅ Mock location diizinkan untuk {pkg}")

    update.message.reply_text("\n".join(results))


def deny_fakegps(update, context):
    if not context.args:
        update.message.reply_text("Gunakan format: /deny_fakegps <package1>,<package2>,...")
        return

    packages = " ".join(context.args).split(",")
    update.message.reply_text("⚠️ Perintah ini hanya berjalan di perangkat root dengan Termux root access.")

    results = []
    for pkg in packages:
        pkg = pkg.strip()
        if pkg:
            os.system(f"appops set {pkg} android:mock_location deny")
            results.append(f"❌ Mock location ditolak untuk {pkg}")

    update.message.reply_text("\n".join(results))


def register_appops_handlers(dp):
    dp.add_handler(CommandHandler("add_fakegps", add_fakegps))
    dp.add_handler(CommandHandler("deny_fakegps", deny_fakegps))
