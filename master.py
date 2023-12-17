import asyncio
import os
from json import load, loads

from bilibili_api import sync
from bilibili_api.live import LiveDanmaku
from mysql.connector import connect

from EventHandler.DANMU_MSG_handler import handle_danmu_msg
from EventHandler.LIVE_Handler import handle_live
from EventHandler.PREPARING_handler import handle_preparing
from EventHandler.SEND_GIFT_handler import handle_send_gift
from Utils.EVENT_IDX import TEXT_TYPE
from Utils.RecordDanmaku import record_danmaku
from Utils.ReloadRoomConfig import reload_room_config

path = os.getcwd()
with open(os.path.join(path, "Configs/masterConfig.json")) as masterConfigFile:
    masterConfig = load(masterConfigFile)
with open(os.path.join(path, "Configs/mysql.json")) as mysqlFile:
    mydb = connect(**load(mysqlFile))

ROOM_IDS = masterConfig["room_ids"]
'''
roomConfigs
    - <room_id>:
        - 'room_config': <>
        - 'master_credential': <>
        - 'live_danmaku': <>
        - 'live_room': <>
'''
roomConfigs = {}
for room_id in ROOM_IDS:
    roomConfigs[room_id] = {}
    reload_room_config(update_room_id=room_id, room_config=roomConfigs[room_id])

event_types = {'LIVE', 'SEND_GIFT', 'DANMU_MSG', 'PREPARING', 'VERIFICATION_SUCCESSFUL', 'VIEW', 'ONLINE_RANK_COUNT',
               'ONLINE_RANK_V2', 'WATCHED_CHANGE', 'STOP_LIVE_ROOM_LIST', 'INTERACT_WORD', ''}


def bind(live_danmaku: LiveDanmaku):
    __live_danmaku = live_danmaku

    @__live_danmaku.on("LIVE")
    async def live_start(event):
        event_room_id = event['room_display_id']
        await handle_live(event=event,
                          database=mydb,
                          master_config=masterConfig,
                          live_room=roomConfigs[event_room_id]['live_room'],
                          room_config=roomConfigs[event_room_id]['room_config'])

    @__live_danmaku.on("SEND_GIFT")
    async def gift(event):
        event_room_id = event['room_display_id']
        await handle_send_gift(event=event,
                               database=mydb,
                               master_config=masterConfig,
                               live_room=roomConfigs[event_room_id]['live_room'],
                               room_config=roomConfigs[event_room_id]['room_config'])

    @__live_danmaku.on("DANMU_MSG")
    async def recv(event):
        event_room_id = event['room_display_id']
        await handle_danmu_msg(event=event,
                               database=mydb,
                               master_config=masterConfig,
                               live_room=roomConfigs[event_room_id]['live_room'],
                               room_config=roomConfigs[event_room_id]['room_config'])

    @__live_danmaku.on("PREPARING")
    async def live_end(event):
        event_room_id = event['room_display_id']
        await handle_preparing(event=event,
                               database=mydb,
                               master_config=masterConfig,
                               live_room=roomConfigs[event_room_id]['live_room'],
                               room_config=roomConfigs[event_room_id]['room_config'])

    @__live_danmaku.on("TIMEOUT")
    async def timeout():
        event_room_id = __live_danmaku.room_display_id
        reload_room_config(update_room_id=event_room_id, room_config=roomConfigs[event_room_id])

    @__live_danmaku.on("ALL")
    async def any_event(event):
        event_room_id = event['room_display_id']
        if event['type'] == 'DM_INTERACTION':
            try:
                content = loads(event['data']['data']['data'])['combo'][0]['content']
                await record_danmaku(name="大家都在说", received_uid=0, medal_room=0, medal_level=0,
                                     text=content, message_type=TEXT_TYPE, room_id=event_room_id, database=mydb)
                return
            except:
                pass
        if event['type'] not in event_types:
            print(event)
            event_types.add(event['type'])


for room_id in ROOM_IDS:
    bind(roomConfigs[room_id]['live_danmaku'])

if __name__ == "__main__":
    sync(asyncio.gather(*[roomConfigs[room_id]['live_danmaku'].connect() for room_id in ROOM_IDS]))
