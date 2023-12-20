import asyncio

from bilibili_api import Danmaku


async def send_report_checkin(live_room, top_uid_username_count):
    for rank, (uid, username, count) in enumerate(top_uid_username_count):
        if rank >= 10:
            break
        await asyncio.sleep(5)
        await live_room.send_danmaku(Danmaku(f"第{rank + 1}名 {username} 打卡{count}次"), reply_mid=uid)
