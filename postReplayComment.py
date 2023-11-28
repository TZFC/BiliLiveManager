import re
import time
import os
from json import load
from datetime import datetime, timedelta

from bilibili_api import sync
from mysql.connector import connect

from bilibili_api.channel_series import ChannelSeries, ChannelSeriesType, ChannelOrder
from bilibili_api.comment import send_comment, CommentResourceType

from CredentialGetter import getCredential

path = os.getcwd()
masterConfig = load(open(os.path.join(path, "Configs/masterConfig.json")))
ROOM_IDS = masterConfig["room_ids"]
roomConfigs = {room: load(open(os.path.join(path, f"Configs/config{room}.json"))) for room in ROOM_IDS}
masterCredentials = {room: getCredential(roomConfigs[room]["master"]) for room in ROOM_IDS}
mydb = connect(**load(open("Configs/mysql.json")))

with mydb.cursor() as cursor:
    for room_id in ROOM_IDS:
        if not roomConfigs[room_id]["feature_flags"]["replay_comment"]:
            continue
        # get available summaries
        sql = "SELECT start, summary FROM liveTime WHERE room_id=%s AND end IS NOT NULL AND summary IS NOT NULL ORDER BY start ASC"
        val = (room_id,)
        cursor.execute(sql, val)
        summaries = cursor.fetchall()
        if not summaries:
            continue
        print(f"room {room_id} has available summary {str(summaries)}")

        # get all videos in repo
        repo = roomConfigs[room_id]["repo"]
        split_repo = repo.split("/")
        uid = split_repo[-3]
        channel_series_type = ChannelSeriesType.SERIES if "series" in split_repo[-1] else ChannelSeriesType.SEASON
        series_id = eval(re.search(r"sid=\d*", split_repo[-1]).group()[4:])
        while True:
            try:
                channel = ChannelSeries(uid=uid, type_=channel_series_type.SEASON, id_=series_id,
                                        credential=masterCredentials[room_id])
                break
            except:
                time.sleep(1)
        if channel_series_type == ChannelSeriesType.SERIES:
            videos = sync(channel.get_videos())
        else:
            videos = sync(channel.get_videos(ChannelOrder.CHANGE))
        aids = videos['aids']
        details = videos['archives']
        print(f"the latest video is {details[0]}")

        # check if there is new video
        sql = "SELECT aid FROM postProgress WHERE room_id=%s"
        val = (room_id,)
        cursor.execute(sql, val)
        prev_aid = cursor.fetchall()[0]
        if prev_aid == aids[0]:
            continue
        print(f"last checked video {prev_aid}, newest is {aids[0]}")

        # match each available summary with videos
        success = []
        for i in range(len(summaries)):
            title = details[i]["title"]
            try:
                year, month, day, hour = re.findall(r'\d+', title)[-4:]
            except:
                # TODO: log error here
                continue
            video_date = datetime(year=year, month=month, day=day, hour=hour)
            for start, summary in summaries:
                if (start, summary) in success:
                    continue
                if abs(start - video_date) < timedelta(hours=1):
                    if summary != "N/A":
                        sync(send_comment(text=summary, oid=details[i]['aid'], type_=CommentResourceType.VIDEO,
                                          credential=masterCredentials[room_id]))
                        print(f"summary sent to {details[i]['aid']} with text {summary}")
                    success.append((start, summary))
                    break
        print(f"all success matched are {str(success)}")

        # remove success matches from database
        for start, summary in success:
            sql = "DELETE FROM liveTime WHERE room_id=%s AND start=%s AND summary=%s"
            val = (room_id, start, summary)
            cursor.execute(sql, val)
            mydb.commit()

        # update postProgress
        sql = "UPDATE postProgress SET aid=%s WHERE room_id=%s"
        val = (aids[0], room_id)
        cursor.execute(sql, val)
        mydb.commit()
