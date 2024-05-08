# (安全网)放出封禁名单中所有人
from bilibili_api.exceptions import ResponseCodeException
from bilibili_api.live import LiveRoom
from datetime import datetime
from time import sleep


async def unban_retry(live_room: LiveRoom, uid: int):
    for retry_time in range(3):
        try:
            await live_room.unban_user(uid)
            return
        except:
            sleep(1)
    print("All 3 attempts to unban failed")


async def unban_all(live_room: LiveRoom, database):
    sql = 'SELECT uid,time FROM banned WHERE room_id = %s'
    val = (live_room.room_display_id,)
    with database.cursor() as cursor:
        cursor.execute(sql, val)
    result = cursor.fetchall()
    if not result:
        return
    else:
        for uid, time in result:
            if time < datetime.now():
                print(f"{uid} not properly released. Releasing at live end.")
            try:
                await unban_retry(live_room, uid)
            except ResponseCodeException as e:
                print(f"unban failed for {uid}")
                print(e)
            sql = "DELETE FROM banned WHERE uid=%s AND room_id=%s"
            val = (uid, live_room.room_display_id)
            with database.cursor() as cursor:
                cursor.execute(sql, val)