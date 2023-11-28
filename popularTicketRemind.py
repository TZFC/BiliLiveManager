import time
import os
from json import load

from bilibili_api import sync, Danmaku
from bilibili_api.live import LiveRoom

from CredentialGetter import getCredential

path = os.getcwd()
masterConfig = load(open(os.path.join(path, "Configs/masterConfig.json")))
ROOM_IDS = masterConfig["room_ids"]
roomConfigs = {room: load(open(os.path.join(path, f"Configs/config{room}.json"))) for room in ROOM_IDS}
masterCredentials = {room: getCredential(roomConfigs[room]["master"]) for room in ROOM_IDS}
liveRooms = {room: LiveRoom(room, credential=masterCredentials[room]) for room in ROOM_IDS}

for room_id in ROOM_IDS:
    if not roomConfigs[room_id]["feature_flags"]["renqi_remind"]:
        continue
    # 查询是否正在直播
    info = sync(liveRooms[room_id].get_room_info())
    live_status = info['room_info']['live_status']
    if live_status != 1:
        continue
    # 查询是否已经直播至少一小时
    live_start_time = info['room_info']['live_start_time']
    if live_start_time + 3600 > time.time():
        continue
    sync(liveRooms[room_id].send_danmaku(Danmaku("点点上方免费人气票！")))
    sync(liveRooms[room_id].send_popular_ticket())
    time.sleep(5)
