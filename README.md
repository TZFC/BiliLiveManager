# BiliLiveManager

Basic features:
Send email on Live start
Send email with danmaku preceded by keyword on Live end

Optional features:
Send comment to jump to marked timestamp under livestream replay
Send reminder on the hour
Ban/Unban users on keywords and gift
Record and report active user ranking

# How to deploy (tested with AWS EC2 Ubuntu & AWS RDS mysql)?

## 1. Prepare virtual environment on EC2 Ubuntu

Note: Allow internet access from 0.0.0.0/0 when setting up EC2

Note: python3.10 and python3.12 WILL NOT WORK

```
sudo apt update
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.11 -y
screen -S BLM
git clone https://github.com/TZFC/BiliLiveManager
cd BiliLiveManager
python3.11 -m venv py311
source py311/bin/activate
pip install -r requirements.txt
```

## 2. Create mysql database

Remember to allow access from your EC2 instance when setting up database

Fill database access information into mysql.json
```
vim Configs/mysql.json
```

Create tables

```
CREATE TABLE credentials (master VARCHAR(255), sessdata VARCHAR(255), bili_jct VARCHAR(255), buvid3 VARCHAR(255), dedeuserid VARCHAR(255), ac_time_value VARCHAR(255))
CREATE TABLE liveTime (room_id INT, start TIMESTAMP, end TIMESTAMP, summary VARCHAR(255))
CREATE TABLE danmu (name VARCHAR(255), uid INT, text VARCHAR(255), type INT, medal_id INT, medal_level INT, time TIMESTAMP, room_id INT, danmu_id VARCHAR(255) UNIQUE)
CREATE TABLE banned (uid INT, reason VARCHAR(255), time TIMESTAMP, room_id INT)
CREATE TABLE postProgress (room_id INT, aid INT)
CREATE TABLE checkin (uid INT, room_id INT, name VARCHAR(255), slot_0 INT, slot_1 INT, slot_2 INT, slot_3 INT, slot_4 INT, slot_5 INT, slot_6 INT, slot_7 INT, slot_8 INT, slot_9 INT, slot_10 INT, slot_11 INT, slot_12 INT, slot_13 INT, slot_14 INT, slot_15 INT, slot_16 INT, slot_17 INT, slot_18 INT, slot_19 INT, slot_20 INT, slot_21 INT, slot_22 INT, slot_23 INT, slot_24 INT, slot_25 INT, slot_26 INT, slot_27 INT, slot_28 INT, slot_29 INT, count INT AS SUM(slot_0, slot_1, slot_2, slot_3, slot_4, slot_5, slot_6, slot_7, slot_8, slot_9, slot_10, slot_11, slot_12, slot_13, slot_14, slot_15, slot_16, slot_17, slot_18, slot_19, slot_20, slot_21, slot_22, slot_23, slot_24, slot_25, slot_26, slot_27, slot_28, slot_29), all_time INT, UNIQUE (uid, room_id))
CREATE TABLE blacklist (uid INT)
```


## 3. Log into bilibili.com in **PRIVATE** browser window

Get credentials following [this guide](https://nemo2011.github.io/bilibili-api/#/get-credential)

Store your credentials in database, give this account a nickname as master
```
python
from json import load
from mysql.connector import connect
mydb = connect(**load(open("Configs/mysql.json")))
cur = mydb.cursor()
sql = "UPDATE credentials SET sessdata=%s, bili_jct=%s, buvid3=%s, dedeuserid=%s, ac_time_value=%s WHERE master=%s"
val = ("<sessdata>", "<bili_jct>", "<buvid3>","<dedeuserid>", "<ac_time_value>", "<master>")
cur.execute(sql, val)
mydb.commit()
quit()
```

## 4. Get gmail credentials

Get gmail app password following [this guide](https://support.google.com/mail/answer/185833?hl=en)

Rename and fill [Configs/masterCongid.json](https://github.com/TZFC/BiliLiveManager/blob/main/Configs/masterConfig.json)

## 5. Fill in which Stream(s) to monitor

Fill the room id, and the account nickname into room_ids
of [Configs/masterConfig.json](https://github.com/TZFC/BiliLiveManager/blob/main/Configs/masterConfig.json)

Note: Put room_id in quotes!

## 6. Create a config{room_id}.json per stream

See
template [Configs/config{room_id}.json](https://github.com/TZFC/BiliLiveManager/blob/main/Configs/config%7Broom_id%7D.json)

Note: Feature flag 0 is OFF ; 1 is ON

## 7. Run master.py

```
python master.py 1>output.txt 2>error.txt &
```

## 8. Install and run apache server

```
sudo apt install apache2
sudo chown -R ubuntu /var/www
sudo service apache2 restart
cd var/www/html
```

modify index.html and {room_id}.html according to [web/index.html](https://github.com/TZFC/BiliLiveManager/blob/53e430c98d2f5a1c634a47efe8c0043544fdc287/web/index.html)

When used in obs/哔哩哔哩直播姬：

'browser source' -> <EC2_public_ip>/{room_id}.html -> banner_style.css

## 9. set cron jobs


```
55 * * * * cd /home/ubuntu/BiliLiveManager && py311/bin/python popularTicketRemind.py 2> popout.txt &
5 * * * * cd /home/ubuntu/BiliLiveManager && py311/bin/python refreshCredentials.py 2> refout.txt &
10 * * * * cd /home/ubuntu/BiliLiveManager && py311/bin/python postReplayComment.py 2> postout.txt &
@reboot cd /home/ubuntu/BiliLiveManager && py311/bin/python master.py 1>out.txt 2>newerror.txt &
@reboot sudo /etc/init.d/apache2 restart
```

