async def get_top_k_checkin(master: str, room_id: int, database, top_k: int) -> list:
    with database.cursor() as cursor:
        sql = "SELECT dedeuserid FROM credentials WHERE master = %s"
        val = (master,)
        cursor.execute(sql, val)
        dedeuserid = int(cursor.fetchall()[0][0])

        sql = ("SELECT uid, count FROM checkin "
               f"WHERE room_id = %s AND uid <> %s "
               f"ORDER BY count DESC LIMIT %s")
        val = (room_id, dedeuserid, top_k)
        cursor.execute(sql, val)
        result = cursor.fetchall()
    return result
