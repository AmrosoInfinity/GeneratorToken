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
    # 1. Konfigurasi Logging yang lebih detail
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        handlers=[logging.StreamHandler(sys.stdout)] # Memastikan log tampil di GitHub Actions
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

    logger.info("🛠 Memulai registrasi handler dengan urutan prioritas...")

    # --- KELOMPOK 1: PERINTAH SPESIFIK (PRIORITAS UTAMA) ---
    # Register Token & Input Token harus di paling atas agar tidak 'dimakan' AI
    register_input_token(dp, owner_id)
    register_token_handlers(dp) # Ini yang menangani /token
    
    # --- KELOMPOK 2: KEAMANAN & ADMIN ---
    register_block(dp, owner_id)
    register_suspect(dp, owner_id)
    register_checktoken(dp, owner_id)

    # --- KELOMPOK 3: FITUR FUNGSIONAL LAIN ---
    register_appops_handlers(dp)
    register_command_handlers(dp)

    # --- KELOMPOK 4: HANDLER UMUM (CATCH-ALL) ---
    # register_chat_handlers dan group_activity biasanya menangani MessageHandler(Filters.text)
    # Ini HARUS ditaruh paling bawah agar tidak memblokir CommandHandler di atas
    register_group_activity(dp, owner_id)
    register_chat_handlers(dp) 

    logger.info("✅ Registrasi selesai. Mencoba menghubungkan ke Telegram...")

    # 4. Jalankan Bot
    # drop_pending_updates=True sangat penting di GitHub Actions agar bot 
    # tidak 'hang' karena memproses ribuan chat yang masuk saat bot mati.
    updater.start_polling(drop_pending_updates=True)
    
    logger.info("🤖 Bot AKTIF. Gunakan /token untuk mencoba.")
    
    updater.idle()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Menangkap error fatal agar terlihat di log GitHub
        logging.error(f"❌ KESALAHAN SISTEM: {e}", exc_info=True)
