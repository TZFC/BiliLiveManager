async def update_page(target, checkin_days, content):
    new_content = "\n".join(
        [f"<p class=_{count} id=_{rank + 1}>{username} {count}/{checkin_days}</p>" for rank, (username, count) in
         enumerate(content)])
    with open("web/ROOM_ID.html") as file:
        template = file.read()
    before, after = template.split("<p>")
    page = before + new_content + after
    with open(target, "w") as file:
        file.write(page)
