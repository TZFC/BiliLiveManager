import asyncio
import os
from datetime import datetime
from json import load

from bilibili_api import sync
from bilibili_api.live import LiveDanmaku, LiveRoom
from mysql.connector import connect, MySQLConnection

from EventHandler.DANMU_MSG_handler import handle_danmu_msg
from EventHandler.LIVE_Handler import handle_live
from EventHandler.OTHER_handler import handle_dm_interaction, handle_super_chat_message, handle_guard_buy
from EventHandler.PREPARING_handler import handle_preparing
from EventHandler.SEND_GIFT_handler import handle_send_gift
from Utils.CredentialGetter import get_credential
from Utils.EVENT_IDX import event_types


def load_credential(credential_dict):
    with open(os.path.join(path, "Configs/masterConfig.json")) as masterConfigFile:
        masterConfig = load(masterConfigFile)
    for master in masterConfig['masters']:
        credential_dict[master] = get_credential(master)


def load_config(room_infos, room_ids, credential_dict):
    for room_id in room_ids:
        with open(os.path.join(path, f"Configs/config{room_id}.json")) as roomConfigFile:
            room_config = load(roomConfigFile)
        room_infos[room_id] = {'room_config': room_config,
                               'master_credential': credential_dict[room_config["master"]],
                               'live_danmaku': LiveDanmaku(room_id, credential=credential_dict[room_config["master"]]),
                               'live_room': LiveRoom(room_id, credential=credential_dict[room_config["master"]]),
                               'state': {'pre-checkin': False,
                                         'uid': int(credential_dict[room_config["master"]].dedeuserid),
                                         }
                               }


def bind(live_danmaku: LiveDanmaku, master_config):
    __live_danmaku = live_danmaku

    @__live_danmaku.on("LIVE")
    async def live_start(event):
        __event_room_id = event['room_display_id']
        await handle_live(event=event,
                          database=mydb,
                          master_config=master_config,
                          room_info=roomInfos[__event_room_id])

    @__live_danmaku.on("SEND_GIFT")
    async def gift(event):
        __event_room_id = event['room_display_id']
        await handle_send_gift(event=event,
                               database=mydb,
                               master_config=master_config,
                               room_info=roomInfos[__event_room_id])

    @__live_danmaku.on("DANMU_MSG")
    async def recv(event):
        __event_room_id = event['room_display_id']
        await handle_danmu_msg(event=event,
                               database=mydb,
                               master_config=master_config,
                               room_info=roomInfos[__event_room_id])

    @__live_danmaku.on("PREPARING")
    async def live_end(event):
        __event_room_id = event['room_display_id']
        await handle_preparing(event=event,
                               database=mydb,
                               master_config=master_config,
                               room_info=roomInfos[__event_room_id])

    @__live_danmaku.on("DISCONNECT")
    async def disconnect(event):
        __event_room_id = event['room_display_id']
        await refresh_credentials(credential_dict=credential_dict, database=mydb)

    @__live_danmaku.on("ALL")
    async def any_event(event):
        if event['type'] == 'DM_INTERACTION':
            __event_room_id = event['room_display_id']
            await handle_dm_interaction(event=event,
                                        database=mydb,
                                        master_config=master_config,
                                        room_info=roomInfos[__event_room_id])
        elif event['type'] in {'SUPER_CHAT_MESSAGE', 'SUPER_CHAT_MESSAGE_JPN'}:
            __event_room_id = event['room_display_id']
            await handle_super_chat_message(event=event,
                                            database=mydb,
                                            master_config=master_config,
                                            room_info=roomInfos[__event_room_id])
        elif event['type'] == 'GUARD_BUY':
            __event_room_id = event['room_display_id']
            await handle_guard_buy(event=event,
                                   database=mydb,
                                   master_config=master_config,
                                   room_info=roomInfos[__event_room_id])
        if event['type'] not in event_types:
            print(event)
            event_types.add(event['type'])


async def refresh_credentials_loop(credential_dict: dict, database: MySQLConnection):
    while True:
        try:
            await refresh_credentials(credential_dict, database)
            await asyncio.sleep(3 * 60 * 60)
        except:
            print(f"refresh failed at {datetime.now()}")
            await asyncio.sleep(5 * 60)


async def refresh_credentials(credential_dict: dict, database: MySQLConnection):
    for master, credential in credential_dict.items():
        if await credential.check_refresh():
            await credential.refresh()
            sql = ("UPDATE credentials SET sessdata = %s, bili_jct = %s, buvid3 = %s, ac_time_value = %s "
                   "WHERE master = %s")
            val = (
                credential.sessdata, credential.bili_jct, credential.buvid3, credential.ac_time_value, master)
            with database.cursor() as cursor:
                cursor.execute(sql, val)
                database.commit()


# Main entry point
path = os.getcwd()
with open(os.path.join(path, "Configs/masterConfig.json")) as masterConfigFile:
    masterConfig = load(masterConfigFile)
with open(os.path.join(path, "Configs/mysql.json")) as mysqlFile:
    mydb = connect(**load(mysqlFile))

ROOM_IDS = masterConfig["room_ids"]

'''
roomInfos
    - <room_id>:
        - 'room_config': <>
        - 'master_credential': <>
        - 'live_danmaku': <>
        - 'live_room': <>
        - 'state': <>
'''
roomInfos = {}

'''
credential_dict
    - master: credential
'''
credential_dict = {}

load_credential(credential_dict)
load_config(room_infos=roomInfos, room_ids=ROOM_IDS, credential_dict=credential_dict)

for room_id in ROOM_IDS:
    bind(live_danmaku=roomInfos[room_id]['live_danmaku'], master_config=masterConfig)

if __name__ == "__main__":
    sync(asyncio.gather(*[roomInfos[room_id]['live_danmaku'].connect() for room_id in ROOM_IDS],
                        refresh_credentials_loop(credential_dict=credential_dict, database=mydb)
                        ))
