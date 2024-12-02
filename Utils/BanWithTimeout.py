import asyncio

from bilibili_api.exceptions import ResponseCodeException
from bilibili_api.live import LiveRoom
from bilibili_api import Danmaku
from Utils.UnbanAll import unban_retry

async def ban_with_timeout(live_room: LiveRoom, uid: int, offense: tuple, database):
    try:
        await live_room.ban_user(uid, hour = 0)
        select_sql = "SELECT * FROM ban_history WHERE uid = %s and room_id = %s"
        insert_sql = "INSERT INTO ban_history (uid, room_id) VALUES (%s, %s)"
        val = (uid, live_room.room_display_id)
        with database.cursor() as cursor:
            cursor.execute(select_sql, val)
            result = cursor.fetchone()
            if not result:
                cursor.execute(insert_sql, val)
                database.commit()
        if not result:
            if offense[1] % 60 == 0:
                message = f"发{offense[0]}会被关{offense[1] // 60}分，送{offense[2]}提前解"
            else:
                message = f"发{offense[0]}会被关{offense[1] / 60:.1f}分，送{offense[2]}提前解"
            await live_room.send_danmaku(Danmaku(message), reply_mid=uid)

    except Exception as e:
        print(f"ban failed for {uid}")
        print(e)
    await asyncio.sleep(offense[1])
    try:
        await unban_retry(live_room, uid)
    except ResponseCodeException as e:
        print(f"unban failed for {uid}")
        print(e)
    sql = "DELETE FROM banned WHERE uid=%s AND room_id=%s"
    val = (uid, live_room.room_display_id)
    with database.cursor() as cursor:
        cursor.execute(sql, val)
    database.commit()
