import asyncio
import os
from datetime import datetime
from json import load

from bilibili_api import Danmaku, sync
from bilibili_api.live import LiveDanmaku, LiveRoom
from mysql.connector import connect

from Utils.BanOnKeyword import ban_on_keyword
from Utils.Checkin import record_checkin
from Utils.CredentialGetter import get_credential
from Utils.EVENT_IDX import *
from Utils.EmailSender import send_mail_async
from Utils.RecordDanmaku import record_danmaku
from Utils.Summarizer import summarize
from Utils.Uid2Username import uid2username
from Utils.UnbanOnGift import unban_on_gift
from web.UpdatePage import update_page

path = os.getcwd()
with open(os.path.join(path, "Configs/masterConfig.json")) as masterConfigFile:
    masterConfig = load(masterConfigFile)
ROOM_IDS = masterConfig["room_ids"]
roomConfigs = {}
for room in ROOM_IDS:
    with open(os.path.join(path, f"Configs/config{room}.json")) as roomConfigFile:
        roomConfigs[room] = load(roomConfigFile)
masterCredentials = {room: get_credential(roomConfigs[room]["master"]) for room in ROOM_IDS}
liveDanmakus = {room: LiveDanmaku(room, credential=masterCredentials[room]) for room in ROOM_IDS}
liveRooms = {room: LiveRoom(room, credential=masterCredentials[room]) for room in ROOM_IDS}
with open("Configs/mysql.json") as mysqlFile:
    mydb = connect(**load(mysqlFile))


def bind(room: LiveDanmaku):
    __room = room

    @__room.on("LIVE")
    async def liveStart(event):
        if "live_time" not in event["data"].keys():
            # 直播姬开播会有两次LIVE，其中一次没有live_time，以此去重
            return
        update_credentials()

        room_id = event['room_display_id']

        # 记录开播时间
        sql = "INSERT INTO liveTime (room_id, start) VALUES (%s, %s)"
        val = (room_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        with mydb.cursor() as cursor:
            cursor.execute(sql, val)
        mydb.commit()

        async with asyncio.TaskGroup() as tg:
            # 发送开播提醒
            info = await liveRooms[room_id].get_room_info()
            tg.create_task(send_mail_async(
                sender=masterConfig["username"],
                to=roomConfigs[room_id]["listener_email"],
                subject=f"{roomConfigs[room_id]['nickname']}开始直播{info['room_info']['title']}",
                text=f"https://live.bilibili.com/{room_id}",
                mime_text=info['room_info']['area_name'],
                image=info['room_info']['cover']))

            # 发送打招呼弹幕
            tg.create_task(liveRooms[room_id].send_danmaku(Danmaku("来啦！")))

    @__room.on("SEND_GIFT")
    async def gift(event):
        room_id = event['room_display_id']
        # 解封用户
        if not roomConfigs[room_id]["feature_flags"]["unban"]:
            return
        await unban_on_gift(sender_uid=event["data"]["data"]["uid"],
                            gift=event['data']['data']['giftName'],
                            room_id=room_id,
                            live_room=liveRooms[room_id],
                            database=mydb)

    @__room.on("DANMU_MSG")
    async def recv(event):
        room_id = event['room_display_id']
        received_uid = event["data"]["info"][SENDER_INFO_IDX][SENDER_UID_IDX]
        text = event["data"]["info"][TEXT_IDX]
        message_type = event["data"]["info"][0][MSG_TYPE_IDX]

        # 封禁关键词
        if roomConfigs[room_id]["feature_flags"]["unban"]:
            await ban_on_keyword(text=text,
                                 message_type=message_type,
                                 received_uid=received_uid,
                                 room_id=room_id,
                                 live_room=liveRooms[room_id],
                                 room_config=roomConfigs[room_id],
                                 database=mydb)
        # 记录弹幕
        try:
            medal_room = event["data"]["info"][MEDAL_INFO_IDX][MEDAL_ROOMID_IDX]
            medal_level = event["data"]["info"][MEDAL_INFO_IDX][MEDAL_LEVEL_IDX]
        except:
            medal_room = 0
            medal_level = 0
        await record_danmaku(name=event["data"]["info"][SENDER_INFO_IDX][SENDER_USERNAME_IDX],
                             received_uid=received_uid,
                             medal_room=medal_room,
                             medal_level=medal_level,
                             text=text,
                             message_type=message_type,
                             room_id=room_id,
                             database=mydb)

    @__room.on("PREPARING")
    async def live_end(event):
        room_id = event['room_display_id']

        # 记录下播时间
        sql = "UPDATE liveTime SET end = %s WHERE room_id = %s AND end IS NULL"
        val = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), room_id)
        with mydb.cursor() as cursor:
            cursor.execute(sql, val)
        mydb.commit()

        # 提炼路灯邮件文 及 跳转文
        email_text, jump_text, start_time, end_time = summarize(room_id, database=mydb)

        async with asyncio.TaskGroup() as tg:
            # 寄出邮件
            if email_text:
                tg.create_task(
                    send_mail_async(sender=masterConfig["username"], to=roomConfigs[room_id]["listener_email"],
                                    subject=f"{roomConfigs[room_id]['nickname']}于{start_time}路灯",
                                    text=email_text, mime_text=f"{event}"))
            else:
                tg.create_task(
                    send_mail_async(sender=masterConfig["username"], to=roomConfigs[room_id]["listener_email"],
                                    subject=f"{roomConfigs[room_id]['nickname']}于{start_time}路灯",
                                    text="本期无路灯", mime_text=f"{event}"))

            if roomConfigs[room_id]["feature_flags"]["checkin"]:
                # 统计直播间发言人
                top_uid_count = await record_checkin(start_time=start_time,
                                                     end_time=end_time,
                                                     master=roomConfigs[room_id]['master'],
                                                     room_id=room_id,
                                                     checkin_days=roomConfigs[room_id]['checkin_days'],
                                                     database=mydb)
                top_username_count = await asyncio.gather(*map(uid2username, top_uid_count))
                await update_page(target=f"/var/www/html/{room_id}.html",
                                  checkin_days=roomConfigs[room_id]['checkin_days'],
                                  content=top_username_count)

            if roomConfigs[room_id]["feature_flags"]["replay_comment"]:
                # 记录路灯跳转
                sql = "UPDATE liveTime SET summary = %s WHERE room_id = %s AND end IS NOT NULL AND summary IS NULL"
                if jump_text:
                    val = (jump_text, room_id)
                else:
                    val = ("N/A", room_id)
                with mydb.cursor() as cursor:
                    cursor.execute(sql, val)
                mydb.commit()
            else:
                # 删除直播场次记录
                sql = "DELETE FROM liveTime WHERE room_id = %s"
                val = (room_id,)
                with mydb.cursor() as cursor:
                    cursor.execute(sql, val)
                mydb.commit()

        # 删除弹幕记录
        sql = "DELETE FROM danmu WHERE room_id = %s"
        val = (room_id,)
        with mydb.cursor() as cursor:
            cursor.execute(sql, val)
        mydb.commit()


for room in liveDanmakus.values():
    bind(room)


def update_credentials():
    # 重载直播间设置, 刷新Credential
    for check_room_id in ROOM_IDS:
        with open(f"Configs/config{check_room_id}.json") as configFile:
            roomConfigs[check_room_id] = load(configFile)
        masterCredentials[check_room_id] = get_credential(roomConfigs[check_room_id]["master"])
        liveDanmakus[check_room_id].credential = masterCredentials[check_room_id]
        liveRooms[check_room_id].credential = masterCredentials[check_room_id]


if __name__ == "__main__":
    try:
        sync(asyncio.gather(*[room.connect() for room in liveDanmakus.values()]))
    except Warning:
        update_credentials()
        raise Warning
