async def update_page(target, checkin_days, content):
    new_content = "\n".join([f"<p class=_{count}>{username} {count}/{checkin_days}</p>" for username, count in content])
    with open("web/ROOM_ID.html") as file:
        template = file.read()
    before, after = template.split("<p>")
    page = before + new_content + after
    with open(target, "w") as file:
        file.write(page)
