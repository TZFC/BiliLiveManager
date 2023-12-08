from datetime import datetime


async def record_checkin(start_time: datetime, end_time: datetime, master: str, blacklist: list, room_id: int,
                         database):
    with database.cursor() as cursor:
        sql = "SELECT dedeuserid FROM credentials WHERE master = %s"
        val = (master,)
        cursor.execute(sql, val)
        dedeuserid = int(cursor.fetchall()[0][0])

        sql = "SELECT slot_0, slot_1, slot_2, slot_3, slot_4, slot_5, slot_6, slot_7, slot_8, slot_9 WHERE uid = %s AND room_id = %s"
        val = (dedeuserid, room_id)
        cursor.execute(sql, val)
        slots: tuple = cursor.fetchall()[0]
        head = slots.index(1)
        next_head = head + 1 if head != 9 else 0

        sql = "SELECT DISTINCT uid FROM danmu WHERE room_id = %s AND time BETWEEN %s AND %s"
        val = (room_id, start_time, end_time)
        cursor.execute(sql, val)
        result = cursor.fetchall()
        unique_uid = [item[0] for item in result]

        sql = f"UPDATE checkin SET slot_{head} = 0 where room_id = %s"
        val = (room_id,)
        cursor.execute(sql, val)

        sql = f"INSERT INTO checkin (room_id, uid, slot_{head}) VALUES(%s, %s, 1) ON DUPLICATE KEY UPDATE slot_{head} = 1"
        val = [(room_id, uid) for uid in unique_uid if uid not in blacklist and uid != dedeuserid]
        cursor.executemany(sql, val)

        sql = f"UPDATE checkin SET slot_{next_head} = 1 where room_id = %s AND uid = %s"
        val = (room_id, dedeuserid)
        cursor.execute(sql, val)

    database.commit()
