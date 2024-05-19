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

        # 获取舰长记录
        sql = "SELECT uid, username, guard_name, guard_num FROM guard WHERE room_id = %s"
        val = (room_id,)
        cursor.execute(sql, val)
        guard_record = cursor.fetchall()

        # 删除舰长记录
        sql = "DELETE FROM guard WHERE room_id = %s"
        val = (room_id,)
        cursor.execute(sql, val)
        database.commit()

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

    sum_guard_record = {} #{(uid, guard_name):[username, guard_num_sum]}
    for uid, username, guard_name, guard_num in guard_record:
        try:
            sum_guard_record[(uid, guard_name)][0] = username
            sum_guard_record[(uid, guard_name)][1] += guard_num
        except KeyError:
            sum_guard_record[(uid, guard_name)] = [username, guard_num]

    guard_rows = []
    for (uid, guard_name), [username, guard_num_sum] in sum_guard_record.items():
        guard_rows.append("\t".join([
            username, str(uid), str(guard_name), str(guard_num_sum)
        ]))
    sorted(guard_rows)

    email_text = "\n".join(email_rows+guard_rows)
    jump_text = "\n".join(jump_rows)
    return email_text, jump_text, start_time, end_time
