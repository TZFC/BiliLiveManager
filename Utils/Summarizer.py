import os
from datetime import datetime, timedelta
from json import load

OFFSET = timedelta(minutes=1)
path = os.getcwd()


def summarize(room_id: int, database) -> (str, str, datetime, datetime):
    with database.cursor() as cursor:
        sql = "SELECT start, end FROM liveTime WHERE room_id = %s AND end IS NOT NULL AND summary IS NULL"
        val = (room_id,)
        cursor.execute(sql, val)
        result = cursor.fetchall()
        if not result:
            return None, None, None, None
        start_time, end_time = result[0]

        # 找出路灯
        with open(os.path.join(path, f"Configs/config{room_id}.json")) as roomConfigFile:
            room_config = load(roomConfigFile)
        regex = '|'.join(['^' + keyword for keyword in room_config['keyword']])
        cursor.execute(f"SELECT time, SUBSTRING(text, 3), name, uid FROM danmu "
                       f"WHERE room_id = %s AND time BETWEEN %s AND %s "
                       f"AND text RLIKE '{regex}'",
                       (room_id, start_time, end_time))
        raw_danmu = cursor.fetchall()

    email_rows = []
    jump_rows = []
    for row in raw_danmu:
        email_rows.append("\t".join([
            str(row[0]),  # 时间
            row[1],  # 去除指令词的路灯内容
            row[2],  # 发送者用户名
            str(row[3]),  # 发送者uid
        ]))
        jump_rows.append(" ".join([
            str(row[0] - start_time - OFFSET),  # 相对开播时间
            row[1],  # 去除指令词的路灯内容
        ]))

    email_text = "\n".join(email_rows)
    jump_text = "\n".join(jump_rows)

    return email_text, jump_text, start_time, end_time
