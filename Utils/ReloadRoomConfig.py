import os
from json import load

from bilibili_api.live import LiveDanmaku, LiveRoom

from Utils.CredentialGetter import get_credential

path = os.getcwd()


def load_room_info(update_room_id: int, room_info: dict):
    # 重载直播间设置, 刷新Credential
    with open(os.path.join(path, f"Configs/config{update_room_id}.json")) as update_roomConfigFile:
        update_config = load(update_roomConfigFile)
    update_credential = get_credential(update_config["master"])
    room_info['room_config'] = update_config
    room_info['master_credential'] = update_credential
    if 'live_danmaku' in room_info:
        room_info['live_danmaku'].credential = update_credential
    else:
        room_info['live_danmaku'] = LiveDanmaku(update_room_id, credential=update_credential)
    room_info['live_room'] = LiveRoom(update_room_id, credential=update_credential)
    if 'state' not in room_info:
        room_info['state'] = {'pre-checkin': False}
