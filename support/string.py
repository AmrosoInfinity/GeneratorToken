# support/string.py

# Menu utama
TOKEN_MENU_TEXT = "📌 Pilih token:"

# Validasi timezone
NEED_TIMEZONE_TEXT = "⚠️ Anda belum set timezone. Silakan pilih:"
CHOOSE_TIMEZONE_TEXT = "🕒 Pilih timezone Anda:"

# Timezone options
TIMEZONE_WIB = "WIB (Asia/Jakarta)"
TIMEZONE_WITA = "WITA (Asia/Makassar)"
TIMEZONE_WIT = "WIT (Asia/Jayapura)"

# Konfirmasi timezone
TIMEZONE_SET_SUCCESS = "✅ Timezone Anda diset ke {tz}. Sekarang bisa request token."
TIMEZONE_SET_FAIL = "❌ Timezone tidak valid. Gunakan format seperti `Asia/Jakarta`."

# Token messages
TOKEN_GRAB = "=== Token Grab ===\n```{token}```"
TOKEN_GOJEK = "=== Token Gojek ===\n```{token}```"
TOKEN_NOT_FOUND = "Tidak ada token {service} ditemukan."

# Limit messages
LIMIT_BLOCKED = "⚠️ User {mention} (ID: {id}) sedang diblokir hingga {until}."
LIMIT_EXCEEDED = "⚠️ User {mention} (ID: {id}) melebihi batas 3 request per hari dan telah di-mute selama 2 jam."
LIMIT_INFO = "🕒 Waktu request: {now}\n✅ Request ke-{count} hari ini.\n🎯 Sisa kesempatan: {remaining}"
