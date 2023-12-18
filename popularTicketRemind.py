import os
import time
from json import load

from bilibili_api import sync, Danmaku

from Utils.EVENT_IDX import LIVE_STATUS_STREAMING
from Utils.ReloadRoomConfig import reload_room_info

path = os.getcwd()
with open(os.path.join(path, "Configs/masterConfig.json")) as masterConfigFile:
    masterConfig = load(masterConfigFile)

ROOM_IDS = masterConfig["room_ids"]
roomInfos = {}
for room_id in ROOM_IDS:
    roomInfos[room_id] = {}
    reload_room_info(update_room_id=room_id, room_info=roomInfos[room_id])
    if not roomInfos[room_id]['room_config']["feature_flags"]["renqi_remind"]:
        continue
    # 查询是否正在直播
    info = sync(roomInfos[room_id]['live_room'].get_room_info())
    live_status = info['room_info']['live_status']
    if live_status != LIVE_STATUS_STREAMING:
        continue
    # 查询是否已经直播至少一小时
    live_start_time = info['room_info']['live_start_time']
    if live_start_time + 3600 > time.time():
        continue
    sync(roomInfos[room_id]['live_room'].send_danmaku(Danmaku("点点上方免费人气票！")))
    sync(roomInfos[room_id]['live_room'].send_popular_ticket())
    time.sleep(5)
