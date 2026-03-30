def checktoken_handler(update, context):
    raw_text = update.message.text
    # Hilangkan mention bot dan simbol bintang
    token = raw_text.replace("@AmrosolBot", "").replace("*", "").strip()
    token_length = len(token)

    lat = "-6.1901"
    lng = "106.8326"
    url = f"https://p.grabtaxi.com/api/passenger/v3/grabfood/content/restaurants?latlng={lat},{lng}"

    headers = {
        "Authorization": token,
        "X-Location": f"{lat},{lng}",
        "x-mts-ssid": token,
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Grab/5.397.0 (Android 15; Build 139598668)"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        status_code = resp.status_code

        if status_code == 200:
            reply = (
                "✅ Token valid.\n"
                f"🔢 Panjang token: {token_length} karakter\n"
                f"📡 Status code: {status_code}\n"
                "📍 Lokasi dicek: Stasiun Gondangdia"
            )
        else:
            reply = (
                "❌ Token tidak valid.\n"
                f"🔢 Panjang token: {token_length} karakter\n"
                f"📡 Status code: {status_code}\n"
                "📍 Lokasi dicek: Stasiun Gondangdia"
            )

        update.message.reply_text(reply)

    except Exception as e:
        update.message.reply_text(f"⚠️ Error saat cek token: {e}")

    remove_user_token_message(context, update.message.chat_id, update.message.message_id)
