import os
from json import load

from bilibili_api import sync
from mysql.connector import connect

from Utils.CredentialGetter import get_credential

# from Utils.EmailSender import sendEmail

path = os.getcwd()

with open(os.path.join(path, "Configs/masterConfig.json")) as masterConfigFile:
    masterConfig = load(masterConfigFile)
for master in masterConfig["masters"]:
    credential = get_credential(master)
    if sync(credential.check_refresh()):
        sync(credential.refresh())
        sql = "UPDATE credentials SET sessdata = %s, bili_jct = %s, buvid3 = %s, ac_time_value = %s WHERE master = %s"
        val = (credential.sessdata, credential.bili_jct, credential.buvid3, credential.ac_time_value, master)
        with open("Configs/mysql.json") as mysqlFile:
            mydb = connect(**load(mysqlFile))
        with mydb.cursor() as cursor:
            cursor.execute(sql, val)
            mydb.commit()
