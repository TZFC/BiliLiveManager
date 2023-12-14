import os
import time
from json import load

from bilibili_api import sync, Danmaku
from mysql.connector import connect

from Utils.EVENT_IDX import LIVE_STATUS_STREAMING
from Utils.ReloadRoomConfig import reload_room_config

path = os.getcwd()
with open(os.path.join(path, "Configs/masterConfig.json")) as masterConfigFile:
    masterConfig = load(masterConfigFile)
with open(os.path.join(path, "Configs/mysql.json")) as mysqlFile:
    mydb = connect(**load(mysqlFile))

ROOM_IDS = masterConfig["room_ids"]
roomConfigs = {}
for room_id in ROOM_IDS:
    roomConfigs[room_id] = {}
    reload_room_config(update_room_id=room_id, room_config=roomConfigs[room_id])
    if not roomConfigs[room_id]['room_config']["feature_flags"]["renqi_remind"]:
        continue
    # 查询是否正在直播
    info = sync(roomConfigs[room_id]['live_room'].get_room_info())
    live_status = info['room_info']['live_status']
    if live_status != LIVE_STATUS_STREAMING:
        continue
    # 查询是否已经直播至少一小时
    live_start_time = info['room_info']['live_start_time']
    if live_start_time + 3600 > time.time():
        continue
    sync(roomConfigs[room_id]['live_room'].send_danmaku(Danmaku("点点上方免费人气票！")))
    sync(roomConfigs[room_id]['live_room'].send_popular_ticket())
    time.sleep(5)
