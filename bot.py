import os
import logging
from telegram.ext import Updater
from generatorToken import register_token_menu
from chatOpenAi import register_chat_handlers
from appopsPermission import register_appops_handlers
from commandBot import register_command_handlers
from checkToken import register_checktoken

def main():
    # Setup logging (akan tampil di console GitHub Actions)
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)

    # Ambil token dari environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("⚠️ TELEGRAM_BOT_TOKEN belum diset di environment.")
    logger.debug("Token terbaca, panjang: %d", len(token))

    # Inisialisasi updater dan dispatcher
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # Register semua handler dari modul terpisah
    logger.debug("Registering handlers...")
    register_token_menu(dp)       # tombol /token (Grab/Gojek + timezone)
    register_chat_handlers(dp)        # modul chatOpenAi
    register_appops_handlers(dp)      # modul appopsPermission
    register_command_handlers(dp)     # modul commandBot
    register_checktoken(dp)
    logger.debug("Handlers registered.")

    # Jalankan bot
    print("🤖 Bot sudah berjalan... tekan Ctrl+C untuk berhenti.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
