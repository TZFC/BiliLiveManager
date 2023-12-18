async def update_page(target, checkin_days, content):
    highest_count = content[0][-1]
    new_content = "\n".join([f'''<p class="{'top' if count == highest_count else "not_top"} {count}" id=_{rank + 1}>{username if username else uid} {count}/{checkin_days}</p>'''
                             for rank, (uid, username, count) in enumerate(content)])
    with open("web/ROOM_ID.html") as file:
        template = file.read()
    before, after = template.split("<p>")
    page = before + new_content + after
    with open(target, "w") as file:
        file.write(page)
