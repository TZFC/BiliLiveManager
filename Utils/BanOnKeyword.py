import asyncio
from datetime import datetime

from Utils.BanWithTimeout import ban_with_timeout

TEXT_MSG = 0


async def ban_on_keyword(text: str, message_type: int, received_uid: int, room_id: int, live_room, room_config,
                         database):
    if message_type == TEXT_MSG:
        for index in range(len(room_config["ban_words"])):
            banned_word = room_config["ban_words"][index]
            if banned_word in text:
                asyncio.create_task(ban_with_timeout(live_room=live_room,
                                                     uid=received_uid,
                                                     timeout=room_config["ban_timeout"][index],
                                                     database=database))
                sql = "INSERT INTO banned (uid, reason, time, room_id) VALUES (%s, %s, %s, %s)"
                val = (received_uid, room_config["unban_gift"][index],
                       datetime.now().strftime('%Y-%m-%d %H:%M:%S'), room_id)
                with database.cursor() as cursor:
                    cursor.execute(sql, val)
                database.commit()
