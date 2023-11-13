import json

from bilibili_api import sync
from mysql.connector import connect
from CredentialGetter import getCredential
#from Utils.EmailSender import sendEmail

# Hard coding 'tzfc' for now. Will iterate through user list when needed
credential = getCredential("tzfc")
if sync(credential.check_refresh()):
    sync(credential.refresh())
    val = (credential.sessdata, credential.bili_jct, credential.buvid3, credential.ac_time_value)
    sql = "UPDATE credentials SET sessdata = %s, bili_jct = %s, buvid3 = %s, ac_time_value = %s WHERE user = 'tzfc'"
    with connect(**json.load(open("./mysql.json"))) as mydb:
        with mydb.cursor() as cursor:
            cursor.execute(sql, val)
            mydb.commit()