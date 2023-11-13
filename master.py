import asyncio

from bilibili_api import Credential, Danmaku, sync
from bilibili_api.live import LiveDanmaku, LiveRoom
from json import load
from mysql.connector import connect
from datetime import datetime
from CredentialGetter import getCredential
from EmailSender import send_mail_async
from Summarizer import summarize

BANNED = {"看", "动", "太", "泰", "态", "有"}
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

masterConfig = load(open(f"Configs/masterConfig.json"))
ROOM_IDS = masterConfig["room_ids"]
roomConfigs = {room: load(open(f"Configs/config{room}.json")) for room in ROOM_IDS}
masterCredentials = {room: getCredential(roomConfigs[room]["master"]) for room in ROOM_IDS}
liveDanmakus = {room: LiveDanmaku(room, credential=masterCredentials[room]) for room in ROOM_IDS}
liveRooms = {room: LiveRoom(room, credential=masterCredentials[room]) for room in ROOM_IDS}
mydb = connect(**load(open("Configs/mysql.json")))

def bind(room: LiveDanmaku):
    __room = room
    # FIXME : Multi[le LIVE triggered, why?
    @__room.on("DANMU_MSG")
    async def recv(event):
        room_id = event['room_display_id']
        received_uid = event["data"]["info"][SENDER_INFO_IDX][SENDER_UID_IDX]
        text = event["data"]["info"][TEXT_IDX]
        # 封禁片哥
        if roomConfigs[room_id]["feature_flags"]["ban"]:
            if text in BANNED:
                await liveRooms[room_id].ban_user(uid=received_uid)
                return
        # 记录弹幕
        sql = "INSERT INTO danmu (name, uid, text, medal_id, medal_level, time, room_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        try:
            medal_room = event["data"]["info"][MEDAL_INFO_IDX][MEDAL_ROOMID_IDX]
            medal_level = event["data"]["info"][MEDAL_INFO_IDX][MEDAL_LEVEL_IDX]
        except:
            medal_room = 0
            medal_level = 0
        val = (event["data"]["info"][SENDER_INFO_IDX][SENDER_USERNAME_IDX],
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
        room_id = event['room_display_id']
        sql = "SELECT * FROM liveTime WHERE room_id = %s AND end IS NULL"
        val = (room_id,)
        with mydb.cursor() as cursor:
            cursor.execute(sql, val)
            res = cursor.fetchall()
        if res:
            # Dupilicated LIVE event, why?
            return
        async with asyncio.TaskGroup() as tg:
            # 发送开播提醒
            info = await liveRooms[room_id].get_room_info()
            title = info['room_info']['title']
            image = info['room_info']['cover']
            tg.create_task(send_mail_async(sender=masterConfig["username"], to=roomConfigs[room_id]["listener_email"],
                                           subject=f"{roomConfigs[room_id]['nickname']}开始直播{title}",
                                           text=f"{title}", image = None))

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
        room_id = event['room_display_id']
        # FIXME: duplicate LIVE events?
        # 删除重复开播记录
        with mydb.cursor() as cur:
            sql = "SELECT * FROM liveTime WHERE room_id = %s AND summary IS NULL"
            val = (room_id,)
            cur.execute(sql, val)
            result = cur.fetchall()
            start = result[0][1]
            sql = "DELETE FROM liveTime WHERE room_id = %s AND summary IS NULL"
            val = (room_id,)
            cur.execute(sql, val)
            mydb.commit()
            sql = "INSERT INTO liveTime (room_id, start) VALUES (%s, %s)"
            val = (room_id, start)
            cur.execute(sql, val)
            mydb.commit()

        # 记录下播时间
        sql = "UPDATE liveTime SET end = %s WHERE room_id = %s AND end IS NULL"
        val = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), room_id)
        with mydb.cursor() as cursor:
            cursor.execute(sql, val)
        mydb.commit()

        # 提炼路灯邮件文 及 跳转文
        email_text, jump_text, start_time, end_time = summarize(room_id)

        # 寄出邮件
        if email_text:
            await send_mail_async(sender=masterConfig["username"], to=roomConfigs[room_id]["listener_email"],
                                  subject=f"{roomConfigs[room_id]['nickname']}于{start_time}路灯",
                                  text=email_text)
        else:
            await send_mail_async(sender=masterConfig["username"], to=roomConfigs[room_id]["listener_email"],
                                  subject=f"{roomConfigs[room_id]['nickname']}于{start_time}路灯",
                                  text="本期无路灯")

        if roomConfigs[room_id]["feature_flags"]["replay_comment"]:
            # 记录路灯跳转
            sql = "UPDATE liveTime SET summary = %s WHERE room_id = %s AND summary IS NULL"
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
