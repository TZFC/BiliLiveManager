import asyncio

from bilibili_api.exceptions import ResponseCodeException
from bilibili_api.live import LiveRoom


async def ban_with_timeout(liveRoom: LiveRoom, uid: int, timeout: int, database):
    try:
        await liveRoom.ban_user(uid)
    except ResponseCodeException:
        return
    await asyncio.sleep(timeout)
    try:
        await liveRoom.unban_user(uid)
    except ResponseCodeException:
        return
    sql = "DELETE FROM banned WHERE uid=%s AND room_id=%s"
    val = (uid, liveRoom.room_display_id)
    with database.cursor() as cursor:
        cursor.execute(sql, val)
    database.commit()