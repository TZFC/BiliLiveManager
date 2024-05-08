import asyncio

from bilibili_api.exceptions import ResponseCodeException

from Utils.UnbanAll import unban_retry


async def unban_on_gift(sender_uid: int, gift: str, room_id: int, live_room, database):
    sql = "SELECT reason, time FROM banned WHERE uid=%s AND room_id=%s"
    val = (sender_uid, room_id)
    with database.cursor() as cursor:
        cursor.execute(sql, val)
        result = cursor.fetchall()
    try:
        reason, time = result[0]
    except:
        return
    if reason == gift:
        try:
            await unban_retry(live_room, sender_uid)
        except ResponseCodeException as e:
            print(f"unban failed for {sender_uid}")
            print(e)
            return
        sql = "DELETE FROM banned WHERE uid=%s AND room_id=%s"
        val = (sender_uid, room_id)
        with database.cursor() as cursor:
            cursor.execute(sql, val)
        database.commit()
    else:
        return
