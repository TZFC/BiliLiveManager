import asyncio
from datetime import datetime

from Utils.EmailSender import send_mail_async
from Utils.Summarizer import summarize
from Utils.UnbanAll import unban_all


async def handle_preparing(event, database, master_config, room_info):
    room_id = event['room_display_id']
    # 记录下播时间
    sql = "UPDATE liveTime SET end = %s WHERE room_id = %s AND end IS NULL"
    val = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), room_id)
    with database.cursor() as cursor:
        cursor.execute(sql, val)
    database.commit()

    # 提炼路灯邮件文 及 跳转文 及 上舰记录
    email_text, jump_text, start_time, end_time = await summarize(room_id, room_info=room_info, database=database)

    async with asyncio.TaskGroup() as tg:
        # (安全网) 放出所有因为错误没放出的禁言
        tg.create_task(unban_all(room_info['live_room'], database))

        # 寄出邮件
        if email_text:
            tg.create_task(
                send_mail_async(sender=master_config["username"], to=room_info['room_config']["listener_email"],
                                subject=f"{room_info['room_config']['nickname']}于{start_time}路灯",
                                text=email_text))
        else:
            tg.create_task(
                send_mail_async(sender=master_config["username"], to=room_info['room_config']["listener_email"],
                                subject=f"{room_info['room_config']['nickname']}于{start_time}路灯",
                                text="本期无路灯"))

        if not start_time:
            return

        if room_info['room_config']["feature_flags"]["replay_comment"]:
            # 记录路灯跳转
            sql = "UPDATE liveTime SET summary = %s WHERE room_id = %s AND end IS NOT NULL AND summary IS NULL"
            if jump_text:
                val = (jump_text, room_id)
            else:
                val = ("N/A", room_id)
            with database.cursor() as cursor:
                cursor.execute(sql, val)
            database.commit()
        else:
            # 删除直播场次记录
            sql = "DELETE FROM liveTime WHERE room_id = %s"
            val = (room_id,)
            with database.cursor() as cursor:
                cursor.execute(sql, val)
            database.commit()

    # 删除弹幕记录
    sql = "DELETE FROM danmu WHERE room_id = %s"
    val = (room_id,)
    with database.cursor() as cursor:
        cursor.execute(sql, val)
    database.commit()
