import asyncio

from bilibili_api.exceptions import ResponseCodeException
from bilibili_api.live import LiveRoom


async def ban_with_timeout(live_room: LiveRoom, uid: int, timeout: int, database):
    try:
        await live_room.ban_user(uid)
    except ResponseCodeException:
        return
    await asyncio.sleep(timeout)
    try:
        await live_room.unban_user(uid)
    except ResponseCodeException:
        pass
    sql = "DELETE FROM banned WHERE uid=%s AND room_id=%s"
    val = (uid, live_room.room_display_id)
    with database.cursor() as cursor:
        cursor.execute(sql, val)
    database.commit()
