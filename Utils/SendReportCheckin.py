import asyncio

from bilibili_api import Danmaku


async def send_report_checkin(live_room, top_uid_username_count):
    for rank, (uid, username, count) in enumerate(top_uid_username_count):
        if rank >= 10:
            break
        text = f"第{rank + 1}名 {username} 打卡{count}次"
        for chunk in range(len(text)//20+1):
            await asyncio.sleep(5)
            await live_room.send_danmaku(Danmaku(text[chunk*20:(chunk+1)*20]), reply_mid=uid)
