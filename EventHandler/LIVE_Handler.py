import asyncio
from datetime import datetime

from bilibili_api import Danmaku

from Utils.EmailSender import send_mail_async


async def handle_live(event, database, master_config, room_info):
    if "live_time" not in event["data"].keys():
        # 直播姬开播会有两次LIVE，其中一次没有live_time，以此去重
        return
    room_id = event['room_display_id']
    start = datetime.fromtimestamp(event['data']['live_time'])
    info = await room_info['live_room'].get_room_info()

    async with asyncio.TaskGroup() as tg:
        # 发送开播提醒
        tg.create_task(send_mail_async(
            sender=master_config["username"],
            to=room_info['room_config']["listener_email"],
            subject=f"{room_info['room_config']['nickname']}开始直播{info['room_info']['title']}",
            text=f"https://live.bilibili.com/{room_id}",
            mime_text=info['room_info']['area_name'],
            image=info['room_info']['cover']))

        # 发送打招呼弹幕
        tg.create_task(room_info['live_room'].send_danmaku(Danmaku("来啦！")))

        # 记录开播时间
        sql = "INSERT INTO liveTime (room_id, start) VALUES (%s, %s)"
        val = (room_id, start)
        with database.cursor() as cursor:
            cursor.execute(sql, val)
        database.commit()
