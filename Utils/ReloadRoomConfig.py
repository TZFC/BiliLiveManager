import os
from json import load

from bilibili_api.live import LiveDanmaku, LiveRoom

from Utils.CredentialGetter import get_credential

path = os.getcwd()


def load_room_info(room_id: int, room_info: dict):
    # 加载直播间设置
    with open(os.path.join(path, f"Configs/config{room_id}.json")) as roomConfigFile:
        config = load(roomConfigFile)
    credential = get_credential(config["master"])
    room_info['room_config'] = config
    room_info['master_credential'] = credential
    room_info['live_danmaku'] = LiveDanmaku(room_id, credential=credential)
    room_info['live_room'] = LiveRoom(room_id, credential=credential)
