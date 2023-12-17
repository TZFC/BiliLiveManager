from bilibili_api.user import User
from asyncio import sleep


async def uid2username(uid_count):
    user = User(uid=uid_count[0])
    info = await user.get_user_info()
    if not info['name']:
        await sleep(1)
        info = await user.get_user_info()
    return info['name'], uid_count[1]
