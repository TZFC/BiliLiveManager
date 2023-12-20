from datetime import datetime

from Utils.EVENT_IDX import TEXT_TYPE


async def record_checkin(start_time: datetime, end_time: datetime, master: str, room_id: int, checkin_days: int,
                         database):
    with database.cursor() as cursor:
        sql = "SELECT dedeuserid FROM credentials WHERE master = %s"
        val = (master,)
        cursor.execute(sql, val)
        dedeuserid = int(cursor.fetchall()[0][0])

        sql_prefix = "SELECT slot_0"
        sql_postfix = " FROM checkin WHERE uid = %s AND room_id = %s"
        sql = ""
        for i in range(1, checkin_days):
            sql += f", slot_{i}"
        sql = sql_prefix + sql + sql_postfix
        val = (dedeuserid, room_id)
        cursor.execute(sql, val)
        slots: tuple = cursor.fetchall()[0]
        head = slots.index(1)
        next_head = head + 1 if head != checkin_days - 1 else 0

        sql = (f"SELECT DISTINCT uid, name FROM danmu "
               f"WHERE room_id = %s AND time BETWEEN %s AND %s AND type = {TEXT_TYPE} ")
        val = (room_id, start_time, end_time)
        cursor.execute(sql, val)
        unique_uid_name = cursor.fetchall()

        sql = f"UPDATE checkin SET slot_{head} = 0 WHERE room_id = %s"
        val = (room_id,)
        cursor.execute(sql, val)

        sql = "SELECT uid FROM blacklist"
        cursor.execute(sql)
        result = cursor.fetchall()
        blacklist = {uid[0] for uid in result}

        for uid, name in unique_uid_name:
            if uid not in blacklist and uid != dedeuserid:
                sql = (f"INSERT INTO checkin (room_id, uid, name, slot_{head}, all_time) VALUES(%s, %s, %s, 1, 1) "
                       f"ON DUPLICATE KEY UPDATE name = %s, slot_{head} = 1, all_time = all_time + 1")
                val = (room_id, uid, name, name)
                cursor.execute(sql, val)

        sql = f"UPDATE checkin SET slot_{next_head} = 1 where room_id = %s AND uid = %s"
        val = (room_id, dedeuserid)
        cursor.execute(sql, val)
