import asyncio
import os
from json import load

from bilibili_api import sync
from bilibili_api.live import LiveDanmaku
from mysql.connector import connect

from EventHandler.DANMU_MSG_handler import handle_danmu_msg
from EventHandler.LIVE_Handler import handle_live
from EventHandler.OTHER_handler import handle_dm_interaction, handle_super_chat_message
from EventHandler.PREPARING_handler import handle_preparing
from EventHandler.SEND_GIFT_handler import handle_send_gift
from Utils.ReloadRoomConfig import reload_room_info

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
        - ‘state’: <>
'''
roomInfos = {}
for room_id in ROOM_IDS:
    roomInfos[room_id] = {}
    reload_room_info(update_room_id=room_id, room_info=roomInfos[room_id])

event_types = {
    'LIVE', 'SEND_GIFT', 'DANMU_MSG', 'PREPARING', 'VERIFICATION_SUCCESSFUL', 'VIEW', 'ONLINE_RANK_COUNT',
    'ONLINE_RANK_V2', 'WATCHED_CHANGE', 'STOP_LIVE_ROOM_LIST', 'INTERACT_WORD', 'DANMU_AGGREGATION',
    'ROOM_REAL_TIME_MESSAGE_UPDATE', 'ENTRY_EFFECT', 'POPULAR_RANK_CHANGED', 'LIKE_INFO_V3_CLICK',
    'LIKE_INFO_V3_UPDATE', 'POPULARITY_RED_POCKET_WINNER_LIST', 'POPULARITY_RED_POCKET_START', 'WIDGET_BANNER',
    'AREA_RANK_CHANGED', 'POPULARITY_RED_POCKET_NEW', 'NOTICE_MSG', 'GUARD_BUY', 'USER_TOAST_MSG', 'COMBO_SEND',
    'COMMON_NOTICE_DANMAKU', 'DM_INTERACTION', 'TRADING_SCORE', 'ENTRY_EFFECT_MUST_RECEIVE',
    'MESSAGEBOX_USER_MEDAL_CHANGE', 'LITTLE_MESSAGE_BOX', 'GUARD_HONOR_THOUSAND', 'SYS_MSG', 'ONLINE_RANK_TOP3',
    'USER_PANEL_RED_ALARM', 'SUPER_CHAT_MESSAGE', 'PK_BATTLE_PRE_NEW', 'PK_BATTLE_PRE', 'PK_BATTLE_START_NEW',
    'PK_BATTLE_START', 'PK_BATTLE_PROCESS_NEW', 'PK_BATTLE_PROCESS', 'PK_BATTLE_FINAL_PROCESS', 'PK_BATTLE_END',
    'PK_BATTLE_SETTLE_USER', 'PK_BATTLE_SETTLE_V2', 'PK_BATTLE_SETTLE', 'LIVE_OPEN_PLATFORM_GAME',
    'LIVE_INTERACT_GAME_STATE_CHANGE', 'LIKE_INFO_V3_NOTICE', 'SUPER_CHAT_MESSAGE_JPN', 'LIVE_PANEL_CHANGE_CONTENT',
    'GIFT_PANEL_PLAN', 'GIFT_STAR_PROCESS', 'ROOM_SKIN_MSG', 'USER_INFO_UPDATE', 'CUSTOM_NOTICE_CARD',
    'GIFT_STAR_PROCESS', 'WIDGET_GIFT_STAR_PROCESS', 'ROOM_CHANGE', 'SHOPPING_CART_SHOW', 'RECOMMEND_CARD',
    'GOTO_BUY_FLOW'}


def bind(live_danmaku: LiveDanmaku):
    __live_danmaku = live_danmaku

    @__live_danmaku.on("LIVE")
    async def live_start(event):
        event_room_id = event['room_display_id']
        await handle_live(event=event,
                          database=mydb,
                          master_config=masterConfig,
                          room_info=roomInfos[event_room_id])

    @__live_danmaku.on("SEND_GIFT")
    async def gift(event):
        event_room_id = event['room_display_id']
        await handle_send_gift(event=event,
                               database=mydb,
                               master_config=masterConfig,
                               room_info=roomInfos[event_room_id])

    @__live_danmaku.on("DANMU_MSG")
    async def recv(event):
        event_room_id = event['room_display_id']
        await handle_danmu_msg(event=event,
                               database=mydb,
                               master_config=masterConfig,
                               room_info=roomInfos[event_room_id])

    @__live_danmaku.on("PREPARING")
    async def live_end(event):
        event_room_id = event['room_display_id']
        await handle_preparing(event=event,
                               database=mydb,
                               master_config=masterConfig,
                               room_info=roomInfos[event_room_id])

    @__live_danmaku.on("TIMEOUT")
    async def timeout():
        event_room_id = __live_danmaku.room_display_id
        reload_room_info(update_room_id=event_room_id, room_info=roomInfos[event_room_id])

    @__live_danmaku.on("ALL")
    async def any_event(event):
        event_room_id = event['room_display_id']
        if event['type'] == 'DM_INTERACTION':
            await handle_dm_interaction(event=event,
                                        database=mydb,
                                        master_config=masterConfig,
                                        room_info=roomInfos[event_room_id])
        elif event['type'] in {'SUPER_CHAT_MESSAGE', 'SUPER_CHAT_MESSAGE_JPN'}:
            await handle_super_chat_message(event=event,
                                            database=mydb,
                                            master_config=masterConfig,
                                            room_info=roomInfos[event_room_id])
        if event['type'] not in event_types:
            print(event)
            event_types.add(event['type'])


for room_id in ROOM_IDS:
    bind(roomInfos[room_id]['live_danmaku'])

if __name__ == "__main__":
    sync(asyncio.gather(*[roomInfos[room_id]['live_danmaku'].connect() for room_id in ROOM_IDS]))
