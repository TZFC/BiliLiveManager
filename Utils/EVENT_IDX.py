from enum import Enum

class Index(Enum):
    TEXT_IDX = 1
    SENDER_INFO_IDX = 2
    MEDAL_INFO_IDX = 3
    SENDER_UID_IDX = 0
    SENDER_USERNAME_IDX = 1
    MEDAL_LEVEL_IDX = 0
    MEDAL_NAME_IDX = 1
    MEDAL_USERNAME_IDX = 2
    MEDAL_ROOMID_IDX = 3
    MEDAL_STREAMERUID_IDX = -1
    MSG_TYPE_IDX = 12  # event["data"]["info"][0][MSG_TYPE_IDX] text:0 ; emoticon:1