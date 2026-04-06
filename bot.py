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

    logger.info("🛠 Memulai registrasi handler FLAT...")

    # --- REGISTRASI FULL FLAT (WAJIB URUTAN INI) ---

    # 1. PERINTAH UTAMA & INPUT (BIAR /TOKEN GAK MATI)
    register_input_token(dp, owner_id)
    register_token_handlers(dp)       # Handler /token (Grab/Gojek)
    register_checktoken(dp, owner_id)  # Handler /checktoken (Validasi)
    register_command_handlers(dp)      # Handler /help, dll
    register_appops_handlers(dp)       # Handler /appops

    # 2. SISTEM KEAMANAN
    register_block(dp, owner_id)
    register_suspect(dp, owner_id)

    # 3. FITUR UMUM / CATCH-ALL (WAJIB PALING BAWAH)
    # Alasan: Biar teks token gak dicolong AI sebelum nyampe ke checktoken
    register_group_activity(dp, owner_id)
    register_chat_handlers(dp)         # AI / OpenAI Chat

    logger.info("✅ Registrasi selesai. Menghubungkan ke Telegram...")

    # 4. Jalankan Bot
    updater.start_polling(drop_pending_updates=True)
    
    logger.info("🤖 Bot AKTIF.")
    
    updater.idle()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"❌ KESALAHAN SISTEM: {e}", exc_info=True)
