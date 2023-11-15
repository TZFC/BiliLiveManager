from json import load

from bilibili_api import Credential
from mysql.connector import connect


def getCredential(user: str) -> Credential:
    with connect(**load(open("../Configs/mysql.json"))) as mydb:
        with mydb.cursor() as cursor:
            cursor.execute("SELECT sessdata, bili_jct, buvid3, ac_time_value FROM credentials WHERE user = 'tzfc'")
            sess, jct, bd3, act = cursor.fetchone()
    credential = Credential(sessdata=sess, bili_jct=jct, buvid3=bd3, ac_time_value=act)
    return credential
