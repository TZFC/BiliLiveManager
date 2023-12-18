async def get_top_k_checkin(master_uid: int, room_id: int, database, top_k: int) -> list:
    with database.cursor() as cursor:
        sql = ("SELECT uid, count FROM checkin "
               f"WHERE room_id = %s AND uid <> %s "
               f"ORDER BY count DESC LIMIT %s")
        val = (room_id, master_uid, top_k)
        cursor.execute(sql, val)
        result = cursor.fetchall()
    return result
