import datetime
from telegram.ext import ChatMemberHandler
from utils.group_activity_logger import log_group_event, send_daily_report

def group_activity_handler(update, context):
    chat = update.effective_chat
    member = update.my_chat_member
    actor = update.effective_user

    if member.new_chat_member.status in ["member", "administrator"]:
        log_group_event("join", chat.id, chat.title)
    elif member.new_chat_member.status in ["left", "kicked"]:
        log_group_event("leave", chat.id, chat.title, actor.id, actor.username)

def register_group_activity(dp, owner_id: int):
    dp.bot_data["owner_id"] = owner_id
    dp.add_handler(ChatMemberHandler(group_activity_handler, ChatMemberHandler.MY_CHAT_MEMBER))

    # scheduler harian untuk laporan
    def daily_report_job(context):
        send_daily_report(context.bot, owner_id)

    job_queue = dp.job_queue
    job_queue.run_daily(daily_report_job, time=datetime.time(hour=0, minute=0))  # jam 00:00 WIB
