async def update_page(target, content):
    new_content = "\n\t".join([f"<p>{username} {count}/10</p>" for username, count in content])
    print(f"new_content{new_content}")
    with open("web/ROOM_ID.html") as file:
        template = file.read()
    before, after = template.split("<p>")
    page = before+new_content+after
    with open(target,"w") as file:
        file.write(page)