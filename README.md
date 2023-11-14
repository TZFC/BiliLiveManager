# BiliLiveManager

Basic features:
  Send email on Live start
  Send email with danmaku preceded by keyword on Live end

Optional features:
  Send comment to jump to marked timestamp under livestream replay
  Send reminder on the hour
  Ban/Unban users on keywords
  Record and report active user ranking
Welcome to the BiliLiveManager wiki!

# How to deploy?
## 1. Install python **3.11** and dependencies
Note: python3.10 and python3.12 WILL NOT WORK

Create virtual environment
```
python3.11 -m venv py311
```

Activate virtual environment
```
source py311/bin/activate
```

Install dependencies
```
pip install -r requirements.txt
```
## 2. Clone this repo
```
git clone https://github.com/TZFC/BiliLiveManager
```
Note: Use the production branch if you already have ./Configs

## 3. Create mysql database
Fill information into [Configs/mysql.json](https://github.com/TZFC/BiliLiveManager/blob/main/Configs/mysql.json)

Create table credentials
```
CREATE TABLE credentials (user VARCHAR, sessdata VARCHAR, bili_jct VARCHAR, buvid3 VARCHAR, ac_time_value VARCHAR)
```

Create table liveTime
```
CREATE TABLE credentials (room_id INT, start TIMESTAMP, end TIMESTAMP, summary VARCHAR)
```

Create table danmu
```
CREATE TABLE danmu (name VARCHAR, uid INT, text VARCHAR, medal_id INT, medal_level INT, time TIMESTAMP, room_id INT)
```

## 4. Log into bilibili.com in **PRIVATE** browser window
Get credentials following [this guide](https://nemo2011.github.io/bilibili-api/#/get-credential)

Store your credentials in database

User is your custom nickname
```
from json import load
from mysql.connector import connect
mydb = connect(**load(open("Configs/mysql.json")))
cur = mydb.cursor()
sql = "INSERT INTO credentials (user, sessdata, bili_jct, buvid3, ac_time_value) VALUES (%s, %s, %s, %s, %s)"
val = (USER, SESSDATA, BILI_JCT, BUVID3, AC_TIME_VALUE)
cur.execute(sql, val)
mydb.commit()
```

## 5. Get gmail credentials
Get gmail app password following [this guide](https://support.google.com/mail/answer/185833?hl=en)

Fill your email address and app password into username and password fields of [Configs/masterCongid.json](https://github.com/TZFC/BiliLiveManager/blob/main/Configs/masterConfig.json)

## 6. Fill in which Stream to monitor
Fill the room id into room_ids of [Configs/masterConfig.json](https://github.com/TZFC/BiliLiveManager/blob/main/Configs/masterConfig.json)

Note: Put room id in quote!

## 7. Create a config{room_id}.json per streamer
See template [Configs/config{room_id}.json](https://github.com/TZFC/BiliLiveManager/blob/main/Configs/config%7Broom_id%7D.json)

Note: Feature flag 0 is OFF ; 1 is ON

## 8. Run master.py
```
python master.py &
```

## 9. (optional) Run refreshCredentials.py
You may want to set a cron job to run it daily at noon
```
crontab -e
```
```
0 12 * * * python refreshCredentials.py
```
