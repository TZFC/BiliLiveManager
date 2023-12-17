from datetime import datetime

from Utils.BanOnKeyword import ban_on_keyword
from Utils.EVENT_IDX import *
from Utils.RecordDanmaku import record_danmaku


async def handle_danmu_msg(event, database, master_config, live_room, room_config):
    room_id = event['room_display_id']
    received_uid = event["data"]["info"][SENDER_INFO_IDX][SENDER_UID_IDX]
    text = event["data"]["info"][TEXT_IDX]
    message_type = event["data"]["info"][0][MSG_TYPE_IDX]

    # 封禁关键词
    if room_config["feature_flags"]["unban"]:
        await ban_on_keyword(text=text,
                             message_type=message_type,
                             received_uid=received_uid,
                             room_id=room_id,
                             live_room=live_room,
                             room_config=room_config,
                             database=database)
    # 记录弹幕
    try:
        medal_room = event["data"]["info"][MEDAL_INFO_IDX][MEDAL_ROOMID_IDX]
        medal_level = event["data"]["info"][MEDAL_INFO_IDX][MEDAL_LEVEL_IDX]
    except:
        medal_room = 0
        medal_level = 0
    await record_danmaku(name=event["data"]["info"][SENDER_INFO_IDX][SENDER_USERNAME_IDX],
                         received_uid=received_uid,
                         time=datetime.fromtimestamp(event['data']["info"][TIMESTAMP_IDX]['ts']),
                         medal_room=medal_room,
                         medal_level=medal_level,
                         text=text,
                         message_type=message_type,
                         room_id=room_id,
                         database=database)
