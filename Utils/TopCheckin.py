from mysql.connector import MySQLConnection


async def get_top_k_checkin(master_uid: int, room_id: int, database: MySQLConnection, top_k: int) -> list:
    with database.cursor() as cursor:
        sql = ("SELECT uid, name, count FROM checkin "
               f"WHERE room_id = %s AND uid <> %s "
               f"ORDER BY count DESC LIMIT %s")
        val = (room_id, master_uid, top_k)
        cursor.execute(sql, val)
        result = cursor.fetchall()
    return result


async def get_top_checkin(master_uid: int, room_id: int, database: MySQLConnection) -> list:
    with database.cursor() as cursor:
        sql = ("SELECT uid, name, count FROM checkin "
               f"WHERE room_id = %s AND uid <> %s AND count > 0 "
               f"ORDER BY count DESC")
        val = (room_id, master_uid)
        cursor.execute(sql, val)
        result = cursor.fetchall()
    return result
