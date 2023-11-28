from datetime import datetime, timedelta
from json import load

from mysql.connector import connect

OFFSET = timedelta(seconds=5)


def isDeng(row: dict, field_index: dict, room_id: int, roomConfig) -> bool:
    text = row[field_index["text"]]
    keywords = roomConfig["keyword"]
    if (text[:2] in keywords):
        return True
    else:
        return False


def summarize(room_id: int) -> (str, str, datetime, datetime):
    with connect(**load(open("Configs/mysql.json"))) as mydb:
        with mydb.cursor() as cursor:
            cursor.execute("SELECT start, end FROM liveTime WHERE room_id = %s AND end IS NOT NULL AND summary IS NULL",
                           (room_id,))
            result = cursor.fetchall()
            if not result:
                return None, None, None, None
            start_time, end_time = result[0]
            cursor.execute("SELECT * FROM danmu WHERE room_id = %s AND time BETWEEN %s AND %s",
                           (room_id, start_time, end_time))
            raw_danmu = cursor.fetchall()
            field_index = {field_name: index for index, field_name in enumerate(cursor.column_names)}

    # 找出路灯关键词
    roomConfig = load(open(f"Configs/config{room_id}.json"))
    email_rows, jump_rows = list(zip(*[
        (
            # email fields
            "\t".join([
                str(row[field_index["time"]] - OFFSET),  # 时间
                row[field_index["text"]][2:],  # 去除指令词的路灯内容
                row[field_index["name"]],  # 发送者用户名
                str(row[field_index["uid"]])  # 发送者uid
            ]),
            # jump fields
            " ".join([
                str(row[field_index["time"]] - start_time - OFFSET),  # 相对开播时间
                row[field_index["text"]][2:]  # 去除指令词的路灯内容
            ])
        ) for row in raw_danmu if isDeng(row, field_index, room_id, roomConfig)
    ])) or ([], [])
    email_text = "\n".join(email_rows)
    jump_text = "\n".join(jump_rows)

    # //TODO: find where ? and haha is and report in email_text
    return email_text, jump_text, start_time, end_time
