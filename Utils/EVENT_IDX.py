TEXT_IDX = 1
SENDER_INFO_IDX = 2
TIMESTAMP_IDX = 9
MEDAL_INFO_IDX = 3
SENDER_UID_IDX = 0
SENDER_USERNAME_IDX = 1
MEDAL_LEVEL_IDX = 0
MEDAL_NAME_IDX = 1
MEDAL_USERNAME_IDX = 2
MEDAL_ROOMID_IDX = 3
MEDAL_STREAMERUID_IDX = -1
MSG_TYPE_IDX = 12  # event["data"]["info"][0][MSG_TYPE_IDX] text:0 ; emoticon:1
TEXT_TYPE = 0
EMOTICON_TYPE = 1
LIVE_STATUS_STREAMING = 1
DM_INTERACTION_ONGOING = 4
DM_INTERACTION_END = 5

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
    'GOTO_BUY_FLOW', 'SUPER_CHAT_MESSAGE_DELETE', 'WARNING', 'FULL_SCREEN_SPECIAL_EFFECT', 'RING_STATUS_CHANGE',
    'RING_STATUS_CHANGE_V2', 'ANCHOR_LOT_CHECKSTATUS', 'ANCHOR_LOT_START', 'ANCHOR_LOT_END', 'ANCHOR_LOT_AWARD',
    'room_admin_entrance', 'ROOM_ADMINS', 'PLAYTOGETHER_ICON_CHANGE', 'ANCHOR_HELPER_DANMU', 'PK_BATTLE_RANK_CHANGE',
    'SUPER_CHAT_ENTRANCE', 'ROOM_BLOCK_MSG', 'ROOM_CONTENT_AUDIT_REPORT', 'MESSAGEBOX_USER_GAIN_MEDAL', 'CARD_MSG',
    'GIFT_BOARD_RED_DOT', 'CONFIRM_AUTO_FOLLOW', 'LIKE_GUIDE_USER', 'POPULAR_RANK_GUIDE_CARD',
    'POPULARITY_RED_POCKET_V2_NEW', 'POPULARITY_RED_POCKET_V2_START', 'POPULARITY_RED_POCKET_V2_WINNER_LIST'}
