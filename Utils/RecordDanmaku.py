from datetime import datetime


async def record_danmaku(name: str, received_uid: int, medal_room: int, medal_level: int,
                         text: str, message_type: int, room_id: int, database):
    sql = ("INSERT INTO danmu (name, uid, text, type, medal_id, medal_level, time, room_id)"
           " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

    val = (name,
           received_uid,
           text,
           message_type,
           medal_room,
           medal_level,
           datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
           room_id)
    with database.cursor() as cursor:
        cursor.execute(sql, val)
    database.commit()
