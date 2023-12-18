import asyncio

from bilibili_api import Danmaku


async def send_report_checkin(live_room, top_uid_count):
    for rank, (uid, count) in enumerate(top_uid_count):
        await live_room.send_danmaku(Danmaku(f"以 {count} 次打卡获得第 {rank+1} 名"), reply_mid=uid)
        await asyncio.sleep(5)