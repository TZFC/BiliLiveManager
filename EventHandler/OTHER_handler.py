import asyncio
from datetime import datetime
from json import loads

from Utils.Checkin import record_checkin
from Utils.EVENT_IDX import *
from Utils.RecordDanmaku import record_danmaku
from Utils.SendReportCheckin import send_report_checkin
from Utils.TopCheckin import get_top_checkin
from web.UpdatePage import update_page


async def handle_dm_interaction(event, database, master_config, room_info):
    room_id = event['room_display_id']
    try:
        data = loads(event['data']['data']['data'])
        content = "--" + data['combo'][0]['content']
        event_id = event['data']['data']['id']
        if any(live_end_word in data['combo'][0]['content'] for live_end_word in {"晚安", "午安", "拜拜"}):
            info = await room_info['live_room'].get_room_info()
            live_status = info['room_info']['live_status']
            if live_status == LIVE_STATUS_STREAMING \
                    and room_info['room_config']["feature_flags"]["checkin"] \
                    and not room_info['state']['pre-checkin']:
                room_info['state']['pre-checkin'] = True
                async with asyncio.TaskGroup() as tg:
                    with database.cursor() as cursor:
                        sql = "SELECT start FROM liveTime WHERE room_id = %s AND end IS NULL AND summary IS NULL"
                        val = (room_id,)
                        cursor.execute(sql, val)
                        start_time = cursor.fetchall()[0][0]
                    # 统计直播间发言人
                    await record_checkin(start_time=start_time,
                                         end_time=datetime.fromtimestamp(event['data']["info"][TIMESTAMP_IDX]['ts']),
                                         master=room_info['room_config']['master'],
                                         room_id=room_id,
                                         checkin_days=room_info['room_config']['checkin_days'],
                                         database=database)
                    top_uid_name_count = await get_top_checkin(master_uid=room_info['master_credential'].dedeuserid,
                                                               room_id=room_id, database=database)
                    tg.create_task(send_report_checkin(live_room=room_info['live_room'],
                                                       top_uid_username_count=top_uid_name_count))
                    tg.create_task(update_page(target=f"/var/www/html/{room_id}.html",
                                               checkin_days=room_info['room_config']['checkin_days'],
                                               content=top_uid_name_count))
            return
        await record_danmaku(name="他们都在说", received_uid=0, time=datetime.now().replace(microsecond=0),
                             medal_room=room_id, medal_level=99, text=content, message_type=TEXT_TYPE, room_id=room_id,
                             danmu_id=event_id, database=database)
        return
    except Exception as e:
        print(event)
        print(e)


async def handle_super_chat_message(event, database, master_config, room_info):
    room_id = event['room_display_id']
    try:
        name = event['data']['data']['user_info']['uname']
        uid = event['data']['data']['uid']
        timestamp = event['data']['data']['ts']
        content = event['data']['data']['message']
        try:
            medal_room = event['data']['data']["medal_info"]['anchor_roomid']
            medal_level = event['data']['data']["medal_info"]['medal_level']
        except:
            medal_room = 0
            medal_level = 0
        await record_danmaku(name=name, received_uid=uid, time=datetime.fromtimestamp(timestamp), medal_room=medal_room,
                             medal_level=medal_level, text=content, message_type=TEXT_TYPE, room_id=room_id,
                             danmu_id=None, database=database)
    except:
        pass
