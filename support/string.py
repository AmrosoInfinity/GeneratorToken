# support/string.py

TOKEN_MENU_TEXT = "📌 Pilih token:"

NEED_TIMEZONE_TEXT = "⚠️ Anda belum set timezone. Silakan pilih:"
CHOOSE_TIMEZONE_TEXT = "🕒 Pilih timezone Anda:"
NO_SELECTION_MSG = "Anda tidak memilih apapun 🙄"
NOT_YOUR_BUTTON_MSG = "Tombol ini bukan untukmu 🥱"
TOKEN_FREE_GRAB_MSG = "Selamat menggunakan token Grab free!\n\n`{token}`"
TOKEN_FREE_GOJEK_MSG = "Selamat menggunakan token Gojek free!\n\n`{token}`"

TIMEZONE_WIB = "WIB (Asia/Jakarta)"
TIMEZONE_WITA = "WITA (Asia/Makassar)"
TIMEZONE_WIT = "WIT (Asia/Jayapura)"

TIMEZONE_SET_SUCCESS = "✅ Timezone Anda diset ke {tz}. Sekarang bisa request token."

TOKEN_GRAB = "=== Token Grab ===\n```{token}```"
TOKEN_GOJEK = "=== Token Gojek ===\n```{token}```"
TOKEN_NOT_FOUND = "Tidak ada token {service} ditemukan."

LIMIT_BLOCKED = "⚠️ User {mention} (ID: {id}) sedang diblokir hingga {until}."
LIMIT_EXCEEDED = "⚠️ User {mention} (ID: {id}) melebihi batas 3 request per hari dan telah di-mute selama 30 menit."
LIMIT_MUTE_FAILED = "⚠️ Tidak bisa mute {mention} (id={id}), kemungkinan owner/admin utama."
LIMIT_INFO = "🕒 Waktu request: {now}\n✅ Request ke-{count} hari ini.\n🎯 Sisa kesempatan: {remaining}"

CHECKTOKEN_VALID_MSG = (
    "✅ Token valid.\n"
    "🔢 Panjang token: {length} karakter\n"
    "📡 Status code: {status}\n"
    "📜 Selamat Token Grab bisa digunakan, \n Semangat bekerja pejuang rupiah, tetap ingat keluarga dirumah"
)

CHECKTOKEN_SOURCE_AMROSOL_MSG = "🔑 Sumber token: Amrosol Token"
CHECKTOKEN_SOURCE_EXTERNAL_MSG = "🔑 Sumber token: {name} [external]"
CHECKTOKEN_SOURCE_UNKNOWN_MSG = "🔑 Sumber token: Unknown"

CHECKTOKEN_INVALID_MSG = (
    "❌ Token tidak valid.\n"
    "🔢 Panjang token: {length} karakter\n"
    "📡 Status code: {status}\n"
    "💡 Token Grab Invoked, Gunakan token lain ya"
)

# Pesan prompt awal
CHECKTOKEN_PROMPT_MSG = (
    "Silakan paste token Anda di chat.\n"
    "Pesan token akan otomatis dihapus setelah dicek."
)

# Pesan kesalahan spesifik
CHECKTOKEN_INVALID_PREFIX_MSG = (
    "⚠️ Token tidak valid karena karakter awal bukan 'ey'. "
    "Walaupun panjang lebih dari 100, tetap bukan token Grab."
)

CHECKTOKEN_INVALID_LENGTH_MSG = (
    "⚠️ Token tidak valid karena panjang di bawah 100 karakter. "
    "Meskipun diawali 'ey', panjang tidak wajar sehingga bukan token Grab."
)

CHECKTOKEN_ERROR_MSG = "⚠️ Error saat cek token: {error}"
