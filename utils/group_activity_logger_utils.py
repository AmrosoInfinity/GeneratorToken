import os
import json
import time
from telegram import ParseMode

DATA_DIR = "data"
REPORT_DIR = "report"
GROUP_ACTIVITY_FILE = os.path.join(DATA_DIR, "group_activity.json")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

def load_activity():
    if os.path.exists(GROUP_ACTIVITY_FILE):
        try:
            with open(GROUP_ACTIVITY_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []  # file kosong → default list
                return json.loads(content)
        except (json.JSONDecodeError, OSError):
            # kalau file rusak atau tidak bisa dibaca
            return []
    return []

def save_activity(activity):
    with open(GROUP_ACTIVITY_FILE, "w", encoding="utf-8") as f:
        json.dump(activity, f)

activity_log = load_activity()

def log_group_event(event_type: str, chat_id: int, chat_title: str, actor_id: int = None, actor_name: str = None):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    entry = {
        "time": now,
        "event": event_type,   # "join" atau "leave"
        "chat_id": chat_id,
        "chat_title": chat_title,
        "actor_id": actor_id,
        "actor_name": actor_name
    }
    activity_log.append(entry)
    save_activity(activity_log)

def send_daily_report(bot, owner_id: int):
    if not activity_log:
        bot.send_message(owner_id, "Tidak ada aktivitas grup hari ini.")
        return

    # Buat tabel laporan
    report_lines = ["<b>Laporan Harian Aktivitas Grup</b>", ""]
    report_lines.append("<pre>Waktu              | Event | ID Grup       | Nama Grup        | Actor</pre>")
    report_lines.append("<pre>-------------------+-------+---------------+------------------+----------------</pre>")
    for entry in activity_log:
        actor = f"{entry['actor_name']} ({entry['actor_id']})" if entry['actor_id'] else "-"
        report_lines.append(
            f"<pre>{entry['time']:<18} | {entry['event']:<5} | {entry['chat_id']:<13} | {entry['chat_title']:<16} | {actor}</pre>"
        )

    report_text = "\n".join(report_lines)
    bot.send_message(owner_id, report_text, parse_mode=ParseMode.HTML)

    # Simpan arsip ke report/ dengan nama file per tanggal
    filename = os.path.join(REPORT_DIR, f"report_{time.strftime('%Y%m%d')}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(activity_log, f)

    # reset log setelah laporan harian dikirim
    activity_log.clear()
    save_activity(activity_log)
