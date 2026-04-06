import os
import logging
import sys
from telegram.ext import Updater

# Import SEMUA modul
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
    # 1. Konfigurasi Logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__)

    # 2. Ambil Environment Variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    raw_owner = os.getenv("BOT_OWNER_ID")
    owner_id = int(raw_owner) if raw_owner else 0

    if not token or not owner_id:
        logger.error("❌ Environment Variables (TOKEN/OWNER_ID) tidak ditemukan!")
        return

    # 3. Inisialisasi Updater
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    logger.info("🛠 Memulai registrasi handler...")

    # --- LEVEL 0: SISTEM & KEAMANAN ---
    register_block(dp, owner_id)
    register_suspect(dp, owner_id)

    # --- LEVEL 1: COMMANDS (Harus di Atas MessageHandler) ---
    # Register /token, /checktoken, dan input owner
    register_input_token(dp, owner_id)
    register_token_handlers(dp)   # Handler /token
    register_checktoken(dp, owner_id) # Handler /checktoken

    # --- LEVEL 2: TOOLS & UTILITIES ---
    register_appops_handlers(dp)
    register_command_handlers(dp)

    # --- LEVEL 3: CHAT & ACTIVITY (CATCH-ALL) ---
    # register_group_activity dan register_chat_handlers diletakkan paling bawah.
    # register_chat_handlers (AI) sering menggunakan Filters.text yang luas,
    # jadi harus setelah checkToken agar input token tidak dimakan AI.
    register_group_activity(dp, owner_id)
    register_chat_handlers(dp) 

    logger.info("✅ Registrasi selesai. Menghubungkan ke Telegram...")

    # 4. Jalankan Bot
    # drop_pending_updates=True mencegah bot hang saat baru dinyalakan
    updater.start_polling(drop_pending_updates=True)
    
    logger.info("🤖 Bot AKTIF.")
    
    updater.idle()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"❌ KESALAHAN SISTEM: {e}", exc_info=True)
