import os
import re
import time
from datetime import datetime, timedelta
from json import load

from bilibili_api import sync
from bilibili_api.channel_series import ChannelSeries, ChannelSeriesType, ChannelOrder
from bilibili_api.comment import send_comment, CommentResourceType
from bilibili_api.user import User
from mysql.connector import connect

from Utils.ReloadRoomConfig import reload_room_config

path = os.getcwd()
with open(os.path.join(path, "Configs/masterConfig.json")) as masterConfigFile:
    masterConfig = load(masterConfigFile)
with open(os.path.join(path, "Configs/mysql.json")) as mysqlFile:
    mydb = connect(**load(mysqlFile))

ROOM_IDS = masterConfig["room_ids"]
roomConfigs = {}
for room_id in ROOM_IDS:
    roomConfigs[room_id] = {}
    reload_room_config(update_room_id=room_id, room_config=roomConfigs[room_id])

with mydb.cursor() as cursor:
    for room_id in ROOM_IDS:
        if not roomConfigs[room_id]['room_config']["feature_flags"]["replay_comment"]:
            continue
        # get available summaries
        sql = "SELECT start, summary FROM liveTime WHERE room_id=%s AND end IS NOT NULL AND summary IS NOT NULL ORDER BY start"
        val = (room_id,)
        cursor.execute(sql, val)
        summaries = cursor.fetchall()
        if not summaries:
            continue

        # get all videos details in repo
        repo = roomConfigs[room_id]['room_config']["repo"]
        split_repo = repo.split("/")
        if split_repo[-1] == "video":
            uid = split_repo[-2]
            repo_owner = User(uid=uid, credential=roomConfigs[room_id]['master_credential'])
            videos = sync(repo_owner.get_videos())
            details = videos['list']['vlist']
        else:
            uid = split_repo[-3]
            channel_series_type = ChannelSeriesType.SERIES if "series" in split_repo[-1] else ChannelSeriesType.SEASON
            series_id = eval(re.search(r"sid=\d*", split_repo[-1]).group()[4:])
            while True:
                try:
                    channel = ChannelSeries(uid=uid, type_=channel_series_type, id_=series_id,
                                            credential=roomConfigs[room_id]['master_credential'])
                    break
                except:
                    time.sleep(1)
            if channel_series_type == ChannelSeriesType.SERIES:
                videos = sync(channel.get_videos())
            else:
                videos = sync(channel.get_videos(ChannelOrder.CHANGE))
            details = videos['archives']

        # check if there is new video
        sql = "SELECT aid FROM postProgress WHERE room_id=%s"
        val = (room_id,)
        cursor.execute(sql, val)
        prev_aid = cursor.fetchall()[0][0]
        if prev_aid == details[0]['aid']:
            continue

        # match each available summary with videos
        success = []
        for i in reversed(range(min(len(summaries), len(details)))):
            title = details[i]["title"]
            four_part_date = re.search(r"(\d+)年(\d+)月(\d+)日(\d+)点", title)
            if four_part_date:
                year, month, day, hour = four_part_date.groups()
                video_date = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour))
            else:
                three_part_date = re.search(r"(\d+)-(\d+)-(\d+)", title)
                if not three_part_date:
                    # TODO: log error here. Only four and three part dates are allowed
                    continue
                year, month, day = three_part_date.groups()
                hour = None
                video_date = datetime(year=int(year), month=int(month), day=int(day))
            for start, summary in summaries:
                if (start, summary) in success:
                    continue
                if hour is None:
                    if start.year == video_date.year and start.month == video_date.month and start.day == video_date.day:
                        if summary != "N/A":
                            sync(send_comment(text=summary, oid=details[i]['aid'], type_=CommentResourceType.VIDEO,
                                              credential=roomConfigs[room_id]['master_credential']))
                        success.append((start, summary))
                        break
                else:
                    if abs(start - video_date) < timedelta(hours=1):
                        if summary != "N/A":
                            sync(send_comment(text=summary, oid=details[i]['aid'], type_=CommentResourceType.VIDEO,
                                              credential=roomConfigs[room_id]['master_credential']))
                        success.append((start, summary))
                        break

        # remove success matches from database
        for start, summary in success:
            sql = "DELETE FROM liveTime WHERE room_id=%s AND start=%s AND summary=%s"
            val = (room_id, start, summary)
            cursor.execute(sql, val)
            mydb.commit()

        # update postProgress
        sql = "UPDATE postProgress SET aid=%s WHERE room_id=%s"
        val = (details[0]['aid'], room_id)
        cursor.execute(sql, val)
        mydb.commit()
