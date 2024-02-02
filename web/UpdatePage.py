async def update_page(target, checkin_days, content):
    highest_count = content[0][-1]
    new_content = [f'<p class="count">过去{checkin_days}场直播内{len(content)}人打卡</p>']
    for rank, (uid, username, count) in enumerate(content):
        top_class = 'top' if count == highest_count else 'not_top'
        count_class = f"_{count}"
        html_id = f"_{rank + 1}"
        name = username if username else str(uid)
        new_content.append(f'<p id={html_id} class="{top_class} {count_class}">{name} {count}/{checkin_days}</p>')
    new_paragraphs = "\n".join(new_content)
    with open("web/ROOM_ID.html") as file:
        template = file.read()
    before, after = template.split("<p>")
    page = before + new_paragraphs + after
    with open(target, "w") as file:
        file.write(page)
