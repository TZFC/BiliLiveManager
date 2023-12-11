import asyncio
from datetime import datetime

from Utils.BanWithTimeout import ban_with_timeout
from Utils.EVENT_IDX import TEXT_TYPE


async def ban_on_keyword(text: str, message_type: int, received_uid: int, room_id: int,
                         live_room, room_config, database):
    if message_type == TEXT_TYPE:
        offense = {}  # timeout : reason
        for index in range(len(room_config["ban_words"])):
            banned_word = room_config["ban_words"][index]
            if banned_word in text:
                offense[room_config["ban_timeout"][index]] = room_config["unban_gift"][index]
        if not offense:
            return
        max_timeout = max(offense.keys())
        max_reason = offense[max_timeout]
        asyncio.create_task(ban_with_timeout(live_room=live_room,
                                             uid=received_uid,
                                             timeout=max_timeout,
                                             database=database))
        sql = "INSERT INTO banned (uid, reason, time, room_id) VALUES (%s, %s, %s, %s)"
        val = (received_uid, max_reason,
               datetime.now().strftime('%Y-%m-%d %H:%M:%S'), room_id)
        with database.cursor() as cursor:
            cursor.execute(sql, val)
        database.commit()
