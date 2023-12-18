import asyncio
from datetime import datetime

from Utils.BanOnKeyword import ban_on_keyword
from Utils.Checkin import record_checkin
from Utils.EVENT_IDX import *
from Utils.RecordDanmaku import record_danmaku
from Utils.SendReportCheckin import send_report_checkin
from Utils.TopCheckin import get_top_k_checkin
from Utils.Uid2Username import uid2username
from web.UpdatePage import update_page


async def handle_danmu_msg(event, database, master_config, live_room, room_config, credential):
    room_id = event['room_display_id']
    received_uid = event["data"]["info"][SENDER_INFO_IDX][SENDER_UID_IDX]
    text = event["data"]["info"][TEXT_IDX]
    message_type = event["data"]["info"][0][MSG_TYPE_IDX]

    async with (asyncio.TaskGroup() as tg):
        # 主播及master指令
        streamer_uid = await live_room._LiveRoom__get_ruid()
        if received_uid in {room_config['master_credential'].dedeuserid, streamer_uid}:
            if "checkin" in text:
                info = await room_config['live_room'].get_room_info()
                live_status = info['room_info']['live_status']
                if live_status == LIVE_STATUS_STREAMING \
                        and room_config["feature_flags"]["checkin"] \
                        and not room_config['state']['pre-checkin']:
                    with database.cursor() as cursor:
                        sql = "SELECT start FROM liveTime WHERE room_id = %s AND end IS NULL AND summary IS NULL"
                        val = (room_id,)
                        cursor.execute(sql, val)
                        start_time = cursor.fetchall()[0][0]
                    # 统计直播间发言人
                    await record_checkin(start_time=start_time,
                                         end_time=datetime.fromtimestamp(event['data']["info"][TIMESTAMP_IDX]['ts']),
                                         master=room_config['master'],
                                         room_id=room_id,
                                         checkin_days=room_config['checkin_days'],
                                         database=database)
                    top_uid_count = await get_top_k_checkin(master_uid=credential.dedeuserid,
                                                            room_id=room_id, database=database, top_k=10)
                    top_uid_username_count = await asyncio.gather(*map(uid2username, top_uid_count))
                    tg.create_task(send_report_checkin(live_room=live_room, top_uid_username_count=top_uid_username_count))
                    tg.create_task(update_page(target=f"/var/www/html/{room_id}.html",
                                               checkin_days=room_config['checkin_days'],
                                               content=top_uid_username_count))
                    room_config['state']['pre-checkin'] = True
        # 封禁关键词
        if room_config["feature_flags"]["unban"]:
            tg.create_task(ban_on_keyword(text=text,
                                          message_type=message_type,
                                          received_uid=received_uid,
                                          room_id=room_id,
                                          live_room=live_room,
                                          room_config=room_config,
                                          database=database))
        # 记录弹幕
        try:
            medal_room = event["data"]["info"][MEDAL_INFO_IDX][MEDAL_ROOMID_IDX]
            medal_level = event["data"]["info"][MEDAL_INFO_IDX][MEDAL_LEVEL_IDX]
        except:
            medal_room = 0
            medal_level = 0
        tg.create_task(record_danmaku(name=event["data"]["info"][SENDER_INFO_IDX][SENDER_USERNAME_IDX],
                                      received_uid=received_uid,
                                      time=datetime.fromtimestamp(event['data']["info"][TIMESTAMP_IDX]['ts']),
                                      medal_room=medal_room,
                                      medal_level=medal_level,
                                      text=text,
                                      message_type=message_type,
                                      room_id=room_id,
                                      danmu_id=None,
                                      database=database))
