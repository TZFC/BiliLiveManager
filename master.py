import asyncio
from datetime import datetime
from json import load

from bilibili_api import Danmaku, sync
from bilibili_api.live import LiveDanmaku, LiveRoom
from mysql.connector import connect

from CredentialGetter import getCredential
from EmailSender import send_mail_async
from Summarizer import summarize
from Utils.BanWithTimeout import ban_with_timeout
from Utils.EVENT_IDX import Index

masterConfig = load(open("Configs/masterConfig.json"))
ROOM_IDS = masterConfig["room_ids"]
roomConfigs = {room: load(open(f"Configs/config{room}.json")) for room in ROOM_IDS}
masterCredentials = {room: getCredential(roomConfigs[room]["master"]) for room in ROOM_IDS}
liveDanmakus = {room: LiveDanmaku(room, credential=masterCredentials[room]) for room in ROOM_IDS}
liveRooms = {room: LiveRoom(room, credential=masterCredentials[room]) for room in ROOM_IDS}
mydb = connect(**load(open("Configs/mysql.json")))


def bind(room: LiveDanmaku):
    __room = room

    @__room.on("SEND_GIFT")
    async def gift(event):
        room_id = event['room_display_id']
        # 解封用户
        if not roomConfigs[room_id]["feature_flags"]["unban"]:
            return
        sender_uid = event["data"]["data"]["uid"]
        sql = "SELECT reason, time FROM banned WHERE uid=%s AND room_id=%s"
        val = (sender_uid, room_id)
        with mydb.cursor() as cursor:
            cursor.execute(sql, val)
            result = cursor.fetchall()
        try:
            reason, time = result[0]
        except:
            return
        if reason == event['data']['data']['giftName']:
            asyncio.create_task(liveRooms[room_id].unban_user(uid=sender_uid))
            sql = "DELETE FROM banned WHERE uid=%s AND room_id=%s"
            val = (sender_uid, room_id)
            with mydb.cursor() as cursor:
                cursor.execute(sql, val)
            mydb.commit()
        else:
            return

    @__room.on("DANMU_MSG")
    async def recv(event):
        room_id = event['room_display_id']
        received_uid = event["data"]["info"][Index.SENDER_INFO_IDX][Index.SENDER_UID_IDX]
        text = event["data"]["info"][Index.TEXT_IDX]

        # 封禁关键词
        if roomConfigs[room_id]["feature_flags"]["unban"]:
            if event["data"]["info"][0][Index.MSG_TYPE_IDX] == 0:  # only effective on text MSG
                for index in range(len(roomConfigs[room_id]["ban_words"])):
                    banned_word = roomConfigs[room_id]["ban_words"][index]
                    if banned_word in text:
                        asyncio.create_task(ban_with_timeout(liveRoom=liveRooms[room_id],
                                                             uid=received_uid,
                                                             timeout=roomConfigs[room_id]["ban_timeout"][index],
                                                             database=mydb))
                        sql = "INSERT INTO banned (uid, reason, time, room_id) VALUES (%s, %s, %s, %s)"
                        val = (received_uid, roomConfigs[room_id]["unban_gift"][index],
                               datetime.now().strftime('%Y-%m-%d %H:%M:%S'), room_id)
                        with mydb.cursor() as cursor:
                            cursor.execute(sql, val)
                        mydb.commit()

        # 记录弹幕
        sql = "INSERT INTO danmu (name, uid, text, medal_id, medal_level, time, room_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        try:
            medal_room = event["data"]["info"][Index.MEDAL_INFO_IDX][Index.MEDAL_ROOMID_IDX]
            medal_level = event["data"]["info"][Index.MEDAL_INFO_IDX][Index.MEDAL_LEVEL_IDX]
        except:
            medal_room = 0
            medal_level = 0
        val = (event["data"]["info"][Index.SENDER_INFO_IDX][Index.SENDER_USERNAME_IDX],
               received_uid,
               text,
               medal_room,
               medal_level,
               datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
               room_id)
        with mydb.cursor() as cursor:
            cursor.execute(sql, val)
        mydb.commit()

    @__room.on("LIVE")
    async def liveStart(event):
        if "live_time" not in event["data"].keys():
            # 直播姬开播会有两次LIVE，其中一次没有live_time，以此去重
            return
        # 重载直播间设置, 刷新Credential
        for check_room_id in ROOM_IDS:
            roomConfigs[check_room_id] = load(open(f"Configs/config{check_room_id}.json"))
            masterCredentials[check_room_id] = getCredential(roomConfigs[check_room_id]["master"])
            liveDanmakus[check_room_id].credential = masterCredentials[check_room_id]
            liveRooms[check_room_id].credential = masterCredentials[check_room_id]
        room_id = event['room_display_id']
        async with asyncio.TaskGroup() as tg:
            # 发送开播提醒
            info = await liveRooms[room_id].get_room_info()
            title = info['room_info']['title']
            image = info['room_info']['cover']
            area = info['room_info']['area_name']
            tg.create_task(send_mail_async(sender=masterConfig["username"], to=roomConfigs[room_id]["listener_email"],
                                           subject=f"{roomConfigs[room_id]['nickname']}开始直播{title}",
                                           text=f"{event}", mimeText=area, image=image))

            # 发送打招呼弹幕
            tg.create_task(liveRooms[room_id].send_danmaku(Danmaku("来啦！")))

            # 记录开播时间
            sql = "INSERT INTO liveTime (room_id, start) VALUES (%s, %s)"
            val = (room_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            with mydb.cursor() as cursor:
                cursor.execute(sql, val)
            mydb.commit()

    @__room.on("PREPARING")
    async def liveEnd(event):
        async with asyncio.TaskGroup() as tg:
            room_id = event['room_display_id']

            # 记录下播时间
            sql = "UPDATE liveTime SET end = %s WHERE room_id = %s AND end IS NULL"
            val = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), room_id)
            with mydb.cursor() as cursor:
                cursor.execute(sql, val)
            mydb.commit()

            # 提炼路灯邮件文 及 跳转文
            email_text, jump_text, start_time, end_time = summarize(room_id)
            if not any([email_text, jump_text, start_time, end_time]):
                return

            # 寄出邮件
            if email_text:
                tg.create_task(
                    send_mail_async(sender=masterConfig["username"], to=roomConfigs[room_id]["listener_email"],
                                    subject=f"{roomConfigs[room_id]['nickname']}于{start_time}路灯",
                                    text=email_text, mimeText=f"{event}"))
            else:
                tg.create_task(
                    send_mail_async(sender=masterConfig["username"], to=roomConfigs[room_id]["listener_email"],
                                    subject=f"{roomConfigs[room_id]['nickname']}于{start_time}路灯",
                                    text="本期无路灯", mimeText=f"{event}"))

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

if __name__ == "__main__":
    sync(asyncio.gather(*[room.connect() for room in liveDanmakus.values()]))
