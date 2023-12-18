from datetime import datetime
from json import loads

from Utils.EVENT_IDX import *
from Utils.RecordDanmaku import record_danmaku


async def handle_dm_interaction(event, database, master_config, room_info):
    room_id = event['room_display_id']
    try:
        data = loads(event['data']['data']['data'])
        content = "--" + data['combo'][0]['content']
        id = event['data']['data']['id']
        await record_danmaku(name="他们都在说", received_uid=0, time=datetime.now().replace(microsecond=0),
                             medal_room=room_id, medal_level=99, text=content, message_type=TEXT_TYPE, room_id=room_id,
                             danmu_id=id, database=database)
        return
    except:
        pass


async def handle_super_chat_message(event, database, master_config, room_info):
    room_id = event['room_display_id']
    try:
        name = event['data']['data']['user_info']['uname']
        uid = event['data']['data']['uid']
        timestamp = event['data']['data']['ts']
        content = event['data']['data']['message']
        try:
            medal_room = event['data']['data']["medal_info"]['anchor_roomid']
            medal_level = event['data']['data']["medal_info"]['medal_level']
        except:
            medal_room = 0
            medal_level = 0
        await record_danmaku(name=name, received_uid=uid, time=datetime.fromtimestamp(timestamp), medal_room=medal_room,
                             medal_level=medal_level, text=content, message_type=TEXT_TYPE, room_id=room_id,
                             danmu_id=None, database=database)
    except:
        pass
