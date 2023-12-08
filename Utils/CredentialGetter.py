from json import load

from bilibili_api import Credential
from mysql.connector import connect


def get_credential(master: str) -> Credential:
    with connect(**load(open("Configs/mysql.json"))) as mydb:
        with mydb.cursor() as cursor:
            cursor.execute(
                f"SELECT sessdata, bili_jct, buvid3, ac_time_value, dedeuserid FROM credentials WHERE master = '{master}'")
            sessdata, bili_jct, buvid3, ac_time_value, dedeuserid = cursor.fetchone()
    credential = Credential(sessdata=sessdata, bili_jct=bili_jct, buvid3=buvid3, ac_time_value=ac_time_value, dedeuserid=dedeuserid)
    return credential
