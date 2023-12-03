import asyncio


async def unban_on_gift(sender_uid: int, gift: str,room_id: int, live_room, database):
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
        asyncio.create_task(live_room.unban_user(uid=sender_uid))
        sql = "DELETE FROM banned WHERE uid=%s AND room_id=%s"
        val = (sender_uid, room_id)
        with database.cursor() as cursor:
            cursor.execute(sql, val)
        database.commit()
    else:
        return