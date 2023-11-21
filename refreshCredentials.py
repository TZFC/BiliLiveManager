from json import load
import os

from bilibili_api import sync
from mysql.connector import connect

from CredentialGetter import getCredential

# from Utils.EmailSender import sendEmail

path = os.getcwd()

# Hard coding 'tzfc' for now. Will iterate through user list when needed
masterConfig = load(open(os.path.join(path, "Configs/masterConfig.json")))
for master in masterConfig["masters"]:
    credential = getCredential(master)
    if sync(credential.check_refresh()):
        sync(credential.refresh())
        sql = "UPDATE credentials SET sessdata = %s, bili_jct = %s, buvid3 = %s, ac_time_value = %s WHERE user = %s"
        val = (credential.sessdata, credential.bili_jct, credential.buvid3, credential.ac_time_value. master)
        with connect(**load(open(os.path.join(path, "mysql.json")))) as mydb:
            with mydb.cursor() as cursor:
                cursor.execute(sql, val)
                mydb.commit()
