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

create virtual environment
```
python3.11 -m venv py311
```

activate virtual environment
```
source py311/bin/activate
```

install dependencies
```
pip install -r requirements.txt
```
## 2. clone this repo
```
git clone https://github.com/TZFC/BiliLiveManager
```
Note: Use the production branch if you already have ./Configs

## 3. create mysql database
fill information into [Configs/mysql.json](https://github.com/TZFC/BiliLiveManager/blob/main/Configs/mysql.json)

## 4. log into bilibili.com in **PRIVATE** browser window
get credentials following [this guide](https://nemo2011.github.io/bilibili-api/#/get-credential)

store your credentials in database

user is your custom nickname
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

## 5. get gmail credentials
get gmail app password following [this guide](https://support.google.com/mail/answer/185833?hl=en)

fill your email address and app password into username and password fields of [Configs/masterCongid.json](https://github.com/TZFC/BiliLiveManager/blob/main/Configs/masterConfig.json)

## 6. fill in which Stream to monitor
fill the room id into room_ids of [Configs/masterCongid.json](https://github.com/TZFC/BiliLiveManager/blob/main/Configs/masterConfig.json)

Note: put room id in quote!

## 7. create a config{room_id}.json per streamer
see template [Configs/config{room_id}.json](https://github.com/TZFC/BiliLiveManager/blob/main/Configs/config%7Broom_id%7D.json)

Note: feature flag 0 is off ; 1 is on

## 8. run master.py
```
python master.py &
```

## 9. (optional) run refreshCredentials.py
you may want to set a cron job to run it daily at midnight
