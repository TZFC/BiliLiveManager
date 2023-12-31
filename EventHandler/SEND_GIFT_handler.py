from Utils.UnbanOnGift import unban_on_gift


async def handle_send_gift(event, database, master_config, room_info):
    room_id = event['room_display_id']
    # 解封用户
    if not room_info['room_config']["feature_flags"]["unban"]:
        return
    await unban_on_gift(sender_uid=event["data"]["data"]["uid"],
                        gift=event['data']['data']['giftName'],
                        room_id=room_id,
                        live_room=room_info['live_room'],
                        database=database)
