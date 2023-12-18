import os
from json import load

from bilibili_api.live import LiveDanmaku, LiveRoom

from Utils.CredentialGetter import get_credential

path = os.getcwd()


def reload_room_config(update_room_id: int, room_config: dict):
    # 重载直播间设置, 刷新Credential
    with open(os.path.join(path, f"Configs/config{update_room_id}.json")) as update_roomConfigFile:
        update_config = load(update_roomConfigFile)
    update_credential = get_credential(update_config["master"])
    room_config['room_config'] = update_config
    room_config['master_credential'] = update_credential
    room_config['live_danmaku'] = LiveDanmaku(update_room_id, credential=update_credential)
    room_config['live_room'] = LiveRoom(update_room_id, credential=update_credential)
    if 'state' not in room_config:
        room_config['state'] = {'pre-checkin': False}
