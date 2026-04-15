import os
import json
import time
from telegram import ParseMode

DATA_DIR = "data"
REPORT_DIR = "report"
GROUPACTIVITYFILE = os.path.join(DATA_DIR, "groupactivity.json")
os.makedirs(DATA_DIR, existok=True)
os.makedirs(REPORTDIR, existok=True)

def load_activity():
    if os.path.exists(GROUPACTIVITYFILE):
        with open(GROUPACTIVITYFILE, "r") as f:
            return json.load(f)
    return []

def save_activity(activity):
    with open(GROUPACTIVITYFILE, "w") as f:
        json.dump(activity, f)

activitylog = loadactivity()

def loggroupevent(eventtype: str, chatid: int, chattitle: str, actorid: int = None, actor_name: str = None):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    entry = {
        "time": now,
        "event": event_type,   # "join" atau "leave"
        "chatid": chatid,
        "chattitle": chattitle,
        "actorid": actorid,
        "actorname": actorname
    }
    activity_log.append(entry)
    saveactivity(activitylog)

def senddailyreport(bot, owner_id: int):
    if not activity_log:
        bot.sendmessage(ownerid, "Tidak ada aktivitas grup hari ini.")
        return

    # Buat tabel laporan
    report_lines = ["<b>Laporan Harian Aktivitas Grup</b>", ""]
    report_lines.append("<pre>Waktu              | Event | ID Grup       | Nama Grup        | Actor</pre>")
    report_lines.append("<pre>-------------------+-------+---------------+------------------+----------------</pre>")
    for entry in activity_log:
        actor = f"{entry['actorname']} ({entry['actorid']})" if entry['actor_id'] else "-"
        report_lines.append(
            f"<pre>{entry['time']:<18} | {entry['event']:<5} | {entry['chatid']:<13} | {entry['chattitle']:<16} | {actor}</pre>"
        )

    reporttext = "\n".join(reportlines)
    bot.sendmessage(ownerid, reporttext, parsemode=ParseMode.HTML)

    # Simpan arsip ke report/ dengan nama file per tanggal
    filename = os.path.join(REPORTDIR, f"report{time.strftime('%Y%m%d')}.json")
    with open(filename, "w") as f:
        json.dump(activity_log, f)

    # reset log setelah laporan harian dikirim
    activity_log.clear()
    saveactivity(activitylog)