import os
import logging
from telegram.ext import Updater

# Import semua modul handler
from generatorToken import register_token_handlers
from chatOpenAi import register_chat_handlers
from appopsPermission import register_appops_handlers
from commandBot import register_command_handlers
from checkToken import register_checktoken
from blockHandler import register_block
from suspectHandler import register_suspect
from groupActivity import register_group_activity
from ownerInputToken import register_input_token

def main():
    # Setup logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)

    # Ambil token bot dari environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("⚠️ TELEGRAM_BOT_TOKEN belum diset di environment.")
    logger.debug("Token terbaca, panjang: %d", len(token))

    # Ambil owner ID dari environment (wajib ada, tidak ada default)
    raw_owner = os.getenv("BOT_OWNER_ID")
    if not raw_owner:
        raise ValueError("⚠️ BOT_OWNER_ID belum diset di environment.")
    owner_id = int(raw_owner)

    # Inisialisasi updater dan dispatcher
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # Register semua handler
    logger.debug("Registering handlers...")
    register_group_activity(dp, owner_id=owner_id)
    register_checktoken(dp, owner_id=owner_id)
    register_block(dp, owner_id=owner_id)
    register_suspect(dp, owner_id=owner_id)
    register_input_token(dp, owner_id=owner_id)
    register_token_handlers(dp)
    register_chat_handlers(dp)
    register_appops_handlers(dp)
    register_command_handlers(dp)
    logger.debug("Handlers registered.")

    # Jalankan bot
    print("🤖 Bot sudah berjalan... tekan Ctrl+C untuk berhenti.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
