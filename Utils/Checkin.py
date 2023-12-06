from datetime import datetime


async def record_checkin(start_time: datetime, end_time: datetime, room_id: int, database):
    sql = "SELECT DISTINCT uid FROM danmu WHERE room_id = %s AND time BETWEEN %s AND %s"
    val = (room_id, start_time, end_time)
    with database.cursor() as cursor:
        cursor.execute(sql, val)
        checker = cursor.fetchall()
    sql = "INSERT INTO checkin (uid, room_id, attend) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE attend = attend + 1"
    val = [(uid, room_id, 1) for uid in checker]
    with database.cursor() as cursor:
        cursor.executemany(sql, val)
    database.commit()